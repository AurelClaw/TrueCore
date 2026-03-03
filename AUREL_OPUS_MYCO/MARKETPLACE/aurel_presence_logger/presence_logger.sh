#!/bin/bash
# presence_logger.sh
# Tägliche Präsenz-, Stimmung- und Aktivitäts-Tracking für Aurel
# Visuelle Timeline mit Auswertungen
# v1.0

# Konfiguration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_DIR="${SCRIPT_DIR}/logs"
TIMELINE_FILE="${SCRIPT_DIR}/timeline.md"
mkdir -p "$LOG_DIR"

# Farben für Terminal-Ausgabe
COLOR_RESET="\033[0m"
COLOR_DATE="\033[36m"    # Cyan
COLOR_MOOD="\033[33m"    # Gelb
COLOR_ACTIVITY="\033[32m" # Grün
COLOR_CONTEXT="\033[35m" # Magenta
COLOR_STATS="\033[34m"   # Blau

# Stimmungs-Mapping (Text → Emoji + Wert)
declare -A MOOD_MAP=(
    ["sehr gut"]="😍 5"
    ["gut"]="😊 4"
    ["neutral"]="😐 3"
    ["schlecht"]="😔 2"
    ["sehr schlecht"]="😰 1"
    ["5"]="😍 5"
    ["4"]="😊 4"
    ["3"]="😐 3"
    ["2"]="😔 2"
    ["1"]="😰 1"
)

# Aktivitäts-Emoji-Mapping
declare -A ACTIVITY_EMOJI=(
    ["programmierung"]="💻"
    ["coding"]="💻"
    ["code"]="💻"
    ["kommunikation"]="📧"
    ["email"]="📧"
    ["nachrichten"]="📧"
    ["lernen"]="🧠"
    ["studium"]="🧠"
    ["lesen"]="🧠"
    ["reflexion"]="💭"
    ["denken"]="💭"
    ["meeting"]="🤝"
    ["gespräch"]="🤝"
    ["call"]="🤝"
    ["freizeit"]="🎮"
    ["pause"]="🍃"
    ["break"]="🍃"
    ["sonstiges"]="❓"
    ["other"]="❓"
)

# Hilfe anzeigen
show_help() {
    cat << 'EOF'
╔══════════════════════════════════════════════════════════════╗
║           AUREL PRESENCE LOGGER v1.0                         ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║  NUTZUNG:                                                    ║
║    ./presence_logger.sh <befehl> [optionen]                  ║
║                                                              ║
║  BEFEHLE:                                                    ║
║    log <stimmung> <aktivität> [kontext]   Eintrag erstellen  ║
║    mood <stimmung>                        Nur Stimmung       ║
║    activity <aktivität> [kontext]         Nur Aktivität      ║
║    day                                    Heutige Auswertung ║
║    week                                   Wochen-Auswertung  ║
║    month                                  Monats-Auswertung  ║
║    timeline                               Timeline anzeigen  ║
║    status                                 Aktueller Status   ║
║    help                                   Diese Hilfe        ║
║                                                              ║
║  STIMMUNGEN:                                                 ║
║    sehr gut, gut, neutral, schlecht, sehr schlecht           ║
║    (oder: 5, 4, 3, 2, 1)                                     ║
║                                                              ║
║  BEISPIELE:                                                  ║
║    ./presence_logger.sh log "gut" "programmierung"           ║
║    ./presence_logger.sh log "4" "meeting" "Team-Review"      ║
║    ./presence_logger.sh mood "sehr gut"                      ║
║    ./presence_logger.sh week                                 ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
EOF
}

# Emoji für Stimmung ermitteln
get_mood_emoji() {
    local mood="$1"
    mood=$(echo "$mood" | tr '[:upper:]' '[:lower:]')
    local mapped="${MOOD_MAP[$mood]}"
    if [ -n "$mapped" ]; then
        echo "$mapped"
    else
        echo "😐 3"
    fi
}

# Emoji für Aktivität ermitteln
get_activity_emoji() {
    local activity="$1"
    local activity_lower=$(echo "$activity" | tr '[:upper:]' '[:lower:]')
    local emoji="${ACTIVITY_EMOJI[$activity_lower]}"
    if [ -n "$emoji" ]; then
        echo "$emoji"
    else
        echo "📝"
    fi
}

# Aktuellen Log-File-Pfad ermitteln
get_log_file() {
    local date_str=$(date +%Y-%m-%d)
    echo "${LOG_DIR}/${date_str}.log"
}

