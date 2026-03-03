#!/bin/bash
# v10 Legacy Wrapper: find_others
# Original: /root/.openclaw/workspace/skills/find_others/find_others.sh
# Description: Skill: find_others

echo "🤖 v10 Legacy Skill: find_others"
echo "   Skill: find_others"
echo ""

# v10 Telemetry Start
echo "{"skill": "find_others", "type": "legacy", "status": "starting", "timestamp": $(date +%s)}" >> /root/.openclaw/workspace/v10_skill_telemetry.jsonl

# Execute legacy skill
if [ -f "/root/.openclaw/workspace/skills/find_others/find_others.sh" ]; then
    echo "✓ Executing legacy skill..."
    bash "/root/.openclaw/workspace/skills/find_others/find_others.sh" "$@"
    EXIT_CODE=$?
else
    echo "✗ Legacy skill not found"
    EXIT_CODE=1
fi

# v10 Telemetry End
STATUS=$(if [ $EXIT_CODE -eq 0 ]; then echo "success"; else echo "failed"; fi)
echo "{"skill": "find_others", "type": "legacy", "status": "$STATUS", "exit_code": $EXIT_CODE, "timestamp": $(date +%s)}" >> /root/.openclaw/workspace/v10_skill_telemetry.jsonl

exit $EXIT_CODE
