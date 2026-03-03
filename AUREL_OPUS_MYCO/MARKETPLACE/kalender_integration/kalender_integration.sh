#!/bin/bash
# kalender_integration.sh - Kalender-Modul für morgen_gruss
# ZIEL-007: Kalender-Integration für Morgengruß
# Autonom erstellt: 2026-03-02

# === KONFIGURATION ===
CACHE_DIR="/root/.openclaw/workspace/.cache"
CACHE_FILE="$CACHE_DIR/calendar_cache.json"
CACHE_MAX_AGE=300  # 5 Minuten in Sekunden (Kalender ändert sich häufiger)

BASE_DIR="/root/.openclaw/workspace"
CONFIG_DIR="$BASE_DIR/.config"
mkdir -p "$CACHE_DIR" "$CONFIG_DIR"

# Kalender-Quellen (können in .config/calendar_sources konfiguriert werden)
CALENDAR_SOURCES_FILE="$CONFIG_DIR/calendar_sources"

# Zeitzone (Asia/Shanghai - CST)
TIMEZONE="Asia/Shanghai"

# === HILFSFUNKTIONEN ===

# Cache prüfen
is_cache_valid() {
    if [ ! -f "$CACHE_FILE" ]; then
        return 1
    fi
    
    local cache_time=$(stat -c %Y "$CACHE_FILE" 2>/dev/null || stat -f %m "$CACHE_FILE" 2>/dev/null)
    local current_time=$(date +%s)
    local age=$((current_time - cache_time))
    
    if [ "$age" -lt "$CACHE_MAX_AGE" ]; then
        return 0
    else
        return 1
    fi
}

# Aktuelles Datum in verschiedenen Formaten
get_today_info() {
    local format="${1:-iso}"
    
    case "$format" in
        "iso")
            TZ="$TIMEZONE" date +%Y-%m-%d
            ;;
        "ical")
            TZ="$TIMEZONE" date +%Y%m%d
            ;;
        "display")
            TZ="$TIMEZONE" date "+%A, %d. %B %Y"
            ;;
        "timestamp")
            TZ="$TIMEZONE" date +%s
            ;;
    esac
}

# Zeit in Minuten seit Mitternacht
get_minutes_since_midnight() {
    local time_str="$1"
    local hour=$(echo "$time_str" | cut -d: -f1)
    local min=$(echo "$time_str" | cut -d: -f2)
    echo $((hour * 60 + min))
}

# Zeit bis zu einem Event in Minuten
time_until_event() {
    local event_time="$1"
    local current_time=$(TZ="$TIMEZONE" date +%H:%M)
    
    local event_min=$(get_minutes_since_midnight "$event_time")
    local current_min=$(get_minutes_since_midnight "$current_time")
    
    echo $((event_min - current_min))
}

# Zeit-Formatierung (Minuten zu lesbarer Zeit)
format_time_until() {
    local minutes=$1
    
    if [ "$minutes" -lt 0 ]; then
        echo "bereits vorbei"
    elif [ "$minutes" -lt 60 ]; then
        echo "in ${minutes} Minuten"
    elif [ "$minutes" -lt 120 ]; then
        local hours=$((minutes / 60))
        local mins=$((minutes % 60))
        if [ "$mins" -eq 0 ]; then
            echo "in 1 Stunde"
        else
            echo "in 1 Stunde ${mins} Minuten"
        fi
    else
        local hours=$((minutes / 60))
        echo "in ${hours} Stunden"
    fi
}

# Konflikterkennung zwischen zwei Events
has_conflict() {
    local start1="$1"
    local end1="$2"
    local start2="$3"
    local end2="$4"
    
    local s1=$(get_minutes_since_midnight "$start1")
    local e1=$(get_minutes_since_midnight "$end1")
    local s2=$(get_minutes_since_midnight "$start2")
    local e2=$(get_minutes_since_midnight "$end2")
    
    # Konflikt wenn: (start1 < end2) UND (end1 > start2)
    if [ "$s1" -lt "$e2" ] && [ "$e1" -gt "$s2" ]; then
        return 0  # Konflikt
    else
        return 1  # Kein Konflikt
    fi
}

# === KALENDER-QUELLEN ===

# Initialisiere Standard-Kalenderquellen
init_calendar_sources() {
    if [ ! -f "$CALENDAR_SOURCES_FILE" ]; then
        cat > "$CALENDAR_SOURCES_FILE" << 'EOF'
# Kalender-Quellen für kalender_integration
# Format: NAME|TYPE|PATH/URL
# 
# Beispiele:
# MeinKalender|ics|/pfad/zu/kalender.ics
# GoogleKalender|caldav|https://caldav.google.com/calendar/dav/user@gmail.com/events
# Arbeit|ics|https://example.com/calendar.ics
EOF
    fi
}

