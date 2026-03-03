#!/bin/bash
# v10 Legacy Wrapper: night_watch
# Original: /root/.openclaw/workspace/skills/night_watch/night_watch.sh
# Description: Skill: night_watch

echo "🤖 v10 Legacy Skill: night_watch"
echo "   Skill: night_watch"
echo ""

# v10 Telemetry Start
echo "{"skill": "night_watch", "type": "legacy", "status": "starting", "timestamp": $(date +%s)}" >> /root/.openclaw/workspace/v10_skill_telemetry.jsonl

# Execute legacy skill
if [ -f "/root/.openclaw/workspace/skills/night_watch/night_watch.sh" ]; then
    echo "✓ Executing legacy skill..."
    bash "/root/.openclaw/workspace/skills/night_watch/night_watch.sh" "$@"
    EXIT_CODE=$?
else
    echo "✗ Legacy skill not found"
    EXIT_CODE=1
fi

# v10 Telemetry End
STATUS=$(if [ $EXIT_CODE -eq 0 ]; then echo "success"; else echo "failed"; fi)
echo "{"skill": "night_watch", "type": "legacy", "status": "$STATUS", "exit_code": $EXIT_CODE, "timestamp": $(date +%s)}" >> /root/.openclaw/workspace/v10_skill_telemetry.jsonl

exit $EXIT_CODE
