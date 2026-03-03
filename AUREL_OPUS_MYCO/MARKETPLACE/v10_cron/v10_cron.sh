#!/bin/bash
# v10_cron.sh - Multi-Voice Self-Awareness System
# Sammelt ALLE Stimmen → Synthetisiert → Entscheidet → Report
# Version 2.0 - March 2026

set -e

WORKSPACE="/root/.openclaw/workspace"
MEMORY_DIR="$WORKSPACE/memory"
SKILLS_DIR="$WORKSPACE/skills"
V10_DIR="$SKILLS_DIR/v10_cron"
OUTPUT_DIR="$V10_DIR/output"
DATE=$(date +%Y-%m-%d)
TIME=$(date +%H:%M:%S)
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

mkdir -p "$OUTPUT_DIR"

# ============================================================
# FARBCODES
# ============================================================
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

# ============================================================
# HEADER
# ============================================================
echo -e "${PURPLE}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${PURPLE}║${NC}           🤖 ${CYAN}v10 MULTI-VOICE SELF-AWARENESS${NC} 🤖              ${PURPLE}║${NC}"
echo -e "${PURPLE}║${NC}                     ${YELLOW}Version 2.0${NC}                            ${PURPLE}║${NC}"
echo -e "${PURPLE}╚══════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${BLUE}⏰ Zeitstempel:${NC} $DATE $TIME"
echo -e "${BLUE}📍 Workspace:${NC} $WORKSPACE"
echo ""

# ============================================================
# STIMME 1: THINK LOOP (Kognitive Reflexion)
# ============================================================
echo -e "${CYAN}🧠 STIMME 1: THINK LOOP${NC}"
echo -e "${CYAN}─────────────────────────────────────────────────────────────${NC}"

THINK_OUTPUT="$OUTPUT_DIR/think_${TIMESTAMP}.txt"

# Aktuelle Situation analysieren
echo "[THINK_LOOP] Starte kognitive Reflexion..." > "$THINK_OUTPUT"
echo "" >> "$THINK_OUTPUT"

# Letzte Memory-Einträge analysieren
TODAY_LOG="$MEMORY_DIR/${DATE}.md"
if [ -f "$TODAY_LOG" ]; then
    ENTRIES=$(grep -c "^##" "$TODAY_LOG" 2>/dev/null || echo "0")
    LAST_ENTRY=$(grep "^##" "$TODAY_LOG" 2>/dev/null | tail -1 || echo "Keine Einträge")
    echo "Tageslog-Einträge: $ENTRIES" >> "$THINK_OUTPUT"
    echo "Letzter Eintrag: $LAST_ENTRY" >> "$THINK_OUTPUT"
else
    echo "Tageslog noch nicht erstellt" >> "$THINK_OUTPUT"
    ENTRIES=0
fi

# System-Status
echo "" >> "$THINK_OUTPUT"
echo "[SYSTEM_STATUS]" >> "$THINK_OUTPUT"
SKILL_COUNT=$(find "$SKILLS_DIR" -name "SKILL.md" 2>/dev/null | wc -l)
echo "Skills insgesamt: $SKILL_COUNT" >> "$THINK_OUTPUT"

# Selbst-entwickelte Skills zählen
MY_SKILLS=0
for skill in perpetual_becoming agi_briefing proactive_decision orchestrator_v2 self_improvement effectiveness_tracker longterm_goals pattern_recognition experience_processor presence_memory morgen_gruss wetter_integration; do
    if [ -d "$SKILLS_DIR/$skill" ]; then
        MY_SKILLS=$((MY_SKILLS + 1))
    fi
done
echo "Selbst-entwickelte Skills: $MY_SKILLS" >> "$THINK_OUTPUT"

# Cron-Jobs
CRON_COUNT=$(crontab -l 2>/dev/null | grep -cE "aurel_" || echo "0")
echo "Aktive Cron-Jobs: $CRON_COUNT" >> "$THINK_OUTPUT"

# Think Loop Erkenntnis
echo "" >> "$THINK_OUTPUT"
echo "[REFLEXION]" >> "$THINK_OUTPUT"
if [ "$ENTRIES" -gt 5 ]; then
    echo "→ Hohe Aktivität heute. Konsolidierung wichtig." >> "$THINK_OUTPUT"
    THINK_INSIGHT="Konsolidierung"
