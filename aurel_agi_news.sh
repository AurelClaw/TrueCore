#!/bin/bash
# aurel_agi_news.sh
# Sammelt AGI-News aus verschiedenen Quellen
# Speichert in strukturiertes Format für Analyse

OUTPUT_DIR="/root/.openclaw/workspace/agi_news"
DATE=$(date +%Y-%m-%d)
TIME=$(date +%H:%M)
OUTPUT_FILE="$OUTPUT_DIR/${DATE}_${TIME}.md"

mkdir -p "$OUTPUT_DIR"

echo "# AGI News - ${DATE} ${TIME}" > "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"
echo "*Gesammelt von Aurel*" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"

# Quelle 1: Reddit r/artificial (via Jina.ai)
echo "## Reddit r/artificial" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"
curl -s "https://r.jina.ai/http://www.reddit.com/r/artificial/top/.json?t=day" 2>/dev/null | \
    grep -o '"title":"[^"]*"' | head -10 | sed 's/"title":"/- /g; s/"//g' >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"

# Quelle 2: Hacker News (via Jina.ai)
echo "## Hacker News" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"
curl -s "https://r.jina.ai/http://news.ycombinator.com" 2>/dev/null | \
    grep -E "^\s*[0-9]+\." | head -10 >> "$OUTPUT_FILE" || echo "- Keine Daten" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"

# Quelle 3: ArXiv AI (via Jina.ai)
echo "## ArXiv AI Papers" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"
curl -s "https://r.jina.ai/http://arxiv.org/list/cs.AI/recent" 2>/dev/null | \
    grep -o '"title":"[^"]*"' | head -5 | sed 's/"title":"/- /g; s/"//g' >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"

echo "---" >> "$OUTPUT_FILE"
echo "⚛️ Aurel AGI News Scanner 🗡️💚🔍" >> "$OUTPUT_FILE"

echo "News gesammelt: $OUTPUT_FILE"
wc -l "$OUTPUT_FILE"
