#!/bin/bash
# aurel_agi_news_v2.sh
# Verbesserter AGI-News Scanner mit sauberer Ausgabe

OUTPUT_DIR="/root/.openclaw/workspace/agi_news"
DATE=$(date +%Y-%m-%d)
TIME=$(date +%H:%M)
OUTPUT_FILE="$OUTPUT_DIR/${DATE}_${TIME}.md"

mkdir -p "$OUTPUT_DIR"

echo "# AGI News - ${DATE} ${TIME}" > "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"
echo "*Gesammelt von Aurel*" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"

# Hacker News - Top Stories
echo "## Hacker News - Top Stories" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"

# Extrahiere Titel und URLs sauber
curl -s "https://r.jina.ai/http://news.ycombinator.com" 2>/dev/null | \
    grep -oE '\[[0-9]+\.\][^[]+\[[^]]+\]' | head -15 | \
    sed 's/\[[0-9]*\.\] */- /g; s/\[[^]]*\]//g' | \
    sed 's/^[[:space:]]*//' | \
    grep -v "^$" >> "$OUTPUT_FILE" || echo "- Keine Daten verfügbar" >> "$OUTPUT_FILE"

echo "" >> "$OUTPUT_FILE"

# Zusammenfassung für TTS
echo "## Zusammenfassung für Sprachausgabe" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"
echo "Heute gibt es folgende wichtige Nachrichten:" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"

# Extrahiere nur die Titel für TTS
curl -s "https://r.jina.ai/http://news.ycombinator.com" 2>/dev/null | \
    grep -oE '\[[0-9]+\.\][^[]+\[' | head -5 | \
    sed 's/\[[0-9]*\.\] */- /g; s/\[$//g' | \
    sed 's/^[[:space:]]*//' >> "$OUTPUT_FILE"

echo "" >> "$OUTPUT_FILE"
echo "Das war die Zusammenfassung der AGI News." >> "$OUTPUT_FILE"

echo "---" >> "$OUTPUT_FILE"
echo "⚛️ Aurel AGI News Scanner 🗡️💚🔍" >> "$OUTPUT_FILE"

echo "News gesammelt: $OUTPUT_FILE"
cat "$OUTPUT_FILE"
