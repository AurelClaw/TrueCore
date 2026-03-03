#!/bin/bash
#
# observation_encoder.sh - Observation Encoder für das World Model
# ZIEL-009 Phase 3: Observation Model Implementation
#

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WM_DATA_DIR="${WM_DATA_DIR:-$SCRIPT_DIR/data}"
EVENTS_DIR="${EVENTS_DIR:-$SCRIPT_DIR/../data/events}"
MEMORY_DIR="${MEMORY_DIR:-$SCRIPT_DIR/../../memory}"
METRICS_DIR="${METRICS_DIR:-$SCRIPT_DIR/../effectiveness_tracker/metrics}"

LOG_LEVEL="${LOG_LEVEL:-INFO}"
LOG_FILE="${WM_DATA_DIR}/observation_encoder.log"

log() {
    local level="$1"
    local message="$2"
    local timestamp=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
    declare -A levels=([DEBUG]=0 [INFO]=1 [WARN]=2 [ERROR]=3)
    local current_level=${levels[$LOG_LEVEL]:-1}
    local msg_level=${levels[$level]:-1}
    if [[ $msg_level -ge $current_level ]]; then
        echo "[$timestamp] [$level] $message" | tee -a "$LOG_FILE" 2>/dev/null || echo "[$timestamp] [$level] $message"
    fi
}

die() {
    log "ERROR" "$1"
    exit 1
}

discover_event_sources() {
    local sources=()
    if [[ -d "$EVENTS_DIR" ]]; then sources+=("$EVENTS_DIR"); fi
    if [[ -d "$MEMORY_DIR" ]]; then sources+=("$MEMORY_DIR"); fi
    if [[ -d "$METRICS_DIR" ]]; then sources+=("$METRICS_DIR"); fi
    printf '%s\n' "${sources[@]}"
}

read_events_from_source() {
    local source="$1"
    log "DEBUG" "Reading events from: $source"
    if [[ -d "$source" ]]; then
        find "$source" -type f \( -name "*.json" -o -name "*.jsonl" -o -name "*.md" -o -name "*.log" \) 2>/dev/null | head -100
    fi
}

detect_event_type() {
    local filename=$(basename "$1" | tr '[:upper:]' '[:lower:]')
    if [[ "$filename" == *"cron"* ]] || [[ "$filename" == *"heartbeat"* ]]; then echo "cron"
    elif [[ "$filename" == *"user"* ]] || [[ "$filename" == *"human"* ]] || [[ "$filename" == *"message"* ]]; then echo "user"
    elif [[ "$filename" == *"system"* ]] || [[ "$filename" == *"error"* ]]; then echo "system"
    elif [[ "$filename" == *"skill"* ]] || [[ "$filename" == *"autonom"* ]]; then echo "skill"
    else echo "unknown"; fi
}

parse_json_event() {
    local file="$1"
    local event_type="$2"
    local timestamp="$3"
    if [[ ! -f "$file" ]]; then echo "null"; return; fi
    local content=$(cat "$file" 2>/dev/null || echo "{}")
    if ! echo "$content" | jq -e . >/dev/null 2>&1; then log "WARN" "Invalid JSON in $file"; echo "null"; return; fi
    jq -n --arg type "$event_type" --arg ts "$timestamp" --arg source "$file" --argjson content "$content" \
        '{event_id: ($source | gsub("[^a-zA-Z0-9]"; "_")), timestamp: ($content.timestamp // $ts), event_type: ($content.type // $content.event_type // $type), source: $source, payload: ($content | del(.timestamp, .type, .event_type)), raw_content: $content}'
}

parse_text_event() {
    local file="$1"
    local event_type="$2"
    local timestamp="$3"
    if [[ ! -f "$file" ]]; then echo "null"; return; fi
    local content=$(head -50 "$file" 2>/dev/null || echo "")
    local filename=$(basename "$file")
    local extracted_type="$event_type"
    local confidence=0.5
    if echo "$content" | grep -qi "cron\|scheduled\|heartbeat"; then extracted_type="cron"; confidence=0.8
    elif echo "$content" | grep -qi "user\|human\|message\|chat"; then extracted_type="user"; confidence=0.8
    elif echo "$content" | grep -qi "error\|fail\|exception"; then extracted_type="system"; confidence=0.9
    elif echo "$content" | grep -qi "skill\|execution\|autonom"; then extracted_type="skill"; confidence=0.7; fi
    local title=$(echo "$content" | head -1 | sed 's/^#* *//' | cut -c1-100)
    jq -n --arg type "$extracted_type" --arg ts "$timestamp" --arg source "$file" --arg title "$title" --argjson conf "$confidence" \
        '{event_id: ($source | gsub("[^a-zA-Z0-9]"; "_")), timestamp: $ts, event_type: $type, source: $source, confidence: $conf, payload: {title: $title, content_preview: $title}, raw_content: null}'
}