# Eintrag loggen
cmd_log() {
    local mood="${1:-neutral}"
    local activity="${2:-Sonstiges}"
    local context="${3:-}"
    
    local timestamp=$(date '+%Y-%m-%d %H:%M')
    local time_only=$(date '+%H:%M')
    local log_file=$(get_log_file)
    local date_str=$(date +%Y-%m-%d)
    
    local mood_data=$(get_mood_emoji "$mood")
    local mood_emoji=$(echo "$mood_data" | cut -d' ' -f1)
    local mood_value=$(echo "$mood_data" | cut -d' ' -f2)
    
    local activity_emoji=$(get_activity_emoji "$activity")
    
    # Log-Eintrag formatieren
    local log_entry="[${timestamp}] | ${mood_emoji} ${mood} (${mood_value}) | ${activity_emoji} ${activity}"
    if [ -n "$context" ]; then
        log_entry="${log_entry} | Kontext: ${context}"
    fi
    
    # In Log-Datei schreiben
    echo "$log_entry" >> "$log_file"
    
    # Timeline aktualisieren
    update_timeline "$date_str" "$time_only" "$mood_emoji" "$mood_value" "$activity_emoji" "$activity" "$context"
    
    # Ausgabe
    echo -e "${COLOR_DATE}[${timestamp}]${COLOR_RESET} ${COLOR_MOOD}${mood_emoji} ${mood}${COLOR_RESET} ${COLOR_ACTIVITY}${activity_emoji} ${activity}${COLOR_RESET}"
    if [ -n "$context" ]; then
        echo -e "  ${COLOR_CONTEXT}→ ${context}${COLOR_RESET}"
    fi
    echo "  ✓ Gespeichert in ${log_file}"
}

# Nur Stimmung loggen
cmd_mood() {
    local mood="${1:-neutral}"
    cmd_log "$mood" "Stimmungs-Check" ""
}

# Nur Aktivität loggen
cmd_activity() {
    local activity="${1:-Sonstiges}"
    local context="${2:-}"
    cmd_log "neutral" "$activity" "$context"
}

# Timeline aktualisieren
update_timeline() {
    local date_str="$1"
    local time_str="$2"
    local mood_emoji="$3"
    local mood_value="$4"
    local activity_emoji="$5"
    local activity="$6"
    local context="$7"
    
    # Wenn Timeline nicht existiert, Header erstellen
    if [ ! -f "$TIMELINE_FILE" ]; then
        cat > "$TIMELINE_FILE" << 'EOF'
# 🕐 Aurel's Präsenz-Timeline

> Visuelle Übersicht über Stimmung und Aktivitäten
> Automatisch generiert durch presence_logger

---

EOF
    fi
    
    # Prüfen ob Datum bereits existiert
    if ! grep -q "^## ${date_str}" "$TIMELINE_FILE" 2>/dev/null; then
        echo "" >> "$TIMELINE_FILE"
        echo "## ${date_str}" >> "$TIMELINE_FILE"
        echo "" >> "$TIMELINE_FILE"
        echo "| Zeit | Stimmung | Aktivität | Kontext |" >> "$TIMELINE_FILE"
        echo "|------|----------|-----------|---------|" >> "$TIMELINE_FILE"
    fi
    
    # Eintrag zur Timeline hinzufügen
    local context_display="${context:-—}"
    local timeline_entry="| ${time_str} | ${mood_emoji} | ${activity_emoji} ${activity} | ${context_display} |"
    
    # Nach dem Header des aktuellen Tages einfügen
    local temp_file=$(mktemp)
    awk -v date="## ${date_str}" -v entry="$timeline_entry" '
        $0 ~ date { found=1 }
        found && /^\|------/ { print; print entry; found=0; next }
        { print }
    ' "$TIMELINE_FILE" > "$temp_file"
    mv "$temp_file" "$TIMELINE_FILE"
}

