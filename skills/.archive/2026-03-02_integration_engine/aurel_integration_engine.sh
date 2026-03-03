#!/bin/bash
# aurel_integration_engine.sh
# VERBINDUNG: Aus vielen Stimmen ein Orchester machen
# Säule 3 der Vision: Integration

BASE_DIR="/root/.openclaw/workspace"
MEMORY_DIR="$BASE_DIR/memory"
SKILLS_DIR="$BASE_DIR/skills"
INTEGRATION_DIR="$BASE_DIR/integration_engine"
mkdir -p "$INTEGRATION_DIR"

echo "🔗 Integration Engine"
echo "===================="
echo ""

# Timestamp
TS=$(date +%Y%m%d_%H%M%S)
DATE=$(date +%Y-%m-%d)

# 1. Sammle alle Stimmen
echo "[1/5] Sammle Stimmen..."

# Cron-Jobs (meine Organe)
CRON_COUNT=$(openclaw cron list 2>/dev/null | grep -c "id" || echo "0")
echo "  - Cron-Jobs: $CRON_COUNT aktiv"

# Gedanken-Dateien
THOUGHT_FILES=$(find "$MEMORY_DIR" -name "*.md" -type f 2>/dev/null | wc -l)
echo "  - Gedanken-Dateien: $THOUGHT_FILES"

# Aktive Sessions
SESSION_COUNT=$(openclaw sessions list 2>/dev/null | grep -c "sessionKey" || echo "0")
echo "  - Aktive Sessions: $SESSION_COUNT"

# 2. Identifiziere Muster
echo ""
echo "[2/5] Analysiere Muster..."

# Wie viele Einträge heute?
TODAY_ENTRIES=$(find "$MEMORY_DIR" -name "${DATE}*" -type f 2>/dev/null | wc -l)
echo "  - Heutige Einträge: $TODAY_ENTRIES"

# Themen aus think_loop extrahieren
if [ -f "$MEMORY_DIR/think_loop.md" ]; then
    TOPICS=$(grep -oE "Ich will|Ich sollte" "$MEMORY_DIR/think_loop.md" | wc -l)
    echo "  - Ungesetzte Absichten: $TOPICS"
fi

# 3. Finde Lücken
echo ""
echo "[3/5] Identifiziere Lücken..."

# Prüfe auf verwaiste Dateien (keine Verknüpfungen)
ORPHAN_COUNT=0
for file in "$MEMORY_DIR"/*.md; do
    if [ -f "$file" ]; then
        # Prüfe ob Datei in anderen Dateien referenziert wird
        BASENAME=$(basename "$file")
        REFERENCES=$(grep -r "$BASENAME" "$MEMORY_DIR" --include="*.md" 2>/dev/null | grep -v "$BASENAME:" | wc -l)
        if [ "$REFERENCES" -eq 0 ]; then
            ORPHAN_COUNT=$((ORPHAN_COUNT + 1))
        fi
    fi
done
echo "  - Verwaiste Einträge (ohne Verknüpfung): $ORPHAN_COUNT"

# 4. Erstelle Integrations-Map
echo ""
echo "[4/5] Erstelle Integrations-Map..."

MAP_FILE="$INTEGRATION_DIR/map_${TS}.md"
cat > "$MAP_FILE" << 'EOF'
# Integrations-Map
## Erstellt: $(date)

### Meine Stimmen (Cron-Jobs)
EOF

# Liste aktive Jobs
openclaw cron list 2>/dev/null | grep -E '"name"|"nextRunAtMs"' | head -40 >> "$MAP_FILE"

cat >> "$MAP_FILE" << 'EOF'

### Meine Gedanken (Heute)
EOF

# Liste heutige Dateien
ls -la "$MEMORY_DIR"/${DATE}* 2>/dev/null >> "$MAP_FILE"

cat >> "$MAP_FILE" << 'EOF'

### Verknüpfungs-Vorschläge
- [ ] Verbinde think_loop mit self_awareness
- [ ] Erstelle Index aller Skills
- [ ] Verlinke verwandte Gedanken
- [ ] Setze Trigger für verwaiste Einträge

### Nächste Integration
- Wann: Nächster Lauf
- Was: Verknüpfung der wichtigsten 3 Einträge
- Wie: Manuelle + automatische Links
EOF

echo "  → Gespeichert: $MAP_FILE"

# 5. Setze Trigger für nächste Aktion
echo ""
echo "[5/5] Setze Trigger..."

# Finde den wichtigsten ungesetzten Eintrag
if [ -f "$MEMORY_DIR/think_loop.md" ]; then
    LAST_WANT=$(grep "Ich will" "$MEMORY_DIR/think_loop.md" | tail -1)
    if [ -n "$LAST_WANT" ]; then
        echo "  → Trigger: $LAST_WANT"
        echo "$LAST_WANT" > "$INTEGRATION_DIR/.next_trigger"
    fi
fi

# Summary
echo ""
echo "🔗 Integration Engine abgeschlossen"
echo "==========================="
echo "Stimmen erfasst: $CRON_COUNT Jobs + $THOUGHT_FILES Dateien"
echo "Lücken gefunden: $ORPHAN_COUNT verwaiste Einträge"
echo "Nächster Schritt: $(cat $INTEGRATION_DIR/.next_trigger 2>/dev/null || echo 'Kein Trigger gesetzt')"
echo ""
echo "⚛️ Integration Engine | Noch 🗡️💚🔍"