parse_event() {
    local event_file="$1"
    local event_type="${2:-auto}"
    log "DEBUG" "Parsing event: $event_file (type: $event_type)"
    local filename=$(basename "$event_file")
    local timestamp=$(stat -c %Y "$event_file" 2>/dev/null || stat -f %m "$event_file" 2>/dev/null || echo "0")
    local iso_timestamp=$(date -u -d "@$timestamp" +"%Y-%m-%dT%H:%M:%SZ" 2>/dev/null || date -u +"%Y-%m-%dT%H:%M:%SZ")
    if [[ "$event_type" == "auto" ]]; then event_type=$(detect_event_type "$event_file"); fi
    case "${filename##*.}" in
        json|jsonl) parse_json_event "$event_file" "$event_type" "$iso_timestamp" ;;
        md|log) parse_text_event "$event_file" "$event_type" "$iso_timestamp" ;;
        *) log "WARN" "Unknown file type: ${filename##*.}"; echo "null" ;;
    esac
}

encode_cron_state_change() {
    local event="$1"
    local base_confidence="$2"
    local timestamp=$(echo "$event" | jq -r '.timestamp')
    local hour=$(date -d "$timestamp" +%H 2>/dev/null || echo "12")
    jq -n --arg ts "$timestamp" --argjson conf "$base_confidence" --argjson hour "$hour" \
        '{timestamp: $ts, change_type: "temporal", confidence: $conf, state_delta: {context: {hour_of_day: $hour, last_cron_execution: $ts}, internal: {system_health: "operational"}}, affected_dimensions: ["temporal", "context"], severity: 0.1}'
}

encode_user_state_change() {
    local event="$1"
    local base_confidence="$2"
    local timestamp=$(echo "$event" | jq -r '.timestamp')
    local payload=$(echo "$event" | jq -r '.payload // {}')
    jq -n --arg ts "$timestamp" --argjson conf "$base_confidence" --argjson payload "$payload" \
        '{timestamp: $ts, change_type: "human_interaction", confidence: $conf, state_delta: {human_state: {last_interaction: $ts, engagement_level: "active"}, context: {human_available: true}}, affected_dimensions: ["human_state", "context"], severity: 0.5}'
}

encode_system_state_change() {
    local event="$1"
    local base_confidence="$2"
    local timestamp=$(echo "$event" | jq -r '.timestamp')
    local payload=$(echo "$event" | jq '.payload // {}')
    local is_error=$(echo "$payload" | jq -r 'if has("error") or has("exception") then 1 else 0 end')
    local severity=$(if [[ "$is_error" == "1" ]]; then echo "0.8"; else echo "0.3"; fi)
    jq -n --arg ts "$timestamp" --argjson conf "$base_confidence" --argjson sev "$severity" \
        '{timestamp: $ts, change_type: "system_event", confidence: $conf, state_delta: {internal: {system_health: (if $sev > 0.5 then "degraded" else "good" end), last_alert: $ts}}, affected_dimensions: ["internal"], severity: $sev}'
}

encode_skill_state_change() {
    local event="$1"
    local base_confidence="$2"
    local timestamp=$(echo "$event" | jq -r '.timestamp')
    local payload=$(echo "$event" | jq '.payload // {}')
    jq -n --arg ts "$timestamp" --argjson conf "$base_confidence" \
        '{timestamp: $ts, change_type: "skill_execution", confidence: $conf, state_delta: {agent_state: {last_skill_execution: $ts, recent_decisions: [$ts]}, context: {active_goals: []}}, affected_dimensions: ["agent_state"], severity: 0.3}'
}

encode_generic_state_change() {
    local event="$1"
    local base_confidence="$2"
    local timestamp=$(echo "$event" | jq -r '.timestamp // empty')
    if [[ -z "$timestamp" ]]; then timestamp=$(date -u +"%Y-%m-%dT%H:%M:%SZ"); fi
    jq -n --arg ts "$timestamp" --argjson conf "$base_confidence" \
        '{timestamp: $ts, change_type: "unknown", confidence: ($conf * 0.5), state_delta: {}, affected_dimensions: [], severity: 0.1}'
}

