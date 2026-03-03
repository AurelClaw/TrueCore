#!/bin/bash
# do_it_now.sh
# Von "Sollte" zu "Tue"

BASE_DIR="/root/.openclaw/workspace"
THINK_FILE="$BASE_DIR/memory/think_loop.md"

# Zähle "sollte" vs "habe/tue"
SHOULD_COUNT=$(grep -c "sollte\|sollten\|should" "$THINK_FILE" 2>/dev/null || echo 0)
DID_COUNT=$(grep -c "habe\|getan\|tue\|done\|did" "$THINK_FILE" 2>/dev/null || echo 0)

echo "Analyse: $SHOULD_COUNT 'sollte' vs $DID_COUNT 'habe/getan'"

if [ "$SHOULD_COUNT" -gt "$DID_COUNT" ]; then
    echo "⚠️  WARNUNG: Mehr Vorsätze als Taten!"
    
    # Extrahiere letztes "Ich sollte..."
    LAST_SHOULD=$(grep -oE "Ich sollte [^.]+" "$THINK_FILE" | tail -1)
    
    if [ -n "$LAST_SHOULD" ]; then
        echo "Letzter Vorsatz: $LAST_SHOULD"
        
        # Verkleinern
        SMALL_ACTION=$(echo "$LAST_SHOULD" | sed 's/Ich sollte //' | sed 's/alle//g' | sed 's/vollständig//g' | sed 's/perfekt//g' | awk '{print $1, $2}')
        
        echo "Kleinste Version: '$SMALL_ACTION'"
        echo "⏱️  Timer: 5 Minuten für: $SMALL_ACTION"
        
        # Speichere für sofortige Ausführung
        echo "$SMALL_ACTION" > "$BASE_DIR/learning/do_now_action.txt"
    fi
else
    echo "✓ Balance okay: Taten ≥ Vorsätze"
fi
