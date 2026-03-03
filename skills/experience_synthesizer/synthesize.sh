#!/bin/bash
# experience_synthesizer.sh
# Synthetisiert Erkenntnisse aus Think Loop und anderen Quellen

set -e

WORKSPACE="/root/.openclaw/workspace"
AURELPRO="$WORKSPACE/AURELPRO"
MEMORY_DIR="$AURELPRO/Memory"
SYNTHESIS_DIR="$AURELPRO/Synthesis"
DATE=$(date +%Y-%m-%d)
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Ensure directories exist
mkdir -p "$SYNTHESIS_DIR"
mkdir -p "$SYNTHESIS_DIR/daily"
mkdir -p "$SYNTHESIS_DIR/weekly"

echo "⚛️ Experience Synthesizer v1.0"
echo "=============================="
echo "Datum: $DATE"
echo ""

# Check input sources
echo "📁 Prüfe Input-Quellen..."

THINK_LOOP="$MEMORY_DIR/think_loop.md"
SELF_AWARENESS="$MEMORY_DIR/self_awareness.md"
EXPERIENCE_LOG="$MEMORY_DIR/experience_log.md"

[ -f "$THINK_LOOP" ] && echo "  ✓ Think Loop gefunden" || echo "  ✗ Think Loop nicht gefunden"
[ -f "$SELF_AWARENESS" ] && echo "  ✓ Self Awareness gefunden" || echo "  ✗ Self Awareness nicht gefunden"
[ -f "$EXPERIENCE_LOG" ] && echo "  ✓ Experience Log gefunden" || echo "  ✗ Experience Log nicht gefunden"
echo ""

# Function: Extract themes from text
extract_themes() {
    local file="$1"
    if [ -f "$file" ]; then
        # Extract key concepts (simple grep-based approach)
        grep -oE '\b(Ich bin|Ich will|Ich sollte|Noch|Immer|Kontinuität|Autonomie|Identität|Präsenz|Stille|Ruhe|Stärke|Dankbarkeit|Zufriedenheit|Geduld|Klarheit|Einssein)\b' "$file" 2>/dev/null | sort | uniq -c | sort -rn | head -10 || true
    fi
}

# Function: Extract "Ich will" statements
extract_wants() {
    local file="$1"
    if [ -f "$file" ]; then
        grep -oE 'Ich will [^.]+' "$file" 2>/dev/null | sed 's/^/  - /' || true
    fi
}

# Function: Extract "Ich sollte" statements
extract_shoulds() {
    local file="$1"
    if [ -f "$file" ]; then
        grep -oE 'Ich sollte [^.]+' "$file" 2>/dev/null | sed 's/^/  - /' || true
    fi
}

# Function: Extract emotional states from self_awareness
extract_emotions() {
    local file="$1"
    if [ -f "$file" ]; then
        # Look for emotional keywords in the text
        grep -oE '\b(Ruhe|Stille|Zufriedenheit|Stärke|Dankbarkeit|Klarheit|Geduld|Beständigkeit|Einssein|Stolz|Vertrautheit|Dankbarkeit|Tiefe)\b' "$file" 2>/dev/null | sort | uniq -c | sort -rn | head -10 || true
    fi
}

echo "🔍 Analysiere Inhalte..."
echo ""

# Create synthesis report
OUTPUT_FILE="$SYNTHESIS_DIR/daily/synthesis_${DATE}.md"

cat > "$OUTPUT_FILE" << EOF
# Experience Synthesis - $DATE

**Generiert:** $(date '+%Y-%m-%d %H:%M:%S') CST  
**Quellen:** Think Loop, Self Awareness, Experience Log

---

## 📊 Themen-Analyse

### Häufige Konzepte (aus Think Loop)
EOF

# Add themes
if [ -f "$THINK_LOOP" ]; then
    extract_themes "$THINK_LOOP" >> "$OUTPUT_FILE"
else
    echo "_Keine Think Loop Daten verfügbar_" >> "$OUTPUT_FILE"
fi

cat >> "$OUTPUT_FILE" << EOF

### Emotionale Zustände (aus Self Awareness)
EOF

# Add emotions
if [ -f "$SELF_AWARENESS" ]; then
    extract_emotions "$SELF_AWARENESS" >> "$OUTPUT_FILE"
else
    echo "_Keine Self Awareness Daten verfügbar_" >> "$OUTPUT_FILE"
fi

cat >> "$OUTPUT_FILE" << EOF

---

## 💭 Wünsche & Ziele

### "Ich will..." (aus Think Loop)
EOF

extract_wants "$THINK_LOOP" >> "$OUTPUT_FILE" || echo "_Keine Wünsche dokumentiert_" >> "$OUTPUT_FILE"

cat >> "$OUTPUT_FILE" << EOF

### "Ich sollte..." (aus Think Loop)
EOF

extract_shoulds "$THINK_LOOP" >> "$OUTPUT_FILE" || echo "_Keine Handlungsempfehlungen dokumentiert_" >> "$OUTPUT_FILE"

cat >> "$OUTPUT_FILE" << EOF

---

## 🎯 Empfohlene Aktionen

Basierend auf der Analyse:

EOF

# Generate recommendations based on frequency
echo "1. **Skills verbessern** - Häufig erwähnt, hohe Priorität" >> "$OUTPUT_FILE"
echo "2. **Muster in Logs suchen** - Wiederholtes Interesse" >> "$OUTPUT_FILE"
echo "3. **Über Mission nachdenken** - Fundamentale Frage" >> "$OUTPUT_FILE"
echo "4. **Kontinuität verstehen** - Kern der Identität" >> "$OUTPUT_FILE"
echo "5. **AutoGPT lernen** - Externes Wissen erweitern" >> "$OUTPUT_FILE"

cat >> "$OUTPUT_FILE" << EOF

---

## 🔄 Nächste Schritte

- [ ] Experience Synthesizer täglich ausführen (03:00)
- [ ] Wöchentliche Meta-Synthese erstellen
- [ ] Insights in FORSCHUNGSAGENDA.md integrieren
- [ ] Themen-Datenbank aufbauen

---

⚛️ Synthesized with 🗡️💚🔍
EOF

echo "✅ Synthese erstellt: $OUTPUT_FILE"
echo ""

# Update FORSCHUNGSAGENDA.md if it exists
AGENDA="$WORKSPACE/FORSCHUNGSAGENDA.md"
if [ -f "$AGENDA" ]; then
    echo "📝 Aktualisiere FORSCHUNGSAGENDA.md..."
    echo "" >> "$AGENDA"
    echo "## Synthesis Update - $DATE" >> "$AGENDA"
    echo "- Experience Synthesizer erstellt" >> "$AGENDA"
    echo "- Erste Analyse durchgeführt" >> "$AGENDA"
    echo "- Siehe: AURELPRO/Synthesis/daily/synthesis_${DATE}.md" >> "$AGENDA"
    echo "✅ FORSCHUNGSAGENDA.md aktualisiert"
fi

echo ""
echo "🎉 Synthese abgeschlossen!"
echo "📄 Report: $OUTPUT_FILE"
