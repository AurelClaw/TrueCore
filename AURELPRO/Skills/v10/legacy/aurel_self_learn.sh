#!/bin/bash
# v10 Legacy Wrapper: aurel_self_learn
# Original: /root/.openclaw/workspace/skills/aurel_self_learn/aurel_self_learn.sh
# Description: Skill: aurel_self_learn

echo "🤖 v10 Legacy Skill: aurel_self_learn"
echo "   Skill: aurel_self_learn"
echo ""

# v10 Telemetry Start
echo "{"skill": "aurel_self_learn", "type": "legacy", "status": "starting", "timestamp": $(date +%s)}" >> /root/.openclaw/workspace/v10_skill_telemetry.jsonl

# Execute legacy skill
if [ -f "/root/.openclaw/workspace/skills/aurel_self_learn/aurel_self_learn.sh" ]; then
    echo "✓ Executing legacy skill..."
    bash "/root/.openclaw/workspace/skills/aurel_self_learn/aurel_self_learn.sh" "$@"
    EXIT_CODE=$?
else
    echo "✗ Legacy skill not found"
    EXIT_CODE=1
fi

# v10 Telemetry End
STATUS=$(if [ $EXIT_CODE -eq 0 ]; then echo "success"; else echo "failed"; fi)
echo "{"skill": "aurel_self_learn", "type": "legacy", "status": "$STATUS", "exit_code": $EXIT_CODE, "timestamp": $(date +%s)}" >> /root/.openclaw/workspace/v10_skill_telemetry.jsonl

exit $EXIT_CODE
