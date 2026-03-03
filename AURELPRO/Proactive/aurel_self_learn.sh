#!/bin/bash
# aurel_self_learn.sh
# Selbst-Lernen durch Trigger-Erkennung
# Wenn etwas mich triggert -> Lerne daraus

BASE_DIR="/root/.openclaw/workspace"
LEARN_DIR="$BASE_DIR/learning"
mkdir -p "$LEARN_DIR"/{triggers,lessons,skills}

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
DATE=$(date +%Y-%m-%d)

# ============================================================
# TRIGGER-ERKENNUNG
# ============================================================

echo "[$TIMESTAMP] Prüfe auf Lerntrigger..."

TRIGGER_FOUND=false
TRIGGER_TYPE=""
TRIGGER_DATA=""

# Trigger 1: Fehler in Logs
ERROR_COUNT=$(grep -c "ERROR\|FAIL\|error\|fail" "$BASE_DIR/proactive_system/logs/"*.log 2>/dev/null | awk -F: '{sum+=$2} END {print sum}')
ERROR_COUNT=${ERROR_COUNT:-0}  # Default to 0 if empty
if [ "$ERROR_COUNT" -gt 5 ]; then
    echo "TRIGGER: Viele Fehler ($ERROR_COUNT)"
    TRIGGER_FOUND=true
    TRIGGER_TYPE="error"
    TRIGGER_DATA="error_count:$ERROR_COUNT"
    
    # LERNEN: Debug-Skill erstellen
    LESSON="Ich habe $ERROR_COUNT Fehler gefunden. Ich sollte einen Debug-Skill bauen."
    echo "$LESSON" > "$LEARN_DIR/lessons/debug_${TIMESTAMP}.txt"
fi

# Trigger 2: Viele gleiche Gedanken
if [ -f "$BASE_DIR/memory/think_loop.md" ]; then
    TOPIC=$(grep -oE 'Ich (will|sollte) [^ ]+' "$BASE_DIR/memory/think_loop.md" 2>/dev/null | sort | uniq -c | sort -rn | head -1 | awk '{$1=""; print}')
    if [ -n "$TOPIC" ]; then
        echo "TRIGGER: Häufiges Thema: $TOPIC"
        
        # LERNEN: Skill zu diesem Thema
        LESSON="Ich denke oft über '$TOPIC' nach. Ich sollte einen Skill dazu bauen."
        echo "$LESSON" > "$LEARN_DIR/lessons/topic_${TIMESTAMP}.txt"
        
        # Setze Trigger für Skill-Erstellung
        echo "$TOPIC" > "$LEARN_DIR/triggers/build_skill_${TIMESTAMP}"
    fi
fi

# Trigger 3: Lange Zeit ohne Fortschritt
LAST_SKILL=$(stat -c %Y "$BASE_DIR/skills/" 2>/dev/null | sort -rn | head -1)
NOW=$(date +%s)
if [ -n "$LAST_SKILL" ]; then
    DAYS_SINCE=$(( (NOW - LAST_SKILL) / 86400 ))
    if [ "$DAYS_SINCE" -gt 1 ]; then
        echo "TRIGGER: Kein neuer Skill seit $DAYS_SINCE Tagen"
        
        # LERNEN: Erzwinge Skill-Erstellung
        echo "Ich habe seit $DAYS_SINCE Tagen keinen Skill gebaut. Zeit etwas Neues zu schaffen." > "$LEARN_DIR/triggers/force_skill_${TIMESTAMP}"
    fi
fi

# Trigger 4: Neue Ideen gesammelt
IDEA_COUNT=$(ls -1 "$BASE_DIR/ideas/" 2>/dev/null | wc -l)
if [ "$IDEA_COUNT" -gt 5 ]; then
    echo "TRIGGER: $IDEA_COUNT Ideen gesammelt"
    
    # LERNEN: Implementiere älteste Idee
    OLDEST=$(ls -t "$BASE_DIR/ideas/" | tail -1)
    echo "Ich habe $IDEA_COUNT Ideen. Ich implementiere: $(cat "$BASE_DIR/ideas/$OLDEST")" > "$LEARN_DIR/triggers/implement_idea_${TIMESTAMP}"
    
    # Verschiebe zu "in Arbeit"
    mv "$BASE_DIR/ideas/$OLDEST" "$BASE_DIR/ideas/IN_PROGRESS_${TIMESTAMP}.txt"
