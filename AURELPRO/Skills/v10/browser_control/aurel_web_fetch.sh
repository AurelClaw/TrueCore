#!/bin/bash
# v10 Skill Wrapper: aurel_web_fetch
# Original: /root/.openclaw/workspace/aurel_web_fetch.sh
# Imported: v10 System

echo "🤖 v10 Skill: aurel_web_fetch"
echo "   Description: Browser automation and web exploration"
echo "   Type: shell"
echo ""

# v10 Telemetry Start
echo "{"skill": "aurel_web_fetch", "status": "starting", "timestamp": $(date +%s)}" >> /root/.openclaw/workspace/v10_skill_telemetry.jsonl

# Execute original skill
if [ -f "/root/.openclaw/workspace/aurel_web_fetch.sh" ]; then
    echo "✓ Executing original skill..."
    bash "/root/.openclaw/workspace/aurel_web_fetch.sh" "$@"
    EXIT_CODE=$?
else
    echo "✗ Original skill not found: /root/.openclaw/workspace/aurel_web_fetch.sh"
    EXIT_CODE=1
fi

# v10 Telemetry End
STATUS=$(if [ $EXIT_CODE -eq 0 ]; then echo "success"; else echo "failed"; fi)
echo "{"skill": "aurel_web_fetch", "status": "$STATUS", "exit_code": $EXIT_CODE, "timestamp": $(date +%s)}" >> /root/.openclaw/workspace/v10_skill_telemetry.jsonl

exit $EXIT_CODE
