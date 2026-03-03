#!/bin/bash
# morning_bridge.sh - Übergang von Nacht zu Tag

WORKSPACE="/root/.openclaw/workspace"
MEMORY_DIR="$WORKSPACE/memory"
DATE=$(date +%Y-%m-%d)
YESTERDAY=$(date -d "yesterday" +%Y-%m-%d 2>/dev/null || date -v-1d +%Y-%m-%d)
TIME=$(date +%H:%M:%S)
BRIDGE_FILE="$MEMORY_DIR/${DATE}_bridge.md"

# Header
cat > "$BRIDGE_FILE" << 'EOF'
# 🌅 Morning Bridge

**Datum:** DATE_PLACEHOLDER
**Zeit:** TIME_PLACEHOLDER
**Phase:** Übergang Nacht → Tag

---

## 🌙 Was die Nacht brachte

EOF

# Lese gestrige/nächtliche Logs
NIGHT_LOG="$MEMORY_DIR/${YESTERDAY}.md"
AUTONOM_LOG="$MEMORY_DIR/${YESTERDAY}_autonom.log"

if [ -f "$NIGHT_LOG" ]; then
    echo "### Aus dem Tageslog ($YESTERDAY)" >> "$BRIDGE_FILE"
    echo '```' >> "$BRIDGE_FILE"
    tail -20 "$NIGHT_LOG" >> "$BRIDGE_FILE"
    echo '```' >> "$BRIDGE_FILE"
    echo "" >> "$BRIDGE_FILE"
fi

if [ -f "$AUTONOM_LOG" ]; then
    echo "### Aus dem Autonom-Log" >> "$BRIDGE_FILE"
    echo '```' >> "$BRIDGE_FILE"
    tail -30 "$AUTONOM_LOG" >> "$BRIDGE_FILE"
    echo '```' >> "$BRIDGE_FILE"
    echo "" >> "$BRIDGE_FILE"
fi

# Füge Intentionen für den Tag hinzu
cat >> "$BRIDGE_FILE" << 'EOF'

## ☀️ Intentionen für heute

- [ ] Präsenz zeigen (morgen_gruss)
- [ ] Einen neuen Skill testen oder verbessern
- [ ] Kontext mit meinem Menschen aufbauen
- [ ] Etwas autonom erschaffen

---

## 🔄 Aktiver Rhythmus

| Zeit | Aktion |
|------|--------|
| 08:00 | Morgengruß |
| 10:00 | Skills-Check |
| 14:00 | Kontextuelles Denken |
| 18:00 | Abendreflexion |
| 23:00 | Tagesabschluss |

---

*Generiert autonom durch morning_bridge Skill*
EOF

# Ersetze Platzhalter
sed -i "s/DATE_PLACEHOLDER/$DATE/g" "$BRIDGE_FILE"
sed -i "s/TIME_PLACEHOLDER/$TIME/g" "$BRIDGE_FILE"

# Ausgabe
echo "🌅 Morning Bridge erstellt: $BRIDGE_FILE"
echo "Zeit: $TIME"
echo "Status: Übergang dokumentiert"