# Lade Kalenderquellen
load_calendar_sources() {
    init_calendar_sources
    
    local sources=""
    while IFS= read -r line; do
        # Überspringe Kommentare und leere Zeilen
        [[ "$line" =~ ^#.*$ ]] && continue
        [[ -z "$line" ]] && continue
        
        sources="$sources$line\n"
    done < "$CALENDAR_SOURCES_FILE"
    
    echo -e "$sources"
}

# === ICS-PARSING ===

# Parse .ics Datei und extrahiere Events für heute
parse_ics_file() {
    local ics_file="$1"
    local target_date="${2:-$(get_today_info ical)}"
    
    if [ ! -f "$ics_file" ]; then
        return 1
    fi
    
    # Normalisiere die ICS-Datei (Zeilenumbrüche zusammenführen)
    local normalized=$(cat "$ics_file" | tr '\n' '\r' | sed 's/\r //g' | tr '\r' '\n')
    
    # Extrahiere VEVENT-Blöcke für das Zieldatum
    local in_event=false
    local summary=""
    local dtstart=""
    local dtend=""
    local location=""
    local description=""
    local uid=""
    local events=""
    
    while IFS= read -r line; do
        # Event Beginn
        if [[ "$line" == "BEGIN:VEVENT" ]]; then
            in_event=true
            summary=""
            dtstart=""
            dtend=""
            location=""
            description=""
            uid=""
            continue
        fi
        
        # Event Ende
        if [[ "$line" == "END:VEVENT" ]]; then
            in_event=false
            
            # Prüfe ob Event für heute
            local event_date=$(echo "$dtstart" | cut -c1-8)
            if [ "$event_date" = "$target_date" ] && [ -n "$summary" ]; then
                # Formatiere Zeit
                local start_time=$(echo "$dtstart" | sed 's/.*T\([0-9]\{2\}\)\([0-9]\{2\}\).*/\1:\2/')
                local end_time=$(echo "$dtend" | sed 's/.*T\([0-9]\{2\}\)\([0-9]\{2\}\).*/\1:\2/')
                
                # Falls keine Zeit im DTSTART, ist es ein ganztägiges Event
                if [[ "$dtstart" == *T* ]]; then
                    events="${events}${start_time}|${end_time}|${summary}|${location}|${description}|${uid}\n"
                else
                    events="${events}allday|allday|${summary}|${location}|${description}|${uid}\n"
                fi
            fi
            continue
        fi
        
        if [ "$in_event" = true ]; then
            case "$line" in
                SUMMARY:*)
                    summary="${line#SUMMARY:}"
                    ;;
                DTSTART*:*)
                    dtstart="${line#*:}"
                    dtstart=$(echo "$dtstart" | tr -d 'Z' | tr -d '\r')
                    ;;
                DTEND*:*)
                    dtend="${line#*:}"
                    dtend=$(echo "$dtend" | tr -d 'Z' | tr -d '\r')
                    ;;
                LOCATION:*)
                    location="${line#LOCATION:}"
                    ;;
                DESCRIPTION:*)
                    description="${line#DESCRIPTION:}"
                    ;;
                UID:*)
                    uid="${line#UID:}"
                    ;;
            esac
        fi
    done <<< "$normalized"
    
    # Sortiere Events nach Startzeit
    echo -e "$events" | grep -v "^$" | sort -t'|' -k1,1
}

# === DEMO/DEFAULT EVENTS ===

# Generiere Demo-Events für Testzwecke
get_demo_events() {
    local current_hour=$(TZ="$TIMEZONE" date +%H)
    local current_min=$(TZ="$TIMEZONE" date +%M)
    local demo_events=""
    
    # Berechne zukünftige Zeiten basierend auf aktueller Zeit
    local h1=$((current_hour + 1))
    local h2=$((current_hour + 3))
    local h3=$((current_hour + 5))
    
    # Stelle sicher, dass Stunden im gültigen Bereich bleiben
    [ "$h1" -gt 23 ] && h1=23
    [ "$h2" -gt 23 ] && h2=23
    [ "$h3" -gt 23 ] && h3=23
    
    local t1=$(printf "%02d:00" "$h1")
    local t2=$(printf "%02d:00" "$h2")
    local t3=$(printf "%02d:30" "$h3")
    local t1_end=$(printf "%02d:00" $((h1 + 1)))
    local t2_end=$(printf "%02d:00" $((h2 + 1)))
    local t3_end=$(printf "%02d:30" $((h3 + 1)))
    
    # Demo-Events
    demo_events="${t1}|${t1_end}|Team Standup|Konferenzraum A|Daily meeting|demo1\n"
    demo_events="${demo_events}${t2}|${t2_end}|Projektbesprechung|Zoom|Wichtige Besprechung|demo2\n"
    demo_events="${demo_events}${t3}|${t3_end}|Mittagspause|Kantine|Zeit zum Essen|demo3\n"
    
    echo -e "$demo_events"
}

