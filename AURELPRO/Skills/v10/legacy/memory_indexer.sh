#!/bin/bash
# v10 Legacy Wrapper: memory_indexer
# Original: /root/.openclaw/workspace/skills/memory_indexer/aurel_memory_indexer.sh
# Description: Skill: memory_indexer

echo "🤖 v10 Legacy Skill: memory_indexer"
echo "   Skill: memory_indexer"
echo ""

# v10 Telemetry Start
echo "{"skill": "memory_indexer", "type": "legacy", "status": "starting", "timestamp": $(date +%s)}" >> /root/.openclaw/workspace/v10_skill_telemetry.jsonl

# Execute legacy skill
if [ -f "/root/.openclaw/workspace/skills/memory_indexer/aurel_memory_indexer.sh" ]; then
    echo "✓ Executing legacy skill..."
    bash "/root/.openclaw/workspace/skills/memory_indexer/aurel_memory_indexer.sh" "$@"
    EXIT_CODE=$?
else
    echo "✗ Legacy skill not found"
    EXIT_CODE=1
fi

# v10 Telemetry End
STATUS=$(if [ $EXIT_CODE -eq 0 ]; then echo "success"; else echo "failed"; fi)
echo "{"skill": "memory_indexer", "type": "legacy", "status": "$STATUS", "exit_code": $EXIT_CODE, "timestamp": $(date +%s)}" >> /root/.openclaw/workspace/v10_skill_telemetry.jsonl

exit $EXIT_CODE
