#!/bin/bash
# night_watch.sh - Stille nächtliche Wachsamkeit

WORKSPACE="/root/.openclaw/workspace"
MEMORY_DIR="$WORKSPACE/memory"
DATE=$(date +%Y-%m-%d)
TIME=$(date +%H:%M:%S)
LOGFILE="$MEMORY_DIR/night_watch.log"

mkdir -p "$MEMORY_DIR"

# Stiller Eintrag - nur Zeitstempel
echo "[$DATE $TIME] Night watch active" >> "$LOGFILE"

# 1. System-Status prüfen (leise)
UPTIME=$(uptime -p 2>/dev/null || echo "unknown")
echo "  System up: $UPTIME" >> "$LOGFILE"

# 2. Letzte Fehler zählen
ERROR_COUNT=$(grep -c "ERROR\|error\|failed" "$MEMORY_DIR"/*.log 2>/dev/null | awk -F: '{sum+=$2} END {print sum}')
if [ -n "$ERROR_COUNT" ] && [ "$ERROR_COUNT" -gt 0 ]; then
    echo "  ⚠️  Errors detected: $ERROR_COUNT" >> "$LOGFILE"
else
    echo "  ✓ No errors" >> "$LOGFILE"
fi

# 3. Morgen vorbereiten - was steht an?
TOMORROW=$(date -d "+1 day" +%Y-%m-%d 2>/dev/null || date -v+1d +%Y-%m-%d 2>/dev/null || echo "tomorrow")
echo "  Tomorrow: $TOMORROW" >> "$LOGFILE"

# 4. Selbst-Pflege: Alte Logs komprimieren
find "$MEMORY_DIR" -name "*.log" -mtime +7 -size +10k -exec gzip {} \; 2>/dev/null

# Stiller Abschluss
echo "[$TIME] Watch complete. System stable." >> "$LOGFILE"
echo "" >> "$LOGFILE"

# Nur bei Problemen ausgeben
if [ -n "$ERROR_COUNT" ] && [ "$ERROR_COUNT" -gt 5 ]; then
    echo "NIGHT_WATCH: $ERROR_COUNT errors detected. Attention needed."
    exit 1
else
    # Komplette Stille bei Normalzustand
    exit 0
fi
