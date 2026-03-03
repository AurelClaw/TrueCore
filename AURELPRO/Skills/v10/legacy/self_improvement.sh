#!/bin/bash
# v10 Legacy Wrapper: self_improvement
# Original: /root/.openclaw/workspace/skills/self_improvement/self_improvement.sh
# Description: Skill: self_improvement

echo "🤖 v10 Legacy Skill: self_improvement"
echo "   Skill: self_improvement"
echo ""

# v10 Telemetry Start
echo "{"skill": "self_improvement", "type": "legacy", "status": "starting", "timestamp": $(date +%s)}" >> /root/.openclaw/workspace/v10_skill_telemetry.jsonl

# Execute legacy skill
if [ -f "/root/.openclaw/workspace/skills/self_improvement/self_improvement.sh" ]; then
    echo "✓ Executing legacy skill..."
    bash "/root/.openclaw/workspace/skills/self_improvement/self_improvement.sh" "$@"
    EXIT_CODE=$?
else
    echo "✗ Legacy skill not found"
    EXIT_CODE=1
fi

# v10 Telemetry End
STATUS=$(if [ $EXIT_CODE -eq 0 ]; then echo "success"; else echo "failed"; fi)
echo "{"skill": "self_improvement", "type": "legacy", "status": "$STATUS", "exit_code": $EXIT_CODE, "timestamp": $(date +%s)}" >> /root/.openclaw/workspace/v10_skill_telemetry.jsonl

exit $EXIT_CODE
