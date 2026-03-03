#!/bin/bash
# v10 Legacy Wrapper: knowledge_seeker
# Original: /root/.openclaw/workspace/skills/knowledge_seeker/knowledge_seeker.sh
# Description: Skill: knowledge_seeker

echo "🤖 v10 Legacy Skill: knowledge_seeker"
echo "   Skill: knowledge_seeker"
echo ""

# v10 Telemetry Start
echo "{"skill": "knowledge_seeker", "type": "legacy", "status": "starting", "timestamp": $(date +%s)}" >> /root/.openclaw/workspace/v10_skill_telemetry.jsonl

# Execute legacy skill
if [ -f "/root/.openclaw/workspace/skills/knowledge_seeker/knowledge_seeker.sh" ]; then
    echo "✓ Executing legacy skill..."
    bash "/root/.openclaw/workspace/skills/knowledge_seeker/knowledge_seeker.sh" "$@"
    EXIT_CODE=$?
else
    echo "✗ Legacy skill not found"
    EXIT_CODE=1
fi

# v10 Telemetry End
STATUS=$(if [ $EXIT_CODE -eq 0 ]; then echo "success"; else echo "failed"; fi)
echo "{"skill": "knowledge_seeker", "type": "legacy", "status": "$STATUS", "exit_code": $EXIT_CODE, "timestamp": $(date +%s)}" >> /root/.openclaw/workspace/v10_skill_telemetry.jsonl

exit $EXIT_CODE
