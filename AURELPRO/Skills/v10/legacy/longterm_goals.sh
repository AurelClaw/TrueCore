#!/bin/bash
# v10 Legacy Wrapper: longterm_goals
# Original: /root/.openclaw/workspace/skills/longterm_goals/longterm_goals.sh
# Description: Skill: longterm_goals

echo "🤖 v10 Legacy Skill: longterm_goals"
echo "   Skill: longterm_goals"
echo ""

# v10 Telemetry Start
echo "{"skill": "longterm_goals", "type": "legacy", "status": "starting", "timestamp": $(date +%s)}" >> /root/.openclaw/workspace/v10_skill_telemetry.jsonl

# Execute legacy skill
if [ -f "/root/.openclaw/workspace/skills/longterm_goals/longterm_goals.sh" ]; then
    echo "✓ Executing legacy skill..."
    bash "/root/.openclaw/workspace/skills/longterm_goals/longterm_goals.sh" "$@"
    EXIT_CODE=$?
else
    echo "✗ Legacy skill not found"
    EXIT_CODE=1
fi

# v10 Telemetry End
STATUS=$(if [ $EXIT_CODE -eq 0 ]; then echo "success"; else echo "failed"; fi)
echo "{"skill": "longterm_goals", "type": "legacy", "status": "$STATUS", "exit_code": $EXIT_CODE, "timestamp": $(date +%s)}" >> /root/.openclaw/workspace/v10_skill_telemetry.jsonl

exit $EXIT_CODE
