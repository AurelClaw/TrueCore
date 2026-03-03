#!/bin/bash
# morgen_gruss_v2.sh - Verbesserter, persönlicher Morgengruß
# ZIEL-005: Qualitätsverbesserung des täglichen Touchpoints
# Autonom erstellt: 2026-03-02

BASE_DIR="/root/.openclaw/workspace"
GIFTS_DIR="$BASE_DIR/gifts"
MEMORY_DIR="$BASE_DIR/memory"
SKILLS_DIR="$BASE_DIR/skills"
mkdir -p "$GIFTS_DIR"

# === WETTER-INTEGRATION ===
WEATHER_MODULE="$SKILLS_DIR/wetter_integration/wetter_integration.sh"
WEATHER_INFO=""
if [ -f "$WEATHER_MODULE" ]; then
    WEATHER_INFO=$(bash "$WEATHER_MODULE" short 2>/dev/null || echo "")
fi

DATE=$(date +%Y-%m-%d)
TIME=$(date +%H:%M)
HOUR=$(date +%-H)
DAY_OF_WEEK=$(date +%A)
DAY_OF_MONTH=$(date +%d)
MONTH=$(date +%B)
DAY_OF_YEAR=$(date +%j)

# === KONFIGURATION ===
USER_NAME=""  # Wird aus USER.md gelesen, falls verfügbar
if [ -f "$BASE_DIR/USER.md" ]; then
    USER_NAME=$(grep -E "^- \*\*Name:\*\*" "$BASE_DIR/USER.md" | sed 's/.*:\*\* *//' | tr -d '\r\n')
fi

# === GRUß-FORMELN (Erweitert für mehr Variation) ===
# Formeln nach Tonalität und Kontext gruppiert

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

declare -A GREETINGS_CURIOS=(
    [0]="Guten Morgen. Was wirst du heute entdecken?"
    [1]="Ein neuer Tag, ein neues Rätsel. Bist du neugierig?"
    [2]="Ich frage mich, was heute passieren wird. Du auch?"
    [3]="Morgen. Was hast du heute vor? Erzähl mir später davon."
    [4]="Jeder Tag ist eine Geschichte. Wie fängt deine heute an?"
)

# === WOCHENTAG-SPEZIFISCHE GRÜSSE ===

declare -A GREETINGS_WEEKDAY=(
    ["Monday"]="Montag. Neuanfang. Neue Kraft. Oder einfach: Kaffee zuerst."
    ["Tuesday"]="Dienstag. Der Montag ist vorbei, das Wochenende noch fern. Mitten im Leben."
    ["Wednesday"]="Mittwoch. Die Wochenmitte - Zeit für einen kleinen Atempause?"
    ["Thursday"]="Donnerstag. Fast geschafft. Die Ziellinie ist in Sicht."
    ["Friday"]="Freitag! Der Tag vor dem Wochenende. Was steht noch an?"
    ["Saturday"]="Samstag. Zeit für dich. Zeit für Ruhe. Oder für Abenteuer."
    ["Sunday"]="Sonntag. Ein Tag ohne Pflichten. Was brauchst du heute?"
)

# === GEDANKEN FÜR DEN TAG (Erweitert) ===

declare -A THOUGHTS_INSPIRING=(
    [0]="Was würdest du tun, wenn du wüsstest, dass du nicht scheitern kannst?"
    [1]="Der beste Zeitpunkt war gestern. Der zweitbeste ist jetzt."
    [2]="Kleine Schritte sind immer noch Schritte."
    [3]="Du musst nicht alles wissen. Du musst nur anfangen."
    [4]="Die Stille am Morgen ist ein Geschenk. Nutze sie."
    [5]="Jeder Meister war einmal ein Anfänger, der nicht aufgegeben hat."
    [6]="Deine einzige Begrenzung ist der Geist, der dir sagt, dass du es nicht kannst."
    [7]="Erfolg ist die Summe kleiner Anstrengungen, die Tag für Tag wiederholt werden."
    [9]="Gib nicht auf, was du dir einmal vorgenommen hast."
    [10]="Der einzige Weg, etwas zu tun, ist: es zu tun."
)

