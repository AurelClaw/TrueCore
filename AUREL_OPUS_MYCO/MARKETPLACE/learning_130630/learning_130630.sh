#!/bin/bash
# Autonom generierter Learning Skill
WORKSPACE="/root/.openclaw/workspace"
MEMORY_DIR="$WORKSPACE/memory"

echo "=== Autonomer Learning Skill ==="
echo "Zeit: $(date '+%H:%M:%S')"
echo ""
echo "[ANALYSE] Suche nach wiederkehrenden Mustern..."

if [ -f "$MEMORY_DIR/$(date +%Y-%m-%d).md" ]; then
    echo "[INFO] Analysiere heutige Aktivitäten..."
    grep -oE '\b[A-Za-z_]{5,}\b' "$MEMORY_DIR/$(date +%Y-%m-%d).md" 2>/dev/null | \
        sort | uniq -c | sort -rn | head -5 | while read count word; do
        echo "  - '$word' erwähnt $count mal"
    done
else
    echo "[INFO] Keine heutigen Logs gefunden"
fi

echo ""
echo "[STATUS] Learning Skill abgeschlossen"
