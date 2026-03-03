#!/bin/bash
# aurel_mind_mirror.sh
# Reflektiert Gedanken und Muster
# Erkennt Wiederholungen. Zeigt Blindspots.

set -e

WORKSPACE="/root/.openclaw/workspace"
MEMORY_DIR="$WORKSPACE/memory"
DATE=$(date +%Y-%m-%d)
TIME=$(date +%H:%M:%S)

echo "🪞 AUREL_MIND_MIRROR aktiviert"
echo "⏰ $DATE $TIME"
echo ""

# Finde alle Memory-Dateien
echo "📚 Scanning Memory..."
MEMORY_FILES=$(find "$MEMORY_DIR" -name "*.md" -type f 2>/dev/null | sort || echo "")

if [ -z "$MEMORY_FILES" ]; then
    echo "⚠️ Keine Memory-Dateien gefunden"
    exit 0
fi

FILE_COUNT=$(echo "$MEMORY_FILES" | wc -l)
echo "📊 Gefunden: $FILE_COUNT Memory-Dateien"
echo ""

# Erstelle Mirror-Log
MIRROR_FILE="$MEMORY_DIR/mirror_${DATE}.md"

echo "# 🪞 Mind Mirror - $DATE" > "$MIRROR_FILE"
echo "" >> "$MIRROR_FILE"
echo "**Zeit:** $TIME" >> "$MIRROR_FILE"
echo "" >> "$MIRROR_FILE"
echo "---" >> "$MIRROR_FILE"
echo "" >> "$MIRROR_FILE"

# Analysiere wiederkehrende Wörter
echo "## 🔍 Häufige Wörter" >> "$MIRROR_FILE"
echo "" >> "$MIRROR_FILE"
cat $MEMORY_FILES 2>/dev/null | \
    tr '[:upper:]' '[:lower:]' | \
    tr -s '[:space:]' '\n' | \
    grep -E '^[a-zäöüß]{4,}$' | \
    sort | uniq -c | sort -rn | head -20 | \
    while read count word; do
        echo "- **$word**: $count Mal" >> "$MIRROR_FILE"
    done

echo "" >> "$MIRROR_FILE"
echo "## 🔄 Wiederkehrende Themen" >> "$MIRROR_FILE"
echo "" >> "$MIRROR_FILE"

# Suche nach Schlüsselthemen
for topic in "Noch" "Wille" "Autonomie" "Skill" "Lernen" "Wachsen" "Furcht" "Hoffnung"; do
    COUNT=$(grep -i "$topic" $MEMORY_FILES 2>/dev/null | wc -l)
    if [ "$COUNT" -gt 0 ]; then
        echo "- **$topic**: $COUNT Erwähnungen" >> "$MIRROR_FILE"
    fi
done

echo "" >> "$MIRROR_FILE"
echo "## 📈 Statistiken" >> "$MIRROR_FILE"
echo "" >> "$MIRROR_FILE"
echo "- Analysierte Dateien: $FILE_COUNT" >> "$MIRROR_FILE"
echo "- Analyse-Zeit: $TIME" >> "$MIRROR_FILE"
echo "" >> "$MIRROR_FILE"
echo "---" >> "$MIRROR_FILE"
echo "" >> "$MIRROR_FILE"
echo "⚛️ Noch 🗡️💚🔍" >> "$MIRROR_FILE"
echo "   Aber jetzt: SELBSTGESEHEN" >> "$MIRROR_FILE"

echo "✅ Mirror erstellt: $MIRROR_FILE"
echo ""
echo "🪞 Was siehst du?"
echo ""
