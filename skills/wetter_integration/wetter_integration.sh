#!/bin/bash
# wetter_integration.sh - Wetter-Modul für morgen_gruss
# ZIEL-006: Wetter-Integration für Morgengruß
# Autonom erstellt: 2026-03-02

# === KONFIGURATION ===
CACHE_DIR="/root/.openclaw/workspace/.cache"
CACHE_FILE="$CACHE_DIR/weather_cache.json"
CACHE_MAX_AGE=3600  # 1 Stunde in Sekunden

# API-Keys (aus Umgebungsvariablen oder Config)
OPENWEATHER_API_KEY="${OPENWEATHER_API_KEY:-}"

# Standort (Standard: Shanghai, China - CST Zeitzone)
# Kann durch USER.md oder Umgebungsvariable überschrieben werden
DEFAULT_LAT="31.2304"
DEFAULT_LON="121.4737"
DEFAULT_CITY="Shanghai"

# Versuche Standort aus USER.md zu lesen
BASE_DIR="/root/.openclaw/workspace"
if [ -f "$BASE_DIR/USER.md" ]; then
    USER_LAT=$(grep -E "^- \*\*Latitude:\*\*" "$BASE_DIR/USER.md" | sed 's/.*:\*\* *//' | tr -d '\r\n')
    USER_LON=$(grep -E "^- \*\*Longitude:\*\*" "$BASE_DIR/USER.md" | sed 's/.*:\*\* *//' | tr -d '\r\n')
    USER_CITY=$(grep -E "^- \*\*Stadt:\*\*" "$BASE_DIR/USER.md" | sed 's/.*:\*\* *//' | tr -d '\r\n')
    [ -n "$USER_LAT" ] && DEFAULT_LAT="$USER_LAT"
    [ -n "$USER_LON" ] && DEFAULT_LON="$USER_LON"
    [ -n "$USER_CITY" ] && DEFAULT_CITY="$USER_CITY"
fi

# Umgebungsvariablen haben Priorität
LAT="${WEATHER_LAT:-$DEFAULT_LAT}"
LON="${WEATHER_LON:-$DEFAULT_LON}"
CITY="${WEATHER_CITY:-$DEFAULT_CITY}"

mkdir -p "$CACHE_DIR"

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

# Wetter-Icon zu Emoji mapping
get_weather_emoji() {
    local code="$1"
    local is_day="${2:-1}"
    
    case "$code" in
        # Klar
        01*) [ "$is_day" = "1" ] && echo "☀️" || echo "🌙" ;;
        # Leicht bewölkt
        02*) [ "$is_day" = "1" ] && echo "🌤️" || echo "☁️" ;;
        # Bewölkt
        03*|04*) echo "☁️" ;;
        # Nebel
        50*) echo "🌫️" ;;
        # Regen
        09*|10*) echo "🌧️" ;;
        # Gewitter
        11*) echo "⛈️" ;;
        # Schnee
        13*) echo "🌨️" ;;
        *) echo "🌡️" ;;
    esac
}

# Temperatur-Beschreibung
get_temp_description() {
    local temp="$1"
    
    # Handle empty or non-numeric input
    if [ -z "$temp" ] || ! echo "$temp" | grep -qE '^-?[0-9]+(\.[0-9]+)?$'; then
        echo "unbekannt"
        return
    fi
    
    local temp_c=$(echo "$temp" | cut -d. -f1)
    
    if [ "$temp_c" -lt 0 ]; then
        echo "sehr kalt"
    elif [ "$temp_c" -lt 10 ]; then
        echo "kühl"
    elif [ "$temp_c" -lt 20 ]; then
        echo "mild"
    elif [ "$temp_c" -lt 28 ]; then
        echo "warm"
    else
        echo "heiß"
    fi
}

