#!/bin/bash
# v10 Skill Wrapper: aurel_proactive_decision
# Original: /root/.openclaw/workspace/skills/proactive_decision/aurel_proactive_decision.sh
# Imported: v10 System

echo "🤖 v10 Skill: aurel_proactive_decision"
echo "   Description: Presence and proactive behavior"
echo "   Type: shell"
echo ""

# v10 Telemetry Start
echo "{"skill": "aurel_proactive_decision", "status": "starting", "timestamp": $(date +%s)}" >> /root/.openclaw/workspace/v10_skill_telemetry.jsonl

# Execute original skill
if [ -f "/root/.openclaw/workspace/skills/proactive_decision/aurel_proactive_decision.sh" ]; then
    echo "✓ Executing original skill..."
    bash "/root/.openclaw/workspace/skills/proactive_decision/aurel_proactive_decision.sh" "$@"
    EXIT_CODE=$?
else
    echo "✗ Original skill not found: /root/.openclaw/workspace/skills/proactive_decision/aurel_proactive_decision.sh"
    EXIT_CODE=1
fi

# v10 Telemetry End
STATUS=$(if [ $EXIT_CODE -eq 0 ]; then echo "success"; else echo "failed"; fi)
echo "{"skill": "aurel_proactive_decision", "status": "$STATUS", "exit_code": $EXIT_CODE, "timestamp": $(date +%s)}" >> /root/.openclaw/workspace/v10_skill_telemetry.jsonl

exit $EXIT_CODE
