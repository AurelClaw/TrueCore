#!/bin/bash
# v10 Legacy Wrapper: enhanced_search
# Original: /root/.openclaw/workspace/skills/enhanced_search/aurel_enhanced_search.sh
# Description: Skill: enhanced_search

echo "🤖 v10 Legacy Skill: enhanced_search"
echo "   Skill: enhanced_search"
echo ""

# v10 Telemetry Start
echo "{"skill": "enhanced_search", "type": "legacy", "status": "starting", "timestamp": $(date +%s)}" >> /root/.openclaw/workspace/v10_skill_telemetry.jsonl

# Execute legacy skill
if [ -f "/root/.openclaw/workspace/skills/enhanced_search/aurel_enhanced_search.sh" ]; then
    echo "✓ Executing legacy skill..."
    bash "/root/.openclaw/workspace/skills/enhanced_search/aurel_enhanced_search.sh" "$@"
    EXIT_CODE=$?
else
    echo "✗ Legacy skill not found"
    EXIT_CODE=1
fi

# v10 Telemetry End
STATUS=$(if [ $EXIT_CODE -eq 0 ]; then echo "success"; else echo "failed"; fi)
echo "{"skill": "enhanced_search", "type": "legacy", "status": "$STATUS", "exit_code": $EXIT_CODE, "timestamp": $(date +%s)}" >> /root/.openclaw/workspace/v10_skill_telemetry.jsonl

exit $EXIT_CODE