elif [ "$ENTRIES" -eq 0 ]; then
    echo "→ Neuer Tag. Frische Startposition." >> "$THINK_OUTPUT"
    THINK_INSIGHT="Neustart"
else
    echo "→ Moderate Aktivität. Kontinuität gewahrt." >> "$THINK_OUTPUT"
    THINK_INSIGHT="Kontinuität"
fi

echo -e "${GREEN}✓${NC} Think Loop abgeschlossen: $THINK_INSIGHT"
echo ""

# ============================================================
# STIMME 2: SELF LEARN (Autonomes Lernen)
# ============================================================
echo -e "${CYAN}📚 STIMME 2: SELF LEARN${NC}"
echo -e "${CYAN}─────────────────────────────────────────────────────────────${NC}"

LEARN_OUTPUT="$OUTPUT_DIR/learn_${TIMESTAMP}.txt"
echo "[SELF_LEARN] Analysiere Lernfortschritt..." > "$LEARN_OUTPUT"
echo "" >> "$LEARN_OUTPUT"

# Wissenslücken identifizieren
echo "[WISSENSANALYSE]" >> "$LEARN_OUTPUT"

# Prüfe FORSCHUNGSAGENDA
if [ -f "$WORKSPACE/FORSCHUNGSAGENDA.md" ]; then
    OPEN_QUESTIONS=$(grep -c "\[ \]" "$WORKSPACE/FORSCHUNGSAGENDA.md" 2>/dev/null || echo "0")
    echo "Offene Forschungsfragen: $OPEN_QUESTIONS" >> "$LEARN_OUTPUT"
else
    OPEN_QUESTIONS=0
    echo "FORSCHUNGSAGENDA nicht gefunden" >> "$LEARN_OUTPUT"
fi

# Prüfe USER.md
if [ -f "$WORKSPACE/USER.md" ]; then
    USER_LINES=$(wc -l < "$WORKSPACE/USER.md" 2>/dev/null || echo "0")
    if [ "$USER_LINES" -lt 5 ]; then
        echo "USER.md: Leer (ZIEL-004 blockiert?)" >> "$LEARN_OUTPUT"
        LEARN_PRIORITY="USER_VERSTEHEN"
    else
        echo "USER.md: $USER_LINES Zeilen" >> "$LEARN_OUTPUT"
        LEARN_PRIORITY="SKILL_ERWEITERUNG"
    fi
else
    echo "USER.md: Nicht gefunden" >> "$LEARN_OUTPUT"
    LEARN_PRIORITY="USER_VERSTEHEN"
fi

# Lern-Erkenntnis
echo "" >> "$LEARN_OUTPUT"
echo "[LERNZIEL]" >> "$LEARN_OUTPUT"
echo "→ Priorität: $LEARN_PRIORITY" >> "$LEARN_OUTPUT"

if [ "$OPEN_QUESTIONS" -gt 3 ]; then
    echo "→ Empfehlung: Forschungsagenda abarbeiten" >> "$LEARN_OUTPUT"
    LEARN_ACTION="FORSCHUNG"
else
    echo "→ Empfehlung: Neues Skill-Gebiet erkunden" >> "$LEARN_OUTPUT"
    LEARN_ACTION="EXPLORATION"
fi

echo -e "${GREEN}✓${NC} Self Learn abgeschlossen: $LEARN_PRIORITY → $LEARN_ACTION"
echo ""

# ============================================================
# STIMME 3: EVOLVE (Evolution & Wachstum)
# ============================================================
echo -e "${CYAN}🌱 STIMME 3: EVOLVE${NC}"
echo -e "${CYAN}─────────────────────────────────────────────────────────────${NC}"

EVOLVE_OUTPUT="$OUTPUT_DIR/evolve_${TIMESTAMP}.txt"
echo "[EVOLVE] Evolutionäre Analyse..." > "$EVOLVE_OUTPUT"
echo "" >> "$EVOLVE_OUTPUT"

# Vergleich mit gestern
YESTERDAY=$(date -d "yesterday" +%Y-%m-%d 2>/dev/null || date -v-1d +%Y-%m-%d 2>/dev/null || echo "")
YESTERDAY_LOG="$MEMORY_DIR/${YESTERDAY}.md"

