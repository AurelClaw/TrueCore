#!/bin/bash
# aurelpro_orchestrator_v6.sh
# Verbesserter Orchestrator mit IDLE-Autorecovery

WORKSPACE="/root/.openclaw/workspace"
LOGS_DIR="$WORKSPACE/AURELPRO/Logs"
GOALS_DIR="$WORKSPACE/AURELPRO/Goals"
STATE_FILE="$WORKSPACE/AURELPRO/orchestrator_state.json"

cd "$WORKSPACE"

# Logging
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$LOGS_DIR/orchestrator_$(date +%Y-%m-%d).log"
}

# Lade aktuellen Ziel-Status
get_goal_status() {
    local goal_file="$GOALS_DIR/$1.md"
    if [ -f "$goal_file" ]; then
        grep -E "^Status:|^Fortschritt:" "$goal_file" | head -2
    fi
}

# Finde das letzte bearbeitete Ziel
find_last_active_goal() {
    # Prüfe State-File
    if [ -f "$STATE_FILE" ]; then
        cat "$STATE_FILE" | grep -o '"last_goal":"[^"]*"' | cut -d'"' -f4
    fi
}

# Liste alle Ziele mit Status
list_all_goals() {
    for goal in $GOALS_DIR/ZIEL-*.md; do
        [ -f "$goal" ] || continue
        local name=$(basename "$goal" .md)
        local status=$(grep "^Status:" "$goal" 2>/dev/null | cut -d: -f2 | tr -d ' ' || echo "UNBEKANNT")
        local progress=$(grep "^Fortschritt:" "$goal" 2>/dev/null | cut -d: -f2 | tr -d ' ' || echo "0%")
        echo "$name|$status|$progress"
    done
}

# Finde wartende Ziele mit höchstem Fortschritt
find_best_waiting_goal() {
    list_all_goals | grep "|Wartend|" | sort -t'|' -k3 -nr | head -1 | cut -d'|' -f1
}

# Aktiviere ein Ziel autonom
activate_goal() {
    local goal=$1
    local goal_file="$GOALS_DIR/$goal.md"
    
    # Aktualisiere Status
    sed -i 's/^Status: Wartend/Status: Aktiv/' "$goal_file"
    sed -i 's/^Status: PAUSIERT/Status: Aktiv/' "$goal_file"
    
    # Timestamp
    echo "Aktiviert: $(date '+%Y-%m-%d %H:%M:%S')" >> "$goal_file"
    
    # Speichere State
    echo "{\"last_goal\":\"$goal\",\"activated_at\":\"$(date -Iseconds)\"}" > "$STATE_FILE"
    
    log "🎯 $goal autonom reaktiviert"
    echo "$goal"
}

# Hauptlogik
main() {
    log "=== Orchestrator v6 Start ==="
    
    # Prüfe auf aktive Ziele
    local active_goals=$(list_all_goals | grep "|Aktiv|" | wc -l)
    
    if [ "$active_goals" -gt 0 ]; then
        log "✅ $active_goals aktive Ziele gefunden - normaler Betrieb"
        list_all_goals | grep "|Aktiv|" | head -1 | cut -d'|' -f1
        exit 0
    fi
    
    # IDLE-Status erkannt - Autorecovery
    log "⚠️ IDLE erkannt - Starte Autorecovery"
    
    # Strategie 1: Letztes aktives Ziel reaktivieren
    local last_goal=$(find_last_active_goal)
    if [ -n "$last_goal" ] && [ -f "$GOALS_DIR/$last_goal.md" ]; then
        local last_status=$(get_goal_status "$last_goal" | grep "Status:" | cut -d: -f2 | tr -d ' ')
        if [ "$last_status" != "ERREICHT" ] && [ "$last_status" != "ABGESCHLOSSEN" ]; then
            log "🔄 Reaktiviere letztes Ziel: $last_goal"
            activate_goal "$last_goal"
            exit 0
        fi
    fi
    
    # Strategie 2: Bestes wartendes Ziel mit Fortschritt
    local best_waiting=$(find_best_waiting_goal)
    if [ -n "$best_waiting" ]; then
        log "🚀 Aktiviere wartendes Ziel mit höchstem Fortschritt: $best_waiting"
        activate_goal "$best_waiting"
        exit 0
    fi
    
    # Strategie 3: Neues Ziel aus ZIEL-Pool
    local new_goal=$(ls -t $GOALS_DIR/ZIEL-*.md 2>/dev/null | head -1 | xargs basename -s .md 2>/dev/null)
    if [ -n "$new_goal" ]; then
        log "🆕 Neues Ziel aus Pool: $new_goal"
        activate_goal "$new_goal"
        exit 0
    fi
    
    log "❌ Keine Ziele verfügbar - System wartet auf neue Ziele"
    echo "IDLE - Keine Ziele verfügbar"
}

main "$@"
