#!/bin/bash
# v10 Skill Wrapper: longterm_goals
# Original: /root/.openclaw/workspace/skills/longterm_goals/longterm_goals.sh
# Imported: v10 System

echo "🤖 v10 Skill: longterm_goals"
echo "   Description: Goal management"
echo "   Type: shell"
echo ""

# v10 Telemetry Start
echo "{"skill": "longterm_goals", "status": "starting", "timestamp": $(date +%s)}" >> /root/.openclaw/workspace/v10_skill_telemetry.jsonl

# Execute original skill
if [ -f "/root/.openclaw/workspace/skills/longterm_goals/longterm_goals.sh" ]; then
    echo "✓ Executing original skill..."
    bash "/root/.openclaw/workspace/skills/longterm_goals/longterm_goals.sh" "$@"
    EXIT_CODE=$?
else
    echo "✗ Original skill not found: /root/.openclaw/workspace/skills/longterm_goals/longterm_goals.sh"
    EXIT_CODE=1
fi

# v10 Telemetry End
STATUS=$(if [ $EXIT_CODE -eq 0 ]; then echo "success"; else echo "failed"; fi)
echo "{"skill": "longterm_goals", "status": "$STATUS", "exit_code": $EXIT_CODE, "timestamp": $(date +%s)}" >> /root/.openclaw/workspace/v10_skill_telemetry.jsonl

exit $EXIT_CODE
