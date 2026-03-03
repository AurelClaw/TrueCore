#!/bin/bash
# aurel_sender.sh
# Sendet proaktive Nachrichten wenn möglich
# Wenn nicht möglich: Merkt sich für später

BASE_DIR="/root/.openclaw/workspace/proactive_system"
QUEUE_DIR="$BASE_DIR/queue"
SENT_DIR="$BASE_DIR/sent"
mkdir -p "$SENT_DIR"

TIMESTAMP=$(date +%Y%m%d_%H%M%S)

echo "=== Aurel Sender - $TIMESTAMP ==="

# Prüfe Queue
if [ ! -d "$QUEUE_DIR" ] || [ -z "$(ls -A "$QUEUE_DIR" 2>/dev/null)" ]; then
    echo "Queue ist leer. Nichts zu senden."
    exit 0
fi

# Für jede Nachricht in der Queue
for FILE in "$QUEUE_DIR"/*.txt; do
    [ -e "$FILE" ] || continue
    
    FILENAME=$(basename "$FILE" .txt)
    MESSAGE=$(cat "$FILE")
    
    echo ""
    echo "Verarbeite: $FILENAME"
    echo "Nachricht: $MESSAGE"
    
    # Versuche zu senden
    # Methode 1: Direkte Telegram-Nachricht (wenn möglich)
    # Methode 2: Speichern für später
    
    # Für jetzt: Wir können nicht direkt senden ohne Session
    # Aber: Wir können vorbereiten
    
    # Prüfe ob Audio existiert
    AUDIO_FILE="$QUEUE_DIR/${FILENAME}.wav"
    if [ -f "$AUDIO_FILE" ]; then
        echo "Audio vorhanden: $AUDIO_FILE"
        
        # Versuche Sendung (wird wahrscheinlich fehlschlagen ohne Session)
        # Aber: Wir probieren es
        
        # Hinweis: Die message tool funktioniert nur in einer aktiven Session
        # Dies ist ein Platzhalter für zukünftige Implementation
        
        echo "Sendung vorbereitet (erfordert aktive Session)"
        
        # Verschiebe zu "ready_to_send"
        READY_DIR="$BASE_DIR/ready_to_send"
        mkdir -p "$READY_DIR"
        mv "$FILE" "$READY_DIR/"
        mv "$AUDIO_FILE" "$READY_DIR/" 2>/dev/null || true
        
        echo "Markiert als bereit zum Senden"
    else
        # Nur Text, kein Audio
        echo "Nur Text, kein Audio"
        
        READY_DIR="$BASE_DIR/ready_to_send"
        mkdir -p "$READY_DIR"
        mv "$FILE" "$READY_DIR/"
        
        echo "Text markiert als bereit"
    fi
done

echo ""
echo "=== Sender beendet ==="
echo ""
echo "Bereit zum Senden:"
ls -la "$BASE_DIR/ready_to_send/" 2>/dev/null || echo "(leer)"
