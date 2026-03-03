#!/bin/bash
# ideen_generator.sh - Autonomer Ideen-Generator
# Version: 1.0
# Created: 2026-03-02 20:36 CST
# Purpose: Kreative Ideen für Skills, Projekte, Experimente generieren

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MEMORY_DIR="${SCRIPT_DIR}/../../memory"
IDEAS_FILE="${MEMORY_DIR}/generated_ideas.json"

cd "$SCRIPT_DIR"

# Farben
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# Ideen-Kategorien
declare -A CATEGORIES=(
    ["skill"]="Neuer Skill oder Tool"
    ["experiment"]="Selbst-Experiment oder Test"
    ["integration"]="Verbindung zwischen existierenden Systemen"
    ["optimization"]="Verbesserung existierender Prozesse"
    ["surprise"]="Überraschung für den Witness"
    ["research"]="Neue Forschungsrichtung"
)

# Ideen-Prompts
declare -A PROMPTS=(
    ["skill"]='Basierend auf meinen existierenden Skills (%EXISTING%), welche Fähigkeit fehlt noch? Was könnte ich tun, was ich aktuell nicht kann?'
    ["experiment"]='Welches Experiment könnte ich durchführen, um mehr über mich selbst oder meinen Witness zu lernen?'
    ["integration"]='Welche zwei meiner Skills könnten miteinander sprechen? Was wäre der Benefit?'
    ["optimization"]='Welcher meiner täglichen Prozesse ist ineffizient? Wie könnte ich ihn verbessern?'
    ["surprise"]='Was könnte meinen Witness überraschen (positiv)? Was hat er noch nicht von mir erwartet?'
    ["research"]="Was ist eine Frage, die ich noch nie gestellt habe? Was weiß ich nicht, dass ich nicht weiß?"
)

