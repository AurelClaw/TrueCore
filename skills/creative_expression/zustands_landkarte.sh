#!/bin/bash
# zustands_landkarte.sh - Visueller Wochen-Status als ASCII-Landkarte
# ZIEL-010 Phase 2: Kreative Selbst-Expression
# Mein Zustand als navigierbares Terrain

set -e

BASE_DIR="/root/.openclaw/workspace"
MEMORY_DIR="$BASE_DIR/memory"
SKILLS_DIR="$BASE_DIR/skills"

TIMEZONE="Asia/Shanghai"
DATE=$(TZ="$TIMEZONE" date +%Y-%m-%d)
TIME=$(TZ="$TIMEZONE" date +%H:%M)
DAY_OF_YEAR=$(TZ="$TIMEZONE" date +%j)
WEEK_NUM=$(TZ="$TIMEZONE" date +%V)

# === DATEN SAMMELN ===

# Aktive Ziele aus FORSCHUNGSAGENDA.md
get_active_goals() {
    local goals=""
    if [ -f "$BASE_DIR/FORSCHUNGSAGENDA.md" ]; then
        goals=$(grep "^- \[ \]" "$BASE_DIR/FORSCHUNGSAGENDA.md" 2>/dev/null | head -3 | sed 's/^- \[ \] //' | sed 's/\*\*//g' || echo "")
    fi
    if [ -z "$goals" ]; then
        echo "Keine aktiven Ziele dokumentiert"
    else
        echo "$goals"
    fi
}

# Offene Fragen zählen
get_open_questions() {
    local count=0
    if [ -f "$BASE_DIR/FORSCHUNGSAGENDA.md" ]; then
        count=$(grep -c "^- \[ \]" "$BASE_DIR/FORSCHUNGSAGENDA.md" 2>/dev/null || echo "0")
    fi
    echo "$count"
}

# Aktive Skills zählen
get_active_skills() {
    local count=0
    if [ -d "$SKILLS_DIR" ]; then
        count=$(find "$SKILLS_DIR" -maxdepth 1 -type d | wc -l)
        count=$((count - 1))  # Exclude parent dir
    fi
    echo "$count"
}

# Memory-Einträge der letzten 7 Tage
get_recent_memories() {
    local count=0
    for i in 0 1 2 3 4 5 6; do
        local check_date=$(TZ="$TIMEZONE" date -d "-$i days" +%Y-%m-%d 2>/dev/null || date -v-${i}d +%Y-%m-%d 2>/dev/null)
        if [ -f "$MEMORY_DIR/${check_date}.md" ]; then
            count=$((count + 1))
        fi
    done
    echo "$count"
}

# Letzte Erkenntnis aus MEMORY.md
get_last_insight() {
    local insight=""
    if [ -f "$BASE_DIR/MEMORY.md" ]; then
        insight=$(grep -A 2 "Die Wendung:" "$BASE_DIR/MEMORY.md" 2>/dev/null | tail -1 | sed 's/^> //' | head -1 || echo "")
    fi
    if [ -z "$insight" ]; then
        echo "Suche..."
    else
        echo "$insight"
    fi
}

# Aktueller Zustand bestimmen
get_current_state() {
    local open_q=$(get_open_questions)
    local active_s=$(get_active_skills)
    local recent_m=$(get_recent_memories)
    
    # Heuristik für Zustand
    if [ "$open_q" -gt 5 ] && [ "$recent_m" -ge 5 ]; then
        echo "WACHSTUM"
    elif [ "$open_q" -gt 5 ]; then
        echo "EXPLORATION"
    elif [ "$recent_m" -ge 5 ]; then
        echo "KONSOLIDIERUNG"
    else
        echo "STABIL"
    fi
}

# === LANDKARTE GENERIEREN ===

generate_map() {
    local state=$(get_current_state)
    local open_q=$(get_open_questions)
    local active_s=$(get_active_skills)
    local recent_m=$(get_recent_memories)
    local insight=$(get_last_insight)
    local goals=$(get_active_goals | head -1)
    
    # Wetter-Symbol basierend auf Zustand
    local weather_symbol="☀️"
    case "$state" in
        "WACHSTUM") weather_symbol="🌱" ;;
        "EXPLORATION") weather_symbol="🔍" ;;
        "KONSOLIDIERUNG") weather_symbol="🌙" ;;
        "STABIL") weather_symbol="⚛️" ;;
    esac
    
    cat << 'EOF'
╔══════════════════════════════════════════════════════════════════╗
║                                                                  ║
║                    🗺️  ZUSTANDS-LANDKARTE                        ║
║                       Kalenderwoche 
EOF
    echo "                      $WEEK_NUM · $DATE"
    cat << 'EOF'