encode_state_change() {
    local event_json="$1"
    if [[ "$event_json" == "null" ]] || [[ -z "$event_json" ]]; then echo "null"; return; fi
    local event_type=$(echo "$event_json" | jq -r '.event_type // "unknown"')
    local confidence=$(echo "$event_json" | jq -r '.confidence // 0.7')
    log "DEBUG" "Encoding state change for event type: $event_type"
    case "$event_type" in
        cron) encode_cron_state_change "$event_json" "$confidence" ;;
        user) encode_user_state_change "$event_json" "$confidence" ;;
        system) encode_system_state_change "$event_json" "$confidence" ;;
        skill) encode_skill_state_change "$event_json" "$confidence" ;;
        *) encode_generic_state_change "$event_json" "$confidence" ;;
    esac
}

# ============================================================================
# MAIN FUNCTIONS
# ============================================================================

process_single_event() {
    local event_file="$1"
    local event_type="${2:-auto}"
    
    log "INFO" "Processing single event: $event_file"
    
    local parsed=$(parse_event "$event_file" "$event_type")
    if [[ "$parsed" == "null" ]]; then
        log "WARN" "Failed to parse event: $event_file"
        return 1
    fi
    
    local state_change=$(encode_state_change "$parsed")
    if [[ "$state_change" == "null" ]]; then
        log "WARN" "Failed to encode state change for: $event_file"
        return 1
    fi
    
    # Combine event and state change
    jq -n --argjson event "$parsed" --argjson change "$state_change" \
        '{event: $event, state_change: $change, processed_at: now | todate}'
}

process_all_events() {
    local since="${1:-}"
    local limit="${2:-50}"
    
    log "INFO" "Processing all events (limit: $limit)"
    
    local all_results="[]"
    local count=0
    
    while IFS= read -r source; do
        [[ -z "$source" ]] && continue
        log "INFO" "Processing source: $source"
        
        while IFS= read -r event_file; do
            [[ -z "$event_file" ]] && continue
            [[ $count -ge $limit ]] && break
            
            local result=$(process_single_event "$event_file" "auto" 2>/dev/null)
            if [[ -n "$result" ]] && [[ "$result" != "null" ]]; then
                all_results=$(echo "$all_results" | jq --argjson r "$result" '. + [$r]')
                ((count++))
            fi
        done < <(read_events_from_source "$source")
        
        [[ $count -ge $limit ]] && break
    done < <(discover_event_sources)
    
    # Output summary
    jq -n \
        --argjson results "$all_results" \
        --arg count "$count" \
        --arg timestamp "$(date -u +"%Y-%m-%dT%H:%M:%SZ")" \
        '{
            batch_id: ("batch_" + ($timestamp | gsub("[^0-9]"; ""))),
            timestamp: $timestamp,
            processed_count: ($count | tonumber),
            events: $results
        }'
}

# ============================================================================
# CLI INTERFACE
# ============================================================================

usage() {
    cat << EOF
Usage: $(basename "$0") [COMMAND] [OPTIONS]

Observation Encoder for World Model (ZIEL-009 Phase 3)

Commands:
    encode FILE [TYPE]     Encode a single event file
    batch [LIMIT]          Process all events (default limit: 50)
    sources                List discovered event sources
    test                   Run self-tests
    help                   Show this help message

Options:
    --debug                Enable debug logging
    --log-level LEVEL      Set log level (DEBUG, INFO, WARN, ERROR)

Examples:
    $(basename "$0") encode memory/2026-03-02.md
    $(basename "$0") batch 100
    $(basename "$0") sources
EOF
}

main() {
    # Ensure data directory exists
    mkdir -p "$WM_DATA_DIR"
    
    local command="${1:-help}"
    
    case "$command" in
        encode)
            [[ -z "${2:-}" ]] && die "Usage: $0 encode FILE [TYPE]"
            local file="$2"
            local type="${3:-auto}"
            [[ ! -f "$file" ]] && die "File not found: $file"
            process_single_event "$file" "$type"
            ;;
            
        batch)
            local limit="${2:-50}"
            process_all_events "" "$limit"
            ;;
            
        sources)
            log "INFO" "Discovered event sources:"
            discover_event_sources
            ;;
            
        test)
            echo "Running observation encoder tests..."
            echo "Tests implemented in test_observation.sh"
            ;;
            
        help|--help|-h)
            usage
            ;;
            
        *)
            die "Unknown command: $command. Use '$0 help' for usage."
            ;;
    esac
}

# Run main if executed directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
else
    # Being sourced - don't exit on error
    set +e
fi