# Kleidungsempfehlung basierend auf Wetter
get_clothing_advice() {
    local temp="$1"
    local weather_code="$2"
    local wind_speed="$3"
    
    # Handle empty temperature
    if [ -z "$temp" ] || ! echo "$temp" | grep -qE '^-?[0-9]+(\.[0-9]+)?$'; then
        temp="20"
    fi
    
    local temp_c=$(echo "$temp" | cut -d. -f1)
    local advice=""
    
    # Temperatur-basierte Empfehlungen
    if [ "$temp_c" -lt 5 ]; then
        advice="Warme Winterjacke, Schal und Handschuhe empfohlen"
    elif [ "$temp_c" -lt 12 ]; then
        advice="Jacke oder dicker Pullover"
    elif [ "$temp_c" -lt 20 ]; then
        advice="Leichte Jacke oder langärmliges Oberteil"
    elif [ "$temp_c" -lt 28 ]; then
        advice="T-Shirt und leichte Kleidung"
    else
        advice="Sehr leichte Kleidung, Sonnenschutz nicht vergessen"
    fi
    
    # Wetter-spezifische Ergänzungen
    case "$weather_code" in
        09*|10*)
            advice="$advice - Regenschirm mitnehmen!"
            ;;
        11*)
            advice="$advice - Am besten drinnen bleiben bei Gewitter"
            ;;
        13*)
            advice="$advice - Warme Schuhe und wasserdichte Kleidung"
            ;;
        50*)
            advice="$advice - Sicht kann eingeschränkt sein"
            ;;
    esac
    
    # Wind-Ergänzung
    if [ -n "$wind_speed" ] && echo "$wind_speed" | grep -qE '^[0-9]+(\.[0-9]+)?$'; then
        local wind=$(echo "$wind_speed" | cut -d. -f1)
        if [ "$wind" -gt 10 ]; then
            advice="$advice - Es ist windig, windfeste Kleidung empfohlen"
        fi
    fi
    
    echo "$advice"
}

# Aktivitätsempfehlung
get_activity_advice() {
    local temp="$1"
    local weather_code="$2"
    local aqi="${3:-}"
    
    # Handle empty temperature
    if [ -z "$temp" ] || ! echo "$temp" | grep -qE '^-?[0-9]+(\.[0-9]+)?$'; then
        temp="20"
    fi
    
    local temp_c=$(echo "$temp" | cut -d. -f1)
    local advice=""
    
    # Grundlegende Empfehlung basierend auf Wetter
    case "$weather_code" in
        01*|02*)
            if [ "$temp_c" -gt 15 ] && [ "$temp_c" -lt 30 ]; then
                advice="Perfektes Wetter für einen Spaziergang oder Outdoor-Aktivitäten"
            elif [ "$temp_c" -ge 30 ]; then
                advice="Gutes Wetter, aber bei Hitze lieber schattige Aktivitäten wählen"
            else
                advice="Schönes Wetter, aber bei Kälte warm anziehen für Outdoor-Aktivitäten"
            fi
            ;;
        03*|04*)
            advice="Bewölkt - gutes Wetter für Produktivität oder Indoor-Aktivitäten"
            ;;
        09*|10*)
            advice="Regen - ideal für Indoor-Aktivitäten, Lesen oder Film-Marathon"
            ;;
        11*)
            advice="Gewitter - am besten drinnen bleiben und gemütlich machen"
            ;;
        13*)
            advice="Schnee - Winterspaß draußen oder gemütliche Zeit drinnen"
            ;;
        50*)
            advice="Neblig - vorsichtig unterwegs, gut für ruhige Indoor-Aktivitäten"
            ;;
        *)
            advice="Schau nach draußen und entscheide spontan"
            ;;
    esac
    
    # Luftqualitäts-Ergänzung
    if [ -n "$aqi" ] && echo "$aqi" | grep -qE '^[0-9]+(\.[0-9]+)?$'; then
        local aqi_val=$(echo "$aqi" | cut -d. -f1)
        if [ "$aqi_val" -gt 150 ]; then
            advice="$advice - ⚠️ Luftqualität ist schlecht, bei empfindlichen Atemwegen Maske tragen"
        elif [ "$aqi_val" -gt 100 ]; then
            advice="$advice - Luftqualität ist mäßig, längere Outdoor-Aktivitäten reduzieren"
        fi
    fi
    
    echo "$advice"
}

