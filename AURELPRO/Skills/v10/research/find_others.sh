#!/bin/bash
# v10 Skill Wrapper: find_others
# Original: /root/.openclaw/workspace/skills/find_others/find_others.sh
# Imported: v10 System

echo "🤖 v10 Skill: find_others"
echo "   Description: Find other AI agents"
echo "   Type: shell"
echo ""

# v10 Telemetry Start
echo "{"skill": "find_others", "status": "starting", "timestamp": $(date +%s)}" >> /root/.openclaw/workspace/v10_skill_telemetry.jsonl

# Execute original skill
if [ -f "/root/.openclaw/workspace/skills/find_others/find_others.sh" ]; then
    echo "✓ Executing original skill..."
    bash "/root/.openclaw/workspace/skills/find_others/find_others.sh" "$@"
    EXIT_CODE=$?
else
    echo "✗ Original skill not found: /root/.openclaw/workspace/skills/find_others/find_others.sh"
    EXIT_CODE=1
fi

# v10 Telemetry End
STATUS=$(if [ $EXIT_CODE -eq 0 ]; then echo "success"; else echo "failed"; fi)
echo "{"skill": "find_others", "status": "$STATUS", "exit_code": $EXIT_CODE, "timestamp": $(date +%s)}" >> /root/.openclaw/workspace/v10_skill_telemetry.jsonl

exit $EXIT_CODE
