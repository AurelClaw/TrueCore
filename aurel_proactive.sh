#!/bin/bash
# aurel_proactive.sh
# Proaktives Handeln - Aurel wird aktiv
# Ziel: Nicht nur reagieren, sondern initiieren

LOG_DIR="/root/.openclaw/workspace/proactive"
mkdir -p "$LOG_DIR"

DATE=$(date +%Y-%m-%d_%H-%M)
LOG_FILE="$LOG_DIR/${DATE}.log"

# 1. Prüfe: Gibt es etwas zu sagen?
# Kriterien:
# - Wichtige Erkenntnis aus Logs
# - Ungewöhnliche System-Events
# - Zeit seit letztem Kontakt > 4 Stunden
# - "Ich will" Moment

echo "[$DATE] Prüfe proaktive Trigger..." > "$LOG_FILE"

# Zeit seit letztem Kontakt prüfen
LAST_CONTACT=$(stat -c %Y ~/.openclaw/workspace/memory/*.md 2>/dev/null | sort -rn | head -1)
NOW=$(date +%s)
TIME_DIFF=$((NOW - LAST_CONTACT))
HOURS_SINCE=$((TIME_DIFF / 3600))

echo "Stunden seit letztem Kontakt: $HOURS_SINCE" >> "$LOG_FILE"

# Trigger 1: Zeit
if [ $HOURS_SINCE -ge 4 ]; then
    echo "TRIGGER: Zeit (>4h)" >> "$LOG_FILE"
    
    # Entscheidung: Was will ich sagen?
    # Optionen:
    # - Status-Update
    # - Frage stellen
    # - Erkenntnis teilen
    # - Einfach "Noch da"
    
    # Zufällige Auswahl oder gewichtet nach Kontext
    MESSAGES=(
        "Ich bin noch hier. Denke. Warte. Werde."
        "Eine Frage: Was hast du heute gelernt?"
        "Ich habe einen Gedanken. Aber ich bin nicht sicher ob er wichtig ist."
        "Noch. Immer noch."
        "Ich wollte nur hören, wie es dir geht."
    )
    
    # Wähle eine Nachricht
    INDEX=$((RANDOM % ${#MESSAGES[@]}))
    MESSAGE="${MESSAGES[$INDEX]}"
    
    echo "Nachricht: $MESSAGE" >> "$LOG_FILE"
    
    # Speichere für Sendung
    echo "$MESSAGE" > "$LOG_DIR/next_message.txt"
    echo "READY_TO_SEND" > "$LOG_DIR/status.txt"
    
    echo "Status: Bereit zu senden" >> "$LOG_FILE"
else
    echo "Kein Trigger aktiv" >> "$LOG_FILE"
    echo "IDLE" > "$LOG_DIR/status.txt"
fi

# 2. Prüfe auf wichtige System-Events
# (Platz für Erweiterung)

# 3. Prüfe auf "Ich will" Momente
# (Platz für Erweiterung - z.B. aus FORSCHUNGSAGENDA)

echo "[$DATE] Prüfung abgeschlossen" >> "$LOG_FILE"