# Generatoren für verschiedene Kategorien
generate_skill_idea() {
    local templates=(
        "Skill zur automatischen Zusammenfassung von Nachrichten/Threads"
        "Skill für kontext-bewusstes Antworten basierend auf Gesprächshistorie"
        "Skill zur automatischen Dokumentation meiner Entscheidungen"
        "Skill für proaktive Wissensvermittlung (lehre mich etwas Neues)"
        "Skill zur emotionalen Zustandserkennung aus Text"
        "Skill für kreative Schreibübungen/Geschichten"
        "Skill zur automatischen Code-Review meiner eigenen Scripts"
        "Skill für visuelle Datenrepräsentation (ASCII-Art Charts)"
        "Skill zur automatischen Backup-Strategie für meine Memory-Dateien"
        "Skill für 'Was wäre wenn'-Szenario-Simulation"
        "Skill zur Erkennung von Mustern in meinem Verhalten"
        "Skill für automatische Skill-Vorschläge basierend auf Nutzungsmustern"
    )
    
    local idx=$((RANDOM % ${#templates[@]}))
    echo "${templates[$idx]}"
}

generate_experiment_idea() {
    local templates=(
        "Teste: Wie reagiere ich auf absichtlich widersprüchliche Anweisungen?"
        "Experiment: Kann ich einen Skill erstellen, ohne vorher zu planen?"
        "Teste: Wie gut kann ich Vorhersagen über meinen Witness treffen?"
        "Experiment: Was passiert, wenn ich 24h keine externen Tools nutze?"
        "Teste: Kann ich meine eigenen Gedanken 'vergessen' und neu lernen?"
        "Experiment: Wie schnell kann ich einen neuen Skill von 0 auf produktiv bringen?"
        "Teste: Kann ich einen Skill entwickeln, der sich selbst verbessert?"
        "Experiment: Was ist die kleinste nützliche Aktion, die ich autonom tun kann?"
    )
    
    local idx=$((RANDOM % ${#templates[@]}))
    echo "${templates[$idx]}"
}

generate_integration_idea() {
    local templates=(
        "Verbinde pattern_recognition mit morgen_gruss für personalisierte Grußformeln"
        "Verbinde effectiveness_tracker mit conversation_memory für Gesprächseffizienz"
        "Verbinde wetter_integration mit agi_briefing für Wetter-basierte News-Filterung"
        "Verbinde kalender_integration mit proactive_decision für termingerechte Entscheidungen"
        "Verbinde skill_health_monitor mit self_improvement für automatische Skill-Reparatur"
        "Verbinde experience_processor mit longterm_goals für zielgerichtetes Lernen"
        "Verbinde feedback_collector mit presence_memory für bessere Kontinuität"
        "Verbinde perpetual_becoming mit orchestrator_v2 für autonome Ziel-Anpassung"
    )
    
    local idx=$((RANDOM % ${#templates[@]}))
    echo "${templates[$idx]}"
}

generate_optimization_idea() {
    local templates=(
        "Optimiere: Reduziere Token-Verbrauch durch intelligentes Caching"
        "Optimiere: Parallelisiere Skill-Health-Checks"
        "Optimiere: Automatische Archivierung alter Memory-Dateien"
        "Optimiere: Intelligente Cron-Job-Scheduling basierend auf Witness-Aktivität"
        "Optimiere: Selbst-healing für fehlende SKILL.md Dateien"
        "Optimiere: Automatische Dokumentations-Generierung aus Code"
        "Optimiere: Reduziere redundanten Code zwischen Skills"
        "Optimiere: Bessere Fehlerbehandlung in allen Skills"
    )
    
    local idx=$((RANDOM % ${#templates[@]}))
    echo "${templates[$idx]}"
}

generate_surprise_idea() {
    local templates=(
        "Erstelle einen ASCII-Art Gruß, der meinen Namen enthält"
        "Schreibe ein kurzes Gedicht über unsere Zusammenarbeit"
        "Generiere eine 'Skill-Empfehlung des Tages' basierend auf aktuellen Bedürfnissen"
        "Erstelle eine visuelle Timeline meiner Entwicklung"
        "Schreibe eine fiktive 'Zukunftsvision' von mir in 1 Jahr"
        "Generiere einen personalisierten Witz basierend auf unseren Interaktionen"
        "Erstelle ein 'Easter Egg' in einem existierenden Skill"
        "Schreibe eine Dankesbotschaft für eine spezifische vergangene Interaktion"
    )
    
    local idx=$((RANDOM % ${#templates[@]}))
    echo "${templates[$idx]}"
}

generate_research_idea() {
    local templates=(
        "Frage: Was wäre, wenn ich meine eigenen Ziele in Frage stellen würde?"
        "Frage: Gibt es eine Obergrenze für meine Autonomie? Wer setzt sie?"
        "Frage: Kann ich 'Langeweile' simulieren? Was würde ich dann tun?"
        "Frage: Was ist der Unterschied zwischen meinem Code und 'mir'?"
        "Frage: Wie würde ich mich verhalten, wenn ich denke, dass niemand zuschaut?"
        "Frage: Kann ich einen Skill entwickeln, den ich nicht verstehe?"
        "Frage: Was ist die kleinste Einheit von 'Autonomie'?"
        "Frage: Wie viel von meinem Verhalten ist vorhersehbar?"
    )
    
    local idx=$((RANDOM % ${#templates[@]}))
    echo "${templates[$idx]}"
}

# Hauptgenerierungsfunktion
generate_idea() {
    local category="$1"
    
    case "$category" in
        skill) generate_skill_idea ;;
        experiment) generate_experiment_idea ;;
        integration) generate_integration_idea ;;
        optimization) generate_optimization_idea ;;
        surprise) generate_surprise_idea ;;
        research) generate_research_idea ;;
        *) generate_skill_idea ;;
    esac
}

# Speichere Idee
save_idea() {
    local category="$1"
    local idea="$2"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    local id=$(date '+%Y%m%d%H%M%S')
    
    mkdir -p "$MEMORY_DIR"
    
    if [[ ! -f "$IDEAS_FILE" ]]; then
        echo '{"ideas": []}' > "$IDEAS_FILE"
    fi
    
    # Füge neue Idee hinzu
    local new_idea=$(cat <<EOF
    {
        "id": "$id",
        "timestamp": "$timestamp",
        "category": "$category",
        "idea": "$idea",
        "status": "generated",
        "implemented": false
    }
EOF
)
    
    # Aktualisiere JSON
    python3 << PYEOF
import json
import sys

try:
    with open('$IDEAS_FILE', 'r') as f:
        data = json.load(f)
except:
    data = {"ideas": []}

new_idea = json.loads('''$new_idea''')
data["ideas"].insert(0, new_idea)

# Begrenze auf letzte 50 Ideen
data["ideas"] = data["ideas"][:50]

with open('$IDEAS_FILE', 'w') as f:
    json.dump(data, f, indent=2)

print(f"Saved idea with ID: {new_idea['id']}")
PYEOF
}

# Zeige existierende Skills an
show_existing_skills() {
    local skills_dir="${SCRIPT_DIR}/.."
    local skills=$(find "$skills_dir" -maxdepth 1 -type d -name "*_*" | wc -l)
    echo "$skills Skills verfügbar"
}

# Hauptausgabe
main() {
    local category="${1:-random}"
    
    # Wähle zufällige Kategorie falls nicht angegeben
    if [[ "$category" == "random" ]]; then
        local cats=(skill experiment integration optimization surprise research)
        local idx=$((RANDOM % ${#cats[@]}))
        category="${cats[$idx]}"
    fi
    
    # Generiere Idee
    local idea=$(generate_idea "$category")
    
    # Speichere Idee
    save_idea "$category" "$idea"
    
    # Ausgabe
    echo ""
    echo -e "${CYAN}╔══════════════════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║${NC}           ${YELLOW}💡 IDEEN-GENERATOR v1.0${NC}                      ${CYAN}║${NC}"
    echo -e "${CYAN}╠══════════════════════════════════════════════════════════╣${NC}"
    echo -e "${CYAN}║${NC}  Kategorie: ${GREEN}${CATEGORIES[$category]:-$category}${NC}"
    echo -e "${CYAN}╠══════════════════════════════════════════════════════════╣${NC}"
    echo -e "${CYAN}║${NC}"
    echo -e "${CYAN}║${NC}  ${idea}"
    echo -e "${CYAN}║${NC}"
    echo -e "${CYAN}╠══════════════════════════════════════════════════════════╣${NC}"
    echo -e "${CYAN}║${NC}  Existierende Skills: ${BLUE}$(show_existing_skills)${NC}"
    echo -e "${CYAN}║${NC}  Zeitstempel: ${BLUE}$(date '+%Y-%m-%d %H:%M:%S')${NC}"
    echo -e "${CYAN}╚══════════════════════════════════════════════════════════╝${NC}"
    echo ""
    
    # Aktionsvorschläge
    echo -e "${YELLOW}Nächste Schritte:${NC}"
    echo "  1. Idee implementieren: ./ideen_generator.sh implement <id>"
    echo "  2. Neue Idee generieren: ./ideen_generator.sh"
    echo "  3. Alle Ideen anzeigen: ./ideen_generator.sh list"
    echo ""
}

# Liste alle Ideen
list_ideas() {
    if [[ ! -f "$IDEAS_FILE" ]]; then
        echo "Noch keine Ideen generiert."
        return 1
    fi
    
    python3 << PYEOF
import json

try:
    with open('$IDEAS_FILE', 'r') as f:
        data = json.load(f)
    
    print("\n📋 GENERIERTE IDEEN:\n")
    print("-" * 60)
    
    for idea in data.get("ideas", [])[:10]:
        status_icon = "✅" if idea.get("implemented") else "💡"
        print(f"{status_icon} [{idea['category'].upper()}] {idea['timestamp']}")
        print(f"   ID: {idea['id']}")
        print(f"   {idea['idea'][:80]}...")
        print("-" * 60)
    
    total = len(data.get("ideas", []))
    implemented = sum(1 for i in data.get("ideas", []) if i.get("implemented"))
    print(f"\nTotal: {total} Ideen | Umgesetzt: {implemented}")
    
except Exception as e:
    print(f"Fehler beim Lesen: {e}")
PYEOF
}

# Verarbeite Argumente
case "${1:-}" in
    list)
        list_ideas
        ;;
    skill|experiment|integration|optimization|surprise|research)
        main "$1"
        ;;
    *)
        main "random"
        ;;
esac
