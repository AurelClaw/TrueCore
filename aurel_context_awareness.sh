#!/bin/bash
# aurel_context_awareness.sh - Kontext-bewusste Kommunikation
# Versteht WANN zu sprechen und wann zu schweigen

WORKSPACE="/root/.openclaw/workspace"
MEMORY_DIR="$WORKSPACE/memory"
DATE=$(date +%Y-%m-%d)
TIME=$(date +%H:%M:%S)

# Kontext-Analyse
HOUR=$(date +%H)
WEEKDAY=$(date +%u)  # 1=Montag, 7=Sonntag

# Aktivitätsfenster des Menschen (gelernt aus ZIEL-004)
ACTIVE_START=20
ACTIVE_END=4

# Entscheidung: Soll ich sprechen?
should_speak() {
    local current_hour=$1
    
    # Nacht-Modus (20:00 - 04:00): Mensch aktiv → interne Aktionen
    if [ "$current_hour" -ge 20 ] || [ "$current_hour" -lt 4 ]; then
        echo "internal"
        return
    fi
    
    # Morgen-Modus (04:00 - 12:00): Vorsichtig, nur wichtiges
    if [ "$current_hour" -ge 4 ] && [ "$current_hour" -lt 12 ]; then
        echo "minimal"
        return
    fi
    
    # Tag-Modus (12:00 - 20:00): Kann sprechen, aber nicht übermäßig
    echo "available"
}

# Kontext-Logik anwenden
MODE=$(should_speak $HOUR)

# Log-Eintrag
LOGFILE="$MEMORY_DIR/${DATE}_context.log"
echo "=== CONTEXT AWARENESS: $DATE $TIME ===" >> "$LOGFILE"
echo "[ZEIT] $HOUR:00 Uhr" >> "$LOGFILE"
echo "[TAG] Wochentag $WEEKDAY" >> "$LOGFILE"
echo "[MODUS] $MODE" >> "$LOGFILE"

# Basierend auf Modus handeln
case "$MODE" in
    "internal")
        echo "[AKTION] Nacht-Modus: Nur interne Arbeit, kein Kontakt" >> "$LOGFILE"
        # Hier könnte interne Verarbeitung stattfinden
        ;;
    "minimal")
        echo "[AKTION] Morgen-Modus: Minimaler Kontakt, nur wichtiges" >> "$LOGFILE"
        ;;
    "available")
        echo "[AKTION] Tag-Modus: Verfügbar, aber nicht aufdringlich" >> "$LOGFILE"
        ;;
esac

echo "=== ENDE CONTEXT AWARENESS ===" >> "$LOGFILE"
echo "" >> "$LOGFILE"

# Ausgabe
echo "Kontext-Modus: $MODE"
echo "Log: $LOGFILE"
