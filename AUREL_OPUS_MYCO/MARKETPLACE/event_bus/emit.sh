#!/bin/bash
EVENT_TYPE="$1"
PAYLOAD="${2:-{}}"
SOURCE="${3:-unknown}"
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
EVENT_FILE="/root/.openclaw/workspace/skills/event_bus/events/${EVENT_TYPE}_$(date +%s).json"
mkdir -p "$(dirname "$EVENT_FILE")"
cat > "$EVENT_FILE" << EOJSON
{
  "timestamp": "$TIMESTAMP",
  "type": "$EVENT_TYPE",
  "payload": $PAYLOAD,
  "source": "$SOURCE"
}
EOJSON
echo "📤 Event: $EVENT_TYPE"
