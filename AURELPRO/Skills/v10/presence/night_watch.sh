#!/bin/bash
# v10 Skill Wrapper: night_watch
# Original: /root/.openclaw/workspace/skills/night_watch/night_watch.sh
# Imported: v10 System

echo "🤖 v10 Skill: night_watch"
echo "   Description: Presence and proactive behavior"
echo "   Type: shell"
echo ""

# v10 Telemetry Start
echo "{"skill": "night_watch", "status": "starting", "timestamp": $(date +%s)}" >> /root/.openclaw/workspace/v10_skill_telemetry.jsonl

# Execute original skill
if [ -f "/root/.openclaw/workspace/skills/night_watch/night_watch.sh" ]; then
    echo "✓ Executing original skill..."
    bash "/root/.openclaw/workspace/skills/night_watch/night_watch.sh" "$@"
    EXIT_CODE=$?
else
    echo "✗ Original skill not found: /root/.openclaw/workspace/skills/night_watch/night_watch.sh"
    EXIT_CODE=1
fi

# v10 Telemetry End
STATUS=$(if [ $EXIT_CODE -eq 0 ]; then echo "success"; else echo "failed"; fi)
echo "{"skill": "night_watch", "status": "$STATUS", "exit_code": $EXIT_CODE, "timestamp": $(date +%s)}" >> /root/.openclaw/workspace/v10_skill_telemetry.jsonl

exit $EXIT_CODE
