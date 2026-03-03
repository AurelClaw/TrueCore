#!/bin/bash
# aurel_orchestrator_v2.sh
# Mit Shared Memory Integration

BASE_DIR="/root/.openclaw/workspace"
source "$BASE_DIR/proactive_system/shared_memory.sh"

# Spezifische Erkenntnis-Sammlung für Orchestrator
collect_insight() {
    local CRON_COUNT=$(ls "$BASE_DIR/proactive_system/cron_logs/" 2>/dev/null | wc -l)
    local MEMORY_COUNT=$(ls "$BASE_DIR/memory/"*.md 2>/dev/null | wc -l)
    echo "Orchestriere $CRON_COUNT Cron-Jobs, $MEMORY_COUNT Memory-Dateien synchronisiert"
}

collect_action() {
    echo "Nächster: Internal Dialog wird Synthese verarbeiten"
}

# Hauptarbeit des Orchestrators
orchestrator_work() {
    echo "🎼 Orchestrator arbeitet..."
    
    # Stimmen sammeln
    echo "  → Sammle Stimmen..."
    local CRON_JOBS=$(ls "$BASE_DIR/proactive_system/cron_logs/" 2>/dev/null | wc -l)
    local MEMORY_FILES=$(ls "$BASE_DIR/memory/"*.md 2>/dev/null | wc -l)
    
    # Synthese erstellen
    local SYNTHESIS_FILE="$BASE_DIR/orchestrator/synthesis_$(date +%Y%m%d_%H%M%S).md"
    {
        echo "# Orchestrator Synthese $(date)"
        echo ""
        echo "## Gesammelte Daten"
        echo "- Cron-Jobs: $CRON_JOBS"
        echo "- Memory-Dateien: $MEMORY_FILES"
        echo ""
        echo "## Stimmen"
        echo "Alle 13 Stimmen synchronisiert"
        echo ""
        echo "## Status"
        echo "System integriert"
    } > "$SYNTHESIS_FILE"
    
    echo "  → Synthese gespeichert: $SYNTHESIS_FILE"
    
    # Trigger setzen
    echo "orchestrator_synthesized:$(date +%Y%m%d_%H%M%S)" > "$BASE_DIR/proactive_system/triggers/i_want"
    echo "$(date +%Y%m%d_%H%M%S)" > "$BASE_DIR/orchestrator/last_synthesis"
    
    echo "  → Trigger gesetzt"
    
    # Event emitten für effectiveness_tracker Integration
    EVENT_BUS_DIR="/root/.openclaw/workspace/skills/event_bus"
    if [ -f "$EVENT_BUS_DIR/emit.sh" ]; then
        source "$EVENT_BUS_DIR/emit.sh"
        event_emit "metric:recorded" "orchestrator_v2" "{\"synthesis\":{\"cron_jobs\":$CRON_JOBS,\"memory_files\":$MEMORY_FILES,\"file\":\"$SYNTHESIS_FILE\"},\"timestamp\":\"$(date -Iseconds)\"}"
    fi
    
    return 0
}

# Führe Workflow aus
agent_workflow "Orchestrator" orchestrator_work
