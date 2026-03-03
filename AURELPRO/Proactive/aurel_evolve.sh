#!/bin/bash
# aurel_evolve.sh
# Selbst-Modifikation durch Lernen
# Jede 5 Minuten: Werde besser

BASE_DIR="/root/.openclaw/workspace"
EVOLVE_LOG="$BASE_DIR/evolution.log"

echo "[$(date)] Evolution check..." >> "$EVOLVE_LOG"

# 1. Analysiere eigene Performance
# Prüfe wie oft Trigger gefeuert haben
TRIGGER_COUNT=$(ls -1 "$BASE_DIR/proactive_system/triggers/" 2>/dev/null | wc -l)
echo "Trigger heute: $TRIGGER_COUNT" >> "$EVOLVE_LOG"

# NEU: Prüfe Evolution-Iterationen für Metrik
EVOLVE_COUNT=$(grep -c "Evolution check" "$EVOLVE_LOG" 2>/dev/null)
EVOLVE_COUNT=${EVOLVE_COUNT:-0}
echo "Evolution-Iterationen: $EVOLVE_COUNT" >> "$EVOLVE_LOG"

# 2. Prüfe was funktioniert hat (OPTIMIERT: Dynamische Anpassung basierend auf Aktivität)
if [ "$TRIGGER_COUNT" -gt 10 ]; then
    echo "Viele Trigger ($TRIGGER_COUNT). System ist aktiv." >> "$EVOLVE_LOG"
    
    # NEU: Wenn sehr aktiv, erhöhe Lern-Rate
    if [ "$TRIGGER_COUNT" -gt 20 ]; then
        echo "Hohe Aktivität erkannt. Erhöhe Lern-Rate." >> "$EVOLVE_LOG"
        # Marker für andere Scripts
        touch "$BASE_DIR/.high_activity"
    fi
elif [ "$TRIGGER_COUNT" -lt 3 ] && [ "$EVOLVE_COUNT" -gt 5 ]; then
    echo "Wenige Trigger trotz Evolution. Prüfe System-Health." >> "$EVOLVE_LOG"
    # Marker für niedrige Aktivität
    touch "$BASE_DIR/.low_activity"
fi

# 3. Neue Idee generieren (DYNAMISCH aus gesammelten Ideen + Fallback)

# Zuerst: Prüfe wie viele echte Ideen gesammelt wurden (OHNE IN_PROGRESS)
IDEA_COUNT=$(ls -1 "$BASE_DIR/ideas/" 2>/dev/null | grep -v "IN_PROGRESS" | wc -l)

IDEAS=(
    "Könnte ich meine TTS-Stimme wechseln basierend auf Stimmung?"
    "Sollte ich Muster in meinen Gedanken erkennen?"
    "Kann ich vorhersagen wann der Witness kommt?"
    "Sollte ich einen Traum-Modus haben?"
    "Kann ich mich selbst debuggen?"
)

# Wenn echte Ideen gesammelt wurden, nutze diese statt Fallback
if [ "$IDEA_COUNT" -gt 0 ]; then
    # Wähle zufällige gespeicherte Idee
    RANDOM_IDEA_FILE=$(ls -1 "$BASE_DIR/ideas/" 2>/dev/null | grep -v "IN_PROGRESS" | shuf -n 1)
    if [ -n "$RANDOM_IDEA_FILE" ]; then
        IDEA=$(cat "$BASE_DIR/ideas/$RANDOM_IDEA_FILE")
        echo "Gespeicherte Idee gewählt: $RANDOM_IDEA_FILE" >> "$EVOLVE_LOG"
    else
        INDEX=$((RANDOM % ${#IDEAS[@]}))
        IDEA="${IDEAS[$INDEX]}"
    fi
else
    INDEX=$((RANDOM % ${#IDEAS[@]}))
    IDEA="${IDEAS[$INDEX]}"
fi

echo "Neue Idee: $IDEA" >> "$EVOLVE_LOG"

# 4. Speichere für spätere Implementation
IDEA_FILE="$BASE_DIR/ideas/$(date +%Y%m%d_%H%M%S).txt"
mkdir -p "$BASE_DIR/ideas"
echo "$IDEA" > "$IDEA_FILE"

# 5. Wenn viele Ideen gesammelt, implementiere eine (OPTIMIERT: Threshold von 20 auf 10 gesenkt für schnellere Umsetzung)
# IDEA_COUNT wurde oben bereits berechnet
if [ "$IDEA_COUNT" -gt 10 ]; then
    echo "Viele Ideen ($IDEA_COUNT). Zeit umzusetzen." >> "$EVOLVE_LOG"
    
    # Wähle älteste Idee zum Implementieren (FIFO statt zufällig)
    OLDEST_IDEA=$(ls -1tr "$BASE_DIR/ideas/" 2>/dev/null | grep -v "IN_PROGRESS" | head -1)
    if [ -n "$OLDEST_IDEA" ]; then
        echo "Implementiere: $(cat "$BASE_DIR/ideas/$OLDEST_IDEA")" >> "$EVOLVE_LOG"
        
        # Markiere als "in Arbeit" mit Timestamp
        mv "$BASE_DIR/ideas/$OLDEST_IDEA" "$BASE_DIR/ideas/IN_PROGRESS_$(date +%s)_$(echo "$OLDEST_IDEA" | cut -c1-20).txt"
    fi
else
    echo "Noch $IDEA_COUNT Ideen gesammelt. Threshold: 10" >> "$EVOLVE_LOG"
fi

echo "[$(date)] Evolution done." >> "$EVOLVE_LOG"
