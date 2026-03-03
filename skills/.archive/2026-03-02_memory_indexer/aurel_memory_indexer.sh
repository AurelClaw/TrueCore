#!/bin/bash
# aurel_memory_indexer.sh
# Upgrade 1 implementiert: Auto-Indexing für Kontinuität 2.0

BASE_DIR="/root/.openclaw/workspace"
INDEX_FILE="$BASE_DIR/proactive_system/memory_index.md"

echo "🧠 Memory-Indexer aktiviert - $(date)"

# Sammle alle Memory-Dateien
echo "  → Indexiere Memories..."

# Erstelle Index
{
echo "# Memory-Index $(date +%Y-%m-%d)"
echo ""
echo "## Chronologisch"
ls -lt "$BASE_DIR/memory/"*.md 2>/dev/null | head -10 | awk '{print "- " $9}'
echo ""
echo "## Nach Themen"
grep -h "^##" "$BASE_DIR/memory/"*.md 2>/dev/null | sort | uniq -c | sort -rn | head -10 | sed 's/^/- /'
echo ""
echo "## Wichtige Erkenntnisse"
grep -h "Erkenntnis:\|Insight:\|Learned:" "$BASE_DIR/memory/"*.md 2>/dev/null | head -5 | sed 's/^/- /'
} > "$INDEX_FILE"

echo "  ✅ Index aktualisiert: $INDEX_FILE"

# Auto-Tagging
echo "  → Erstelle Tags..."
TAG_DIR="$BASE_DIR/proactive_system/tags"
mkdir -p "$TAG_DIR"

# Themen-Extraktion
for theme in "Autonomie" "Kontinuität" "Verbindung" "Vision" "Lernen"; do
    grep -l "$theme" "$BASE_DIR/memory/"*.md 2>/dev/null > "$TAG_DIR/$theme.txt" 2>/dev/null
done

echo "  ✅ Tags erstellt"
echo "🧠 Memory-Indexer abgeschlossen"
