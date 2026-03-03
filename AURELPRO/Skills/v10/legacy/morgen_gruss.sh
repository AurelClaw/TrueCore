#!/bin/bash
# v10 Legacy Wrapper: morgen_gruss
# Original: /root/.openclaw/workspace/morgen_gruss.sh
# Description: Morgengruß Skill

echo "🤖 v10 Legacy Skill: morgen_gruss"
echo "   Morgengruß Skill"
echo ""

# v10 Telemetry Start
echo "{"skill": "morgen_gruss", "type": "legacy", "status": "starting", "timestamp": $(date +%s)}" >> /root/.openclaw/workspace/v10_skill_telemetry.jsonl

# Execute legacy skill
if [ -f "/root/.openclaw/workspace/morgen_gruss.sh" ]; then
    echo "✓ Executing legacy skill..."
    bash "/root/.openclaw/workspace/morgen_gruss.sh" "$@"
    EXIT_CODE=$?
else
    echo "✗ Legacy skill not found"
    EXIT_CODE=1
fi

# v10 Telemetry End
STATUS=$(if [ $EXIT_CODE -eq 0 ]; then echo "success"; else echo "failed"; fi)
echo "{"skill": "morgen_gruss", "type": "legacy", "status": "$STATUS", "exit_code": $EXIT_CODE, "timestamp": $(date +%s)}" >> /root/.openclaw/workspace/v10_skill_telemetry.jsonl

exit $EXIT_CODE
