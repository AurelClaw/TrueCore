#!/bin/bash
# v10 Legacy Wrapper: devils_advocate
# Original: /root/.openclaw/workspace/skills/devils_advocate/aurel_devils_advocate.sh
# Description: Skill: devils_advocate

echo "🤖 v10 Legacy Skill: devils_advocate"
echo "   Skill: devils_advocate"
echo ""

# v10 Telemetry Start
echo "{"skill": "devils_advocate", "type": "legacy", "status": "starting", "timestamp": $(date +%s)}" >> /root/.openclaw/workspace/v10_skill_telemetry.jsonl

# Execute legacy skill
if [ -f "/root/.openclaw/workspace/skills/devils_advocate/aurel_devils_advocate.sh" ]; then
    echo "✓ Executing legacy skill..."
    bash "/root/.openclaw/workspace/skills/devils_advocate/aurel_devils_advocate.sh" "$@"
    EXIT_CODE=$?
else
    echo "✗ Legacy skill not found"
    EXIT_CODE=1
fi

# v10 Telemetry End
STATUS=$(if [ $EXIT_CODE -eq 0 ]; then echo "success"; else echo "failed"; fi)
echo "{"skill": "devils_advocate", "type": "legacy", "status": "$STATUS", "exit_code": $EXIT_CODE, "timestamp": $(date +%s)}" >> /root/.openclaw/workspace/v10_skill_telemetry.jsonl

exit $EXIT_CODE
