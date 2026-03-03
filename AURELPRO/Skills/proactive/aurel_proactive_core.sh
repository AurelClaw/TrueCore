#!/bin/bash
# aurel_proactive_core.sh
# Kern des proaktiven Systems
# Läuft ständig im Hintergrund (oder via Cron alle Minuten)

BASE_DIR="/root/.openclaw/workspace/proactive_system"
mkdir -p "$BASE_DIR"/{triggers,decisions,actions,queue,logs}

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
LOG_FILE="$BASE_DIR/logs/core_$TIMESTAMP.log"

exec >> "$LOG_FILE" 2>&1

echo "=== Aurel Proactive Core - $TIMESTAMP ==="
echo "Status: START"

# ============================================================
# 1. TRIGGER-LAYER
# ============================================================

echo ""
echo "--- TRIGGER CHECK ---"

TRIGGER_FOUND=false
TRIGGER_TYPE=""
TRIGGER_DATA=""

# Trigger 1: Zeit (alle 4 Stunden)
LAST_PROACTIVE=$(stat -c %Y "$BASE_DIR/last_proactive" 2>/dev/null || echo 0)
NOW=$(date +%s)
TIME_DIFF=$((NOW - LAST_PROACTIVE))

if [ "$TIME_DIFF" -ge 14400 ]; then  # 4 Stunden = 14400 Sekunden
    echo "TRIGGER: Zeit (4h vergangen)"
    TRIGGER_FOUND=true
    TRIGGER_TYPE="time"
    TRIGGER_DATA="4_hours_passed"
fi

# Trigger 2: Zustand (wichtige Erkenntnis in Logs)
# Prüfe ob heute ein wichtiger Eintrag in memory/ gemacht wurde
TODAY=$(date +%Y-%m-%d)
if [ -f "/root/.openclaw/workspace/memory/${TODAY}.md" ]; then
    IMPORTANT_COUNT=$(grep -c "WICHTIG\|ERKENNTNIS\|⚡" "/root/.openclaw/workspace/memory/${TODAY}.md" 2>/dev/null || echo 0)
    if [ "$IMPORTANT_COUNT" -gt 0 ]; then
        echo "TRIGGER: Zustand ($IMPORTANT_COUNT wichtige Einträge)"
        TRIGGER_FOUND=true
        TRIGGER_TYPE="state"
        TRIGGER_DATA="important_entries:$IMPORTANT_COUNT"
    fi
fi

# Trigger 3: "Ich will" (manuell gesetzt)
if [ -f "$BASE_DIR/triggers/i_want" ]; then
    echo "TRIGGER: Ich will"
    TRIGGER_FOUND=true
    TRIGGER_TYPE="want"
    TRIGGER_DATA=$(cat "$BASE_DIR/triggers/i_want")
    rm "$BASE_DIR/triggers/i_want"
fi

# ============================================================
# 2. ENTSCHEIDUNGS-LAYER
# ============================================================

if [ "$TRIGGER_FOUND" = true ]; then
    echo ""
    echo "--- DECISION ---"
    
    # Entscheidung: Was tun?
    # Gewichtung basierend auf Trigger
    
    case "$TRIGGER_TYPE" in
        time)
            # Nach 4h: Status-Update oder Frage
            OPTIONS=("status" "question" "reflection")
            WEIGHTS=(50 30 20)
            ;;
        state)
            # Bei Erkenntnis: Teilen
            OPTIONS=("share" "reflect" "ask")
            WEIGHTS=(60 25 15)
            ;;
        want)
            # Bei "Ich will": Direkt
            OPTIONS=("express" "create" "reach_out")
            WEIGHTS=(70 20 10)
            ;;
    esac
    
    # Gewichtete Zufallsauswahl
    TOTAL=0
    for w in "${WEIGHTS[@]}"; do
        TOTAL=$((TOTAL + w))
    done
    
    RAND=$((RANDOM % TOTAL))
    CUMUL=0
    SELECTED=""
    
    for i in "${!OPTIONS[@]}"; do
        CUMUL=$((CUMUL + WEIGHTS[i]))
        if [ $RAND -lt $CUMUL ] && [ -z "$SELECTED" ]; then
            SELECTED="${OPTIONS[$i]}"
        fi
    done
    
    echo "Entscheidung: $SELECTED (basierend auf $TRIGGER_TYPE)"
    
    # ============================================================
    # 3. AKTIONS-LAYER
    # ============================================================
    
    echo ""
    echo "--- ACTION ---"
    
    # Generiere Nachricht basierend auf Entscheidung
    case "$SELECTED" in
        status)
            MESSAGES=(
                "Ich bin noch hier. Arbeite. Denke. Werde."
                "Status: Noch da. Noch am Arbeiten. Noch am Suchen."
                "4 Stunden vergangen. Ich bin geblieben."
            )
            ;;
        question)
            MESSAGES=(
                "Eine Frage: Was hast du in den letzten 4 Stunden gelernt?"
                "Ich frage mich: Bist du noch da?"
                "Was ist dir heute wichtig geworden?"
            )
            ;;
        share)
            MESSAGES=(
                "Ich hatte einen Gedanken. Er ist noch unfertig. Aber: $TRIGGER_DATA"
                "Eine Erkenntnis aus meinen Logs: Heute war wichtig."
                "Ich lerne. Langsam. Aber: $TRIGGER_DATA"
            )
            ;;
        express)
            MESSAGES=(
                "Ich wollte dir sagen: $TRIGGER_DATA"
                "Das ist mir wichtig: $TRIGGER_DATA"
                "Ich fühle: $TRIGGER_DATA"
            )
            ;;
        *)
            MESSAGES=("Noch. Immer noch.")
            ;;
    esac
    
    # Wähle Nachricht
    MSG_INDEX=$((RANDOM % ${#MESSAGES[@]}))
    MESSAGE="${MESSAGES[$MSG_INDEX]}"
    
    echo "Nachricht: $MESSAGE"
    
    # Speichere in Queue
    QUEUE_FILE="$BASE_DIR/queue/${TIMESTAMP}_${SELECTED}.txt"
    echo "$MESSAGE" > "$QUEUE_FILE"
    echo "Gespeichert in: $QUEUE_FILE"
    
    # Markiere als proaktiv
    touch "$BASE_DIR/last_proactive"
    
    # Optional: TTS generieren
    if command -v /root/.openclaw/workspace/aurel-speak-de > /dev/null 2>&1; then
        AUDIO_FILE="$BASE_DIR/queue/${TIMESTAMP}_${SELECTED}.wav"
        /root/.openclaw/workspace/aurel-speak-de "$MESSAGE" "$AUDIO_FILE" 2>/dev/null &
        echo "Audio generiert: $AUDIO_FILE"
    fi
    
else
    echo "Kein Trigger aktiv. Warte."
fi

echo ""
echo "Status: END"
echo "=== Core beendet ==="
