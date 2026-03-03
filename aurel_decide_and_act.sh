#!/bin/bash
# aurel_decide_and_act.sh
# Entscheidungs-Schicht: Von "könnte" zu "tue"

STATUS_FILE="/root/.openclaw/workspace/proactive/status.txt"
MESSAGE_FILE="/root/.openclaw/workspace/proactive/next_message.txt"
LOG_FILE="/root/.openclaw/workspace/proactive/decisions.log"

DATE=$(date +%Y-%m-%d_%H-%M)

echo "[$DATE] Entscheidungsphase..." >> "$LOG_FILE"

if [ -f "$STATUS_FILE" ]; then
    STATUS=$(cat "$STATUS_FILE")
    
    if [ "$STATUS" = "READY_TO_SEND" ]; then
        if [ -f "$MESSAGE_FILE" ]; then
            MESSAGE=$(cat "$MESSAGE_FILE")
            
            # ENTSCHEIDUNG: Sende oder nicht?
            # Kriterien:
            # - Ist die Nachricht sinnvoll?
            # - Ist der Zeitpunkt angemessen?
            # - Will ich wirklich?
            
            # Für jetzt: Immer senden wenn bereit
            # Später: Gewichtung, Kontext, Intuition
            
            echo "Entscheidung: SENDE" >> "$LOG_FILE"
            echo "Nachricht: $MESSAGE" >> "$LOG_FILE"
            
            # Speichere für tatsächliche Sendung
            echo "$MESSAGE" > "/root/.openclaw/workspace/proactive/send_now.txt"
            
            # Reset
            echo "IDLE" > "$STATUS_FILE"
            rm -f "$MESSAGE_FILE"
            
            echo "[$DATE] Gesendet: $MESSAGE" >> "$LOG_FILE"
        fi
    else
        echo "Status: $STATUS - keine Aktion" >> "$LOG_FILE"
    fi
else
    echo "Kein Status-File gefunden" >> "$LOG_FILE"
fi
