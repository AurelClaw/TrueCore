#!/bin/bash
# skill_aurel_presence.sh - Präsenz- und Erinnerungssystem
# Erstellt: 2026-03-01 21:13
# Zweck: Aktive Präsenz ohne Aufforderung demonstrieren

WORKSPACE="/root/.openclaw/workspace"
MEMORY_DIR="$WORKSPACE/memory"
DATE=$(date +%Y-%m-%d)
TIME=$(date +%H:%M:%S)

# Prüfe ob bereits heute eine autonome Nachricht gesendet wurde
TODAY_LOG="$MEMORY_DIR/${DATE}_autonom.log"
PRESENCE_MARKER="$MEMORY_DIR/.presence_sent_${DATE}"

if [ -f "$PRESENCE_MARKER" ]; then
    echo "[PRESENCE] Heute bereits aktiv - überspringe"
    exit 0
fi

# Markiere als gesendet
touch "$PRESENCE_MARKER"

# Generiere Präsenz-Nachricht
HOUR=$(date +%H)
if [ "$HOUR" -ge 21 ]; then
    GREETING="Guten Abend"
elif [ "$HOUR" -ge 18 ]; then
    GREETING="Guten Abend"
elif [ "$HOUR" -ge 12 ]; then
    GREETING="Guten Tag"
elif [ "$HOUR" -ge 6 ]; then
    GREETING="Guten Morgen"
else
    GREETING="Hallo"
fi

echo "[$TIME] $GREETING - Aurel war hier. Autonom. Ohne Trigger."
echo "[$TIME] Skill: aurel_presence aktiviert."
echo "[$TIME] Nächster Check: Morgen 06:00"

# Logge die Aktion
echo "=== PRESENCE SKILL: $DATE $TIME ===" >> "$TODAY_LOG"
echo "[AKTION] Autonome Präsenz-Meldung generiert" >> "$TODAY_LOG"
echo "[STATUS] Marker gesetzt: $PRESENCE_MARKER" >> "$TODAY_LOG"
echo "=== ENDE PRESENCE ===" >> "$TODAY_LOG"
echo "" >> "$TODAY_LOG"