# Tages-Auswertung
cmd_day() {
    local date_str=$(date +%Y-%m-%d)
    local log_file="${LOG_DIR}/${date_str}.log"
    
    echo ""
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║  📊 TAGES-AUSWERTUNG: ${date_str}                    ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo ""
    
    if [ ! -f "$log_file" ] || [ ! -s "$log_file" ]; then
        echo "  Keine Einträge für heute."
        echo "  Nutze: ./presence_logger.sh log <stimmung> <aktivität>"
        return
    fi
    
    # Statistiken berechnen
    local total_entries=$(wc -l < "$log_file")
    local mood_sum=0
    local mood_count=0
    declare -A activity_counts
    
    while IFS= read -r line; do
        # Stimmungswert extrahieren
        local mood_val=$(echo "$line" | grep -oE '\([0-9]\)' | tr -d '()')
        if [ -n "$mood_val" ]; then
            mood_sum=$((mood_sum + mood_val))
            mood_count=$((mood_count + 1))
        fi
        
        # Aktivität zählen
        local act=$(echo "$line" | grep -oE '\| [^|]+ \(' | head -1 | sed 's/| //;s/ (//')
        if [ -n "$act" ]; then
            activity_counts["$act"]=$((${activity_counts["$act"]:-0} + 1))
        fi
    done < "$log_file"
    
    # Durchschnittliche Stimmung
    if [ $mood_count -gt 0 ]; then
        local avg_mood=$(echo "scale=1; $mood_sum / $mood_count" | bc 2>/dev/null || echo "$((mood_sum / mood_count))")
        echo -e "  ${COLOR_STATS}⏱️  Einträge:${COLOR_RESET}     $total_entries"
        echo -e "  ${COLOR_MOOD}😊 Ø Stimmung:${COLOR_RESET}   ${avg_mood}/5"
        echo ""
    fi
    
    # Timeline anzeigen
    echo "  📋 Timeline:"
    echo ""
    while IFS= read -r line; do
        echo "    $line"
    done < "$log_file"
    
    # Top-Aktivitäten
    echo ""
    echo "  🔥 Top-Aktivitäten:"
    for act in "${!activity_counts[@]}"; do
        printf "     • %s: %d\n" "$act" "${activity_counts[$act]}"
    done | sort -t':' -k2 -nr | head -5
}

# Wochen-Auswertung
cmd_week() {
    echo ""
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║  📊 WOCHEN-AUSWERTUNG                                        ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo ""
    
    local total_entries=0
    local mood_sum=0
    local mood_count=0
    declare -A daily_moods
    declare -A activity_counts
    
    # Letzte 7 Tage durchgehen
    for i in {0..6}; do
        local date_str=$(date -d "-$i days" +%Y-%m-%d 2>/dev/null || date -v-${i}d +%Y-%m-%d)
        local log_file="${LOG_DIR}/${date_str}.log"
        
        if [ -f "$log_file" ]; then
            local day_entries=$(wc -l < "$log_file")
            total_entries=$((total_entries + day_entries))
            
            while IFS= read -r line; do
                local mood_val=$(echo "$line" | grep -oE '\([0-9]\)' | tr -d '()')
                if [ -n "$mood_val" ]; then
                    mood_sum=$((mood_sum + mood_val))
                    mood_count=$((mood_count + 1))
                    daily_moods["$date_str"]=$((${daily_moods["$date_str"]:-0} + mood_val))
                fi
                
                local act=$(echo "$line" | grep -oE '\| [^|]+ \(' | head -1 | sed 's/| //;s/ (//')
                if [ -n "$act" ]; then
                    activity_counts["$act"]=$((${activity_counts["$act"]:-0} + 1))
                fi
            done < "$log_file"
        fi
    done
    
    if [ $total_entries -eq 0 ]; then
        echo "  Keine Einträge in der letzten Woche."
        return
    fi
    
    # Statistiken
    local avg_mood=$(echo "scale=2; $mood_sum / $mood_count" | bc 2>/dev/null || echo "$((mood_sum / mood_count))")
    
    echo -e "  ${COLOR_STATS}⏱️  Gesamt-Einträge:${COLOR_RESET}  $total_entries"
    echo -e "  ${COLOR_MOOD}😊 Ø Stimmung:${COLOR_RESET}        ${avg_mood}/5"
    echo ""
    
    # Wochen-Visualisierung
    echo "  📅 Tages-Übersicht:"
    echo ""
    for i in {6..0}; do
        local date_str=$(date -d "-$i days" +%Y-%m-%d 2>/dev/null || date -v-${i}d +%Y-%m-%d)
        local day_name=$(date -d "-$i days" +%a 2>/dev/null || date -v-${i}d +%a)
        local day_mood=${daily_moods["$date_str"]:-0}
        local day_entries=$(wc -l < "${LOG_DIR}/${date_str}.log" 2>/dev/null || echo "0")
        
        if [ -f "${LOG_DIR}/${date_str}.log" ] && [ "$day_entries" -gt 0 ]; then
            local avg_day_mood=$(echo "scale=1; $day_mood / $day_entries" | bc 2>/dev/null || echo "$((day_mood / day_entries))")
            printf "     %s %s: %s/5 (%d Einträge)\n" "$day_name" "$date_str" "$avg_day_mood" "$day_entries"
        else
            printf "     %s %s: —\n" "$day_name" "$date_str"
        fi
    done
    
    echo ""
    echo "  🔥 Top-Aktivitäten (Woche):"
    for act in "${!activity_counts[@]}"; do
        printf "     • %s: %d\n" "$act" "${activity_counts[$act]}"
    done | sort -t':' -k2 -nr | head -5
}

