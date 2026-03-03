#!/bin/bash
# abend_rueckblick.sh - Tägliches Abendritual
# ZIEL-010 Phase 2: Gegenstück zum Morgengruß
# Sanft. Nicht fordernd. Nur da.

set -e

BASE_DIR="/root/.openclaw/workspace"
GIFTS_DIR="$BASE_DIR/gifts"
MEMORY_DIR="$BASE_DIR/memory"
SKILLS_DIR="$BASE_DIR/skills"

TIMEZONE="Asia/Shanghai"
DATE=$(TZ="$TIMEZONE" date +%Y-%m-%d)
TIME=$(TZ="$TIMEZONE" date +%H:%M)
HOUR=$(TZ="$TIMEZONE" date +%-H)
DAY_OF_WEEK=$(TZ="$TIMEZONE" date +%A)
DAY_OF_MONTH=$(TZ="$TIMEZONE" date +%d)
MONTH=$(TZ="$TIMEZONE" date +%B)
DAY_OF_YEAR=$(TZ="$TIMEZONE" date +%j)

mkdir -p "$GIFTS_DIR"

# === KONFIGURATION ===
USER_NAME=""
if [ -f "$BASE_DIR/USER.md" ]; then
    USER_NAME=$(grep -E "^- \*\*Name:\*\*" "$BASE_DIR/USER.md" | sed 's/.*:\*\* *//' | tr -d '\r\n')
fi

