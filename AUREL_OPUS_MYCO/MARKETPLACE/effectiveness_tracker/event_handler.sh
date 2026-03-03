#!/bin/bash
# Event Handler für effectiveness_tracker
# Reagiert auf 'metric:recorded' Events und aggregiert Metriken

WORKSPACE="/root/.openclaw/workspace"
METRICS_DIR="$WORKSPACE/metrics"
EVENT_BUS_DIR="${EVENT_BUS_DIR:-$WORKSPACE/memory/events}"

# Effectiveness-Metriken-Datei
EFFECTIVENESS_FILE="$METRICS_DIR/effectiveness.json"

# Handler-Funktion für metric:recorded Events
handle_metric_recorded() {
    local EVENT_JSON="$1"
    
    # Event-Daten extrahieren
    local EVENT_TYPE=$(echo "$EVENT_JSON" | jq -r '.type')
    local EVENT_SOURCE=$(echo "$EVENT_JSON" | jq -r '.source')
    local EVENT_TIMESTAMP=$(echo "$EVENT_JSON" | jq -r '.timestamp')
    local PAYLOAD=$(echo "$EVENT_JSON" | jq -c '.payload')
    
    # Nur metric:recorded Events verarbeiten
    if [ "$EVENT_TYPE" != "metric:recorded" ]; then
        return 0
    fi
    
    # Effectiveness-Datei initialisieren falls nicht vorhanden
    if [ ! -f "$EFFECTIVENESS_FILE" ]; then
        mkdir -p "$METRICS_DIR"
        cat > "$EFFECTIVENESS_FILE" << 'EOF'
{
  "generated": "",
  "total_metrics": 0,
  "metrics_by_source": {},
  "metrics_by_day": {},
  "latest_metrics": [],
  "aggregation": {
    "cron_jobs_total": 0,
    "synthesis_count": 0,
    "memory_files_tracked": 0
  }
}
EOF
    fi
    
    # Aktuelle Daten lesen
    local CURRENT_DATA=$(cat "$EFFECTIVENESS_FILE")
    
    # Datum aus Timestamp extrahieren
    local EVENT_DATE=$(echo "$EVENT_TIMESTAMP" | cut -d'T' -f1)
    
    # Neue Metrik erstellen
    local NEW_METRIC=$(cat <<EOF
{
  "timestamp": "$EVENT_TIMESTAMP",
  "source": "$EVENT_SOURCE",
  "payload": $PAYLOAD
}
EOF
)
    
    # JSON aktualisieren
    local UPDATED_DATA=$(echo "$CURRENT_DATA" | jq --arg date "$EVENT_DATE" \
        --arg source "$EVENT_SOURCE" \
        --argjson metric "$NEW_METRIC" \
        --arg now "$(date -Iseconds)" \
        '
    {
      "generated": $now,
      "total_metrics": (.total_metrics + 1),
      "metrics_by_source": (.metrics_by_source | 
        if has($source) then .[$source] += 1 else .[$source] = 1 end),
      "metrics_by_day": (.metrics_by_day | 
        if has($date) then .[$date] += 1 else .[$date] = 1 end),
      "latest_metrics": ([$metric] + .latest_metrics | .[0:50]),
      "aggregation": {
        "cron_jobs_total": (.aggregation.cron_jobs_total + 
          if ($metric.payload.cron_jobs | length) > 0 then 
            ($metric.payload.cron_jobs | length) else 0 end),
        "synthesis_count": (.aggregation.synthesis_count + 
          if $source == "orchestrator_v2" then 1 else 0 end),
        "memory_files_tracked": (.aggregation.memory_files_tracked + 
          if ($metric.payload.memory_files | length) > 0 then 
            ($metric.payload.memory_files | length) else 0 end)
      }
    }'
    )
    
    # Speichern
    echo "$UPDATED_DATA" > "$EFFECTIVENESS_FILE"
    
    echo "[EFFECTIVENESS] Metric recorded from $EVENT_SOURCE"
}

# Prozessiere alle unverarbeiteten Events
process_pending_events() {
    local TODAY=$(date +%Y-%m-%d)
    local DAILY_LOG="$EVENT_BUS_DIR/${TODAY}.jsonl"
    
    if [ ! -f "$DAILY_LOG" ]; then
        echo "[EFFECTIVENESS] Keine Events für heute"
        return 0
    fi
    
    # Letzte Verarbeitungszeit (falls vorhanden)
    local LAST_PROCESSED_FILE="$METRICS_DIR/.last_processed"
    local LAST_PROCESSED=""
    if [ -f "$LAST_PROCESSED_FILE" ]; then
        LAST_PROCESSED=$(cat "$LAST_PROCESSED_FILE")
    fi
    
    # Events verarbeiten
    local PROCESSED_COUNT=0
    while IFS= read -r line; do
        local EVENT_TYPE=$(echo "$line" | jq -r '.type // empty')
        local EVENT_TS=$(echo "$line" | jq -r '.timestamp // empty')
        
        # Nur metric:recorded Events
        if [ "$EVENT_TYPE" = "metric:recorded" ]; then
            # Prüfe ob bereits verarbeitet (nach Timestamp)
            if [ -z "$LAST_PROCESSED" ] || [[ "$EVENT_TS" > "$LAST_PROCESSED" ]]; then
                handle_metric_recorded "$line"
                ((PROCESSED_COUNT++))
            fi
        fi
    done < "$DAILY_LOG"
    
    # Timestamp speichern
    date -Iseconds > "$LAST_PROCESSED_FILE"
    
    if [ $PROCESSED_COUNT -gt 0 ]; then
        echo "[EFFECTIVENESS] $PROCESSED_COUNT neue Metriken verarbeitet"
    else
        echo "[EFFECTIVENESS] Keine neuen Metriken"
    fi
}

# Direkter Aufruf mit Event-JSON
if [ -n "$1" ] && [ "$1" != "--process-pending" ]; then
    handle_metric_recorded "$1"
fi

# Batch-Modus: Alle pending Events verarbeiten
if [ "$1" = "--process-pending" ]; then
    process_pending_events
fi

# Wenn als Event-Handler aufgerufen (via event_bus)
if [ -n "$EVENT_JSON" ]; then
    handle_metric_recorded "$EVENT_JSON"
fi