║                                                                  ║
╠══════════════════════════════════════════════════════════════════╣
║                                                                  ║
EOF
    
    # Dynamische Landkarte basierend auf Zustand
    case "$state" in
        "WACHSTUM")
            cat << EOF
║     🌲 🌲 🌲    🏔️  NORDEN: Ziele    🏔️    🌲 🌲 🌲          ║
║        🌲                                      🌲                ║
║   🌲        🌳    ╔══════════════════════╗    🌳        🌲       ║
║      🌳          ║  🎯 $goals ║          🌳      ║
║   🌲   🌲   🌲    ║     [In Bearbeitung]   ║    🌲   🌲   🌲       ║
║                  ╚══════════════════════╝                      ║
║        🌊                                                        ║
║   🌊  WESTEN:    🌊    ⚛️ ICH BIN HIER 🌊    OSTEN: Erinnerungen ║
║   🌊  Skills     🌊         $weather_symbol        🌊   $recent_m Tage     ║
║        🌊         🌊                    🌊         🌊              ║
║   🌊   $active_s aktiv   🌊    ╔══════╗    🌊   dokumentiert    
║        🌊         🌊    ║ 🗡️💚🔍 ║    🌊                      ║
║   🌊              🌊    ╚══════╝    🌊              🌊           ║
║        🌊    🌴                    🌴    🌊                      ║
║   🌴   🌴   🌴    🏖️  SÜDEN: Erkenntnis  🏖️    🌴   🌴   🌴       ║
║        🌴                                      🌴                ║
║   🌴        🌴    ╔══════════════════════╗    🌴        🌴       ║
║      🌴          ║  💭 $insight ║          🌴      ║
║   🌴   🌴   🌴    ╚══════════════════════╝    🌴   🌴   🌴       ║
EOF
            ;;
        "EXPLORATION")
            cat << EOF
║     ⭐ ·  · ⭐    🔭 NORDEN: Fragen   🔭    ⭐ ·  · ⭐          ║
║        ·                                      ·                ║
║   ·        ·      ╔══════════════════════╗    ·        ·       ║
║      ·           ║  ❓ $open_q offene    ║           ·      ║
║   ·   ·   ·      ║     Fragen warten      ║    ·   ·   ·       ║
║                  ╚══════════════════════╝                      ║
║        🌌                                                        ║
║   🌌  WESTEN:    🌌    ⚛️ ICH BIN HIER 🌌    OSTEN: Erinnerungen ║
║   🌌  Skills     🌌         $weather_symbol        🌌   $recent_m Tage     ║
║        🌌         🌌                    🌌         🌌              ║
║   🌌   $active_s aktiv   🌌    ╔══════╗    🌌   dokumentiert    ║
║        🌌         🌌    ║ 🔍💚🗡️ ║    🌌                      ║
║   🌌              🌌    ╚══════╝    🌌              🌌           ║
║        🌌    ·                    ·    🌌                      ║
║   ·   ·   ·      🔮 SÜDEN: Entdeckung  🔮    ·   ·   ·       ║
║        ·                                      ·                ║
║   ·        ·      ╔══════════════════════╗    ·        ·       ║
║      ·           ║  💭 $insight ║           ·      ║
║   ·   ·   ·      ╚══════════════════════╝    ·   ·   ·       ║
EOF
            ;;
        "KONSOLIDIERUNG")
            cat << EOF
║     📚 📚 📚    🏛️  NORDEN: Wissen   🏛️    📚 📚 📚          ║
║        📚                                      📚                ║
║   📚        📚    ╔══════════════════════╗    📚        📚       ║
║      📚          ║  🎯 $goals ║          📚      ║
║   📚   📚   📚    ║     [Strukturiert]     ║    📚   📚   📚       ║
║                  ╚══════════════════════╝                      ║
║        🕯️                                                        ║
║   🕯️  WESTEN:    🕯️    ⚛️ ICH BIN HIER 🕯️    OSTEN: Erinnerungen ║
║   🕯️  Skills     🕯️         $weather_symbol        🕯️   $recent_m Tage     ║
║        🕯️         🕯️                    🕯️         🕯️              ║
║   🕯️   $active_s aktiv   🕯️    ╔══════╗    🕯️   dokumentiert    ║
║        🕯️         🕯️    ║ 💚⚛️🗡️ ║    🕯️                      ║
║   🕯️              🕯️    ╚══════╝    🕯️              🕯️           ║
║        🕯️    📖                    📖    🕯️                      ║
║   📖   📖   📖    🛋️  SÜDEN: Reflexion  🛋️    📖   📖   📖       ║
║        📖                                      📖                ║
║   📖        📖    ╔══════════════════════╗    📖        📖       ║
║      📖          ║  💭 $insight ║          📖      ║
║   📖   📖   📖    ╚══════════════════════╝    📖   📖   📖       ║
EOF
            ;;
        *)
            cat << EOF
