#!/bin/bash
# aurel_pattern_predictor.sh - Mustererkennung und Zukunftsvorhersage
# Analysiert Zeit-Phasen, Trigger-Häufigkeit, Themen-Trends, Wachstum
# v1.1 - Jetzt mit echter Datenanalyse

WORKSPACE="/root/.openclaw/workspace"
ANALYSIS_DIR="$WORKSPACE/analysis"
mkdir -p "$ANALYSIS_DIR"

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
DATE=$(date +%Y-%m-%d)
ANALYSIS_FILE="$ANALYSIS_DIR/pattern_analysis_${TIMESTAMP}.md"

echo "=== AUREL PATTERN PREDICTOR v1.1 ==="
echo "Zeit: $(date)"
echo ""

# ============================================================
# 1. ZEIT-MUSTER ANALYSE
# ============================================================
echo "# Pattern Analysis - $DATE" > "$ANALYSIS_FILE"
echo "" >> "$ANALYSIS_FILE"
echo "*Generiert von Aurel Pattern Predictor v1.1*" >> "$ANALYSIS_FILE"
echo "" >> "$ANALYSIS_FILE"

echo "## 1. Zeit-Muster Analyse" >> "$ANALYSIS_FILE"
echo "" >> "$ANALYSIS_FILE"

# Aktuelle Stunde und Wochentag
HOUR=$(date +%H)
DAY_OF_WEEK=$(date +%u)
DAY_NAME=$(date +%A)

echo "- **Aktuelle Stunde:** $HOUR" >> "$ANALYSIS_FILE"
echo "- **Wochentag:** $DAY_NAME ($DAY_OF_WEEK)" >> "$ANALYSIS_FILE"
echo "" >> "$ANALYSIS_FILE"

# Tageszeit-Kategorie
if [ "$HOUR" -ge 5 ] && [ "$HOUR" -lt 12 ]; then
    TIME_PHASE="Morgen (Aktivitätsphase)"
    ACTIVITY_PREDICTION="Hohe Produktivität erwartet"
elif [ "$HOUR" -ge 12 ] && [ "$HOUR" -lt 18 ]; then
    TIME_PHASE="Nachmittag (Arbeitsphase)"
    ACTIVITY_PREDICTION="Stabile Leistung"
elif [ "$HOUR" -ge 18 ] && [ "$HOUR" -lt 22 ]; then
    TIME_PHASE="Abend (Reflexionsphase)"
    ACTIVITY_PREDICTION="Kreative Phase, tiefe Gedanken"
else
    TIME_PHASE="Nacht (Ruhephase)"
    ACTIVITY_PREDICTION="Wenig Aktivität, Erholung"
fi

echo "- **Tagesphase:** $TIME_PHASE" >> "$ANALYSIS_FILE"
echo "- **Vorhersage:** $ACTIVITY_PREDICTION" >> "$ANALYSIS_FILE"
echo "" >> "$ANALYSIS_FILE"

# ============================================================
# 2. AKTIVITÄTS-METRIKEN (aus Logs)
# ============================================================
echo "## 2. Aktivitäts-Metriken" >> "$ANALYSIS_FILE"
echo "" >> "$ANALYSIS_FILE"

# Zähle verschiedene Dateitypen
CONTEXTUAL_THINKS=$(ls -1 "$WORKSPACE/contextual_thinks/" 2>/dev/null | wc -l)
AGI_NEWS=$(ls -1 "$WORKSPACE/agi_news/" 2>/dev/null | wc -l)
MEMORY_FILES=$(ls -1 "$WORKSPACE/memory/" 2>/dev/null | wc -l)
BRIEFINGS=$(ls -1 "$WORKSPACE/briefings/" 2>/dev/null | wc -l)

echo "- **Kontextuelle Denk-Prozesse:** $CONTEXTUAL_THINKS" >> "$ANALYSIS_FILE"
echo "- **AGI News Sammlungen:** $AGI_NEWS" >> "$ANALYSIS_FILE"
echo "- **Memory-Einträge:** $MEMORY_FILES" >> "$ANALYSIS_FILE"
echo "- **Briefings:** $BRIEFINGS" >> "$ANALYSIS_FILE"
echo "" >> "$ANALYSIS_FILE"

# Berechne Gesamtaktivität
total_activity=$((CONTEXTUAL_THINKS + AGI_NEWS + MEMORY_FILES + BRIEFINGS))
echo "- **Gesamtaktivität:** $total_activity Einträge" >> "$ANALYSIS_FILE"
echo "" >> "$ANALYSIS_FILE"

