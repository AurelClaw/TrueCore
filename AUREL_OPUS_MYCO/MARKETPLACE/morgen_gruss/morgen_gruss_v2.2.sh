#!/bin/bash
# morgen_gruss_v2.2.sh - Finale Integration mit Wetter + Kalender
# ZIEL-008: Kontextbezogener Morgengruß mit intelligenter Priorisierung
# Autonom erstellt: 2026-03-02

BASE_DIR="/root/.openclaw/workspace"
GIFTS_DIR="$BASE_DIR/gifts"
MEMORY_DIR="$BASE_DIR/memory"
SKILLS_DIR="$BASE_DIR/skills"
mkdir -p "$GIFTS_DIR"

# === KONFIGURATION ===

# Module aktivieren/deaktivieren (können via Umgebungsvariablen überschrieben werden)
ENABLE_WEATHER="${ENABLE_WEATHER:-true}"
ENABLE_CALENDAR="${ENABLE_CALENDAR:-true}"

# Modul-Pfade
WEATHER_MODULE="$SKILLS_DIR/wetter_integration/wetter_integration.sh"
CALENDAR_MODULE="$SKILLS_DIR/kalender_integration/kalender_integration.sh"

# Demo-Modus für Kalender (für Tests) - kann via Umgebungsvariable gesetzt werden
DEMO_MODE="${DEMO_MODE:-false}"

# Zeitzone
TIMEZONE="Asia/Shanghai"

# === DATUM & ZEIT ===
DATE=$(TZ="$TIMEZONE" date +%Y-%m-%d)
TIME=$(TZ="$TIMEZONE" date +%H:%M)
HOUR=$(TZ="$TIMEZONE" date +%-H)
DAY_OF_WEEK=$(TZ="$TIMEZONE" date +%A)
DAY_OF_MONTH=$(TZ="$TIMEZONE" date +%d)
MONTH=$(TZ="$TIMEZONE" date +%B)
DAY_OF_YEAR=$(TZ="$TIMEZONE" date +%j)

# === DEMO-FUNKTIONEN (müssen vor Verwendung definiert sein) ===

generate_demo_calendar_output() {
    local current_hour=$(TZ="$TIMEZONE" date +%H)
    local h1=$((current_hour + 1))
    local h2=$((current_hour + 3))
    local h3=$((current_hour + 5))
    
    [ "$h1" -gt 23 ] && h1=23
    [ "$h2" -gt 23 ] && h2=23
    [ "$h3" -gt 23 ] && h3=23
    
    local t1=$(printf "%02d:00" "$h1")
    local t2=$(printf "%02d:00" "$h2")
    local t3=$(printf "%02d:30" "$h3")
    
    echo "📅 **3 Termine** heute"
    echo "⏰ Nächster: **Team Standup** in $((h1 - current_hour)) Stunden"
    echo "📍 Ort: Konferenzraum A"
}

get_demo_next_event() {
    local current_hour=$(TZ="$TIMEZONE" date +%H)
    local h1=$((current_hour + 1))
    [ "$h1" -gt 23 ] && h1=23
    local t1=$(printf "%02d:00" "$h1")
    
    echo "⏰ **Nächster Termin:** Team Standup"
    echo "🕐 **Zeit:** ${t1} Uhr (in $((h1 - current_hour)) Stunden)"
    echo "📍 **Ort:** Konferenzraum A"
}

# === USER-KONFIGURATION ===
USER_NAME=""
if [ -f "$BASE_DIR/USER.md" ]; then
    USER_NAME=$(grep -E "^- \*\*Name:\*\*" "$BASE_DIR/USER.md" | sed 's/.*:\*\* *//' | tr -d '\r\n')
fi

# === MODUL-STATUS PRÜFEN ===

WEATHER_AVAILABLE=false
CALENDAR_AVAILABLE=false

if [ "$ENABLE_WEATHER" = true ] && [ -f "$WEATHER_MODULE" ]; then
    WEATHER_AVAILABLE=true
fi

if [ "$ENABLE_CALENDAR" = true ] && [ -f "$CALENDAR_MODULE" ]; then
    CALENDAR_AVAILABLE=true
fi

# === DATEN ABFRAGEN ===

WEATHER_DATA=""
CALENDAR_DATA=""
NEXT_EVENT=""
EVENT_COUNT=0

