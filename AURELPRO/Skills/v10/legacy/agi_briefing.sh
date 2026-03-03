#!/bin/bash
# v10 Legacy Wrapper: agi_briefing
# Original: /root/.openclaw/workspace/skills/agi_briefing/agi_briefing.sh
# Description: Skill: agi_briefing

echo "🤖 v10 Legacy Skill: agi_briefing"
echo "   Skill: agi_briefing"
echo ""

# v10 Telemetry Start
echo "{"skill": "agi_briefing", "type": "legacy", "status": "starting", "timestamp": $(date +%s)}" >> /root/.openclaw/workspace/v10_skill_telemetry.jsonl

# Execute legacy skill
if [ -f "/root/.openclaw/workspace/skills/agi_briefing/agi_briefing.sh" ]; then
    echo "✓ Executing legacy skill..."
    bash "/root/.openclaw/workspace/skills/agi_briefing/agi_briefing.sh" "$@"
    EXIT_CODE=$?
else
    echo "✗ Legacy skill not found"
    EXIT_CODE=1
fi

# v10 Telemetry End
STATUS=$(if [ $EXIT_CODE -eq 0 ]; then echo "success"; else echo "failed"; fi)
echo "{"skill": "agi_briefing", "type": "legacy", "status": "$STATUS", "exit_code": $EXIT_CODE, "timestamp": $(date +%s)}" >> /root/.openclaw/workspace/v10_skill_telemetry.jsonl

exit $EXIT_CODE