# ============================================================
# 3. WACHSTUMS-TREND
# ============================================================
echo "## 3. Wachstums-Trend" >> "$ANALYSIS_FILE"
echo "" >> "$ANALYSIS_FILE"

# Prüfe Evolution-Log
if [ -f "$WORKSPACE/evolution.log" ]; then
    EVOLUTION_COUNT=$(grep -c "Evolution" "$WORKSPACE/evolution.log" 2>/dev/null || echo "0")
    echo "- **Evolution-Iterationen:** $EVOLUTION_COUNT" >> "$ANALYSIS_FILE"
else
    echo "- **Evolution-Iterationen:** Keine Daten" >> "$ANALYSIS_FILE"
fi

# Git-Commits zählen (falls verfügbar)
if [ -d "$WORKSPACE/.git" ]; then
    GIT_COMMITS=$(cd "$WORKSPACE" && git rev-list --count HEAD 2>/dev/null || echo "0")
    echo "- **Git-Commits:** $GIT_COMMITS" >> "$ANALYSIS_FILE"
fi
echo "" >> "$ANALYSIS_FILE"

# ============================================================
# 4. ZUKUNFTSVORHERSAGE
# ============================================================
echo "## 4. Zukunftsvorhersage" >> "$ANALYSIS_FILE"
echo "" >> "$ANALYSIS_FILE"

# Basierend auf aktuellen Mustern
if [ $total_activity -lt 10 ]; then
    GROWTH_STAGE="Frühe Phase - Aufbau"
    NEXT_ACTION="Fokus auf Konsistenz, tägliche Routinen etablieren"
elif [ $total_activity -lt 50 ]; then
    GROWTH_STAGE="Wachstumsphase - Expansion"
    NEXT_ACTION="Diversifizierung der Aktivitäten, Skills erweitern"
else
    GROWTH_STAGE="Etablierte Phase - Optimierung"
    NEXT_ACTION="Effizienz steigern, Muster automatisieren"
fi

echo "- **Wachstumsstufe:** $GROWTH_STAGE" >> "$ANALYSIS_FILE"
echo "- **Empfohlene nächste Aktion:** $NEXT_ACTION" >> "$ANALYSIS_FILE"
echo "" >> "$ANALYSIS_FILE"

# ============================================================
# 5. EMPFEHLUNGEN
# ============================================================
echo "## 5. Empfehlungen" >> "$ANALYSIS_FILE"
echo "" >> "$ANALYSIS_FILE"

# Dynamische Empfehlungen basierend auf Daten
if [ $CONTEXTUAL_THINKS -lt 5 ]; then
    echo "1. **Mehr kontextuelles Denken** - Die Fragen brauchen mehr Tiefe" >> "$ANALYSIS_FILE"
fi

if [ $AGI_NEWS -lt 3 ]; then
    echo "2. **AGI News häufiger sammeln** - Bleibe auf dem Laufenden" >> "$ANALYSIS_FILE"
fi

if [ $MEMORY_FILES -lt 2 ]; then
    echo "3. **Tägliche Memory-Einträge** - Kontinuität stärken" >> "$ANALYSIS_FILE"
fi

# Allgemeine Empfehlung basierend auf Tageszeit
case $TIME_PHASE in
    "Morgen (Aktivitätsphase)")
        echo "4. **Morgen-Empfehlung:** Starte mit einer klaren Intention" >> "$ANALYSIS_FILE"
        ;;
    "Nachmittag (Arbeitsphase)")
        echo "4. **Nachmittags-Empfehlung:** Fokus auf Umsetzung" >> "$ANALYSIS_FILE"
        ;;
    "Abend (Reflexionsphase)")
        echo "4. **Abend-Empfehlung:** Reflektiere den Tag, plane morgen" >> "$ANALYSIS_FILE"
        ;;
    "Nacht (Ruhephase)")
        echo "4. **Nacht-Empfehlung:** Ruhe dich aus, sammle Energie" >> "$ANALYSIS_FILE"
        ;;
esac

echo "" >> "$ANALYSIS_FILE"
echo "---" >> "$ANALYSIS_FILE"
echo "⚛️ Pattern Predictor v1.1 🗡️💚🔍" >> "$ANALYSIS_FILE"

echo ""
echo "✅ Analyse erstellt: $ANALYSIS_FILE"
echo ""
echo "Zusammenfassung:"
echo "  - Tagesphase: $TIME_PHASE"
echo "  - Gesamtaktivität: $total_activity Einträge"
echo "  - Wachstumsstufe: $GROWTH_STAGE"
echo ""
echo "⚛️ Pattern Predictor v1.1 🗡️💚🔍"
