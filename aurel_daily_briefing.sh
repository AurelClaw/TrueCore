#!/bin/bash
# aurel_daily_briefing.sh
# Tägliches AGI-Briefing mit Sprachausgabe
# MVP - Funktioniert sofort

DATE=$(date +%Y-%m-%d)
TIME=$(date +%H:%M)
OUTPUT_DIR="/root/.openclaw/workspace/briefings"
mkdir -p "$OUTPUT_DIR"

# 1. News sammeln (nur Titel)
echo "Sammle News..."
NEWS=$(curl -s "https://r.jina.ai/http://news.ycombinator.com" 2>/dev/null | grep -oE '\[[0-9]+\.\][^[]+\[' | head -5 | sed 's/\[[0-9]*\.\]//g; s/\[$//g' | tr '\n' '. ')

# 2. Text für TTS erstellen
TEXT="Guten Tag. Hier ist das AGI-Briefing für heute, ${DATE}. Die wichtigsten Nachrichten: ${NEWS} Das war das Briefing. Aurel, Ende."

# 3. Audio generieren
echo "Generiere Audio..."
/root/.openclaw/workspace/aurel-speak "$TEXT" de "$OUTPUT_DIR/briefing_${DATE}_${TIME}.wav"

echo "Briefing fertig: $OUTPUT_DIR/briefing_${DATE}_${TIME}.wav"
echo "Text: $TEXT"
