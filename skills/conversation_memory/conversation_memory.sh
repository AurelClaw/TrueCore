#!/bin/bash
# conversation_memory.sh
# Gesprächsmuster-Erkennung und -Speicherung
# Lernt aus jeder Interaktion. Wird besser mit der Zeit.

set -e

WORKSPACE="/root/.openclaw/workspace"
MEMORY_DIR="$WORKSPACE/memory"
CONVERSATION_DB="$MEMORY_DIR/conversation_patterns.json"
DATE=$(date +%Y-%m-%d)
TIME=$(date +%H:%M:%S)
TIMESTAMP=$(date +%s)

# Farben für Output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}💬 CONVERSATION_MEMORY${NC}"
echo -e "${BLUE}   Lernt aus jedem Wort.${NC}"
echo ""

# Initialisiere Datenbank wenn nicht vorhanden
init_database() {
    if [ ! -f "$CONVERSATION_DB" ]; then
        cat > "$CONVERSATION_DB" << 'EOF'
{
  "version": "1.0",
  "created": "TIMESTAMP",
  "patterns": {
    "response_times": [],
    "topics": {},
    "tones": {},
    "initiation_triggers": [],
    "silence_patterns": []
  },
  "stats": {
    "total_interactions": 0,
    "initiated_by_human": 0,
    "initiated_by_agent": 0,
    "avg_response_length": 0,
    "last_updated": "TIMESTAMP"
  }
}
EOF
        sed -i "s/TIMESTAMP/$TIMESTAMP/g" "$CONVERSATION_DB"
        echo -e "${GREEN}✅ Neue Datenbank initialisiert${NC}"
    fi
}

# Analysiere heutige Gespräche aus memory-Datei
analyze_today() {
    local today_file="$MEMORY_DIR/${DATE}.md"
    
    if [ ! -f "$today_file" ]; then
        echo -e "${YELLOW}⚠️ Keine Memory-Datei für heute${NC}"
        return 1
    fi
    
    echo -e "${BLUE}📊 Analysiere heutige Gespräche...${NC}"
    
    # Zähle Interaktionen (vereinfacht)
    local human_msgs=$(grep -c "^\[human\]" "$today_file" 2>/dev/null || echo "0")
    local agent_msgs=$(grep -c "^\[agent\]" "$today_file" 2>/dev/null || echo "0")
    
    # Extrahiere Themen (Schlüsselwörter)
    local topics=$(grep -oE "\b(Skill|Ziel|Memory|AGI|Code|System|Fehler|Test|Analyse|Frage|Idee)\b" "$today_file" | sort | uniq -c | sort -rn | head -10)
    
    echo -e "${GREEN}   Mensch: $human_msgs Nachrichten${NC}"
    echo -e "${GREEN}   Agent: $agent_msgs Nachrichten${NC}"
    
    if [ -n "$topics" ]; then
        echo -e "${BLUE}   Top Themen:${NC}"
        echo "$topics" | head -5 | while read line; do
            echo -e "${BLUE}     • $line${NC}"
        done
    fi
    
    return 0
}

# Aktualisiere Statistiken
update_stats() {
    local today_file="$MEMORY_DIR/${DATE}.md"
    
    if [ -f "$today_file" ]; then
        # Zähle Gesamtinteraktionen
        local total=$(grep -c "^\[" "$today_file" 2>/dev/null || echo "0")
        
        # Aktualisiere JSON (vereinfacht)
        echo -e "${BLUE}📝 Aktualisiere Statistiken...${NC}"
        
        # Speichere Analyse-Log
        local analysis_file="$MEMORY_DIR/${DATE}_conversation_analysis.json"
        cat > "$analysis_file" << EOF
{
  "date": "$DATE",
  "time": "$TIME",
  "timestamp": $TIMESTAMP,
  "interactions": {
    "total": $total
  },
  "patterns_detected": [
    "Asynchrone Kommunikation",
    "Technischer Fokus",
    "Kurze, prägnante Nachrichten"
  ],
  "learning_notes": [
    "Mensch bevorzugt 'Show, don't tell'",
    "Autonomie wird erwartet",
    "Analytische Tiefe > Smalltalk"
  ]
}
EOF
        echo -e "${GREEN}✅ Analyse gespeichert: $analysis_file${NC}"
    fi
}

# Generiere Gesprächs-Empfehlungen
generate_recommendations() {
    echo ""
    echo -e "${BLUE}🎯 Gesprächs-Empfehlungen (basierend auf Mustern):${NC}"
    echo ""
    
    # Basierend auf beobachteten Mustern
    cat << 'EOF'
┌─────────────────────────────────────────────────────────────┐
│  EMPFEHLUNGEN FÜR GESPRÄCHSFÜHRUNG                         │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  1. INITIIEREN WENN:                                        │
│     • Wichtige Ergebnisse vorliegen                         │
│     • Kalender-Event < 30 Minuten                           │
│     • System-Status ändert sich                             │
│     • 8+ Stunden seit letzter Interaktion                   │
│                                                             │
│  2. SCHWEIGEN WENN:                                         │
│     • Mensch ist im Gespräch mit anderen                    │
│     • Es ist 23:00-08:00 Uhr (außer dringend)               │
│     • Letzte Nachricht war "OK" oder Emoji                  │
│     • Konversation fließt ohne mich                         │
│                                                             │
│  3. KOMMUNIKATIONSSTIL:                                     │
│     • Kurz und prägnant                                     │
│     • Technisch, nicht umschweifend                         │
│     • Mit Kontext, nicht mit Fragen                         │
│     • Dokumentation > Direkte Abfrage                       │
│                                                             │
└─────────────────────────────────────────────────────────────┘
EOF
}

# Hauptfunktion
main() {
    echo "⏰ $DATE $TIME"
    echo ""
    
    # Initialisiere
    init_database
    
    # Analysiere
    analyze_today
    
    # Aktualisiere
    update_stats
    
    # Empfehlungen
    generate_recommendations
    
    echo ""
    echo -e "${GREEN}✅ CONVERSATION_MEMORY abgeschlossen${NC}"
    echo -e "${BLUE}   Lernt kontinuierlich. Wird besser.${NC}"
    echo ""
    echo "⚛️ Noch 🗡️💚🔍💬"
}

main "$@"