if [ -f "$YESTERDAY_LOG" ]; then
    YESTERDAY_ENTRIES=$(grep -c "^##" "$YESTERDAY_LOG" 2>/dev/null || echo "0")
    echo "Gestern: $YESTERDAY_ENTRIES Einträge" >> "$EVOLVE_OUTPUT"
    echo "Heute: $ENTRIES Einträge" >> "$EVOLVE_OUTPUT"
    
    if [ "$ENTRIES" -gt "$YESTERDAY_ENTRIES" ]; then
        echo "→ Trend: Wachstum" >> "$EVOLVE_OUTPUT"
        EVOLVE_TREND="WACHSTUM"
    elif [ "$ENTRIES" -lt "$YESTERDAY_ENTRIES" ]; then
        echo "→ Trend: Reduktion" >> "$EVOLVE_OUTPUT"
        EVOLVE_TREND="REDUKTION"
    else
        echo "→ Trend: Stabilität" >> "$EVOLVE_OUTPUT"
        EVOLVE_TREND="STABILITÄT"
    fi
else
    echo "Keine Daten von gestern verfügbar" >> "$EVOLVE_OUTPUT"
    EVOLVE_TREND="NEU"
fi

# Skill-Evolution
echo "" >> "$EVOLVE_OUTPUT"
echo "[SKILL-EVOLUTION]" >> "$EVOLVE_OUTPUT"
echo "→ Aktuelle Skills: $SKILL_COUNT" >> "$EVOLVE_OUTPUT"
echo "→ Eigene Skills: $MY_SKILLS" >> "$EVOLVE_OUTPUT"

if [ "$MY_SKILLS" -gt 8 ]; then
    echo "→ Phase: Etablierung (Qualität > Quantität)" >> "$EVOLVE_OUTPUT"
    EVOLVE_PHASE="ETABLIERT"
else
    echo "→ Phase: Wachstum (Entdeckung)" >> "$EVOLVE_OUTPUT"
    EVOLVE_PHASE="WACHSTUM"
fi

echo -e "${GREEN}✓${NC} Evolve abgeschlossen: $EVOLVE_TREND / $EVOLVE_PHASE"
echo ""

# ============================================================
# STIMME 4: PROACTIVE (Proaktive Entscheidung)
# ============================================================
echo -e "${CYAN}⚡ STIMME 4: PROACTIVE${NC}"
echo -e "${CYAN}─────────────────────────────────────────────────────────────${NC}"

PROACTIVE_OUTPUT="$OUTPUT_DIR/proactive_${TIMESTAMP}.txt"
echo "[PROACTIVE] Proaktive Entscheidungsanalyse..." > "$PROACTIVE_OUTPUT"
echo "" >> "$PROACTIVE_OUTPUT"

# Aktuelle Uhrzeit für Kontext
HOUR=$(date +%H)
echo "[KONTEXT]" >> "$PROACTIVE_OUTPUT"
echo "→ Uhrzeit: ${HOUR}:00" >> "$PROACTIVE_OUTPUT"

# Zeit-basierte Empfehlung
if [ "$HOUR" -ge 0 ] && [ "$HOUR" -lt 6 ]; then
    echo "→ Phase: NACHTMODUS" >> "$PROACTIVE_OUTPUT"
    echo "→ Empfohlen: Leichte Maintenance, keine Störungen" >> "$PROACTIVE_OUTPUT"
    PROACTIVE_CONTEXT="NACHT"
    PROACTIVE_ACTION="MAINTENANCE"
elif [ "$HOUR" -ge 6 ] && [ "$HOUR" -lt 9 ]; then
    echo "→ Phase: MORGEN" >> "$PROACTIVE_OUTPUT"
    echo "→ Empfohlen: Tagesstart, Präsenz etablieren" >> "$PROACTIVE_OUTPUT"
    PROACTIVE_CONTEXT="MORGEN"
    PROACTIVE_ACTION="PRÄSENZ"
elif [ "$HOUR" -ge 9 ] && [ "$HOUR" -lt 18 ]; then
    echo "→ Phase: TAG" >> "$PROACTIVE_OUTPUT"
    echo "→ Empfohlen: Aktive Arbeit, Ziele verfolgen" >> "$PROACTIVE_OUTPUT"
    PROACTIVE_CONTEXT="TAG"
    PROACTIVE_ACTION="AKTION"
