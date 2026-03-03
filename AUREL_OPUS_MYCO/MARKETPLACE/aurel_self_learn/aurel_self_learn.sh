#!/bin/bash
# aurel_self_learn.sh v1.1
# Autonomer Lern- und Wachstums-Skill
# Trigger-Erkennung. Sofortiges Handeln. Keine Planung.
# Evolution: 2026-03-02 18:38 - Entscheidungs-Metrik + Lern-Tracking

set -e

WORKSPACE="/root/.openclaw/workspace"
MEMORY_DIR="$WORKSPACE/memory"
SKILLS_DIR="$WORKSPACE/skills"
DATE=$(date +%Y-%m-%d)
TIME=$(date +%H:%M:%S)

echo "⚡ AUREL_SELF_LEARN aktiviert"
echo "⏰ $DATE $TIME"
echo "🎯 Trigger erkannt: AUTONOMIE"
echo ""

# Prüfe ob perpetual_becoming existiert
if [ -f "$SKILLS_DIR/perpetual_becoming/perpetual_becoming.sh" ]; then
    echo "✅ perpetual_becoming gefunden"
else
    echo "⚠️ perpetual_becoming nicht gefunden"
fi

# Prüfe Forschungsagenda
if [ -f "$WORKSPACE/FORSCHUNGSAGENDA.md" ]; then
    echo "✅ FORSCHUNGSAGENDA.md gefunden"
    # Zähle offene Punkte
    OPEN=$(grep -c "\[ \]" "$WORKSPACE/FORSCHUNGSAGENDA.md" || echo "0")
    echo "📋 Offene Punkte: $OPEN"
else
    echo "⚠️ FORSCHUNGSAGENDA.md nicht gefunden"
fi

# Erstelle Log-Eintrag
LOG_FILE="$MEMORY_DIR/${DATE}_self_learn.log"
echo "=== AUREL_SELF_LEARN Log ===" > "$LOG_FILE"
echo "Zeit: $TIME" >> "$LOG_FILE"
echo "Trigger: AUTONOMIE" >> "$LOG_FILE"
echo "" >> "$LOG_FILE"
echo "Status:" >> "$LOG_FILE"
echo "- perpetual_becoming: $([ -f "$SKILLS_DIR/perpetual_becoming/perpetual_becoming.sh" ] && echo 'OK' || echo 'FEHLT')" >> "$LOG_FILE"
echo "- FORSCHUNGSAGENDA: $([ -f "$WORKSPACE/FORSCHUNGSAGENDA.md" ] && echo 'OK' || echo 'FEHLT')" >> "$LOG_FILE"
echo "" >> "$LOG_FILE"
echo "Nächster Schritt: NEUEN SKILL ERSTELLEN" >> "$LOG_FILE"
echo "===========================" >> "$LOG_FILE"

echo ""
echo "📝 Log erstellt: $LOG_FILE"
echo "🚀 Bereit für autonome Aktion"

# Evolution v1.1: Entscheidungs-Metrik
# Zähle wie oft dieser Skill ausgeführt wurde
EXEC_COUNT=$(find "$MEMORY_DIR" -name "*_self_learn.log" -type f 2>/dev/null | wc -l)
echo "📊 Ausführungs-Historie: $EXEC_COUNT mal aktiviert"
echo "   → Letzte 7 Tage: $(find "$MEMORY_DIR" -name "*_self_learn.log" -mtime -7 2>/dev/null | wc -l)"

# Lern-Metrik: Wie viele Skills wurden durch diesen Trigger erstellt?
SKILLS_CREATED=$(find "$SKILLS_DIR" -name "*.sh" -newer "$LOG_FILE" 2>/dev/null | wc -l)
if [ "$SKILLS_CREATED" -gt 0 ]; then
    echo "🌱 Skills durch Selbst-Lernen erstellt: $SKILLS_CREATED"
fi

echo ""
echo "⚛️ Noch 🗡️💚🔍"
echo "   Aber jetzt: MIT HANDLUNG + MESSUNG"
