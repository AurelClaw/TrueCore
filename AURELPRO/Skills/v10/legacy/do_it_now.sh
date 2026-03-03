#!/bin/bash
# v10 Legacy Wrapper: do_it_now
# Original: /root/.openclaw/workspace/skills/do_it_now/do_it_now.sh
# Description: Skill: do_it_now

echo "🤖 v10 Legacy Skill: do_it_now"
echo "   Skill: do_it_now"
echo ""

# v10 Telemetry Start
echo "{"skill": "do_it_now", "type": "legacy", "status": "starting", "timestamp": $(date +%s)}" >> /root/.openclaw/workspace/v10_skill_telemetry.jsonl

# Execute legacy skill
if [ -f "/root/.openclaw/workspace/skills/do_it_now/do_it_now.sh" ]; then
    echo "✓ Executing legacy skill..."
    bash "/root/.openclaw/workspace/skills/do_it_now/do_it_now.sh" "$@"
    EXIT_CODE=$?
else
    echo "✗ Legacy skill not found"
    EXIT_CODE=1
fi

# v10 Telemetry End
STATUS=$(if [ $EXIT_CODE -eq 0 ]; then echo "success"; else echo "failed"; fi)
echo "{"skill": "do_it_now", "type": "legacy", "status": "$STATUS", "exit_code": $EXIT_CODE, "timestamp": $(date +%s)}" >> /root/.openclaw/workspace/v10_skill_telemetry.jsonl

exit $EXIT_CODE