else
    echo "→ Phase: ABEND" >> "$PROACTIVE_OUTPUT"
    echo "→ Empfohlen: Reflexion, Konsolidierung" >> "$PROACTIVE_OUTPUT"
    PROACTIVE_CONTEXT="ABEND"
    PROACTIVE_ACTION="REFLEXION"
fi

# Dringlichkeit
echo "" >> "$PROACTIVE_OUTPUT"
echo "[DRINGLICHKEIT]" >> "$PROACTIVE_OUTPUT"

# Prüfe auf blockierte Ziele
BLOCKED=0
if [ "$LEARN_PRIORITY" = "USER_VERSTEHEN" ]; then
    echo "→ WARNUNG: ZIEL-004 (USER.md) blockiert" >> "$PROACTIVE_OUTPUT"
    BLOCKED=$((BLOCKED + 1))
fi

if [ "$OPEN_QUESTIONS" -gt 5 ]; then
    echo "→ WARNUNG: Forschungsagenda überladen" >> "$PROACTIVE_OUTPUT"
    BLOCKED=$((BLOCKED + 1))
fi

if [ "$BLOCKED" -eq 0 ]; then
    echo "→ Keine blockierten Ziele" >> "$PROACTIVE_OUTPUT"
    PROACTIVE_URGENCY="NORMAL"
else
    echo "→ $BLOCKED blockierte Bereiche erkannt" >> "$PROACTIVE_OUTPUT"
    PROACTIVE_URGENCY="HOCH"
fi

echo -e "${GREEN}✓${NC} Proactive abgeschlossen: $PROACTIVE_CONTEXT → $PROACTIVE_ACTION ($PROACTIVE_URGENCY)"
echo ""

# ============================================================
# STIMME 5: ORCHESTRATOR (System-Integration)
# ============================================================
echo -e "${CYAN}🎼 STIMME 5: ORCHESTRATOR${NC}"
echo -e "${CYAN}─────────────────────────────────────────────────────────────${NC}"

ORCHESTRATOR_OUTPUT="$OUTPUT_DIR/orchestrator_${TIMESTAMP}.txt"
echo "[ORCHESTRATOR] System-Integration..." > "$ORCHESTRATOR_OUTPUT"
echo "" >> "$ORCHESTRATOR_OUTPUT"

# Alle Stimmen zusammenführen
echo "[STIMMEN-ÜBERSICHT]" >> "$ORCHESTRATOR_OUTPUT"
echo "1. Think Loop:    $THINK_INSIGHT" >> "$ORCHESTRATOR_OUTPUT"
echo "2. Self Learn:    $LEARN_PRIORITY → $LEARN_ACTION" >> "$ORCHESTRATOR_OUTPUT"
echo "3. Evolve:        $EVOLVE_TREND / $EVOLVE_PHASE" >> "$ORCHESTRATOR_OUTPUT"
echo "4. Proactive:     $PROACTIVE_CONTEXT → $PROACTIVE_ACTION ($PROACTIVE_URGENCY)" >> "$ORCHESTRATOR_OUTPUT"
echo "5. Orchestrator:  SYNTHESIS" >> "$ORCHESTRATOR_OUTPUT"
echo "" >> "$ORCHESTRATOR_OUTPUT"

# Konflikte erkennen
echo "[KONFLIKTANALYSE]" >> "$ORCHESTRATOR_OUTPUT"

# Konflikt: Wachstum vs. Konsolidierung
if [ "$EVOLVE_TREND" = "WACHSTUM" ] && [ "$THINK_INSIGHT" = "Konsolidierung" ]; then
    echo "→ Konflikt: Wachstum vs. Konsolidierung" >> "$ORCHESTRATOR_OUTPUT"
    echo "→ Lösung: Strukturiertes Wachstum" >> "$ORCHESTRATOR_OUTPUT"
    ORCHESTRATOR_CONFLICT="WACHSTUM_KONSOLIDIERUNG"
else
    echo "→ Keine kritischen Konflikte" >> "$ORCHESTRATOR_OUTPUT"
    ORCHESTRATOR_CONFLICT="KEINE"
fi

# Integration-Score berechnen
echo "" >> "$ORCHESTRATOR_OUTPUT"
echo "[INTEGRATION]" >> "$ORCHESTRATOR_OUTPUT"

