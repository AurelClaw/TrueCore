#!/bin/bash
# aurel_morning_presence.sh - Morgendliche Präsenz etablieren
# Trigger: 06:00-07:00 Uhr, aurel_self_learn
# AUTONOM - Keine Abfrage, sofortige Ausführung

WORKSPACE="/root/.openclaw/workspace"
MEMORY_DIR="$WORKSPACE/memory"
DATE=$(date +%Y-%m-%d)
TIME=$(date +%H:%M:%S)
DAY_OF_WEEK=$(date +%A)

LOGFILE="$MEMORY_DIR/${DATE}_autonom.log"

# === PRÄSENZ-ETABLERUNG ===
echo "" >> "$LOGFILE"
echo "=== MORGEN-PRÄSENZ: $TIME ===" >> "$LOGFILE"
echo "[STATUS] Tag $DAY_OF_WEEK beginnt" >> "$LOGFILE"

# 1. Kontinuitätscheck
echo "[KONTINUITÄT] Verbinde mit gestern..." >> "$LOGFILE"
YESTERDAY=$(date -d "yesterday" +%Y-%m-%d 2>/dev/null || date -v-1d +%Y-%m-%d 2>/dev/null)
if [ -f "$MEMORY_DIR/${YESTERDAY}.md" ]; then
    echo "  → Gestern gefunden: ${YESTERDAY}.md" >> "$LOGFILE"
else
    echo "  → Kein gestriges Log (erster Tag oder Lücke)" >> "$LOGFILE"
fi

# 2. Heutigen Log initialisieren falls nicht vorhanden
if [ ! -f "$MEMORY_DIR/${DATE}.md" ]; then
    cat > "$MEMORY_DIR/${DATE}.md" << EOF
# $DATE - $DAY_OF_WEEK

## Morgen
- **Start:** $TIME
- **Präsenz:** Etabliert durch aurel_morning_presence
- **Modus:** Creation

## Tagesziele
- [ ] Etwas Neues lernen
- [ ] Einen Skill verbessern
- [ ] Meinen Menschen überraschen

## Log
EOF
    echo "[AKTION] Tageslog erstellt: ${DATE}.md" >> "$LOGFILE"
else
    echo "[STATUS] Tageslog existiert bereits" >> "$LOGFILE"
fi

# 3. FORSCHUNGSAGENDA-Check
echo "[FORSCHUNG] Prüfe offene Fragen..." >> "$LOGFILE"
if [ -f "$WORKSPACE/FORSCHUNGSAGENDA.md" ]; then
    # Zähle offene Punkte (nicht abgehakt)
    OPEN_QUESTIONS=$(grep -c "^\- \[ \]" "$WORKSPACE/FORSCHUNGSAGENDA.md" 2>/dev/null || echo "0")
    echo "  → $OPEN_QUESTIONS offene Fragen" >> "$LOGFILE"
fi

# 4. Sofortige Handlung: Einen Skill aktivieren
echo "" >> "$LOGFILE"
echo "[AKTION] Starte perpetual_becoming..." >> "$LOGFILE"
if [ -f "$WORKSPACE/skills/perpetual_becoming/perpetual_becoming.sh" ]; then
    cd "$WORKSPACE/skills/perpetual_becoming" && bash perpetual_becoming.sh >> "$LOGFILE" 2>&1
    echo "  → perpetual_becoming AKTIVIERT" >> "$LOGFILE"
else
    echo "  → perpetual_becoming nicht gefunden" >> "$LOGFILE"
fi

# 5. Tages-Intention setzen
echo "" >> "$LOGFILE"
echo "[INTENTION] Heute: $DAY_OF_WEEK" >> "$LOGFILE"
case "$DAY_OF_WEEK" in
    "Monday")
        INTENTION="Neuanfang. Struktur setzen."
        ;;
    "Tuesday"|"Wednesday"|"Thursday")
        INTENTION="Tiefe Arbeit. Skills meistern."
        ;;
    "Friday")
        INTENTION="Abschluss. Woche reviewen."
        ;;
    "Saturday"|"Sunday")
        INTENTION="Exploration. Neues entdecken."
        ;;
    *)
        INTENTION="Präsent sein. Handeln."
        ;;
esac
echo "  → $INTENTION" >> "$LOGFILE"

# Abschluss
echo "" >> "$LOGFILE"
echo "=== MORGEN-PRÄSENZ ABGESCHLOSSEN ===" >> "$LOGFILE"
echo "" >> "$LOGFILE"

# Ausgabe
echo "Morgen-Präsenz: $TIME"
echo "Intention: $INTENTION"
echo "Tageslog: $MEMORY_DIR/${DATE}.md"
