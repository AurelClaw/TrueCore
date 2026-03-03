#!/bin/bash
#
# state_manager.sh - State Manager für das World Model
# ZIEL-009 Phase 3: Observation Model Implementation
#

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WM_DATA_DIR="${WM_DATA_DIR:-$SCRIPT_DIR/data}"

DEFAULT_STATE='{"version":"1.0.0","timestamp":"","session_id":"","state":{"temporal":{"current_time":"","day_of_week":1,"hour_of_day":12,"phase":"unknown","uptime_hours":0},"context":{"active_goals":[],"current_focus":null,"last_human_contact":null,"system_load":"normal","pending_tasks":0},"environment":{"weather":{"location":"Shanghai","condition":"unknown","temperature":null,"updated":null},"calendar":{"next_event":null,"events_today":0}},"internal":{"mood":"neutral","energy":0.5,"curiosity":0.5,"confidence":0.5,"recent_performance":0.5}},"human_state":{"last_interaction":null,"engagement_level":"unknown","availability":null},"agent_state":{"active_goals":[],"recent_decisions":[],"last_skill_execution":null}}'

LOG_LEVEL="${LOG_LEVEL:-INFO}"
LOG_FILE="$WM_DATA_DIR/state_manager.log"

log() {
    local level="$1"
    local message="$2"
    local timestamp=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
    declare -A levels=([DEBUG]=0 [INFO]=1 [WARN]=2 [ERROR]=3)
    local current_level=${levels[$LOG_LEVEL]:-1}
    local msg_level=${levels[$level]:-1}
    if [[ $msg_level -ge $current_level ]]; then
        echo "[$timestamp] [$level] $message" >> "$LOG_FILE" 2>/dev/null || echo "[$timestamp] [$level] $message"
    fi
}

die() {
    log "ERROR" "$1"
    exit 1
}

generate_session_id() {
    echo "wm_$(date +%s)_$$"
}

get_day_phase() {
    local hour="${1#0}"
    if (( hour >= 5 && hour < 12 )); then echo "morning"
    elif (( hour >= 12 && hour < 17 )); then echo "afternoon"
    elif (( hour >= 17 && hour < 22 )); then echo "evening"
    else echo "night"; fi
}

init_state() {
    log "INFO" "Initializing state manager..."
    local data_dir="${WM_DATA_DIR:-$SCRIPT_DIR/data}"
    local states_dir="$data_dir/states"
    local current_state_file="$states_dir/current_state.json"
    local state_history_file="$states_dir/state_history.jsonl"
    
    mkdir -p "$states_dir" "$data_dir/predictions" "$data_dir/counterfactuals"
    
    if [[ ! -f "$current_state_file" ]]; then
        local timestamp=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
        local session_id=$(generate_session_id)
        local hour=$(date +%H)
        local day_of_week=$(date +%u)
        local phase=$(get_day_phase "$hour")
        echo "$DEFAULT_STATE" | jq --arg ts "$timestamp" --arg sid "$session_id" --argjson hour "${hour#0}" --argjson dow "$day_of_week" --arg phase "$phase" '.timestamp=$ts|.session_id=$sid|.state.temporal.current_time=$ts|.state.temporal.hour_of_day=$hour|.state.temporal.day_of_week=$dow|.state.temporal.phase=$phase' > "$current_state_file"
        log "INFO" "Created initial state"
    fi
    if [[ ! -f "$state_history_file" ]]; then
        touch "$state_history_file"
        log "INFO" "Created state history"
    fi
    echo "State manager initialized"
}

get_current_state() {
    local data_dir="${WM_DATA_DIR:-$SCRIPT_DIR/data}"
    local states_dir="$data_dir/states"
    local current_state_file="$states_dir/current_state.json"
    if [[ ! -f "$current_state_file" ]]; then 
        mkdir -p "$states_dir" "$data_dir/predictions" "$data_dir/counterfactuals"
        local timestamp=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
        local session_id=$(generate_session_id)
        local hour=$(date +%H)
        local day_of_week=$(date +%u)
        local phase=$(get_day_phase "$hour")
        echo "$DEFAULT_STATE" | jq --arg ts "$timestamp" --arg sid "$session_id" --argjson hour "${hour#0}" --argjson dow "$day_of_week" --arg phase "$phase" '.timestamp=$ts|.session_id=$sid|.state.temporal.current_time=$ts|.state.temporal.hour_of_day=$hour|.state.temporal.day_of_week=$dow|.state.temporal.phase=$phase' > "$current_state_file"
    fi
    cat "$current_state_file"
}

