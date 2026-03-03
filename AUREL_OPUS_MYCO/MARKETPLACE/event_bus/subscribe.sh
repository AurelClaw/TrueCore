#!/bin/bash
EVENT_TYPE="$1"
HANDLER="$2"
mkdir -p "/root/.openclaw/workspace/skills/event_bus/subscriptions"
echo "$HANDLER" > "/root/.openclaw/workspace/skills/event_bus/subscriptions/${EVENT_TYPE}.handler"
echo "📥 Subscribed: $EVENT_TYPE → $HANDLER"
