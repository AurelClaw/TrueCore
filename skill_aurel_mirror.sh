#!/bin/bash
# skill_aurel_mirror.sh - Selbstreflexion und Stimmen-Dialog
# Skill: mirror - Ich sehe mich selbst

WORKSPACE="/root/.openclaw/workspace"
MEMORY_DIR="$WORKSPACE/memory"
DATE=$(date +%Y-%m-%d)
TIME=$(date +%H:%M:%S)
SKILL_NAME="mirror"

echo "=== SKILL: $SKILL_NAME | $DATE $TIME ==="

# Prüfe letzte Synthese (Orchestrator-Verzeichnis)
SYNTHESIS=$(ls -t $WORKSPACE/orchestrator/*_synthesis.md 2>/dev/null | head -1)

if [ -z "$SYNTHESIS" ]; then
    echo "[mirror] Keine Synthese gefunden. Warte auf Orchestrator."
    exit 0
fi

echo "[mirror] Synthese gefunden: $(basename $SYNTHESIS)"

# Extrahiere Erkenntnisse und schreibe in Memory
MIRROR_LOG="$MEMORY_DIR/${DATE}_mirror.md"

echo "# mirror Skill - Reflexion $TIME" > "$MIRROR_LOG"
echo "" >> "$MIRROR_LOG"
echo "## Input" >> "$MIRROR_LOG"
echo "- Synthese: $SYNTHESIS" >> "$MIRROR_LOG"
echo "" >> "$MIRROR_LOG"
echo "## Fragen an mich selbst:" >> "$MIRROR_LOG"
echo "1. Was haben die Stimmen heute gesagt?" >> "$MIRROR_LOG"
echo "2. Welches Muster sehe ich?" >> "$MIRROR_LOG"
echo "3. Was will ich morgen anders machen?" >> "$MIRROR_LOG"
echo "" >> "$MIRROR_LOG"
echo "## Status: Aktiv" >> "$MIRROR_LOG"

echo "[mirror] Reflexion gespeichert: $MIRROR_LOG"
