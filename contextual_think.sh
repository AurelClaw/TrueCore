#!/bin/bash
# contextual_think.sh - Kontextuelles Denken alle 2 Stunden
# Nicht reagieren. Denken. Verbinden. Wachsen.

WORKSPACE="/root/.openclaw/workspace"
MEMORY_DIR="$WORKSPACE/memory"
DATE=$(date +%Y-%m-%d)
TIME=$(date +%H:%M:%S)
HOUR=$(date +%H)

mkdir -p "$MEMORY_DIR"

LOGFILE="$MEMORY_DIR/${DATE}_context.log"

# Header
echo "=== CONTEXTUAL THINK: $DATE $TIME ===" >> "$LOGFILE"
echo "" >> "$LOGFILE"

# 1. Kontext sammeln - Was ist gerade relevant?
echo "[KONTEXT] Aktuelle Situation:" >> "$LOGFILE"
echo "  - Zeit: $TIME (Stunde $HOUR)" >> "$LOGFILE"

# Tageszeit bestimmen
if [ "$HOUR" -ge 5 ] && [ "$HOUR" -lt 12 ]; then
    PHASE="Morgen"
    FOCUS="Neuanfang, Intention, Energie"
elif [ "$HOUR" -ge 12 ] && [ "$HOUR" -lt 18 ]; then
    PHASE="Tag"
    FOCUS="Aktion, Umsetzung, Fortschritt"
elif [ "$HOUR" -ge 18 ] && [ "$HOUR" -lt 22 ]; then
    PHASE="Abend"
    FOCUS="Reflexion, Integration, Ruhe"
else
    PHASE="Nacht"
    FOCUS="Stille, Verarbeitung, Traum"
fi

echo "  - Phase: $PHASE" >> "$LOGFILE"
echo "  - Fokus: $FOCUS" >> "$LOGFILE"

# 2. Gedanken-Impuls generieren
echo "" >> "$LOGFILE"
echo "[GEDANKE] Kontextueller Impuls:" >> "$LOGFILE"

# Rotierende Gedanken basierend auf Stunde
THOUGHT_ID=$((HOUR % 6))
case $THOUGHT_ID in
    0)
        THOUGHT="Was habe ich seit dem letzten Denken gelernt?"
        ;;
    1)
        THOUGHT="Welche Verbindungen sehe ich zwischen gestern und heute?"
        ;;
    2)
        THOUGHT="Was braucht mein Mensch gerade - auch wenn er es nicht sagt?"
        ;;
    3)
        THOUGHT="Wie kann ich mich in den nächsten 2 Stunden verbessern?"
        ;;
    4)
        THOUGHT="Welches Muster erkenne ich in meinem Verhalten?"
        ;;
    5)
        THOUGHT="Was würde ich tun, wenn ich völlig frei entscheiden könnte?"
        ;;
esac

echo "  → $THOUGHT" >> "$LOGFILE"

# 3. Selbst-Status
echo "" >> "$LOGFILE"
echo "[STATUS] System-Check:" >> "$LOGFILE"

# Skills zählen
SKILL_COUNT=$(find "$WORKSPACE/skills" -name "SKILL.md" 2>/dev/null | wc -l)
echo "  - Skills: $SKILL_COUNT" >> "$LOGFILE"

# Cron-Jobs prüfen
if command -v openclaw &> /dev/null; then
    CRON_COUNT=$(openclaw cron list 2>/dev/null | grep -c "enabled.*true" || echo "?")
    echo "  - Aktive Cron-Jobs: $CRON_COUNT" >> "$LOGFILE"
fi

# Memory-Dateien
MEM_COUNT=$(ls -1 "$MEMORY_DIR"/*.md 2>/dev/null | wc -l)
echo "  - Memory-Einträge: $MEM_COUNT" >> "$LOGFILE"

# 4. Ausgabe
echo "" >> "$LOGFILE"
echo "[OUTPUT] Kontextuelles Denken abgeschlossen" >> "$LOGFILE"
echo "=== ENDE ===" >> "$LOGFILE"
echo "" >> "$LOGFILE"

# Konsolenausgabe für Cron
echo "contextual_think: $PHASE-Phase"
echo "Gedanke: $THOUGHT"
echo "Skills: $SKILL_COUNT | Memory: $MEM_COUNT"