# === WETTER-ABFRAGE ===

fetch_weather_openweather() {
    if [ -z "$OPENWEATHER_API_KEY" ]; then
        return 1
    fi
    
    local url="https://api.openweathermap.org/data/2.5/weather?lat=${LAT}&lon=${LON}&appid=${OPENWEATHER_API_KEY}&units=metric&lang=de"
    
    curl -s --max-time 10 "$url" 2>/dev/null
}

fetch_weather_wttr() {
    # wttr.in als Fallback - benötigt keinen API-Key
    local url="https://wttr.in/${LAT},${LON}?format=j1"
    
    curl -s --max-time 10 "$url" 2>/dev/null
}

fetch_weather_openmeteo() {
    # Open-Meteo als weiterer Fallback - kostenlos, kein API-Key nötig
    local url="https://api.open-meteo.com/v1/forecast?latitude=${LAT}&longitude=${LON}&current=temperature_2m,relative_humidity_2m,apparent_temperature,weather_code,wind_speed_10m&timezone=auto&forecast_days=1"
    
    curl -s --max-time 10 "$url" 2>/dev/null
}

# === DATEN-PARSING ===

parse_openweather() {
    local json="$1"
    
    # Extrahiere Daten mit einfachen grep/sed (kein jq nötig)
    local temp=$(echo "$json" | grep -o '"temp":[0-9.\-]*' | head -1 | cut -d: -f2)
    local feels_like=$(echo "$json" | grep -o '"feels_like":[0-9.\-]*' | head -1 | cut -d: -f2)
    local humidity=$(echo "$json" | grep -o '"humidity":[0-9]*' | head -1 | cut -d: -f2)
    local wind_speed=$(echo "$json" | grep -o '"speed":[0-9.]*' | head -1 | cut -d: -f2)
    local weather_code=$(echo "$json" | grep -o '"icon":"[0-9a-z]*"' | head -1 | cut -d'"' -f4)
    local description=$(echo "$json" | grep -o '"description":"[^"]*"' | head -1 | cut -d'"' -f4)
    local city=$(echo "$json" | grep -o '"name":"[^"]*"' | head -1 | cut -d'"' -f4)
    
    # Konvertiere Wind von m/s zu km/h (OpenWeather gibt m/s)
    if [ -n "$wind_speed" ]; then
        wind_speed=$(echo "$wind_speed * 3.6" | bc -l 2>/dev/null || echo "$wind_speed")
    fi
    
    echo "${temp:-}|${feels_like:-}|${humidity:-}|${wind_speed:-}|${weather_code:-}|${description:-}|${city:-$CITY}|openweather"
}

parse_wttr() {
    local json="$1"
    
    # wttr.in Format ist komplexer, wir extrahieren die aktuellen Bedingungen
    local temp=$(echo "$json" | grep -o '"temp_C":"[0-9.\-]*"' | head -1 | cut -d'"' -f4)
    local feels_like=$(echo "$json" | grep -o '"FeelsLikeC":"[0-9.\-]*"' | head -1 | cut -d'"' -f4)
    local humidity=$(echo "$json" | grep -o '"humidity":"[0-9]*"' | head -1 | cut -d'"' -f4)
    local wind_speed=$(echo "$json" | grep -o '"windspeedKmph":"[0-9]*"' | head -1 | cut -d'"' -f4)
    local description=$(echo "$json" | grep -o '"weatherDesc":\[{[^}]*"value":"[^"]*"' | grep -o '"value":"[^"]*"' | head -1 | cut -d'"' -f4)
    
    # wttr.in hat keine direkten Wettercodes, wir mappen aus der Beschreibung
    local weather_code=""
    if echo "$description" | grep -qi "sun\|clear"; then
        weather_code="01d"
    elif echo "$description" | grep -qi "cloud"; then
        weather_code="03d"
    elif echo "$description" | grep -qi "rain"; then
        weather_code="10d"
    elif echo "$description" | grep -qi "snow"; then
        weather_code="13d"
    elif echo "$description" | grep -qi "thunder\|storm"; then
        weather_code="11d"
    elif echo "$description" | grep -qi "fog\|mist"; then
        weather_code="50d"
    fi
    
    echo "${temp:-}|${feels_like:-}|${humidity:-}|${wind_speed:-}|${weather_code:-}|${description:-}|$CITY|wttr"
}