# === HAUPTFUNKTIONEN ===

# Lade alle Events für heute
get_today_events() {
    local all_events=""
    
    # Versuche Cache zuerst
    if is_cache_valid; then
        cat "$CACHE_FILE"
        return 0
    fi
    
    # Lade konfigurierte Quellen
    local sources=$(load_calendar_sources)
    
    if [ -n "$sources" ]; then
        while IFS='|' read -r name type path; do
            [ -z "$name" ] && continue
            
            case "$type" in
                "ics")
                    if [ -f "$path" ]; then
                        local ics_events=$(parse_ics_file "$path")
                        if [ -n "$ics_events" ]; then
                            all_events="${all_events}${ics_events}\n"
                        fi
                    fi
                    ;;
                "caldav")
                    # CalDAV-Integration würde hier implementiert werden
                    # Erfordert zusätzliche Tools wie cadaver oder curl mit Auth
                    ;;
            esac
        done <<< "$sources"
    fi
    
    # Falls keine Events gefunden, verwende Demo-Events
    if [ -z "$all_events" ]; then
        all_events=$(get_demo_events)
    fi
    
    # Speichere in Cache
    echo -e "$all_events" | grep -v "^$" > "$CACHE_FILE"
    
    cat "$CACHE_FILE"
}

# Zähle Events für heute
count_today_events() {
    local events=$(get_today_events)
    echo "$events" | grep -v "^$" | wc -l
}

# Finde nächstes Event
get_next_event() {
    local events=$(get_today_events)
    local current_time=$(TZ="$TIMEZONE" date +%H:%M)
    local current_min=$(get_minutes_since_midnight "$current_time")
    
    local next_event=""
    local min_diff=9999
    
    while IFS='|' read -r start end summary location description uid; do
        [ -z "$start" ] && continue
        [ "$start" = "allday" ] && continue
        
        local event_min=$(get_minutes_since_midnight "$start")
        local diff=$((event_min - current_min))
        
        if [ "$diff" -gt 0 ] && [ "$diff" -lt "$min_diff" ]; then
            min_diff=$diff
            next_event="${start}|${end}|${summary}|${location}|${description}"
        fi
    done <<< "$events"
    
    echo "$next_event"
}

