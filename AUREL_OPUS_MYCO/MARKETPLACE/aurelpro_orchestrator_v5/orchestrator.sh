#!/bin/bash
# AURELPRO Orchestrator v5.5 - Extended Output with Details
# Zeigt Ziel-Beschreibung, was gemacht wurde, was implementiert wurde

set -e

WORKSPACE="/root/.openclaw/workspace"
AURELPRO_DIR="$WORKSPACE/AURELPRO"
GOALS_DIR="$AURELPRO_DIR/Goals"
LOGS_DIR="$AURELPRO_DIR/Logs"

mkdir -p "$GOALS_DIR" "$LOGS_DIR"

TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
LOG_FILE="$LOGS_DIR/orchestrator_$(date +%Y-%m-%d).log"

# Funktion: Ziel-Fortschritt extrahieren
extract_progress() {
    local goal_file="$1"
    if [[ -f "$goal_file" ]]; then
        grep -oE '[0-9]+%' "$goal_file" 2>/dev/null | head -1 | tr -d '%' || echo "0"
    else
        echo "0"
    fi
}

# Funktion: Ziel-Status extrahieren
extract_status() {
    local goal_file="$1"
    if [[ -f "$goal_file" ]]; then
        if grep -q "status: active\|Status: active\|Status: AKTIV" "$goal_file" 2>/dev/null; then
            echo "🔄 ACTIVE"
        elif grep -q "100%\|ERREICHT\|completed\|DONE" "$goal_file" 2>/dev/null; then
            echo "✅ DONE"
        else
            echo "⏳ PENDING"
        fi
    else
        echo "❓ UNKNOWN"
    fi
}

# Funktion: Ziel-Name extrahieren
extract_name() {
    local goal_file="$1"
    if [[ -f "$goal_file" ]]; then
        grep -m1 "^#" "$goal_file" 2>/dev/null | sed 's/^#* *//' | head -c 60 || basename "$goal_file" .md
    else
        basename "$goal_file" .md
    fi
}

# Funktion: Beschreibung extrahieren
extract_description() {
    local goal_file="$1"
    if [[ -f "$goal_file" ]]; then
        # Suche nach Beschreibung/Description
        grep -A5 -i "^## Beschreibung\|^## Description\|^**Beschreibung**" "$goal_file" 2>/dev/null | 
            grep -v "^##\|^**" | head -3 | sed 's/^[[:space:]]*//' | tr '\n' ' ' | head -c 200 || echo "Keine Beschreibung"
    else
        echo "Keine Beschreibung"
    fi
}

# Funktion: Erledigte Tasks extrahieren
extract_done_tasks() {
    local goal_file="$1"
    if [[ -f "$goal_file" ]]; then
        # Suche nach erledigten Checkboxen
        grep "\- \[x\]" "$goal_file" 2>/dev/null | sed 's/- \[x\] //' | head -3 | sed 's/^[[:space:]]*/✓ /' | tr '\n' '; ' | head -c 150 || echo ""
    else
        echo ""
    fi
}

# Funktion: Implementierte Features extrahieren
extract_implemented() {
    local goal_file="$1"
    if [[ -f "$goal_file" ]]; then
        # Suche nach "Implementiert", "Erstellt", "Fertig"
        grep -i "implementiert\|erstellt\|fertig\|abgeschlossen\|geschafft" "$goal_file" 2>/dev/null | 
            head -2 | sed 's/^[[:space:]]*//' | tr '\n' '; ' | head -c 150 || echo ""
    else
        echo ""
    fi
}

# Funktion: Letzte Aktivität extrahieren
extract_last_activity() {
    local goal_file="$1"
    if [[ -f "$goal_file" ]]; then
        # Suche nach Zeitstempeln oder Aktivitäten
        grep -E "[0-9]{4}-[0-9]{2}-[0-9]{2}|[0-9]{2}:[0-9]{2}" "$goal_file" 2>/dev/null | tail -1 | sed 's/^[[:space:]]*//' | head -c 80 || echo ""
    else
        echo ""
    fi
}

# Header
echo "⚛️ AURELPRO Orchestrator v5.5 | $TIMESTAMP"
echo "═══════════════════════════════════════════════════════════════"
echo ""

# Alle Ziele sammeln
declare -a goals=()
for goal_file in "$GOALS_DIR"/ZIEL-*.md; do
    [[ -f "$goal_file" ]] || continue
    goals+=("$goal_file")