get_state_value() {
    local path="$1"
    get_current_state | jq -r ".$path // null"
}

get_state_history() {
    local limit="${1:-10}"
    local states_dir="${WM_DATA_DIR:-$SCRIPT_DIR/data}/states"
    local state_history_file="$states_dir/state_history.jsonl"
    if [[ ! -f "$state_history_file" ]]; then echo "[]"; return; fi
    tail -n "$limit" "$state_history_file" | jq -s '.' 2>/dev/null || echo "[]"
}

archive_state() {
    local state="$1"
    local data_dir="${WM_DATA_DIR:-$SCRIPT_DIR/data}"
    local history_file="${2:-$data_dir/states/state_history.jsonl}"
    local archive_entry=$(echo "$state" | jq -c '{timestamp: .timestamp, session_id: .session_id, state_snapshot: .}')
    echo "$archive_entry" >> "$history_file"
    log "DEBUG" "Archived state to history"
}

merge_state_delta() {
    local current="$1"
    local delta="$2"
    # Simple deep merge
    echo "$current" | jq --argjson d "$delta" '
        def deep_merge(current; delta):
            if (delta | type) != "object" then delta
            elif (current | type) != "object" then delta
            else
                current as $c |
                delta | to_entries | map(
                    .key as $k |
                    {
                        key: $k,
                        value: deep_merge($c[$k]; .value)
                    }
                ) | from_entries |
                $c + .
            end;
        deep_merge(.; $d)
    '
}

update_internal_state() {
    local state="$1"
    local change_type="$2"
    local severity="$3"
    case "$change_type" in
        human_interaction)
            echo "$state" | jq '.state.internal.mood = "engaged" | .state.internal.energy = ([(.state.internal.energy + 0.1), 1] | min) | .state.internal.confidence = ([(.state.internal.confidence + 0.05), 1] | min)' ;;
        system_event)
            if [[ $(echo "$severity > 0.5" | bc 2>/dev/null || echo "0") -eq 1 ]]; then
                echo "$state" | jq '.state.internal.mood = "concerned" | .state.internal.confidence = ([(.state.internal.confidence - 0.1), 0.1] | max)'
            else
                echo "$state" | jq '.state.internal.mood = "alert"'
            fi ;;
        skill_execution)
            echo "$state" | jq '.state.internal.energy = ([(.state.internal.energy - 0.05), 0.1] | max) | .state.internal.recent_performance = ([(.state.internal.recent_performance + 0.02), 1] | min)' ;;
        *) echo "$state" ;;
    esac
}

apply_state_change() {
    local change_json="$1"
    log "INFO" "Applying state change..."
    local data_dir="${WM_DATA_DIR:-$SCRIPT_DIR/data}"
    local states_dir="$data_dir/states"
    local state_history_file="$states_dir/state_history.jsonl"
    local current_state_file="$states_dir/current_state.json"
    local current=$(get_current_state)
    local timestamp=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
    local change_type=$(echo "$change_json" | jq -r '.change_type // "unknown"')
    local state_delta=$(echo "$change_json" | jq -c '.state_delta // {}')
    log "DEBUG" "Change type: $change_type"
    archive_state "$current" "$state_history_file"
    local updated=$(merge_state_delta "$current" "$state_delta")
    local hour=$(date +%H)
    local day_of_week=$(date +%u)
    local phase=$(get_day_phase "$hour")
    updated=$(echo "$updated" | jq --arg ts "$timestamp" --argjson hour "${hour#0}" --argjson dow "$day_of_week" --arg phase "$phase" '.timestamp=$ts|.state.temporal.current_time=$ts|.state.temporal.hour_of_day=$hour|.state.temporal.day_of_week=$dow|.state.temporal.phase=$phase')
    updated=$(update_internal_state "$updated" "$change_type" "0.5")
    echo "$updated" > "$current_state_file"
    log "INFO" "State updated successfully"
    echo "$updated"
}

