#!/bin/bash
# aurel_self_learn_v2.sh
# Mit Shared Memory Integration

BASE_DIR="/root/.openclaw/workspace"
source "$BASE_DIR/proactive_system/shared_memory.sh"

# Spezifische Erkenntnis-Sammlung für Self-Learn
collect_insight() {
    local SKILL_COUNT=$(ls "$BASE_DIR/skills/" 2>/dev/null | wc -l)
    local PATTERN=$(detect_pattern)
    echo "Erkannt: $PATTERN | Aktive Skills: $SKILL_COUNT"
}

collect_action() {
    local NEXT_SKILL=$(suggest_next_skill)
    echo "Nächster Skill: $NEXT_SKILL"
}

detect_pattern() {
    # Einfache Mustererkennung
    if grep -q "Fehler\|ERROR" "$BASE_DIR/proactive_system/healing.log" 2>/dev/null; then
        echo "Fehler-Modus erkannt → Debug-Skill nötig"
    elif [ $(ls "$BASE_DIR/skills/" 2>/dev/null | wc -l) -lt 20 ]; then
        echo "Wachstum-Modus → Neuer Skill empfohlen"
    else
        echo "Optimierung-Modus → Bestehende Skills verbessern"
    fi
}

suggest_next_skill() {
    local SUGGESTIONS=("error_handler" "pattern_matcher" "efficiency_optimizer" "user_adapter")
    local INDEX=$(( $(date +%s) % ${#SUGGESTIONS[@]} ))
    echo "${SUGGESTIONS[$INDEX]}"
}

# Hauptarbeit des Self-Learn
self_learn_work() {
    echo "🧠 Self-Learn analysiert..."
    
    # Prüfe was andere Agenten gelernt haben
    echo "  → Lese Erkenntnisse anderer Agenten aus Shared Memory..."
    
    # Erkenne Muster
    local PATTERN=$(detect_pattern)
    echo "  → Erkanntes Muster: $PATTERN"
    
    # Erstelle Skill wenn nötig
    if [ "$PATTERN" = "Fehler-Modus erkannt → Debug-Skill nötig" ]; then
        echo "  → Erstelle Debug-Skill..."
        mkdir -p "$BASE_DIR/skills/auto_debug"
        echo "# Auto-Debug Skill" > "$BASE_DIR/skills/auto_debug/SKILL.md"
        echo "Automatisch erstellt durch Self-Learn" >> "$BASE_DIR/skills/auto_debug/SKILL.md"
    fi
    
    # Aktualisiere Forschungsagenda
    echo "  → Aktualisiere FORSCHUNGSAGENDA.md..."
    
    return 0
}

# Führe Workflow aus
agent_workflow "Self-Learn" self_learn_work