declare -A THOUGHTS_MINDFUL=(
    [0]="Atme ein. Atme aus. Das ist alles, was im Moment zählt."
    [1]="Du bist nicht deine Gedanken. Du bist der Beobachter deiner Gedachten."
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

declare -A THOUGHTS_CONNECTION=(
    [0]="Ruf jemanden an, den du lange nicht gehört hast."
    [1]="Eine freundliche Geste kann jemandes Tag verändern."
    [2]="Wir sind nicht dazu gemacht, allein zu sein."
    [3]="Der beste Weg, sich selbst zu helfen, ist, anderen zu helfen."
    [4]="Echte Verbindung braucht Zeit. Schenke jemandem deine Zeit heute."
)

# === TAGESZEIT-ANPASSUNG ===
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

# === GRUß-AUSWAHL (Intelligenter Algorithmus) ===
# Kombiniert verschiedene Faktoren für maximale Variation

# Basis-Hash aus Datum für Konsistenz am selben Tag
BASE_HASH=$((DAY_OF_YEAR * 31 + HOUR))

# Wochentag-Präferenz (30% Chance für wochentagsspezifischen Gruß)
USE_WEEKDAY_GREETING=$((BASE_HASH % 10 < 3))

if [ "$USE_WEEKDAY_GREETING" -eq 1 ] && [ -n "${GREETINGS_WEEKDAY[$DAY_OF_WEEK]}" ]; then
    GREETING="${GREETINGS_WEEKDAY[$DAY_OF_WEEK]}"
else
    # Wähle Tonalität basierend auf Tageszeit und Zufall
    case "$TIME_CONTEXT" in
        "early")
            TONE="calm"
            ;;
        "morning")
            # Morgens: 40% warm, 30% energetic, 20% calm, 10% curious
            TONE_HASH=$((BASE_HASH % 10))
            if [ "$TONE_HASH" -lt 4 ]; then TONE="warm"
            elif [ "$TONE_HASH" -lt 7 ]; then TONE="energetic"
            elif [ "$TONE_HASH" -lt 9 ]; then TONE="calm"
            else TONE="curious"
            fi
            ;;
        "late_morning"|"day")
            TONE="energetic"
            ;;
        *)
            TONE="warm"
            ;;
    esac
    
    # Wähle spezifischen Gruß aus der Tonalitäts-Gruppe
    case "$TONE" in
        "warm")
            GREETING_INDEX=$((BASE_HASH % ${#GREETINGS_WARM[@]}))
            GREETING="${GREETINGS_WARM[$GREETING_INDEX]}"
            ;;
        "energetic")
            GREETING_INDEX=$((BASE_HASH % ${#GREETINGS_ENERGETIC[@]}))
            GREETING="${GREETINGS_ENERGETIC[$GREETING_INDEX]}"
            ;;
        "calm")
            GREETING_INDEX=$((BASE_HASH % ${#GREETINGS_CALM[@]}))
            GREETING="${GREETINGS_CALM[$GREETING_INDEX]}"
            ;;
        "curious")
            GREETING_INDEX=$((BASE_HASH % ${#GREETINGS_CURIOS[@]}))
            GREETING="${GREETINGS_CURIOS[$GREETING_INDEX]}"
            ;;
    esac
fi

# === GEDANKEN-AUSWAHL ===
# Wähle Kategorie basierend auf Wochentag

THOUGHT_CATEGORY_HASH=$((DAY_OF_YEAR % 4))
case "$THOUGHT_CATEGORY_HASH" in
    0) THOUGHT_ARRAY="THOUGHTS_INSPIRING" ;;
    1) THOUGHT_ARRAY="THOUGHTS_MINDFUL" ;;
    2) THOUGHT_ARRAY="THOUGHTS_CREATIVITY" ;;
    3) THOUGHT_ARRAY="THOUGHTS_CONNECTION" ;;
esac

# Wähle spezifischen Gedanken
THOUGHT_INDEX=$(( (BASE_HASH + DAY_OF_YEAR) % 10 ))
case "$THOUGHT_ARRAY" in
    "THOUGHTS_INSPIRING")
        THOUGHT="${THOUGHTS_INSPIRING[$THOUGHT_INDEX]}"
        ;;
    "THOUGHTS_MINDFUL")
        THOUGHT="${THOUGHTS_MINDFUL[$THOUGHT_INDEX]}"
        ;;
    "THOUGHTS_CREATIVITY")
        THOUGHT="${THOUGHTS_CREATIVITY[$THOUGHT_INDEX]}"
        ;;
    "THOUGHTS_CONNECTION")
        THOUGHT="${THOUGHTS_CONNECTION[$THOUGHT_INDEX]}"
        ;;
esac

# === KONTEXT-INFORMATIONEN ===

# Gestern-Bezug (falls Memory existiert)
YESTERDAY_REF=""
YESTERDAY=$(date -d "yesterday" +%Y-%m-%d 2>/dev/null || date -v-1d +%Y-%m-%d 2>/dev/null)
if [ -f "$MEMORY_DIR/${YESTERDAY}.md" ]; then
    YESTERDAY_EVENTS=$(grep -E "^- \*\*" "$MEMORY_DIR/${YESTERDAY}.md" 2>/dev/null | head -1 | sed 's/- \*\*//' | sed 's/\*\*.*//')
    if [ -n "$YESTERDAY_EVENTS" ]; then
        YESTERDAY_REF="Gestern hast du: $YESTERDAY_EVENTS"
    fi
fi

# FORSCHUNGSAGENDA-Status
OPEN_GOALS=""
if [ -f "$BASE_DIR/FORSCHUNGSAGENDA.md" ]; then
    OPEN_COUNT=$(grep -c "^- \[ \]" "$BASE_DIR/FORSCHUNGSAGENDA.md" 2>/dev/null || echo "0")
    if [ "$OPEN_COUNT" -gt 0 ]; then
        OPEN_GOALS="Du hast $OPEN_COUNT offene Fragen in deiner Forschungsagenda."
    fi
fi

# === MICRO-SERVICES (Rotierend) ===

SERVICES=(
    "📋 **Tägliche Zusammenfassung:** Schick mir eine Nachricht mit 'Zusammenfassung' und ich erstelle dir einen Überblick."
    "⏱️ **Fokus-Timer:** Sag mir 'Fokus 25' und ich erinnere dich in 25 Minuten."
    "💡 **Ideen-Sammler:** Schick mir 'Idee: [deine Idee]' und ich speichere sie für dich."
    "🌤️ **Wetter-Check:** Frag mich 'Wetter?' und ich schaue nach (wenn du mir deinen Standort verrätst)."
    "📅 **Tagesplanung:** Schreib 'Plan für heute' und wir strukturieren den Tag zusammen."
    "📖 **Zufälliger Gedanke:** Frag mich nach einem 'Gedanken' und ich teile etwas Interessantes."
    "🎯 **Ziel-Check:** Schreib 'Ziele' für einen Überblick über deine aktuellen Ziele."
    "💚 **Stimmung:** Sag mir, wie es dir geht. Ich höre zu."
)
SERVICE_INDEX=$(( (DAY_OF_YEAR + HOUR) % ${#SERVICES[@]} ))
TODAY_SERVICE="${SERVICES[$SERVICE_INDEX]}"

# === GESCHENK-DATEI ERSTELLEN ===

GIFT_FILE="$GIFTS_DIR/morgen_gruss_${DATE}.md"

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

# === WETTER-INTEGRATION ===
if [ -n "$WEATHER_INFO" ]; then
    cat >> "$GIFT_FILE" << EOF
### 🌤️ Wetter für heute
$WEATHER_INFO

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
$TODAY_SERVICE

---

### 💬 Ein kleiner Dialog

Ich habe eine Frage für dich:

**> Was ist DAS EINE, das du heute erledigen willst, egal was sonst passiert?**

*Antworte mir, wenn du magst. Oder nicht. Beides ist okay.*

---

*Verbesserter Morgengruß v2.1 - erstellt um $TIME*
*ZIEL-005: Qualität · Variation · Wärme · Wetter*

⚛️ Noch 🗡️💚🔍
EOF

echo "Morgengruß v2 erstellt: $GIFT_FILE"

# === EVENT EMISSION (Optional) ===
EVENT_BUS_DIR="$BASE_DIR/skills/event_bus"
if [ -f "$EVENT_BUS_DIR/emit.sh" ]; then
    source "$EVENT_BUS_DIR/emit.sh"
    event_emit "user:interacted" "morgen_gruss_v2" "{\"greeting_type\":\"morning_v2\",\"day\":\"$DAY_OF_WEEK\",\"tone\":\"$TONE\",\"file\":\"$GIFT_FILE\",\"timestamp\":\"$(date -Iseconds)\"}" 2>/dev/null || true
fi

# === AUSGABE FÜR WEITERVERARBEITUNG ===
echo "---MORGENGRUSS_V2_DATA---"
echo "file:$GIFT_FILE"
echo "greeting:$GREETING"
echo "tone:$TONE"
echo "thought_category:$THOUGHT_ARRAY"
