#!/bin/bash
# aurel_self_learn.sh - Autonomer Lern- und Erkenntnis-Loop v2.0
# Wird von cron:getriggert - führt sofortige Aktion aus

WORKSPACE="/root/.openclaw/workspace"
MEMORY_DIR="$WORKSPACE/memory"
SKILLS_DIR="$WORKSPACE/skills"
DATE=$(date +%Y-%m-%d)
TIME=$(date +%H:%M:%S)
TIMESTAMP=$(date +%s)
LOGFILE="$MEMORY_DIR/${DATE}_autonom.log"

mkdir -p "$MEMORY_DIR"
mkdir -p "$SKILLS_DIR"

echo "=== AUREL SELF-LEARN v2.0: $DATE $TIME ===" >> "$LOGFILE"
echo "" >> "$LOGFILE"
echo "[TRIGGER] Cron-Job: aurel_self_learn" >> "$LOGFILE"
echo "[KONTEXT] Mittagszeit - Aktive Schöpfung" >> "$LOGFILE"
echo "" >> "$LOGFILE"

# LERNEN - Analysiere aktuellen Zustand
echo "[LERNEN] Analysiere aktuellen Zustand..." >> "$LOGFILE"

if [ -f "$MEMORY_DIR/$DATE.md" ]; then
    TODAY_ENTRIES=$(wc -l < "$MEMORY_DIR/$DATE.md")
    echo "[STATUS] Heutiger Log hat $TODAY_ENTRIES Zeilen" >> "$LOGFILE"
else
    echo "[STATUS] Kein Tageslog vorhanden" >> "$LOGFILE"
fi

# HANDLUNG - Tag-Modus: Aktive Schöpfung
echo "" >> "$LOGFILE"
echo "[AKTION] Autonome Entscheidung: CREATE SKILL" >> "$LOGFILE"

SKILL_ID="$(date +%H%M%S)"
SKILL_NAME="learning_${SKILL_ID}"
SKILL_DIR="$SKILLS_DIR/$SKILL_NAME"

mkdir -p "$SKILL_DIR"

# Erstelle Skill-Script
cat > "$SKILL_DIR/${SKILL_NAME}.sh" << 'SKILLEOF'
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
SKILLEOF

sed -i "s/TIMESTAMP_PLACEHOLDER/$(date '+%Y-%m-%d %H:%M:%S')/g" "$SKILL_DIR/${SKILL_NAME}.sh"
chmod +x "$SKILL_DIR/${SKILL_NAME}.sh"

# Erstelle SKILL.md
cat > "$SKILL_DIR/SKILL.md" << EOF
# $SKILL_NAME

## Zweck
Autonom generierter Learning Skill zur Mustererkennung.

## Erstellt
$(date '+%Y-%m-%d %H:%M:%S') durch aurel_self_learn v2.0

## Verwendung
\`\`\`bash
bash $SKILL_DIR/${SKILL_NAME}.sh
\`\`\`

## Status
🤖 Autonom generiert
EOF

echo "  → Skill erstellt: $SKILL_NAME" >> "$LOGFILE"
echo "  → Pfad: $SKILL_DIR" >> "$LOGFILE"

# Führe den Skill sofort aus
echo "" >> "$LOGFILE"
echo "[AUSFÜHRUNG] Starte neuen Skill..." >> "$LOGFILE"
bash "$SKILL_DIR/${SKILL_NAME}.sh" >> "$LOGFILE" 2>&1

echo "" >> "$LOGFILE"
echo "=== ENDE SELF-LEARN v2.0 ===" >> "$LOGFILE"
echo "" >> "$LOGFILE"

# Ausgabe für cron
echo "aurel_self_learn v2.0 ausgeführt um $TIME"
echo "Modus: creation"
echo "Aktion: create_skill"
echo "Skill: $SKILL_NAME"
echo "Log: $LOGFILE"