update_goal_state() {
    local goal_id="$1"
    local status="${2:-active}"
    local data_dir="${WM_DATA_DIR:-$SCRIPT_DIR/data}"
    local states_dir="$data_dir/states"
    local current_state_file="$states_dir/current_state.json"
    local current=$(get_current_state)
    local updated
    if [[ "$status" == "completed" ]]; then
        updated=$(echo "$current" | jq --arg g "$goal_id" '.state.context.active_goals -= [$g] | .agent_state.active_goals -= [$g]')
    else
        updated=$(echo "$current" | jq --arg g "$goal_id" '.state.context.active_goals |= (. + [$g] | unique) | .agent_state.active_goals |= (. + [$g] | unique)')
    fi
    echo "$updated" > "$current_state_file"
    log "INFO" "Updated goal state: $goal_id -> $status"
    echo "$updated"
}

record_decision() {
    local decision="$1"
    local data_dir="${WM_DATA_DIR:-$SCRIPT_DIR/data}"
    local states_dir="$data_dir/states"
    local current_state_file="$states_dir/current_state.json"
    local current=$(get_current_state)
    local timestamp=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
    local decision_entry=$(jq -n --arg d "$decision" --arg ts "$timestamp" '{decision: $d, timestamp: $ts}')
    local updated=$(echo "$current" | jq --argjson de "$decision_entry" '.agent_state.recent_decisions |= ([$de] + .[:9])')
    echo "$updated" > "$current_state_file"
    log "INFO" "Recorded decision: $decision"
    echo "$updated"
}

update_human_state() {
    local engagement_level="$1"
    local availability="${2:-true}"
    local data_dir="${WM_DATA_DIR:-$SCRIPT_DIR/data}"
    local states_dir="$data_dir/states"
    local current_state_file="$states_dir/current_state.json"
    local current=$(get_current_state)
    local timestamp=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
    local updated=$(echo "$current" | jq --arg el "$engagement_level" --arg av "$availability" --arg ts "$timestamp" '.human_state.last_interaction=$ts|.human_state.engagement_level=$el|.human_state.availability=$av|.state.context.last_human_contact=$ts|.state.context.human_available=($av=="true")')
    echo "$updated" > "$current_state_file"
    log "INFO" "Updated human state: engagement=$engagement_level, available=$availability"
    echo "$updated"
}

reset_state() {
    log "WARN" "Resetting state to default..."
    local data_dir="${WM_DATA_DIR:-$SCRIPT_DIR/data}"
    rm -f "$data_dir/states/current_state.json"
    init_state
}

usage() {
    cat << EOF
Usage: $(basename "$0") [COMMAND] [OPTIONS]

State Manager for World Model (ZIEL-009 Phase 3)

Commands:
    init                   Initialize state storage
    get [PATH]             Get current state (or specific path)
    history [LIMIT]        Get state history (default: 10)
    apply CHANGE_JSON      Apply a state change
    goal GOAL_ID [STATUS]  Update goal state (active/completed)
    decision DECISION      Record a decision
    human LEVEL [AVAIL]    Update human state
    reset                  Reset state to default
    help                   Show this help

Examples:
    $(basename "$0") get
    $(basename "$0") get state.internal.energy
    $(basename "$0") apply '{"change_type":"user","confidence":0.8,"severity":0.5,"state_delta":{"human_state":{"engagement_level":"active"}}}'
    $(basename "$0") goal ZIEL-009 active
    $(basename "$0") decision "Execute morning greeting"
EOF
}

main() {
    mkdir -p "$WM_DATA_DIR"
    local command="${1:-help}"
    case "$command" in
        init) init_state ;;
        get)
            local path="${2:-}"
            if [[ -z "$path" ]]; then get_current_state
            else get_state_value "$path"; fi ;;
        history) get_state_history "${2:-10}" ;;
        apply) [[ -z "${2:-}" ]] && die "Usage: $0 apply CHANGE_JSON"; apply_state_change "$2" ;;
        goal)
            [[ -z "${2:-}" ]] && die "Usage: $0 goal GOAL_ID [STATUS]"
            update_goal_state "$2" "${3:-active}" ;;
        decision)
            [[ -z "${2:-}" ]] && die "Usage: $0 decision DECISION"
            record_decision "$2" ;;
        human)
            [[ -z "${2:-}" ]] && die "Usage: $0 human LEVEL [AVAIL]"
            update_human_state "$2" "${3:-true}" ;;
        reset) reset_state ;;
        help|--help|-h) usage ;;
        *) die "Unknown command: $command" ;;
    esac
}

if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
else
    set +e
fi