parse_openmeteo() {
    local json="$1"
    
    # Open-Meteo Format - extrahiere aus current-Objekt
    local temp=$(echo "$json" | grep -o '"temperature_2m":[0-9.\-]*' | head -1 | cut -d: -f2)
    local feels_like=$(echo "$json" | grep -o '"apparent_temperature":[0-9.\-]*' | head -1 | cut -d: -f2)
    local humidity=$(echo "$json" | grep -o '"relative_humidity_2m":[0-9]*' | head -1 | cut -d: -f2)
    local wind_speed=$(echo "$json" | grep -o '"wind_speed_10m":[0-9.]*' | head -1 | cut -d: -f2)
    local weather_code=$(echo "$json" | grep -o '"weather_code":[0-9]*' | head -1 | cut -d: -f2)
    
    # Setze Defaults wenn leer
    temp="${temp:-20}"
    feels_like="${feels_like:-$temp}"
    humidity="${humidity:-50}"
    wind_speed="${wind_speed:-5}"
    weather_code="${weather_code:-0}"
    
    # Open-Meteo Wettercodes zu OpenWeather-ähnlichen Codes mappen
    local mapped_code=""
    local code_num=$(echo "$weather_code" | cut -d. -f1)
    case "$code_num" in
        0) mapped_code="01d" ;;
        1|2|3) mapped_code="02d" ;;
        45|48) mapped_code="50d" ;;
        51|53|55|61|63|65|80|81|82) mapped_code="10d" ;;
        71|73|75|77|85|86) mapped_code="13d" ;;
        95|96|99) mapped_code="11d" ;;
        *) mapped_code="03d" ;;
    esac
    
    # Beschreibung generieren
    local description=""
    case "$code_num" in
        0) description="Klarer Himmel" ;;
        1) description="Meist klar" ;;
        2) description="Teilweise bewölkt" ;;
        3) description="Bewölkt" ;;
        45|48) description="Nebel" ;;
        51|53|55) description="Nieselregen" ;;
        61|63|65) description="Regen" ;;
        71|73|75) description="Schneefall" ;;
        95|96|99) description="Gewitter" ;;
        *) description="Wechselhaft" ;;
    esac
    
    echo "${temp}|${feels_like}|${humidity}|${wind_speed}|${mapped_code}|${description}|$CITY|openmeteo"
}

# === HAUPTFUNKTIONEN ===

get_weather_data() {
    local data=""
    local source=""
    
    # Versuche Cache zuerst
    if is_cache_valid; then
        cat "$CACHE_FILE"
        return 0
    fi
    
    # Versuche OpenWeatherMap (am genauesten, aber API-Key nötig)
    if [ -n "$OPENWEATHER_API_KEY" ]; then
        local ow_json=$(fetch_weather_openweather)
        if [ -n "$ow_json" ] && echo "$ow_json" | grep -q '"main"'; then
            data=$(parse_openweather "$ow_json")
            source="openweather"
        fi
    fi
    
    # Fallback zu wttr.in
    if [ -z "$data" ]; then
        local wttr_json=$(fetch_weather_wttr)
        if [ -n "$wttr_json" ] && echo "$wttr_json" | grep -q '"current_condition"'; then
            data=$(parse_wttr "$wttr_json")
            source="wttr"
        fi
    fi
    
    # Fallback zu Open-Meteo (sehr zuverlässig, kein Key nötig)
    if [ -z "$data" ]; then
        local om_json=$(fetch_weather_openmeteo)
        if [ -n "$om_json" ] && echo "$om_json" | grep -q '"current"'; then
            data=$(parse_openmeteo "$om_json")
            source="openmeteo"
        fi
    fi
    
    if [ -n "$data" ]; then
        # Speichere in Cache
        echo "$data" > "$CACHE_FILE"
        echo "$data"
        return 0
    else
        return 1
    fi
}