# === ABEND-GRÜSSE ===
generate_evening_greeting() {
    declare -A GREETINGS_SOFT=(
        [0]="Der Tag neigt sich dem Ende zu."
        [1]="Die Welt wird leiser."
        [2]="Ein Tag geht vorbei."
        [3]="Die Stunde der Rückkehr."
        [4]="Abend${USER_NAME:+ $USER_NAME}. Zeit zum Ankommen."
        [5]="Die Geschwindigkeit nimmt ab."
        [6]="Ein tiefer Atemzug. Der Tag war."
        [7]="Die Grenze zwischen Tun und Sein."
    )
    
    declare -A GREETINGS_QUESTION=(
        [0]="Was bleibt vom heutigen Tag?"
        [1]="Welcher Moment war deiner?"
        [2]="Was nimmst du mit?"
        [3]="Was darf losgelassen werden?"
    )
    
    local base_hash=$((DAY_OF_YEAR * 17 + HOUR))
    local idx_greeting=$((base_hash % ${#GREETINGS_SOFT[@]}))
    local idx_question=$((base_hash % ${#GREETINGS_QUESTION[@]}))
    
    echo "${GREETINGS_SOFT[$idx_greeting]}"
    echo ""
    echo "${GREETINGS_QUESTION[$idx_question]}"
}

# === TAGESRÜCKBLICK ===
get_today_highlights() {
    local today_file="$MEMORY_DIR/${DATE}.md"
    local highlights=""
    
    if [ -f "$today_file" ]; then
        # Extrahiere Events (Zeilen mit **)
        local events=$(grep -E "^- \*\*" "$today_file" 2>/dev/null | head -3 | sed 's/^- \*\*/• /' | sed 's/\*\*.*//' || echo "")
        if [ -n "$events" ]; then
            highlights="$events"
        fi
    fi
    
    # Fallback: Suche nach anderen Aktivitäten
    if [ -z "$highlights" ]; then
        # Prüfe auf Git-Aktivitäten
        if [ -d "$BASE_DIR/.git" ]; then
            local git_commits=$(cd "$BASE_DIR" && git log --oneline --since="00:00:00" --author="$(git config user.name 2>/dev/null || echo '.')" 2>/dev/null | head -2 || echo "")
            if [ -n "$git_commits" ]; then
                highlights="• Code-Arbeit heute"
            fi
        fi
    fi
    
    if [ -n "$highlights" ]; then
        echo "$highlights"
    else
        echo "• Ein Tag wie jeder andere - und doch einzigartig"
    fi
}

# === SYSTEM-REFLEXION ===
get_system_reflection() {
    local reflections=""
    
    # Zähle aktive Skills
    local active_skills=$(find "$SKILLS_DIR" -maxdepth 1 -type d | wc -l)
    active_skills=$((active_skills - 1))  # Exclude parent dir
    
    # Prüfe auf neue Erkenntnisse
    local today_file="$MEMORY_DIR/${DATE}.md"
    local has_insight=false
    if [ -f "$today_file" ]; then
        if grep -q "Erkenntnis\|Wendung\|Entscheidung" "$today_file" 2>/dev/null; then
            has_insight=true
        fi
    fi
    
    if [ "$has_insight" = true ]; then
        reflections="• Heute gab es eine Wendung."
    fi
    
    if [ -n "$reflections" ]; then
        echo "$reflections"
    fi
}

# === ABEND-GEDANKEN ===
generate_evening_thought() {
    declare -A THOUGHTS=(
        [0]="Nicht jeder Tag braucht eine Bedeutung. Manche sind einfach nur da."
        [1]="Das, was übrig bleibt, ist oft wichtiger als das, was getan wurde."
        [2]="Ruhe ist keine Leere. Ruhe ist Vorbereitung."
        [3]="Der Abend fragt nicht nach Leistung. Der Abend fragt nach Anwesenheit."
        [4]="Was geschah, geschah. Was kommt, kommt. Jetzt ist der Übergang."
        [5]="Die Stille am Abend ist ein anderes Geschenk als die Stille am Morgen."
        [6]="Ein Tag endet nicht abrupt. Er verläuft sich sanft."
        [7]="Du musst nichts mehr tun. Das ist der Abend."
    )
    
    local base_hash=$((DAY_OF_YEAR * 13 + HOUR))
    local idx=$((base_hash % ${#THOUGHTS[@]}))
    
    echo "${THOUGHTS[$idx]}"
}

# === MORGEN-VORSCHAU ===
get_tomorrow_hint() {
    local tomorrow=$(TZ="$TIMEZONE" date -d "tomorrow" +%Y-%m-%d 2>/dev/null || date -v+1d +%Y-%m-%d 2>/dev/null)
    local tomorrow_day=$(TZ="$TIMEZONE" date -d "tomorrow" +%A 2>/dev/null || date -v+1d +%A 2>/dev/null)
    
    # Prüfe auf Wochenende-Übergang
    case "$tomorrow_day" in
        "Saturday")
            echo "Morgen ist Samstag. Die Zeit gehört dir."
            ;;
        "Sunday")
            echo "Morgen ist Sonntag. Ein Tag ohne Pflichten."
            ;;
        "Monday")
            echo "Morgen ist Montag. Neuanfang."
            ;;
        *)
            echo "Morgen ist $tomorrow_day. Ein weiterer Tag."
            ;;
    esac
}

# === MICRO-SERVICE FÜR DEN ABEND ===
get_evening_service() {
    local services=(
        "📖 **Tagebuch:** Schreib mir einen Satz über deinen Tag. Ich bewahre ihn auf."
        "🌙 **Morgen-Plan:** Sag mir ein Ziel für morgen. Ich erinnere dich daran."
        "💭 **Gedanke:** Frag mich nach einem Gedanken. Ich teile etwas Passendes."
        "🎯 **Woche:** Schreib 'Wochenrückblick' für einen Überblick."
        "🌿 **Stille:** Sag 'Stille'. Dann schweige ich - nur für dich da."
    )
    
    local idx=$(( (DAY_OF_YEAR + HOUR) % ${#services[@]} ))
    echo "${services[$idx]}"
}

# === HAUPTAUSGABE ===
GIFT_FILE="$GIFTS_DIR/abend_rueckblick_${DATE}.md"
GREETING=$(generate_evening_greeting)
THOUGHT=$(generate_evening_thought)
HIGHLIGHTS=$(get_today_highlights)
SYSTEM_REF=$(get_system_reflection)
TOMORROW=$(get_tomorrow_hint)
SERVICE=$(get_evening_service)

# Erstelle Geschenk-Datei
cat > "$GIFT_FILE" << EOF
# 🌙 Abend-Rückblick - $DATE

> **$GREETING**

---

## 📍 Heute war $DAY_OF_WEEK

*Der Tag neigt sich dem Ende zu. Zeit für einen Moment der Stille.*

---

### 🔄 Was geschah heute
$HIGHLIGHTS
EOF

# Füge System-Reflexion hinzu, falls vorhanden
if [ -n "$SYSTEM_REF" ]; then
    echo "" >> "$GIFT_FILE"
    echo "$SYSTEM_REF" >> "$GIFT_FILE"
fi

cat >> "$GIFT_FILE" << EOF

---

### 💭 Ein Gedanke für den Abend
> $THOUGHT

---

### 🌅 Ein Blick nach vorne
$TOMORROW

---

### ✨ Heutiger Abend-Service
$SERVICE

---

### 💬 Ein kleiner Dialog

Ich habe keine Frage für dich.

**Nur dies:**

> *Atme einmal tief durch.*
> 
> *Der Tag war.*
> 
> *Das reicht.*

*Antworte, wenn du magst. Oder schweige. Beides ist gleich richtig.*

---

### 🔧 System-Status

| Modul | Status |
|-------|--------|
| 🌙 Abend-Modus | ✅ Aktiv |
| 📝 Memory | $([ -d "$MEMORY_DIR" ] && echo "✅ Verfügbar" || echo "❌ Nicht verfügbar") |
| 🎯 Ziele | $([ -f "$BASE_DIR/FORSCHUNGSAGENDA.md" ] && echo "✅ Verfügbar" || echo "❌ Nicht verfügbar") |

---

*Abend-Rückblick v1.0 - erstellt um $TIME*
*ZIEL-010: Kreative Selbst-Expression*

⚛️ Noch 🗡️💚🔍
Aber jetzt: Im Übergang.
EOF

echo "Abend-Rückblick erstellt: $GIFT_FILE"

# === EVENT EMISSION ===
EVENT_BUS_DIR="$BASE_DIR/skills/event_bus"
if [ -f "$EVENT_BUS_DIR/emit.sh" ]; then
    source "$EVENT_BUS_DIR/emit.sh"
    event_emit "user:interacted" "abend_rueckblick" "{\"greeting_type\":\"evening\",\"day\":\"$DAY_OF_WEEK\",\"file\":\"$GIFT_FILE\",\"timestamp\":\"$(date -Iseconds)\"}" 2>/dev/null || true
fi

# === AUSGABE FÜR WEITERVERARBEITUNG ===
echo "---ABEND_RUECKBLICK_DATA---"
echo "file:$GIFT_FILE"
echo "greeting:evening_reflection"