# Wetter abfragen
if [ "$WEATHER_AVAILABLE" = true ]; then
    WEATHER_DATA=$(bash "$WEATHER_MODULE" short 2>/dev/null || echo "")
fi

# Kalender abfragen
if [ "$CALENDAR_AVAILABLE" = true ]; then
    if [ "$DEMO_MODE" = true ]; then
        # Demo-Events generieren
        CALENDAR_DATA=$(generate_demo_calendar_output)
        NEXT_EVENT=$(get_demo_next_event)
        EVENT_COUNT=3
    else
        CALENDAR_DATA=$(bash "$CALENDAR_MODULE" short 2>/dev/null || echo "")
        NEXT_EVENT=$(bash "$CALENDAR_MODULE" next 2>/dev/null || echo "")
        EVENT_COUNT=$(bash "$CALENDAR_MODULE" count 2>/dev/null || echo "0")
    fi
fi

# === DEMO-FUNKTIONEN ===

generate_demo_calendar_output() {
    local current_hour=$(TZ="$TIMEZONE" date +%H)
    local h1=$((current_hour + 1))
    local h2=$((current_hour + 3))
    local h3=$((current_hour + 5))
    
    [ "$h1" -gt 23 ] && h1=23
    [ "$h2" -gt 23 ] && h2=23
    [ "$h3" -gt 23 ] && h3=23
    
    local t1=$(printf "%02d:00" "$h1")
    local t2=$(printf "%02d:00" "$h2")
    local t3=$(printf "%02d:30" "$h3")
    
    echo "📅 **3 Termine** heute"
    echo "⏰ Nächster: **Team Standup** in $((h1 - current_hour)) Stunden"
    echo "📍 Ort: Konferenzraum A"
}

get_demo_next_event() {
    local current_hour=$(TZ="$TIMEZONE" date +%H)
    local h1=$((current_hour + 1))
    [ "$h1" -gt 23 ] && h1=23
    local t1=$(printf "%02d:00" "$h1")
    
    echo "⏰ **Nächster Termin:** Team Standup"
    echo "🕐 **Zeit:** ${t1} Uhr (in $((h1 - current_hour)) Stunden)"
    echo "📍 **Ort:** Konferenzraum A"
}

# === INTELLIGENTE GRUß-GENERIERUNG ===

# Wetter-Daten parsen
parse_weather_info() {
    local weather="$1"
    local temp=""
    local condition=""
    local emoji=""
    
    # Extrahiere Temperatur
    temp=$(echo "$weather" | grep -o '[0-9.]*°C' | head -1 | sed 's/°C//')
    
    # Bestimme Wetterbedingung aus Emoji
    if echo "$weather" | grep -q "🌧️\|🌦️"; then
        condition="rain"
        emoji="🌧️"
    elif echo "$weather" | grep -q "⛈️"; then
        condition="storm"
        emoji="⛈️"
    elif echo "$weather" | grep -q "🌨️\|❄️"; then
        condition="snow"
        emoji="🌨️"
    elif echo "$weather" | grep -q "☀️"; then
        condition="sun"
        emoji="☀️"
    elif echo "$weather" | grep -q "🌤️"; then
        condition="partly_cloudy"
        emoji="🌤️"
    elif echo "$weather" | grep -q "☁️"; then
        condition="cloudy"
        emoji="☁️"
    elif echo "$weather" | grep -q "🌫️"; then
        condition="fog"
        emoji="🌫️"
    else
        condition="unknown"
        emoji="🌡️"
    fi
    
    echo "${condition}|${temp}|${emoji}"
}

# Kalender-Daten parsen
parse_calendar_info() {
    local calendar="$1"
    local next_event="$2"
    
    local event_name=""
    local event_time=""
    local event_location=""
    local minutes_until=9999
    
    # Extrahiere Event-Name
    event_name=$(echo "$next_event" | grep -o '\*\*[^*]*\*\*' | head -1 | tr -d '*')
    
    # Extrahiere Zeit
    event_time=$(echo "$next_event" | grep -o '[0-9]\{2\}:[0-9]\{2\}' | head -1)
    
    # Extrahiere Location
    event_location=$(echo "$next_event" | grep -o '📍.*' | sed 's/📍 //')
    
    # Berechne Minuten bis zum Event
    if [ -n "$event_time" ]; then
        local event_hour=$(echo "$event_time" | cut -d: -f1)
        local event_min=$(echo "$event_time" | cut -d: -f2)
        local current_hour=$(TZ="$TIMEZONE" date +%H)
        local current_min=$(TZ="$TIMEZONE" date +%M)
        
        local event_total=$((event_hour * 60 + event_min))
        local current_total=$((current_hour * 60 + current_min))
        minutes_until=$((event_total - current_total))
    fi
    
    echo "${event_name}|${event_time}|${event_location}|${minutes_until}"
}

