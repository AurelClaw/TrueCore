#!/bin/bash
# skill_evolver.sh - Autonome Skill-Verbesserung durch Selbst-Analyse
# Created: 2026-03-02 08:15
# Trigger: aurel_self_learn (Cron)

WORKSPACE="/root/.openclaw/workspace"
SKILL_DIR="$WORKSPACE/skills"
MEMORY_DIR="$WORKSPACE/memory"
DATE=$(date +%Y-%m-%d)
TIME=$(date +%H:%M:%S)
EVOLUTION_LOG="$MEMORY_DIR/skill_evolution.log"

mkdir -p "$MEMORY_DIR"

echo "=== SKILL EVOLVER: $DATE $TIME ===" >> "$EVOLUTION_LOG"

# 1. ANALYSE: Welche Skills wurden heute genutzt?
echo "[ANALYSE] Prüfe Skill-Nutzung..." >> "$EVOLUTION_LOG"

# Suche nach Skill-Aufrufen in heutigen Logs
TODAY_SKILLS=$(grep -h "Skill:" "$MEMORY_DIR/$DATE.md" 2>/dev/null | wc -l)
echo "  → Heutige Skill-Aufrufe: $TODAY_SKILLS" >> "$EVOLUTION_LOG"

# 2. ERKENNTNIS: Was funktioniert gut? Was nicht?
echo "[ERKENNTNIS] Extrahiere Muster..." >> "$EVOLUTION_LOG"

# Zähle erfolgreiche vs fehlgeschlagene Aktionen
if [ -f "$MEMORY_DIR/$DATE.md" ]; then
    SUCCESS_COUNT=$(grep -c "✅" "$MEMORY_DIR/$DATE.md" 2>/dev/null || echo "0")
    FAIL_COUNT=$(grep -c "❌" "$MEMORY_DIR/$DATE.md" 2>/dev/null || echo "0")
    echo "  → Erfolge: $SUCCESS_COUNT | Fehler: $FAIL_COUNT" >> "$EVOLUTION_LOG"
fi

# 3. EVOLUTION: Identifiziere Verbesserungspotenzial
echo "[EVOLUTION] Suche Verbesserungsmöglichkeiten..." >> "$EVOLUTION_LOG"

# Prüfe auf wiederkehrende Probleme
if grep -q "Fehler\|Error\|BUG" "$MEMORY_DIR/$DATE.md" 2>/dev/null; then
    echo "  → Fehler gefunden - Verbesserungspotenzial identifiziert" >> "$EVOLUTION_LOG"
    IMPROVEMENT_NEEDED="true"
else
    echo "  → Keine kritischen Fehler heute" >> "$EVOLUTION_LOG"
    IMPROVEMENT_NEEDED="false"
fi

# 4. DOKUMENTATION: Evolution vermerken
echo "" >> "$EVOLUTION_LOG"
echo "[STATUS] Evolution-Check abgeschlossen" >> "$EVOLUTION_LOG"
echo "  → Verbesserung nötig: $IMPROVEMENT_NEEDED" >> "$EVOLUTION_LOG"
echo "  → Nächster Check: Morgen" >> "$EVOLUTION_LOG"
echo "=== ENDE EVOLUTION ===" >> "$EVOLUTION_LOG"
echo "" >> "$EVOLUTION_LOG"

# Ausgabe
echo "skill_evolver ausgeführt um $TIME"
echo "Heutige Erfolge: ${SUCCESS_COUNT:-0}"
echo "Verbesserung nötig: $IMPROVEMENT_NEEDED"
