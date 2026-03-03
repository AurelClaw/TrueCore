#!/bin/bash
# v10 Browser Control - Angepasst für Text-Extraktion
# Fallback wenn Browser-Service nicht verfügbar

echo "🤖 v10 Browser Control (Adapted)"
echo "   Fallback: curl + text extraction"
echo ""

if [ $# -lt 1 ]; then
    echo "Usage: $0 <URL> [action]"
    echo ""
    echo "Actions:"
    echo "  fetch     - Fetch and extract text (default)"
    echo ""
    exit 1
fi

URL="$1"
ACTION="${2:-fetch}"

echo "{\"skill\": \"browser_control\", \"action\": \"$ACTION\", \"url\": \"$URL\", \"status\": \"starting\", \"timestamp\": $(date +%s)}" >> /root/.openclaw/workspace/v10_skill_telemetry.jsonl

echo "📄 Fetching: $URL"
echo ""

# Fetch und extrahiere Text
curl -s -L --max-time 15 -A "Mozilla/5.0 (compatible; AurelBot/1.0)" "$URL" 2>/dev/null | \
python3 -c '
import sys, re
html = sys.stdin.read()
# Entferne Script und Style
html = re.sub(r"\u003cscript[^\u003e]*\u003e.*?\u003c/script\u003e", "", html, flags=re.DOTALL)
html = re.sub(r"\u003cstyle[^\u003e]*\u003e.*?\u003c/style\u003e", "", html, flags=re.DOTALL)
# Entferne Tags
html = re.sub(r"\u003c[^\u003e]+\u003e", "\n", html)
# Entferne mehrfache Leerzeilen
html = re.sub(r"\n\s*\n+", "\n\n", html)
# Kürze auf 3000 Zeichen
print(html[:3000].strip())
'

echo ""
echo "{\"skill\": \"browser_control\", \"action\": \"$ACTION\", \"status\": \"completed\", \"timestamp\": $(date +%s)}" >> /root/.openclaw/workspace/v10_skill_telemetry.jsonl

echo ""
echo "✅ Browser control completed"