done

echo "📊 ZIELE-ÜBERSICHT (${#goals[@]} total)"
echo "───────────────────────────────────────────────────────────────"
echo ""

# Ziele anzeigen mit Details
active_count=0
done_count=0
pending_count=0

for goal_file in "${goals[@]}"; do
    name=$(extract_name "$goal_file")
    status=$(extract_status "$goal_file")
    progress=$(extract_progress "$goal_file")
    short_name=$(basename "$goal_file" .md)
    description=$(extract_description "$goal_file")
    done_tasks=$(extract_done_tasks "$goal_file")
    implemented=$(extract_implemented "$goal_file")
    last_activity=$(extract_last_activity "$goal_file")
    
    # Kurze Ziel-Info
    printf "🎯 %-12s %-10s %3s%%\n" "$short_name" "$status" "$progress"
    printf "   📋 %s\n" "$name"
    
    # Beschreibung
    if [[ -n "$description" && "$description" != "Keine Beschreibung" ]]; then
        printf "   📝 %s\n" "$description"
    fi
    
    # Was wurde gemacht (erledigte Tasks)
    if [[ -n "$done_tasks" ]]; then
        printf "   ✅ Erledigt: %s\n" "$done_tasks"
    fi
    
    # Was wurde implementiert
    if [[ -n "$implemented" ]]; then
        printf "   🔧 Implementiert: %s\n" "$implemented"
    fi
    
    # Letzte Aktivität
    if [[ -n "$last_activity" ]]; then
        printf "   🕐 Letzte Aktivität: %s\n" "$last_activity"
    fi
    
    echo ""
    
    # Zählen
    if [[ "$status" == "🔄 ACTIVE" ]]; then
        ((active_count++))
    elif [[ "$status" == "✅ DONE" ]]; then
        ((done_count++))
    else
        ((pending_count++))
    fi
done 2>/dev/null || true

echo "═══════════════════════════════════════════════════════════════"
echo "📈 STATISTIK"
echo "   ✅ Erreicht:  $done_count"
echo "   🔄 Aktiv:     $active_count"
echo "   ⏳ Wartend:   $pending_count"
echo ""

# IDLE-Recovery Logik
if [[ $active_count -eq 0 ]]; then
    echo "⚠️  STATUS: IDLE → Starte Reaktivierung..."
    echo ""
    
    # Suche 80% Ziel
    for goal_file in "${goals[@]}"; do
        progress=$(extract_progress "$goal_file")
        if [[ "$progress" == "80" ]]; then
            name=$(extract_name "$goal_file")
            short_name=$(basename "$goal_file" .md)
            echo "🚀 REAKTIVIERE: $short_name (${progress}%)"
            echo "   $name"
            echo "Status: active" >> "$goal_file"
            echo "Activated: $TIMESTAMP by Orchestrator v5.5" >> "$goal_file"
            echo ""
            echo "✅ Ziel aktiviert und läuft jetzt!"
            active_count=1
            break
        fi
    done 2>/dev/null || true
    
    # Wenn kein 80% Ziel, suche erstes unvollständiges
    if [[ $active_count -eq 0 ]]; then
        for goal_file in "${goals[@]}"; do
            progress=$(extract_progress "$goal_file")
            if [[ "$progress" -lt 100 && "$progress" -gt 0 ]]; then
                name=$(extract_name "$goal_file")
                short_name=$(basename "$goal_file" .md)
                echo "🚀 REAKTIVIERE: $short_name (${progress}%)"
                echo "   $name"
                echo "Status: active" >> "$goal_file"
                echo "Activated: $TIMESTAMP by Orchestrator v5.5" >> "$goal_file"
                echo ""
                echo "✅ Ziel aktiviert und läuft jetzt!"
                active_count=1
                break
            fi
        done 2>/dev/null || true
    fi
    
    if [[ $active_count -eq 0 ]]; then
        echo "ℹ️  Alle Ziele abgeschlossen oder noch nicht gestartet."
        echo "   System wartet auf neue Ziele..."
    fi
else
    echo "✅ STATUS: ACTIVE ($active_count Ziel(e) in Bearbeitung)"
fi

echo ""
echo "⚛️ Noch."

# Log schreiben
echo "[$TIMESTAMP] Orchestrator v5.5 | Goals: ${#goals[@]} | Active: $active_count | Done: $done_count | Pending: $pending_count" >> "$LOG_FILE"