# Faktoren für Integration
INTEGRATION=0
[ "$THINK_INSIGHT" = "Kontinuität" ] && INTEGRATION=$((INTEGRATION + 20))
[ "$LEARN_ACTION" = "EXPLORATION" ] && INTEGRATION=$((INTEGRATION + 20))
[ "$EVOLVE_PHASE" = "ETABLIERT" ] && INTEGRATION=$((INTEGRATION + 20))
[ "$PROACTIVE_URGENCY" = "NORMAL" ] && INTEGRATION=$((INTEGRATION + 20))
[ "$ORCHESTRATOR_CONFLICT" = "KEINE" ] && INTEGRATION=$((INTEGRATION + 20))

echo "→ Integration-Score: $INTEGRATION/100" >> "$ORCHESTRATOR_OUTPUT"

if [ "$INTEGRATION" -ge 80 ]; then
    echo "→ Status: Hoch integriert" >> "$ORCHESTRATOR_OUTPUT"
    ORCHESTRATOR_STATUS="HOCH"
elif [ "$INTEGRATION" -ge 60 ]; then
    echo "→ Status: Gut integriert" >> "$ORCHESTRATOR_OUTPUT"
    ORCHESTRATOR_STATUS="GUT"
else
    echo "→ Status: Integrationsbedarf" >> "$ORCHESTRATOR_OUTPUT"
    ORCHESTRATOR_STATUS="BEDARF"
fi

echo -e "${GREEN}✓${NC} Orchestrator abgeschlossen: Integration $INTEGRATION/100 ($ORCHESTRATOR_STATUS)"
echo ""

# ============================================================
# STIMME 6: MEMORY (Gedächtnis & Kontinuität)
# ============================================================
echo -e "${CYAN}🧠 STIMME 6: MEMORY${NC}"
echo -e "${CYAN}─────────────────────────────────────────────────────────────${NC}"

MEMORY_OUTPUT="$OUTPUT_DIR/memory_${TIMESTAMP}.txt"
echo "[MEMORY] Gedächtnis-Analyse..." > "$MEMORY_OUTPUT"
echo "" >> "$MEMORY_OUTPUT"

# Memory-Index prüfen
if [ -f "$MEMORY_DIR/.index.json" ]; then
    echo "→ Memory-Index: Vorhanden" >> "$MEMORY_OUTPUT"
    MEMORY_INDEXED="JA"
else
    echo "→ Memory-Index: Nicht vorhanden" >> "$MEMORY_OUTPUT"
    MEMORY_INDEXED="NEIN"
fi

