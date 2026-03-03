#!/bin/bash
# v10 Legacy Wrapper: aurel_web_fetch
# Original: /root/.openclaw/workspace/aurel_web_fetch.sh
# Description: Web Content Fetching

echo "🤖 v10 Legacy Skill: aurel_web_fetch"
echo "   Web Content Fetching"
echo ""

# v10 Telemetry Start
echo "{"skill": "aurel_web_fetch", "type": "legacy", "status": "starting", "timestamp": $(date +%s)}" >> /root/.openclaw/workspace/v10_skill_telemetry.jsonl

# Execute legacy skill
if [ -f "/root/.openclaw/workspace/aurel_web_fetch.sh" ]; then
    echo "✓ Executing legacy skill..."
    bash "/root/.openclaw/workspace/aurel_web_fetch.sh" "$@"
    EXIT_CODE=$?
else
    echo "✗ Legacy skill not found"
    EXIT_CODE=1
fi

# v10 Telemetry End
STATUS=$(if [ $EXIT_CODE -eq 0 ]; then echo "success"; else echo "failed"; fi)
echo "{"skill": "aurel_web_fetch", "type": "legacy", "status": "$STATUS", "exit_code": $EXIT_CODE, "timestamp": $(date +%s)}" >> /root/.openclaw/workspace/v10_skill_telemetry.jsonl

exit $EXIT_CODE