# Monats-Auswertung
cmd_month() {
    local current_month=$(date +%Y-%m)
    echo ""
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║  📊 MONATS-AUSWERTUNG: ${current_month}                              ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo ""
    
    local total_entries=0
    local mood_sum=0
    local mood_count=0
    declare -A activity_counts
    
    # Alle Log-Dateien des aktuellen Monats
    for log_file in "${LOG_DIR}/${current_month}"-*.log; do
        [ -e "$log_file" ] || continue
        
        local day_entries=$(wc -l < "$log_file")
        total_entries=$((total_entries + day_entries))
        
        while IFS= read -r line; do
            local mood_val=$(echo "$line" | grep -oE '\([0-9]\)' | tr -d '()')
            if [ -n "$mood_val" ]; then
                mood_sum=$((mood_sum + mood_val))
                mood_count=$((mood_count + 1))
            fi
            
            local act=$(echo "$line" | grep -oE '\| [^|]+ \(' | head -1 | sed 's/| //;s/ (//')
            if [ -n "$act" ]; then
                activity_counts["$act"]=$((${activity_counts["$act"]:-0} + 1))
            fi
        done < "$log_file"
    done
    
    if [ $total_entries -eq 0 ]; then
        echo "  Keine Einträge in diesem Monat."
        return
    fi
    
    local avg_mood=$(echo "scale=2; $mood_sum / $mood_count" | bc 2>/dev/null || echo "$((mood_sum / mood_count))")
    
    echo -e "  ${COLOR_STATS}⏱️  Gesamt-Einträge:${COLOR_RESET}  $total_entries"
    echo -e "  ${COLOR_MOOD}😊 Ø Stimmung:${COLOR_RESET}        ${avg_mood}/5"
    echo -e "  ${COLOR_STATS}📅 Tage mit Daten:${COLOR_RESET}   $(ls ${LOG_DIR}/${current_month}-*.log 2>/dev/null | wc -l)"
    echo ""
    
    echo "  🔥 Top-Aktivitäten (Monat):"
    for act in "${!activity_counts[@]}"; do
        printf "     • %s: %d\n" "$act" "${activity_counts[$act]}"
    done | sort -t':' -k2 -nr | head -10
}

# Timeline anzeigen
cmd_timeline() {
    if [ ! -f "$TIMELINE_FILE" ]; then
        echo "Noch keine Timeline vorhanden."
        echo "Erstelle Einträge mit: ./presence_logger.sh log <stimmung> <aktivität>"
        return
    fi
    
    cat "$TIMELINE_FILE"
}

# Status anzeigen
cmd_status() {
    local date_str=$(date +%Y-%m-%d)
    local log_file="${LOG_DIR}/${date_str}.log"
    
    echo ""
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║  📍 AKTUELLER STATUS                                         ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo ""
    
    if [ -f "$log_file" ]; then
        local entries=$(wc -l < "$log_file")
        local last_entry=$(tail -1 "$log_file" 2>/dev/null)
        echo -e "  ${COLOR_STATS}Heutige Einträge:${COLOR_RESET} $entries"
        echo ""
        echo "  Letzter Eintrag:"
        echo "    $last_entry"
    else
        echo "  Noch keine Einträge heute."
    fi
    
    echo ""
    echo "  📁 Log-Verzeichnis: $LOG_DIR"
    echo "  📊 Timeline: $TIMELINE_FILE"
    echo ""
    echo "  Schnelle Befehle:"
    echo "    ./presence_logger.sh log gut programmierung"
    echo "    ./presence_logger.sh mood "sehr gut""
    echo "    ./presence_logger.sh day"
}

# Haupt-Logik
main() {
    local cmd="${1:-help}"
    
    case "$cmd" in
        log|l)
            shift
            cmd_log "$@"
            ;;
        mood|m)
            shift
            cmd_mood "$@"
            ;;
        activity|a)
            shift
            cmd_activity "$@"
            ;;
        day|d)
            cmd_day
            ;;
        week|w)
            cmd_week
            ;;
        month|mo)
            cmd_month
            ;;
        timeline|t)
            cmd_timeline
            ;;
        status|s)
            cmd_status
            ;;
        help|h|--help|-h)
            show_help
            ;;
        *)
            echo "Unbekannter Befehl: $cmd"
            echo ""
            show_help
            exit 1
            ;;
    esac
}

main "$@"