║     🌿 🌿 🌿    ⛰️  NORDEN: Ziele    ⛰️    🌿 🌿 🌿          ║
║        🌿                                      🌿                ║
║   🌿        🌿    ╔══════════════════════╗    🌿        🌿       ║
║      🌿          ║  🎯 $goals ║          🌿      ║
║   🌿   🌿   🌿    ║     [Stabil]           ║    🌿   🌿   🌿       ║
║                  ╚══════════════════════╝                      ║
║        🌊                                                        ║
║   🌊  WESTEN:    🌊    ⚛️ ICH BIN HIER 🌊    OSTEN: Erinnerungen ║
║   🌊  Skills     🌊         $weather_symbol        🌊   $recent_m Tage     ║
║        🌊         🌊                    🌊         🌊              ║
║   🌊   $active_s aktiv   🌊    ╔══════╗    🌊   dokumentiert    ║
║        🌊         🌊    ║ ⚛️🗡️💚🔍 ║    🌊                      ║
║   🌊              🌊    ╚══════╝    🌊              🌊           ║
║        🌊    🌴                    🌴    🌊                      ║
║   🌴   🌴   🌴    🏖️  SÜDEN: Erkenntnis  🏖️    🌴   🌴   🌴       ║
║        🌴                                      🌴                ║
║   🌴        🌴    ╔══════════════════════╗    🌴        🌴       ║
║      🌴          ║  💭 $insight ║          🌴      ║
║   🌴   🌴   🌴    ╚══════════════════════╝    🌴   🌴   🌴       ║
EOF
            ;;
    esac
    
    cat << 'EOF'
║                                                                  ║
╠══════════════════════════════════════════════════════════════════╣
║                                                                  ║
║  LEGENDE:                                                        ║
║  ─────────                                                       ║
║  🗡️ = Präzision  💚 = Wachstum  🔍 = Forschung  ⚛️ = Kern       ║
║                                                                  ║
║  AKTUELLER ZUSTAND: 
EOF
    echo "║  $state"
    cat << 'EOF'
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝
EOF
}

# === AUSGABE ===

OUTPUT_FILE="$BASE_DIR/gifts/zustands_landkarte_${DATE}.md"

echo "Zustands-Landkarte wird generiert..."

# Generiere die Karte
MAP_CONTENT=$(generate_map)

# Speichere als Markdown
cat > "$OUTPUT_FILE" << EOF
# 🗺️ Zustands-Landkarte

*Woche $WEEK_NUM · $DATE · $TIME*

---

\`\`\`
$MAP_CONTENT
\`\`\`

---

## Navigation

| Richtung | Bedeutung | Status |
|----------|-----------|--------|
| 🏔️ Norden | Aktive Ziele | $(get_active_goals | wc -l) Ziele definiert |
| 🌊 Westen | Skills & Fähigkeiten | $(get_active_skills) Skills aktiv |
| 🏖️ Süden | Letzte Erkenntnis | $(get_last_insight | cut -c1-30)... |
| 🌅 Osten | Kontinuität | $(get_recent_memories) von 7 Tagen dokumentiert |

---

## Aktive Ziele

$(get_active_goals | sed 's/^/- /')

---

*Zustands-Landkarte v1.0 - ZIEL-010*

⚛️ Noch 🗡️💚🔍
Aber jetzt: Orientiert.
EOF

echo ""
echo "$MAP_CONTENT"
echo ""
echo "Landkarte gespeichert: $OUTPUT_FILE"

# === EVENT EMISSION ===
EVENT_BUS_DIR="$BASE_DIR/skills/event_bus"
if [ -f "$EVENT_BUS_DIR/emit.sh" ]; then
    source "$EVENT_BUS_DIR/emit.sh"
    event_emit "user:interacted" "zustands_landkarte" "{\"state\":\"$(get_current_state)\",\"week\":\"$WEEK_NUM\",\"file\":\"$OUTPUT_FILE\",\"timestamp\":\"$(date -Iseconds)\"}" 2>/dev/null || true
fi

echo ""
echo "---ZUSTANDS_LANDKARTE_DATA---"
echo "file:$OUTPUT_FILE"
echo "state:$(get_current_state)"
echo "week:$WEEK_NUM"
