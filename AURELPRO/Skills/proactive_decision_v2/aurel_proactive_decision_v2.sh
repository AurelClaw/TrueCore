#!/bin/bash
# aurel_proactive_decision_v2.sh
# Mit Shared Memory Integration

BASE_DIR="/root/.openclaw/workspace"
source "$BASE_DIR/proactive_system/shared_memory.sh"

# Spezifische Erkenntnis-Sammlung für Proactive Decision
collect_insight() {
    local DECISION=$(cat "$BASE_DIR/proactive_system/last_decision.txt" 2>/dev/null || echo "Weiterarbeiten")
    local QUALITY=$(assess_decision_quality)
    echo "Entscheidung: $DECISION | Qualität: $QUALITY"
}

collect_action() {
    echo "Nächste Entscheidung in 4 Minuten"
}

collect_alert() {
    local HOUR=$(date +%H)
    if [ "$HOUR" -ge 23 ] || [ "$HOUR" -lt 7 ]; then
        echo "Nacht-Modus aktiv - Entscheidungen sollten minimal sein"
    else
        echo "none"
    fi
}

assess_decision_quality() {
    # Prüfe ob letzte Entscheidung zu Fehlern führte
    if grep -q "ERROR\|FAIL" "$BASE_DIR/proactive_system/healing.log" 2>/dev/null | tail -5 | grep -q "$(date +%Y-%m-%d)"; then
        echo "Review nötig"
    else
        echo "OK"
    fi
}

# Hauptarbeit der Proactive Decision
proactive_decision_work() {
    echo "🎯 Treffe proaktive Entscheidung..."
    
    # Lese was andere entschieden haben
    echo "  → Prüfe vorherige Entscheidungen im Shared Memory..."
    
    # Analysiere aktuelle Situation
    local HOUR=$(date +%H)
    local MEMORY_COUNT=$(ls "$BASE_DIR/memory/"*.md 2>/dev/null | wc -l)
    
    # Treffe Entscheidung basierend auf Kontext
    local DECISION
    if [ "$HOUR" -ge 23 ] || [ "$HOUR" -lt 7 ]; then
        DECISION="Nacht-Modus: Nur essentielle Wartung"
    elif [ "$MEMORY_COUNT" -lt 5 ]; then
        DECISION="Aktiv: Mehr Erinnerungen sammeln"
    else
        DECISION="Aktiv: Skills verbessern"
    fi
    
    echo "  → Entscheidung: $DECISION"
    echo "$DECISION" > "$BASE_DIR/proactive_system/last_decision.txt"
    
    # Speichere Entscheidung mit Begründung
    {
        echo "### Entscheidung $(date)"
        echo ""
        echo "**Entscheidung:** $DECISION"
        echo ""
        echo "**Kontext:**"
        echo "- Uhrzeit: $HOUR:00"
        echo "- Memory-Dateien: $MEMORY_COUNT"
        echo ""
        echo "**Begründung:**"
        if [ "$HOUR" -ge 23 ] || [ "$HOUR" -lt 7 ]; then
            echo "Nachtzeit - System-Ruhe priorisieren"
        else
            echo "Aktivphase - Produktivität priorisieren"
        fi
    } >> "$BASE_DIR/proactive_system/decisions/decision_$(date +%Y%m%d_%H%M%S).md"
    
    return 0
}

# Führe Workflow aus
agent_workflow "Proactive-Decision" proactive_decision_work