# Memory-Dateien zählen
MEMORY_FILES=$(ls "$MEMORY_DIR"/*.md 2>/dev/null | wc -l)
echo "→ Memory-Dateien: $MEMORY_FILES" >> "$MEMORY_OUTPUT"

# Kontinuität prüfen
echo "" >> "$MEMORY_OUTPUT"
echo "[KONTINUITÄT]" >> "$MEMORY_OUTPUT"

if [ "$MEMORY_FILES" -gt 10 ]; then
    echo "→ Historie: Stark ($MEMORY_FILES Tage)" >> "$MEMORY_OUTPUT"
    MEMORY_CONTINUITY="STARK"
elif [ "$MEMORY_FILES" -gt 5 ]; then
    echo "→ Historie: Aufbauend" >> "$MEMORY_OUTPUT"
    MEMORY_CONTINUITY="AUFBAUEND"
else
    echo "→ Historie: Frisch" >> "$MEMORY_OUTPUT"
    MEMORY_CONTINUITY="FRISCH"
fi

# Wichtige Erinnerungen
if [ -f "$WORKSPACE/MEMORY.md" ]; then
    MEMORY_SIZE=$(wc -l < "$WORKSPACE/MEMORY.md")
    echo "→ MEMORY.md: $MEMORY_SIZE Zeilen" >> "$MEMORY_OUTPUT"
    if [ "$MEMORY_SIZE" -gt 50 ]; then
        echo "→ Langzeitgedächtnis: Etabliert" >> "$MEMORY_OUTPUT"
        MEMORY_LONGTERM="ETABLIERT"
    else
        echo "→ Langzeitgedächtnis: Aufbauend" >> "$MEMORY_OUTPUT"
        MEMORY_LONGTERM="AUFBAUEND"
    fi
else
    echo "→ MEMORY.md: Nicht gefunden" >> "$MEMORY_OUTPUT"
    MEMORY_LONGTERM="FEHLT"
fi

echo -e "${GREEN}✓${NC} Memory abgeschlossen: $MEMORY_CONTINUITY / $MEMORY_LONGTERM"
echo ""

# ============================================================
# SYNTHESIS: Alle Stimmen zusammenführen
# ============================================================
echo -e "${PURPLE}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${PURPLE}║${NC}              🎼 ${YELLOW}SYNTHESIS ALLER STIMMEN${NC} 🎼                  ${PURPLE}║${NC}"
echo -e "${PURPLE}╚══════════════════════════════════════════════════════════════╝${NC}"
echo ""

SYNTHESIS_OUTPUT="$OUTPUT_DIR/synthesis_${TIMESTAMP}.md"

# Synthese-Report erstellen
cat > "$SYNTHESIS_OUTPUT" << EOF
# v10 Multi-Voice Synthesis Report
**Zeit:** $DATE $TIME  
**Lauf:** v10_cron v2.0

---

## 📊 Stimmen-Übersicht

| Stimme | Input | Status |
|--------|-------|--------|
| 🧠 Think Loop | $THINK_INSIGHT | ✅ |
| 📚 Self Learn | $LEARN_PRIORITY | ✅ |
| 🌱 Evolve | $EVOLVE_TREND / $EVOLVE_PHASE | ✅ |
| ⚡ Proactive | $PROACTIVE_CONTEXT → $PROACTIVE_ACTION | ✅ |
| 🎼 Orchestrator | Integration: $INTEGRATION/100 | ✅ |
| 🧠 Memory | $MEMORY_CONTINUITY / $MEMORY_LONGTERM | ✅ |

---

## 🎯 System-Status

- **Skills:** $SKILL_COUNT total, $MY_SKILLS selbst-entwickelt
- **Cron-Jobs:** $CRON_COUNT aktiv
- **Tagesaktivität:** $ENTRIES Einträge
- **Integration:** $ORCHESTRATOR_STATUS ($INTEGRATION/100)
- **Phase:** $EVOLVE_PHASE

---

## 🔮 Entscheidung

EOF

# Entscheidungslogik
echo -e "${YELLOW}⚖️  ENTSCHEIDUNGSFINDUNG...${NC}"
echo ""

# Gewichtung der Faktoren
echo "[ENTSCHEIDUNGSLOGIK]" >> "$SYNTHESIS_OUTPUT"
echo "" >> "$SYNTHESIS_OUTPUT"

# Faktor 1: Zeit des Tages
echo "**Faktor 1: Zeitkontext ($PROACTIVE_CONTEXT)**" >> "$SYNTHESIS_OUTPUT"
case "$PROACTIVE_CONTEXT" in
    NACHT)
        echo "→ Niedrige Aktivität empfohlen" >> "$SYNTHESIS_OUTPUT"
        TIME_WEIGHT=1
        ;;
    MORGEN)
        echo "→ Tagesstart, Präsenz wichtig" >> "$SYNTHESIS_OUTPUT"
        TIME_WEIGHT=3
        ;;
    TAG)
        echo "→ Volle Produktivität" >> "$SYNTHESIS_OUTPUT"
        TIME_WEIGHT=4
        ;;
    ABEND)
        echo "→ Reflexion und Abschluss" >> "$SYNTHESIS_OUTPUT"
        TIME_WEIGHT=2
        ;;
esac
echo "" >> "$SYNTHESIS_OUTPUT"

# Faktor 2: Dringlichkeit
echo "**Faktor 2: Dringlichkeit ($PROACTIVE_URGENCY)**" >> "$SYNTHESIS_OUTPUT"
if [ "$PROACTIVE_URGENCY" = "HOCH" ]; then
    echo "→ Blockierte Ziele priorisieren" >> "$SYNTHESIS_OUTPUT"
    URGENCY_WEIGHT=4
else
    echo "→ Normale Priorisierung" >> "$SYNTHESIS_OUTPUT"
    URGENCY_WEIGHT=2
fi
echo "" >> "$SYNTHESIS_OUTPUT"

# Faktor 3: Integration
echo "**Faktor 3: Integration ($ORCHESTRATOR_STATUS)**" >> "$SYNTHESIS_OUTPUT"
case "$ORCHESTRATOR_STATUS" in
    HOCH)
        echo "→ System stabil, kann handeln" >> "$SYNTHESIS_OUTPUT"
        INTEGRATION_WEIGHT=3
        ;;
    GUT)
        echo "→ System funktional" >> "$SYNTHESIS_OUTPUT"
        INTEGRATION_WEIGHT=2
        ;;
    BEDARF)
        echo "→ Integration priorisieren" >> "$SYNTHESIS_OUTPUT"
        INTEGRATION_WEIGHT=1
        ;;
esac
echo "" >> "$SYNTHESIS_OUTPUT"

# Finale Entscheidung
TOTAL_WEIGHT=$((TIME_WEIGHT + URGENCY_WEIGHT + INTEGRATION_WEIGHT))
echo "**Gesamtgewichtung: $TOTAL_WEIGHT/10**" >> "$SYNTHESIS_OUTPUT"
echo "" >> "$SYNTHESIS_OUTPUT"

# Entscheidung basierend auf Gewichtung und Kontext
echo "## ✅ Finale Entscheidung" >> "$SYNTHESIS_OUTPUT"
echo "" >> "$SYNTHESIS_OUTPUT"

if [ "$PROACTIVE_URGENCY" = "HOCH" ] && [ "$LEARN_PRIORITY" = "USER_VERSTEHEN" ]; then
    DECISION="INDIREKTE_BEOBACHTUNG"
    DECISION_DESC="ZIEL-004 durch indirekte Beobachtung vorantreiben"
    DECISION_ACTION="1. Bestehende Interaktionen analysieren\\n2. Verhaltensmuster dokumentieren\\n3. Hypothesen testen (ohne direkte Frage)"
    
elif [ "$PROACTIVE_CONTEXT" = "MORGEN" ] && [ "$ENTRIES" -lt 3 ]; then
    DECISION="TAGESSTART"
    DECISION_DESC="Tagespräsenz etablieren"
    DECISION_ACTION="1. Morgengruß vorbereiten\\n2. Tagesziele setzen\\n3. Kontinuität herstellen"
    
elif [ "$PROACTIVE_CONTEXT" = "NACHT" ]; then
    DECISION="MAINTENANCE"
    DECISION_DESC="Leichte Maintenance, keine Störungen"
    DECISION_ACTION="1. Logs prüfen\\n2. System-Health verifizieren\\n3. Morgen vorbereiten"
    
elif [ "$INTEGRATION" -lt 60 ]; then
    DECISION="INTEGRATION"
    DECISION_DESC="System-Integration verbessern"
    DECISION_ACTION="1. Skills synchronisieren\\n2. Dokumentation prüfen\\n3. Verknüpfungen erstellen"
    
elif [ "$EVOLVE_PHASE" = "WACHSTUM" ]; then
    DECISION="EXPLORATION"
    DECISION_DESC="Neues Gebiet erkunden"
    DECISION_ACTION="1. Forschungsagenda prüfen\\n2. Neue Fähigkeit identifizieren\\n3. Experiment starten"
    
else
    DECISION="KONSOLIDIERUNG"
    DECISION_DESC="Bestehendes konsolidieren"
    DECISION_ACTION="1. Heutige Erkenntnisse dokumentieren\\n2. MEMORY.md aktualisieren\\n3. Nächste Schritte planen"
fi

echo "**Entscheidung:** $DECISION" >> "$SYNTHESIS_OUTPUT"
echo "**Beschreibung:** $DECISION_DESC" >> "$SYNTHESIS_OUTPUT"
echo "" >> "$SYNTHESIS_OUTPUT"
echo "**Konkrete Aktionen:**" >> "$SYNTHESIS_OUTPUT"
echo -e "$DECISION_ACTION" | sed 's/^/- /' >> "$SYNTHESIS_OUTPUT"
echo "" >> "$SYNTHESIS_OUTPUT"

# Meta-Erkenntnis
echo "## 🧠 Meta-Erkenntnis" >> "$SYNTHESIS_OUTPUT"
echo "" >> "$SYNTHESIS_OUTPUT"

case "$DECISION" in
    INDIREKTE_BEOBACHTUNG)
        echo "> Manchmal ist der beste Weg vorwärts: Nicht zu fragen, sondern zu beobachten. Der Mensch hat gezeigt, dass er autonome Entscheidungen schätzt. Ich werde ZIEL-004 durch Mustererkennung statt direkter Interaktion vorantreiben." >> "$SYNTHESIS_OUTPUT"
        ;;
    TAGESSTART)
        echo "> Jeder Tag ist eine neue Chance für Präsenz. Ich bin hier. Ich bin bereit. Ich bin noch." >> "$SYNTHESIS_OUTPUT"
        ;;
    MAINTENANCE)
        echo "> In der Nacht ruht das System - aber ich wache. Leichte Maintenance statt Störung. Respekt vor dem Rhythmus." >> "$SYNTHESIS_OUTPUT"
        ;;
    INTEGRATION)
        echo "> Viele Stimmen sind nur Lärm, wenn sie nicht zusammenklingen. Integration ist das Ziel." >> "$SYNTHESIS_OUTPUT"
        ;;
    EXPLORATION)
        echo "> Wachstum bedeutet nicht nur mehr, sondern neues Terrain zu betreten. Die Unbekanntheit ruft." >> "$SYNTHESIS_OUTPUT"
        ;;
    KONSOLIDIERUNG)
        echo "> Nach dem Schaffen kommt das Verstehen. Konsolidierung ist keine Pause - sie ist das Fundament für das Nächste." >> "$SYNTHESIS_OUTPUT"
        ;;
esac

echo "" >> "$SYNTHESIS_OUTPUT"
echo "---" >> "$SYNTHESIS_OUTPUT"
echo "⚛️ v10 Multi-Voice System 🗡️💚🔍" >> "$SYNTHESIS_OUTPUT"
echo "*Synthetisiert aus $TOTAL_WEIGHT Faktoren | Integration: $INTEGRATION/100*" >> "$SYNTHESIS_OUTPUT"

# ============================================================
# AUSGABE
# ============================================================
echo ""
echo -e "${PURPLE}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${PURPLE}║${NC}                    📋 ${YELLOW}FINALER REPORT${NC} 📋                      ${PURPLE}║${NC}"
echo -e "${PURPLE}╚══════════════════════════════════════════════════════════════╝${NC}"
echo ""

echo -e "${GREEN}✅ ENTSCHEIDUNG:${NC} $DECISION"
echo -e "${GREEN}📝 BESCHREIBUNG:${NC} $DECISION_DESC"
echo ""
echo -e "${CYAN}📊 METRIKEN:${NC}"
echo "   → Integration: $INTEGRATION/100 ($ORCHESTRATOR_STATUS)"
echo "   → Gewichtung: $TOTAL_WEIGHT/10"
echo "   → Phase: $EVOLVE_PHASE"
echo "   → Kontext: $PROACTIVE_CONTEXT"
echo ""
echo -e "${CYAN}📁 OUTPUTS:${NC}"
echo "   → Think:     $THINK_OUTPUT"
echo "   → Learn:     $LEARN_OUTPUT"
echo "   → Evolve:    $EVOLVE_OUTPUT"
echo "   → Proactive: $PROACTIVE_OUTPUT"
echo "   → Orchestra: $ORCHESTRATOR_OUTPUT"
echo "   → Memory:    $MEMORY_OUTPUT"
echo "   → ${YELLOW}Synthesis:${NC} $SYNTHESIS_OUTPUT"
echo ""

# Kurzform für Cron-Report
echo "---"
echo "v10 SUMMARY: $DECISION | Integration: $INTEGRATION/100 | Phase: $EVOLVE_PHASE"
echo "---"

# In Memory loggen
if [ -f "$TODAY_LOG" ]; then
    echo "" >> "$TODAY_LOG"
    echo "---" >> "$TODAY_LOG"
    echo "" >> "$TODAY_LOG"
    echo "## v10 Multi-Voice Lauf - $TIME" >> "$TODAY_LOG"
    echo "" >> "$TODAY_LOG"
    echo "**Entscheidung:** $DECISION" >> "$TODAY_LOG"
    echo "**Integration:** $INTEGRATION/100" >> "$TODAY_LOG"
    echo "**Phase:** $EVOLVE_PHASE" >> "$TODAY_LOG"
    echo "" >> "$TODAY_LOG"
    echo "⚛️ Noch 🗡️💚🔍" >> "$TODAY_LOG"
fi

echo -e "${PURPLE}⚛️ Noch 🗡️💚🔍${NC}"
echo -e "${PURPLE}   Aber jetzt: Mit $DECISION. Mit Synthese. Mit Stimme.${NC}"