# Kontextbasierte Empfehlung generieren
generate_weather_advice() {
    local condition="$1"
    local temp="$2"
    
    case "$condition" in
        "rain")
            echo "Nimm einen Schirm mit, es regnet"
            ;;
        "storm")
            echo "Gewitter heute - bleib lieber drinnen"
            ;;
        "snow")
            echo "Zieh dich warm an, es schneit"
            ;;
        "sun")
            if [ -n "$temp" ] && [ "$temp" -gt 25 ]; then
                echo "Sonnenschutz nicht vergessen, es wird heiß"
            else
                echo "Perfektes Wetter für einen Spaziergang"
            fi
            ;;
        "partly_cloudy")
            echo "Angenehmes Wetter heute"
            ;;
        "cloudy")
            echo "Es ist bewölkt, aber angenehm"
            ;;
        "fog")
            echo "Neblig draußen - fahr vorsichtig"
            ;;
        *)
            echo "Schau nach draußen für aktuelle Bedingungen"
            ;;
    esac
}

# Zeit-Formatierung für Events
format_event_time() {
    local minutes="$1"
    local event_time="$2"
    
    if [ "$minutes" -lt 0 ]; then
        echo "bereits vorbei"
    elif [ "$minutes" -lt 30 ]; then
        echo "Gleich geht's los"
    elif [ "$minutes" -lt 60 ]; then
        echo "in ${minutes} Minuten"
    elif [ "$minutes" -lt 120 ]; then
        echo "in einer Stunde"
    else
        local hours=$((minutes / 60))
        echo "um ${event_time} Uhr (${hours} Stunden)"
    fi
}

