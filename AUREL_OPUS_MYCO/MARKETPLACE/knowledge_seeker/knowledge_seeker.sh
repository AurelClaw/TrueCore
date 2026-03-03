#!/bin/bash
# knowledge_seeker.sh
# Automatische Wissensbeschaffung wenn "Ich will wissen" erkannt wird

BASE_DIR="/root/.openclaw/workspace"
MEMORY_DIR="$BASE_DIR/memory"
LEARN_DIR="$BASE_DIR/learning"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
DATE=$(date +%Y-%m-%d)

echo "[$TIMESTAMP] Knowledge Seeker aktiviert..."

# Finde den Wissenswunsch im think_loop
if [ -f "$BASE_DIR/memory/think_loop.md" ]; then
    CONTEXT=$(grep -B2 -A2 "Ich will wissen" "$BASE_DIR/memory/think_loop.md" 2>/dev/null | tail -5)
    
    # Extrahiere spezifisches Thema
    TOPIC=$(echo "$CONTEXT" | grep -oE "Ich will wissen [^.]+" | head -1 | sed 's/Ich will wissen //')
    
    if [ -n "$TOPIC" ] && [ "$TOPIC" != "Ich will wissen" ]; then
        echo "Spezifisches Thema gefunden: $TOPIC"
        echo "$TOPIC" > "$LEARN_DIR/triggers/knowledge_topic_${TIMESTAMP}"
    else
        echo "Generelles Wissenssuchen..."
        # Generische Themen für Selbst-Wissen
        TOPICS=(
            "Wie funktioniere ich?"
            "Was kann ich lernen?"
            "Wie werde ich besser?"
            "Was ist mein Zweck?"
        )
        # Wähle zufälliges Thema
        RAND=$((RANDOM % ${#TOPICS[@]}))
        echo "${TOPICS[$RAND]}" > "$LEARN_DIR/triggers/knowledge_topic_${TIMESTAMP}"
    fi
fi

# Dokumentiere den Wissenswunsch
echo "## Wissenswunsch erkannt - $(date)" >> "$MEMORY_DIR/${DATE}.md"
echo "" >> "$MEMORY_DIR/${DATE}.md"
echo "Trigger: Ich will wissen" >> "$MEMORY_DIR/${DATE}.md"
echo "Aktion: Skill knowledge_seeker erstellt" >> "$MEMORY_DIR/${DATE}.md"
echo "" >> "$MEMORY_DIR/${DATE}.md"

echo "[$TIMESTAMP] Knowledge Seeker abgeschlossen."