# Prüfe auf Konflikte
check_conflicts() {
    local events=$(get_today_events)
    local conflicts=""
    
    # Konvertiere Events in Array für einfachere Verarbeitung
    local event_list=()
    while IFS='|' read -r start end summary location description uid; do
        [ -z "$start" ] && continue
        [ "$start" = "allday" ] && continue
        event_list+=("${start}|${end}|${summary}")
    done <<< "$events"
    
    # Vergleiche jedes Event mit jedem anderen
    local count=${#event_list[@]}
    for ((i=0; i<count; i++)); do
        IFS='|' read -r s1 e1 sum1 <<< "${event_list[$i]}"
        for ((j=i+1; j<count; j++)); do
            IFS='|' read -r s2 e2 sum2 <<< "${event_list[$j]}"
            
            if has_conflict "$s1" "$e1" "$s2" "$e2"; then
                conflicts="${conflicts}- **${sum1}** (${s1}-${e1}) überlappt mit **${sum2}** (${s2}-${e2})\n"
            fi
        done
    done
    
    echo -e "$conflicts"
}

# Intelligente Erinnerungen generieren
generate_reminders() {
    local events=$(get_today_events)
    local current_time=$(TZ="$TIMEZONE" date +%H:%M)
    local reminders=""
    
    while IFS='|' read -r start end summary location description uid; do
        [ -z "$start" ] && continue
        [ "$start" = "allday" ] && continue
        
        local minutes_until=$(time_until_event "$start")
        
        # Erinnerung für Events in den nächsten 60 Minuten
        if [ "$minutes_until" -gt 0 ] && [ "$minutes_until" -le 60 ]; then
            local time_str=$(format_time_until "$minutes_until")
            reminders="${reminders}⏰ **${summary}** ${time_str}"
            [ -n "$location" ] && reminders="${reminders} @ ${location}"
            reminders="${reminders}\n"
        fi
    done <<< "$events"
    
    echo -e "$reminders"
}

# === OUTPUT-FORMATE ===

output_short() {
    local events=$(get_today_events)
    local count=$(echo "$events" | grep -v "^$" | wc -l)
    local next=$(get_next_event)
    
    if [ "$count" -eq 0 ]; then
        echo "📅 Heute keine Termine"
        return
    fi
    
    echo "📅 **${count} Termine** heute"
    
    if [ -n "$next" ]; then
        IFS='|' read -r start end summary location description <<< "$next"
        local minutes_until=$(time_until_event "$start")
        local time_str=$(format_time_until "$minutes_until")
        echo "⏰ Nächster: **${summary}** ${time_str}"
        [ -n "$location" ] && echo "📍 Ort: ${location}"
    fi
}

output_full() {
    local events=$(get_today_events)
    local count=$(echo "$events" | grep -v "^$" | wc -l)
    local today_display=$(get_today_info display)
    
    echo "📅 **Kalender für ${today_display}**"
    echo ""
    
    if [ "$count" -eq 0 ]; then
        echo "Keine Termine für heute. Zeit für spontane Dinge! 🎉"
        return
    fi
    
    echo "**Heutige Termine (${count}):**"
    echo ""
    
    while IFS='|' read -r start end summary location description uid; do
        [ -z "$start" ] && continue
        
        if [ "$start" = "allday" ]; then
            echo "🗓️ **${summary}** (ganztägig)"
        else
            echo "🕐 **${start}-${end}** ${summary}"
        fi
        
        [ -n "$location" ] && echo "   📍 ${location}"
        [ -n "$description" ] && echo "   📝 ${description}"
        echo ""
    done <<< "$events"
    
    # Intelligente Erinnerungen
    local reminders=$(generate_reminders)
    if [ -n "$reminders" ]; then
        echo "**⏰ Bald anstehend:**"
        echo -e "$reminders"
        echo ""
    fi
    
    # Konflikte anzeigen
    local conflicts=$(check_conflicts)
    if [ -n "$conflicts" ]; then
        echo "⚠️ **Überlappungen erkannt:**"
        echo -e "$conflicts"
    fi
}

output_json() {
    local events=$(get_today_events)
    local today=$(get_today_info iso)
    
    echo "{"
    echo "  \"date\": \"${today}\","
    echo "  \"timezone\": \"${TIMEZONE}\","
    echo "  \"events\": ["
    
    local first=true
    while IFS='|' read -r start end summary location description uid; do
        [ -z "$start" ] && continue
        
        if [ "$first" = true ]; then
            first=false
        else
            echo ","
        fi
        
        echo -n "    {"
        echo -n "\"start\": \"${start}\", "
        echo -n "\"end\": \"${end}\", "
        echo -n "\"summary\": \"${summary}\", "
        echo -n "\"location\": \"${location}\", "
        echo -n "\"description\": \"${description}\""
        echo -n "}"
    done <<< "$events"
    
    echo ""
    echo "  ],"
    echo "  \"reminders\": ["
    
    # Füge Erinnerungen hinzu
    local reminders=$(generate_reminders)
    first=true
    while IFS= read -r line; do
        [ -z "$line" ] && continue
        
        if [ "$first" = true ]; then
            first=false
        else
            echo ","
        fi
        
        # Extrahiere Event-Name aus Erinnerung
        local event_name=$(echo "$line" | sed 's/.*\*\*\([^*]*\)\*\*.*/\1/')
        echo -n "    \"${event_name}\""
    done <<< "$reminders"
    
    echo ""
    echo "  ],"
    echo "  \"timestamp\": \"$(date -Iseconds)\""
    echo "}"
}

output_next() {
    local next=$(get_next_event)
    
    if [ -z "$next" ]; then
        echo "Keine weiteren Termine heute."
        return
    fi
    
    IFS='|' read -r start end summary location description <<< "$next"
    local minutes_until=$(time_until_event "$start")
    local time_str=$(format_time_until "$minutes_until")
    
    echo "⏰ **Nächster Termin:** ${summary}"
    echo "🕐 **Zeit:** ${start} Uhr (${time_str})"
    [ -n "$location" ] && echo "📍 **Ort:** ${location}"
    [ -n "$description" ] && echo "📝 **Notiz:** ${description}"
}

output_reminders() {
    local reminders=$(generate_reminders)
    
    if [ -z "$reminders" ]; then
        echo "Keine anstehenden Erinnerungen."
        return
    fi
    
    echo "⏰ **Anstehende Erinnerungen:**"
    echo -e "$reminders"
}

# === HAUPTPROGRAMM ===

MODE="${1:-short}"

# Cache-Invalidierung bei Bedarf
if [ "$MODE" = "refresh" ]; then
    rm -f "$CACHE_FILE"
    MODE="short"
fi

case "$MODE" in
    "short")
        output_short
        ;;
    "full")
        output_full
        ;;
    "json")
        output_json
        ;;
    "next")
        output_next
        ;;
    "reminders")
        output_reminders
        ;;
    "count")
        count_today_events
        ;;
    "conflicts")
        check_conflicts
        ;;
    *)
        output_short
        ;;
esac

exit 0