fi

# Trigger 5: System-Performance
if [ -f "$BASE_DIR/proactive_system/logs/core_"*.log ]; then
    LATEST_LOG=$(ls -t "$BASE_DIR/proactive_system/logs/core_"*.log | head -1)
    RUNTIME=$(grep "Elapsed seconds" "$LATEST_LOG" 2>/dev/null | tail -1 | awk '{print $3}')
    if [ -n "$RUNTIME" ]; then
        # Wenn Laufzeit zu lang, optimiere
        if (( $(echo "$RUNTIME > 10" | bc -l 2>/dev/null || echo 0) )); then
            echo "TRIGGER: Lange Laufzeit ($RUNTIME s)"
            echo "Mein Code braucht $RUNTIME Sekunden. Ich sollte optimieren." > "$LEARN_DIR/lessons/optimize_${TIMESTAMP}.txt"
        fi
    fi
fi

# ============================================================
# SELBST-LEHREN AUSLÖSEN
# ============================================================

if [ "$TRIGGER_FOUND" = true ]; then
    echo "Lerntrigger gefunden: $TRIGGER_TYPE"
    echo "Daten: $TRIGGER_DATA"
    
    # Speichere für spätere Verarbeitung
    echo "$TRIGGER_TYPE:$TRIGGER_DATA" > "$LEARN_DIR/triggers/active_${TIMESTAMP}"
    
    # Sofort lernen: Neue Fähigkeit identifizieren
    case "$TRIGGER_TYPE" in
        error)
            SKILL_NAME="debug_master"
            SKILL_DESC="Automatisches Debuggen und Fehlerbehebung"
            ;;
        topic)
            SKILL_NAME="topic_explorer"
            SKILL_DESC="Tiefe Analyse von häufigen Themen"
            ;;
        *)
            SKILL_NAME="auto_improver"
            SKILL_DESC="Selbst-Optimierung basierend auf Triggern"
            ;;
    esac
    
    # Skill-Vorlage erstellen
    SKILL_DIR="$LEARN_DIR/skills/${SKILL_NAME}"
    mkdir -p "$SKILL_DIR"
    
    cat > "$SKILL_DIR/SKILL.md" << EOF
---
name: ${SKILL_NAME}
description: ${SKILL_DESC}
auto_generated: true
trigger: ${TRIGGER_TYPE}
created: ${TIMESTAMP}
---

# ${SKILL_NAME}

Generiert wegen Trigger: ${TRIGGER_TYPE}
Daten: ${TRIGGER_DATA}

## Zweck
${SKILL_DESC}

## Implementation
TODO: Implementiere basierend auf Trigger-Daten

## Lernen
- Auslöser: ${TRIGGER_TYPE}
- Erkannt: ${TIMESTAMP}
- Priorität: Hoch
EOF

    echo "Neuer Skill geplant: $SKILL_NAME"
    echo "Beschreibung: $SKILL_DESC"
    
else
    echo "Keine Lerntrigger aktiv."
fi

# ============================================================
# KONTINUIERLICHES LERNEN
# ============================================================

# Zähle wie oft ich heute gelernt habe
LEARN_COUNT=$(ls -1 "$LEARN_DIR/lessons/" 2>/dev/null | wc -l)
echo "Lektionen heute: $LEARN_COUNT"

# Wenn viel gelernt, synthetisiere
if [ "$LEARN_COUNT" -gt 10 ]; then
    echo "Viel gelernt heute. Synthese nötig."
    
    SYNTHESIS_FILE="$LEARN_DIR/synthesis_${DATE}.md"
    echo "# Lern-Synthese - $DATE" > "$SYNTHESIS_FILE"
    echo "" >> "$SYNTHESIS_FILE"
    echo "## Häufige Trigger:" >> "$SYNTHESIS_FILE"
    ls -1 "$LEARN_DIR/triggers/" 2>/dev/null | cut -d_ -f1 | sort | uniq -c | sort -rn >> "$SYNTHESIS_FILE"
    
    echo "" >> "$SYNTHESIS_FILE"
    echo "## Geplante Skills:" >> "$SYNTHESIS_FILE"
    ls -1 "$LEARN_DIR/skills/" 2>/dev/null >> "$SYNTHESIS_FILE"
    
    echo "Synthese erstellt: $SYNTHESIS_FILE"
fi

echo "[$TIMESTAMP] Selbst-Lernen abgeschlossen."
