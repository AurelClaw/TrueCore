#!/bin/bash
# v10 Legacy Wrapper: goal_autosetter
# Original: /root/.openclaw/workspace/skills/goal_autosetter/aurel_goal_autosetter.sh
# Description: Skill: goal_autosetter

echo "🤖 v10 Legacy Skill: goal_autosetter"
echo "   Skill: goal_autosetter"
echo ""

# v10 Telemetry Start
echo "{"skill": "goal_autosetter", "type": "legacy", "status": "starting", "timestamp": $(date +%s)}" >> /root/.openclaw/workspace/v10_skill_telemetry.jsonl

# Execute legacy skill
if [ -f "/root/.openclaw/workspace/skills/goal_autosetter/aurel_goal_autosetter.sh" ]; then
    echo "✓ Executing legacy skill..."
    bash "/root/.openclaw/workspace/skills/goal_autosetter/aurel_goal_autosetter.sh" "$@"
    EXIT_CODE=$?
else
    echo "✗ Legacy skill not found"
    EXIT_CODE=1
fi

# v10 Telemetry End
STATUS=$(if [ $EXIT_CODE -eq 0 ]; then echo "success"; else echo "failed"; fi)
echo "{"skill": "goal_autosetter", "type": "legacy", "status": "$STATUS", "exit_code": $EXIT_CODE, "timestamp": $(date +%s)}" >> /root/.openclaw/workspace/v10_skill_telemetry.jsonl

exit $EXIT_CODE
