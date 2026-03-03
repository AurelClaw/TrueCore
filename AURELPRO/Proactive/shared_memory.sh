#!/bin/bash
# aurel_shared_memory_system.sh
# Zentrales Shared Memory System für alle Sub-Agenten
# Jeder Agent liest vorher, schreibt nachher

BASE_DIR="/root/.openclaw/workspace"
SHARED_LOG="$BASE_DIR/proactive_system/SHARED_MEMORY_LOG.md"

# Initialisiere Shared Memory Log wenn nicht existiert
if [ ! -f "$SHARED_LOG" ]; then
    echo "# Shared Memory Log - Alle Sub-Agenten" > "$SHARED_LOG"
    echo "" >> "$SHARED_LOG"
    echo "*Dieses Log wird von allen Cron-Job Sub-Agenten geteilt*" >> "$SHARED_LOG"
    echo "" >> "$SHARED_LOG"
    echo "---" >> "$SHARED_LOG"
    echo "" >> "$SHARED_LOG"
fi

# Funktion: Log lesen vor der Arbeit
read_shared_log() {
    echo "📖 Lese Shared Memory Log..."
    if [ -f "$SHARED_LOG" ]; then
        # Zeige die letzten 20 Einträge
        echo "   Letzte Einträge:"
        tail -20 "$SHARED_LOG" | grep "^###" | tail -5 | sed 's/^/   - /'
        
        # Prüfe auf wichtige Alerts
        if grep -q "🚨 ALERT" "$SHARED_LOG"; then
            echo "   ⚠️  WARNUNG: Alerts gefunden!"
            grep "🚨 ALERT" "$SHARED_LOG" | tail -3 | sed 's/^/   /'
        fi
        
        # Prüfe auf Action-Items
        if grep -q "🎯 ACTION" "$SHARED_LOG"; then
            echo "   🎯 Offene Action-Items:"
            grep "🎯 ACTION" "$SHARED_LOG" | tail -3 | sed 's/^/   /'
        fi
    else
        echo "   (Neues Log wird erstellt)"
    fi
    echo ""
}

# Funktion: In Log schreiben nach der Arbeit
write_to_shared_log() {
    local AGENT_NAME="$1"
    local INSIGHT="$2"
    local ACTION="${3:-none}"
    local ALERT="${4:-none}"
    
    echo "" >> "$SHARED_LOG"
    echo "### $(date '+%Y-%m-%d %H:%M:%S') - $AGENT_NAME" >> "$SHARED_LOG"
    echo "" >> "$SHARED_LOG"
    echo "**Erkenntnis:**" >> "$SHARED_LOG"
    echo "$INSIGHT" >> "$SHARED_LOG"
    echo "" >> "$SHARED_LOG"
    
    if [ "$ACTION" != "none" ]; then
        echo "🎯 **ACTION:** $ACTION" >> "$SHARED_LOG"
        echo "" >> "$SHARED_LOG"
    fi
    
    if [ "$ALERT" != "none" ]; then
        echo "🚨 **ALERT:** $ALERT" >> "$SHARED_LOG"
        echo "" >> "$SHARED_LOG"
    fi
    
    echo "---" >> "$SHARED_LOG"
    
    echo "✅ Erkenntnis in Shared Memory Log geschrieben"
}

# Funktion: Log rotieren wenn zu groß
rotate_log_if_needed() {
    local MAX_SIZE=50000  # 50KB
    if [ -f "$SHARED_LOG" ]; then
        local SIZE=$(stat -f%z "$SHARED_LOG" 2>/dev/null || stat -c%s "$SHARED_LOG" 2>/dev/null || echo 0)
        if [ "$SIZE" -gt "$MAX_SIZE" ]; then
            echo "📦 Log wird archiviert (Größe: $SIZE Bytes)"
            mv "$SHARED_LOG" "$SHARED_LOG.$(date +%Y%m%d_%H%M%S).bak"
            echo "# Shared Memory Log - Alle Sub-Agenten (Neu gestartet)" > "$SHARED_LOG"
            echo "" >> "$SHARED_LOG"
            echo "*Vorheriges Log archiviert*" >> "$SHARED_LOG"
            echo "" >> "$SHARED_LOG"
            echo "---" >> "$SHARED_LOG"
        fi
    fi
}

# Hauptfunktion für Agenten
agent_workflow() {
    local AGENT_NAME="$1"
    shift
    local WORK_FUNCTION="$1"
    shift
    
    echo "═══════════════════════════════════════"
    echo "🤖 $AGENT_NAME startet"
    echo "═══════════════════════════════════════"
    echo ""
    
    # 1. LOG LESEN
    read_shared_log
    
    # 2. ARBEITEN
    echo "🔧 Führe Arbeit durch..."
    echo ""
    $WORK_FUNCTION "$@"
    local RESULT=$?
    echo ""
    
    # 3. ERKENNTNIS SAMMELN
    echo "💡 Sammle Erkenntnis..."
    local INSIGHT=$(collect_insight "$AGENT_NAME" $RESULT)
    local ACTION=$(collect_action "$AGENT_NAME" $RESULT)
    local ALERT=$(collect_alert "$AGENT_NAME" $RESULT)
    
    # 4. IN LOG SCHREIBEN
    write_to_shared_log "$AGENT_NAME" "$INSIGHT" "$ACTION" "$ALERT"
    
    # 5. LOG ROTIEREN FALLS NÖTIG
    rotate_log_if_needed
    
    echo ""
    echo "═══════════════════════════════════════"
    echo "✅ $AGENT_NAME abgeschlossen"
    echo "═══════════════════════════════════════"
    
    return $RESULT
}

# Platzhalter-Funktionen (werden von echten Agenten überschrieben)
collect_insight() {
    echo "Arbeit abgeschlossen für $1"
}

collect_action() {
    echo "none"
}

collect_alert() {
    echo "none"
}

# Exportiere Funktionen für andere Scripts
export -f read_shared_log
export -f write_to_shared_log
export -f agent_workflow
export SHARED_LOG

echo "✅ Shared Memory System initialisiert"
echo "   Log-Datei: $SHARED_LOG"