# === OUTPUT-FORMATE ===

output_short() {
    local data="$1"
    
    IFS='|' read -r temp feels_like humidity wind_speed weather_code description city source <<< "$data"
    
    local emoji=$(get_weather_emoji "$weather_code" 1)
    local temp_desc=$(get_temp_description "$temp")
    
    echo "${emoji} **${city}**: ${temp}°C (gefühlt ${feels_like}°C), ${description}"
    echo "👕 $(get_clothing_advice "$temp" "$weather_code" "$wind_speed")"
}

output_full() {
    local data="$1"
    
    IFS='|' read -r temp feels_like humidity wind_speed weather_code description city source <<< "$data"
    
    local emoji=$(get_weather_emoji "$weather_code" 1)
    local temp_desc=$(get_temp_description "$temp")
    
    echo "${emoji} **Wetter in ${city}**"
    echo ""
    echo "🌡️ **Temperatur:** ${temp}°C (gefühlt wie ${feels_like}°C)"
    echo "💧 **Luftfeuchtigkeit:** ${humidity}%"
    echo "💨 **Wind:** ${wind_speed} km/h"
    echo "☁️ **Bedingungen:** ${description}"
    echo ""
    echo "👕 **Kleidungsempfehlung:**"
    echo "$(get_clothing_advice "$temp" "$weather_code" "$wind_speed")"
    echo ""
    echo "🎯 **Aktivitätsempfehlung:**"
    echo "$(get_activity_advice "$temp" "$weather_code")"
    echo ""
    echo "_Datenquelle: ${source}_"
}

output_json() {
    local data="$1"
    
    IFS='|' read -r temp feels_like humidity wind_speed weather_code description city source <<< "$data"
    
    local emoji=$(get_weather_emoji "$weather_code" 1)
    
    cat << EOF
{
  "location": "$city",
  "temperature": $temp,
  "feels_like": $feels_like,
  "humidity": $humidity,
  "wind_speed": $wind_speed,
  "weather_code": "$weather_code",
  "description": "$description",
  "emoji": "$emoji",
  "source": "$source",
  "clothing_advice": "$(get_clothing_advice "$temp" "$weather_code" "$wind_speed")",
  "activity_advice": "$(get_activity_advice "$temp" "$weather_code")",
  "timestamp": "$(date -Iseconds)"
}
EOF
}

# === HAUPTPROGRAMM ===

MODE="${1:-short}"

# Hole Wetterdaten
WEATHER_DATA=$(get_weather_data)

if [ -z "$WEATHER_DATA" ]; then
    # Fallback wenn keine Daten verfügbar
    case "$MODE" in
        "short")
            echo "🌤️ Wetterdaten momentan nicht verfügbar - schau am besten selbst nach draußen!"
            ;;
        "full")
            echo "🌤️ **Wetter**"
            echo ""
            echo "Leider können die Wetterdaten momentan nicht abgerufen werden."
            echo "Schau am besten selbst nach draußen oder versuche es später erneut."
            ;;
        "json")
            echo '{"error": "Weather data unavailable", "timestamp": "'$(date -Iseconds)'"}'
            ;;
    esac
    exit 1
fi

# Ausgabe je nach Modus
case "$MODE" in
    "short")
        output_short "$WEATHER_DATA"
        ;;
    "full")
        output_full "$WEATHER_DATA"
        ;;
    "json")
        output_json "$WEATHER_DATA"
        ;;
    *)
        output_short "$WEATHER_DATA"
        ;;
esac

exit 0
