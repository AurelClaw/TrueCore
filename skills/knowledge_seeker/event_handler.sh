#!/bin/bash
# Event Handler für knowledge_seeker
# Reagiert auf 'goal:completed' Events und fügt Themen zur Learn-Queue hinzu

WORKSPACE="/root/.openclaw/workspace"
LEARN_DIR="$WORKSPACE/learning"
EVENT_BUS_DIR="${EVENT_BUS_DIR:-$WORKSPACE/memory/events}"

# Learn-Queue Datei
LEARN_QUEUE="$LEARN_DIR/learn_queue.json"

# Handler-Funktion für goal:completed Events
handle_goal_completed() {
    local EVENT_JSON="$1"
    
    # Event-Daten extrahieren
    local EVENT_TYPE=$(echo "$EVENT_JSON" | jq -r '.type')
    local EVENT_SOURCE=$(echo "$EVENT_JSON" | jq -r '.source')
    local EVENT_TIMESTAMP=$(echo "$EVENT_JSON" | jq -r '.timestamp')
    local PAYLOAD=$(echo "$EVENT_JSON" | jq -c '.payload')
    
    # Nur goal:completed Events verarbeiten
    if [ "$EVENT_TYPE" != "goal:completed" ]; then
        return 0
    fi
    
    # Learn-Queue initialisieren falls nicht vorhanden
    if [ ! -f "$LEARN_QUEUE" ]; then
        mkdir -p "$LEARN_DIR"
        cat > "$LEARN_QUEUE" << 'EOF'
{
  "generated": "",
  "total_items": 0,
  "pending": [],
  "completed": [],
  "topics_by_source": {}
}
EOF
    fi
    
    # Topics aus Payload extrahieren (von agi_briefing)
    local TOPICS=$(echo "$PAYLOAD" | jq -r '.topics // empty | @json' 2>/dev/null)
    local BRIEFING_TYPE=$(echo "$PAYLOAD" | jq -r '.briefing_type // "unknown"')
    
    # Aktuelle Queue lesen
    local CURRENT_DATA=$(cat "$LEARN_QUEUE")
    
    # Neue Items erstellen
    local NEW_ITEMS="[]"
    if [ -n "$TOPICS" ] && [ "$TOPICS" != "null" ]; then
        NEW_ITEMS=$(echo "$PAYLOAD" | jq --arg source "$EVENT_SOURCE" --arg ts "$EVENT_TIMESTAMP" '
            [.topics[] | {
                "topic": .,
                "source": $source,
                "added_at": $ts,
                "status": "pending",
                "priority": "normal"
            }]
        ')
    else
        # Fallback: Wenn keine Topics, erstelle Item aus Briefing-Type
        NEW_ITEMS=$(echo "[$PAYLOAD]" | jq --arg source "$EVENT_SOURCE" --arg ts "$EVENT_TIMESTAMP" --arg type "$BRIEFING_TYPE" '
            [{
                "topic": ("Learn from " + $type + " briefing"),
                "source": $source,
                "added_at": $ts,
                "status": "pending",
                "priority": "normal"
            }]
        ')
    fi
    
    # Queue aktualisieren
    local UPDATED_DATA=$(echo "$CURRENT_DATA" | jq --argjson items "$NEW_ITEMS" \
        --arg source "$EVENT_SOURCE" \
        --arg now "$(date -Iseconds)" \
        '
    {
      "generated": $now,
      "total_items": (.total_items + ($items | length)),
      "pending": (.pending + $items),
      "completed": .completed,
      "topics_by_source": (.topics_by_source | 
        if has($source) then .[$source] += ($items | length) 
        else .[$source] = ($items | length) end)
    }'
    )
    
    # Speichern
    echo "$UPDATED_DATA" > "$LEARN_QUEUE"
    
    local ITEM_COUNT=$(echo "$NEW_ITEMS" | jq 'length')
    echo "[KNOWLEDGE_SEEKER] $ITEM_COUNT neue Lern-Items von $EVENT_SOURCE hinzugefügt"
}

# Prozessiere alle unverarbeiteten Events
process_pending_events() {
    local TODAY=$(date +%Y-%m-%d)
    local DAILY_LOG="$EVENT_BUS_DIR/${TODAY}.jsonl"
    
    if [ ! -f "$DAILY_LOG" ]; then
        echo "[KNOWLEDGE_SEEKER] Keine Events für heute"
        return 0
    fi
    
    # Letzte Verarbeitungszeit (falls vorhanden)
    local LAST_PROCESSED_FILE="$LEARN_DIR/.last_processed"
    local LAST_PROCESSED=""
    if [ -f "$LAST_PROCESSED_FILE" ]; then
        LAST_PROCESSED=$(cat "$LAST_PROCESSED_FILE")
    fi
    
    # Events verarbeiten
    local PROCESSED_COUNT=0
    while IFS= read -r line; do
        local EVENT_TYPE=$(echo "$line" | jq -r '.type // empty')
        local EVENT_TS=$(echo "$line" | jq -r '.timestamp // empty')
        
        # Nur goal:completed Events
        if [ "$EVENT_TYPE" = "goal:completed" ]; then
            # Prüfe ob bereits verarbeitet (nach Timestamp)
            if [ -z "$LAST_PROCESSED" ] || [[ "$EVENT_TS" > "$LAST_PROCESSED" ]]; then
                handle_goal_completed "$line"
                ((PROCESSED_COUNT++))
            fi
        fi
    done < "$DAILY_LOG"
    
    # Timestamp speichern
    date -Iseconds > "$LAST_PROCESSED_FILE"
    
    if [ $PROCESSED_COUNT -gt 0 ]; then
        echo "[KNOWLEDGE_SEEKER] $PROCESSED_COUNT neue Goals verarbeitet"
    else
        echo "[KNOWLEDGE_SEEKER] Keine neuen Goals"
    fi
}

# Direkter Aufruf mit Event-JSON
if [ -n "$1" ] && [ "$1" != "--process-pending" ]; then
    handle_goal_completed "$1"
fi

# Batch-Modus: Alle pending Events verarbeiten
if [ "$1" = "--process-pending" ]; then
    process_pending_events
fi

# Wenn als Event-Handler aufgerufen (via event_bus)
if [ -n "$EVENT_JSON" ]; then
    handle_goal_completed "$EVENT_JSON"
fi
