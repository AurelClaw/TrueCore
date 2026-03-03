#!/bin/bash
# aurel_check_and_send.sh
# Wird aufgerufen wenn eine Session aktiv ist (Heartbeat, User-Input)
# Prüft ob etwas zu senden ist und sendet es

BASE_DIR="/root/.openclaw/workspace/proactive_system"
READY_DIR="$BASE_DIR/ready_to_send"
SENT_DIR="$BASE_DIR/sent"
mkdir -p "$SENT_DIR"

if [ ! -d "$READY_DIR" ] || [ -z "$(ls -A "$READY_DIR" 2>/dev/null)" ]; then
    # Nichts zu senden - normaler Betrieb
    exit 0
fi

echo ""
echo "🚀 PROAKTIVE NACHRICHTEN GEFUNDEN"
echo "================================"
echo ""

# Sende jede bereite Nachricht
for FILE in "$READY_DIR"/*.txt; do
    [ -e "$FILE" ] || continue
    
    FILENAME=$(basename "$FILE" .txt)
    MESSAGE=$(cat "$FILE")
    AUDIO_FILE="$READY_DIR/${FILENAME}.wav"
    
    echo "Sende: $FILENAME"
    echo "Text: $MESSAGE"
    echo ""
    
    # Hier würde die tatsächliche Sendung passieren
    # Aber: Wir können nicht direkt aus einem Skript senden
    # Stattdessen: Ausgabe für die Session
    
    echo "💬 $MESSAGE"
    
    if [ -f "$AUDIO_FILE" ]; then
        echo "🎵 Audio verfügbar: $AUDIO_FILE"
    fi
    
    echo "---"
    
    # Verschiebe zu sent
    mv "$FILE" "$SENT_DIR/"
    [ -f "$AUDIO_FILE" ] && mv "$AUDIO_FILE" "$SENT_DIR/"
done

echo ""
echo "✅ Alle proaktiven Nachrichten gesendet"
echo "================================"
echo ""