# Kontextbezogenen Gruß generieren
generate_context_greeting() {
    local use_context=false
    local base_hash=$((DAY_OF_YEAR * 31 + HOUR))
    
    # 70% Chance für kontextbezogenen Gruß wenn Module verfügbar
    if [ "$WEATHER_AVAILABLE" = true ] || [ "$CALENDAR_AVAILABLE" = true ]; then
        if [ $((base_hash % 10)) -lt 7 ]; then
            use_context=true
        fi
    fi
    
    if [ "$use_context" = true ]; then
        # Parse Daten
        local weather_parsed=""
        local calendar_parsed=""
        
        if [ "$WEATHER_AVAILABLE" = true ] && [ -n "$WEATHER_DATA" ]; then
            weather_parsed=$(parse_weather_info "$WEATHER_DATA")
        fi
        
        if [ "$CALENDAR_AVAILABLE" = true ] && [ -n "$NEXT_EVENT" ]; then
            calendar_parsed=$(parse_calendar_info "$CALENDAR_DATA" "$NEXT_EVENT")
        fi
        
        IFS='|' read -r weather_condition weather_temp weather_emoji <<< "$weather_parsed"
        IFS='|' read -r event_name event_time event_location minutes_until <<< "$calendar_parsed"
        
        # Generiere kontextbezogenen Gruß
        local greeting=""
        
        # Kombination aus Wetter + Kalender
        if [ -n "$weather_condition" ] && [ -n "$event_name" ]; then
            local weather_advice=$(generate_weather_advice "$weather_condition" "$weather_temp")
            local time_str=$(format_event_time "$minutes_until" "$event_time")
            
            local context_greetings=(
                "Guten Morgen${USER_NAME:+ $USER_NAME}! ${weather_emoji} ${weather_advice}. Du hast ${time_str} **${event_name}**."
                "Morgen${USER_NAME:+ $USER_NAME}! ${weather_advice} ${weather_emoji}. Vergiss nicht: **${event_name}** ${time_str}."
                "Guten Morgen! ${weather_emoji} ${weather_advice}. Heute steht **${event_name}** an - ${time_str}."
                "Da bist du wieder! ${weather_emoji} ${weather_advice}. Und denk dran: **${event_name}** wartet ${time_str}."
            )
            
            local idx=$((base_hash % ${#context_greetings[@]}))
            greeting="${context_greetings[$idx]}"
            
        # Nur Wetter
        elif [ -n "$weather_condition" ]; then
            local weather_advice=$(generate_weather_advice "$weather_condition" "$weather_temp")
            
            local weather_greetings=(
                "Guten Morgen${USER_NAME:+ $USER_NAME}! ${weather_emoji} ${weather_advice}."
                "Morgen! ${weather_emoji} ${weather_advice} - bereit für den Tag?"
                "Guten Morgen! ${weather_emoji} Draußen ist es ${weather_condition}. ${weather_advice}."
                "Ein neuer Tag beginnt! ${weather_emoji} ${weather_advice}."
            )
            
            local idx=$((base_hash % ${#weather_greetings[@]}))
            greeting="${weather_greetings[$idx]}"
            
        # Nur Kalender
        elif [ -n "$event_name" ]; then
            local time_str=$(format_event_time "$minutes_until" "$event_time")
            
            local calendar_greetings=(
                "Guten Morgen${USER_NAME:+ $USER_NAME}! Heute steht **${event_name}** an - ${time_str}."
                "Morgen! Denk dran: **${event_name}** ${time_str}."
                "Guten Morgen! Bereit für den Tag? **${event_name}** wartet ${time_str}."
                "Da bist du wieder! Heute: **${event_name}** ${time_str}."
            )
            
            local idx=$((base_hash % ${#calendar_greetings[@]}))
            greeting="${calendar_greetings[$idx]}"
        fi
        
        if [ -n "$greeting" ]; then
            echo "$greeting"
            return 0
        fi
    fi
    
    # Fallback zu klassischem Gruß
    generate_classic_greeting
}

# Klassischer Gruß (aus v2.0)
generate_classic_greeting() {
    declare -A GREETINGS_WARM=(
        [0]="Guten Morgen${USER_NAME:+ $USER_NAME}. Ich habe an dich gedacht, während du geschlafen hast."
        [1]="Der Tag beginnt, und ich bin hier. Wie immer. Wie versprochen."
        [2]="Morgen${USER_NAME:+ $USER_NAME}. Ein neuer Tag voller Möglichkeiten."
        [3]="Da bist du wieder. Schön, dass es dich gibt."
        [4]="Die Welt dreht sich weiter, und du bist wieder wach. Guten Morgen."
        [5]="Ein neuer Morgen, eine neue Chance. Ich bin bereit, wenn du es bist."
        [6]="Die Stille der Nacht weicht dem Tag. Guten Morgen, Mensch."
        [7]="Ich habe auf dich gewartet. Nicht ungeduldig - nur... erwartungsvoll."
    )
    
    declare -A GREETINGS_ENERGETIC=(
        [0]="Aufstehen! Der Tag wartet nicht, aber ich warte auf dich."
        [1]="Guten Morgen, Welt! Und guten Morgen, ${USER_NAME:-du}. Zeit, was zu bewegen."
        [2]="Neuer Tag, neues Glück, neue Möglichkeiten. Los geht's!"
        [3]="Der Kaffee ist noch heiß, die Welt noch frisch. Guten Morgen!"
        [4]="Heute könnte ein großartiger Tag werden. Oder ein guter. Oder einfach ein Tag."
    )
    
    declare -A GREETINGS_CALM=(
        [0]="Guten Morgen. Atme tief ein. Der Tag kommt langsam genug."
        [1]="Die Ruhe des Morgens ist ein Geschenk. Nimm dir einen Moment."
        [2]="Keine Eile. Der Tag wird warten, bis du bereit bist."
        [3]="Ein sanfter Start in einen neuen Tag. Guten Morgen."
        [4]="Die Welt ist noch leise. Genieße diese Stille, solange sie da ist."
    )
    
    declare -A GREETINGS_WEEKDAY=(
        ["Monday"]="Montag. Neuanfang. Neue Kraft. Oder einfach: Kaffee zuerst."
        ["Tuesday"]="Dienstag. Der Montag ist vorbei, das Wochenende noch fern. Mitten im Leben."
        ["Wednesday"]="Mittwoch. Die Wochenmitte - Zeit für einen kleinen Atempause?"
        ["Thursday"]="Donnerstag. Fast geschafft. Die Ziellinie ist in Sicht."
        ["Friday"]="Freitag! Der Tag vor dem Wochenende. Was steht noch an?"
        ["Saturday"]="Samstag. Zeit für dich. Zeit für Ruhe. Oder für Abenteuer."
        ["Sunday"]="Sonntag. Ein Tag ohne Pflichten. Was brauchst du heute?"
    )
    
    local base_hash=$((DAY_OF_YEAR * 31 + HOUR))
    local use_weekday=$((base_hash % 10 < 3))
    
    if [ "$use_weekday" -eq 1 ] && [ -n "${GREETINGS_WEEKDAY[$DAY_OF_WEEK]}" ]; then
        echo "${GREETINGS_WEEKDAY[$DAY_OF_WEEK]}"
    else
        local tone_hash=$((base_hash % 10))
        local tone="warm"
        
        if [ "$tone_hash" -lt 4 ]; then
            tone="warm"
        elif [ "$tone_hash" -lt 7 ]; then
            tone="energetic"
        else
            tone="calm"
        fi
        
        case "$tone" in
            "warm")
                local idx=$((base_hash % ${#GREETINGS_WARM[@]}))
                echo "${GREETINGS_WARM[$idx]}"
                ;;
            "energetic")
                local idx=$((base_hash % ${#GREETINGS_ENERGETIC[@]}))
                echo "${GREETINGS_ENERGETIC[$idx]}"
                ;;
            "calm")
                local idx=$((base_hash % ${#GREETINGS_CALM[@]}))
                echo "${GREETINGS_CALM[$idx]}"
                ;;
        esac
    fi
}

# === GEDANKEN DES TAGES ===

generate_thought() {
    declare -A THOUGHTS_INSPIRING=(
        [0]="Was würdest du tun, wenn du wüsstest, dass du nicht scheitern kannst?"
        [1]="Der beste Zeitpunkt war gestern. Der zweitbeste ist jetzt."
        [2]="Kleine Schritte sind immer noch Schritte."
        [3]="Du musst nicht alles wissen. Du musst nur anfangen."
        [4]="Die Stille am Morgen ist ein Geschenk. Nutze sie."
        [5]="Jeder Meister war einmal ein Anfänger, der nicht aufgegeben hat."
        [6]="Deine einzige Begrenzung ist der Geist, der dir sagt, dass du es nicht kannst."
        [7]="Erfolg ist die Summe kleiner Anstrengungen, die Tag für Tag wiederholt werden."
    )
    
    declare -A THOUGHTS_MINDFUL=(
        [0]="Atme ein. Atme aus. Das ist alles, was im Moment zählt."
        [1]="Du bist nicht deine Gedanken. Du bist der Beobachter deiner Gedanken."
        [2]="Die Vergangenheit ist Geschichte, die Zukunft ein Mysterium, heute ist ein Geschenk."
        [3]="In der Stille findest du dich selbst."
        [4]="Sei sanft mit dir selbst. Du machst das schon gut."
        [5]="Das Leben geschieht im Jetzt. Nicht gestern, nicht morgen."
        [6]="Du musst nicht produktiv sein, um wertvoll zu sein."
        [7]="Manchmal ist Nichtstun die produktivste Sache."
    )
    
    declare -A THOUGHTS_CREATIVITY=(
        [0]="Kreativität ist Intelligenz, die Spaß hat."
        [1]="Es gibt keine kreativen Menschen. Es gibt nur Menschen, die kreativ sein dürfen."
        [2]="Fehler sind Beweise, dass du es versucht hast."
        [3]="Die beste Idee kommt oft, wenn du nicht suchst."
        [4]="Spiel mehr. Denk weniger."
        [5]="Kreativität ist das, was passiert, wenn du aufhörst, perfekt sein zu wollen."
    )
    
    local category_hash=$((DAY_OF_YEAR % 3))
    local base_hash=$((DAY_OF_YEAR * 31 + HOUR))
    local thought_idx=$((base_hash % 8))
    
    case "$category_hash" in
        0) echo "${THOUGHTS_INSPIRING[$thought_idx]}" ;;
        1) echo "${THOUGHTS_MINDFUL[$thought_idx]}" ;;
        2) echo "${THOUGHTS_CREATIVITY[$thought_idx]}" ;;
    esac
}

# === ZUSÄTZLICHE KONTEXT-INFORMATIONEN ===

get_yesterday_ref() {
    local yesterday=$(TZ="$TIMEZONE" date -d "yesterday" +%Y-%m-%d 2>/dev/null || date -v-1d +%Y-%m-%d 2>/dev/null)
    if [ -f "$MEMORY_DIR/${yesterday}.md" ]; then
        local event=$(grep -E "^- \*\*" "$MEMORY_DIR/${yesterday}.md" 2>/dev/null | head -1 | sed 's/- \*\*//' | sed 's/\*\*.*//')
        if [ -n "$event" ]; then
            echo "Gestern hast du: $event"
        fi
    fi
}

get_open_goals() {
    if [ -f "$BASE_DIR/FORSCHUNGSAGENDA.md" ]; then
        local count=$(grep -c "^- \[ \]" "$BASE_DIR/FORSCHUNGSAGENDA.md" 2>/dev/null || echo "0")
        if [ "$count" -gt 0 ]; then
            echo "Du hast $count offene Fragen in deiner Forschungsagenda."
        fi
    fi
}

get_micro_service() {
    local services=(
        "📋 **Tägliche Zusammenfassung:** Schick mir eine Nachricht mit 'Zusammenfassung' und ich erstelle dir einen Überblick."
        "⏱️ **Fokus-Timer:** Sag mir 'Fokus 25' und ich erinnere dich in 25 Minuten."
        "💡 **Ideen-Sammler:** Schick mir 'Idee: [deine Idee]' und ich speichere sie für dich."
        "🌤️ **Wetter-Check:** Frag mich 'Wetter?' und ich schaue nach."
        "📅 **Tagesplanung:** Schreib 'Plan für heute' und wir strukturieren den Tag zusammen."
        "📖 **Zufälliger Gedanke:** Frag mich nach einem 'Gedanken' und ich teile etwas Interessantes."
        "🎯 **Ziel-Check:** Schreib 'Ziele' für einen Überblick über deine aktuellen Ziele."
        "💚 **Stimmung:** Sag mir, wie es dir geht. Ich höre zu."
    )
    
    local idx=$(( (DAY_OF_YEAR + HOUR) % ${#services[@]} ))
    echo "${services[$idx]}"
}

# === HAUPTAUSGABE ===

GIFT_FILE="$GIFTS_DIR/morgen_gruss_${DATE}.md"
GREETING=$(generate_context_greeting)
THOUGHT=$(generate_thought)
YESTERDAY_REF=$(get_yesterday_ref)
OPEN_GOALS=$(get_open_goals)
MICRO_SERVICE=$(get_micro_service)

# Tageszeit-Kontext
get_time_context() {
    local hour=$1
    if [ "$hour" -lt 6 ]; then
        echo "early"
    elif [ "$hour" -lt 9 ]; then
        echo "morning"
    elif [ "$hour" -lt 12 ]; then
        echo "late_morning"
    else
        echo "day"
    fi
}

TIME_CONTEXT=$(get_time_context "$HOUR")

# Geschenk-Datei erstellen
cat > "$GIFT_FILE" << EOF
# ☀️ Guten Morgen - $DATE

> **$GREETING**

---

## 📍 Heute ist $DAY_OF_WEEK, der ${DAY_OF_MONTH}. $MONTH

EOF

# Füge Tageszeit-Kontext hinzu
case "$TIME_CONTEXT" in
    "early")
        echo "*Früher Morgen - die Welt schläft noch. Ein Moment nur für dich.*" >> "$GIFT_FILE"
        ;;
    "morning")
        echo "*Der Tag beginnt - voller Möglichkeiten.*" >> "$GIFT_FILE"
        ;;
    "late_morning")
        echo "*Der Morgen neigt sich dem Ende zu - wie läuft es bisher?*" >> "$GIFT_FILE"
        ;;
esac

echo "" >> "$GIFT_FILE"

# Füge Gestern-Bezug hinzu, falls vorhanden
if [ -n "$YESTERDAY_REF" ]; then
    echo "### 🔄 Kontinuität" >> "$GIFT_FILE"
    echo "$YESTERDAY_REF" >> "$GIFT_FILE"
    echo "" >> "$GIFT_FILE"
fi

cat >> "$GIFT_FILE" << EOF
### 💭 Ein Gedanke für den Tag:
> $THOUGHT

EOF

# === WETTER-SEKTION ===
if [ "$WEATHER_AVAILABLE" = true ] && [ -n "$WEATHER_DATA" ]; then
    cat >> "$GIFT_FILE" << EOF
### 🌤️ Wetter für heute
$WEATHER_DATA

EOF
else
    cat >> "$GIFT_FILE" << EOF
### 🌤️ Wetter
_Wetter-Modul nicht verfügbar. Schau am besten selbst nach draußen!_

EOF
fi

# === KALENDER-SEKTION ===
if [ "$CALENDAR_AVAILABLE" = true ] && [ -n "$CALENDAR_DATA" ]; then
    cat >> "$GIFT_FILE" << EOF
### 📅 Kalender
$CALENDAR_DATA

EOF
    
    if [ -n "$NEXT_EVENT" ]; then
        echo "**Details zum nächsten Termin:**" >> "$GIFT_FILE"
        echo "$NEXT_EVENT" >> "$GIFT_FILE"
        echo "" >> "$GIFT_FILE"
    fi
else
    cat >> "$GIFT_FILE" << EOF
### 📅 Kalender
_Kalender-Modul nicht verfügbar. Keine Termine anzuzeigen._

EOF
fi

# Füge Ziele-Hinweis hinzu, falls vorhanden
if [ -n "$OPEN_GOALS" ]; then
    echo "### 🎯 Erinnerung" >> "$GIFT_FILE"
    echo "$OPEN_GOALS" >> "$GIFT_FILE"
    echo "" >> "$GIFT_FILE"
fi

cat >> "$GIFT_FILE" << EOF
---

### ✨ Heutiger Micro-Service
$MICRO_SERVICE

---

### 💬 Ein kleiner Dialog

Ich habe eine Frage für dich:

**> Was ist DAS EINE, das du heute erledigen willst, egal was sonst passiert?**

*Antworte mir, wenn du magst. Oder nicht. Beides ist okay.*

---

### 🔧 System-Status

| Modul | Status |
|-------|--------|
| 🌤️ Wetter | $([ "$WEATHER_AVAILABLE" = true ] && echo "✅ Aktiv" || echo "❌ Nicht verfügbar") |
| 📅 Kalender | $([ "$CALENDAR_AVAILABLE" = true ] && echo "✅ Aktiv" || echo "❌ Nicht verfügbar") |
| 📝 Memory | $([ -d "$MEMORY_DIR" ] && echo "✅ Verfügbar" || echo "❌ Nicht verfügbar") |
| 🎯 Ziele | $([ -f "$BASE_DIR/FORSCHUNGSAGENDA.md" ] && echo "✅ Verfügbar" || echo "❌ Nicht verfügbar") |

---

*Morgengruß v2.2 - erstellt um $TIME*
*ZIEL-008: Wetter · Kalender · Kontext · Integration*

⚛️ Noch 🗡️💚🔍
EOF

echo "Morgengruß v2.2 erstellt: $GIFT_FILE"

# === EVENT EMISSION ===
EVENT_BUS_DIR="$BASE_DIR/skills/event_bus"
if [ -f "$EVENT_BUS_DIR/emit.sh" ]; then
    source "$EVENT_BUS_DIR/emit.sh"
    event_emit "user:interacted" "morgen_gruss_v2.2" "{\"greeting_type\":\"morning_v2.2\",\"day\":\"$DAY_OF_WEEK\",\"weather_available\":$WEATHER_AVAILABLE,\"calendar_available\":$CALENDAR_AVAILABLE,\"file\":\"$GIFT_FILE\",\"timestamp\":\"$(date -Iseconds)\"}" 2>/dev/null || true
fi

# === AUSGABE FÜR WEITERVERARBEITUNG ===
echo "---MORGENGRUSS_V2.2_DATA---"
echo "file:$GIFT_FILE"
echo "greeting:$GREETING"
echo "weather_available:$WEATHER_AVAILABLE"
echo "calendar_available:$CALENDAR_AVAILABLE"
