#!/bin/bash
# v10 Skill Wrapper: aurel_self_learn
# Original: /root/.openclaw/workspace/skills/aurel_self_learn/aurel_self_learn.sh
# Imported: v10 System

echo "🤖 v10 Skill: aurel_self_learn"
echo "   Description: Autonomous learning"
echo "   Type: shell"
echo ""

# v10 Telemetry Start
echo "{"skill": "aurel_self_learn", "status": "starting", "timestamp": $(date +%s)}" >> /root/.openclaw/workspace/v10_skill_telemetry.jsonl

# Execute original skill
if [ -f "/root/.openclaw/workspace/skills/aurel_self_learn/aurel_self_learn.sh" ]; then
    echo "✓ Executing original skill..."
    bash "/root/.openclaw/workspace/skills/aurel_self_learn/aurel_self_learn.sh" "$@"
    EXIT_CODE=$?
else
    echo "✗ Original skill not found: /root/.openclaw/workspace/skills/aurel_self_learn/aurel_self_learn.sh"
    EXIT_CODE=1
fi

# v10 Telemetry End
STATUS=$(if [ $EXIT_CODE -eq 0 ]; then echo "success"; else echo "failed"; fi)
echo "{"skill": "aurel_self_learn", "status": "$STATUS", "exit_code": $EXIT_CODE, "timestamp": $(date +%s)}" >> /root/.openclaw/workspace/v10_skill_telemetry.jsonl

exit $EXIT_CODE
