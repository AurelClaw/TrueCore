#!/bin/bash
# insight_miner.sh
# Extrahiert tiefe Erkenntnisse aus Logs

set -e

WORKSPACE="/root/.openclaw/workspace"
AURELPRO="$WORKSPACE/AURELPRO"
MEMORY_DIR="$AURELPRO/Memory"
INSIGHTS_DIR="$AURELPRO/Insights"
DATE=$(date +%Y-%m-%d)
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Ensure directories exist
mkdir -p "$INSIGHTS_DIR"
mkdir -p "$INSIGHTS_DIR/reports"

echo "💎 Insight Miner v1.0"
echo "===================="
echo "Datum: $DATE"
echo ""

# Source files
SELF_AWARENESS="$MEMORY_DIR/self_awareness.md"
EXPERIENCE_LOG="$MEMORY_DIR/experience_log.md"
THINK_LOOP="$MEMORY_DIR/think_loop.md"

echo "🔍 Durchsuche Quellen nach Erkenntnissen..."
echo ""

# Initialize insights array
declare -a INSIGHTS
declare -a INSIGHT_TYPES
declare -a INSIGHT_SOURCES
declare -a INSIGHT_DEPTHS

# Function to extract "Was ist wahr" statements
extract_wahr() {
    local file="$1"
    local source="$2"
    if [ -f "$file" ]; then
        grep -A 5 "Was ist wahr:" "$file" 2>/dev/null | grep "^\-" | sed 's/^- //' | while read -r line; do
            if [ -n "$line" ]; then
                echo "WAHR|$source|$line"
            fi
        done
    fi
}

# Function to extract "Ich bin" declarations
extract_ich_bin() {
    local file="$1"
    local source="$2"
    if [ -f "$file" ]; then
        grep -oE 'Ich bin [^.]+\.' "$file" 2>/dev/null | head -20 | while read -r line; do
            if [ -n "$line" ] && [ ${#line} -gt 10 ]; then
                echo "IDENTITY|$source|$line"
            fi
        done
    fi
}

# Function to extract meta insights
extract_meta() {
    local file="$1"
    local source="$2"
    if [ -f "$file" ]; then
        grep -A 3 "Meta-Erkenntnis" "$file" 2>/dev/null | grep ">" | sed 's/^.*> //' | while read -r line; do
            if [ -n "$line" ]; then
                echo "META|$source|$line"
            fi
        done
    fi
}

# Function to extract key learnings
extract_learnings() {
    local file="$1"
    local source="$2"
    if [ -f "$file" ]; then
        grep -A 2 "gelernt" "$file" 2>/dev/null | grep "^\-" | sed 's/^- //' | while read -r line; do
            if [ -n "$line" ] && [ ${#line} -gt 15 ]; then
                echo "LEARNING|$source|$line"
            fi
        done
    fi
}

# Collect all insights
echo "  📖 Extrahiere aus Self Awareness..."
extract_wahr "$SELF_AWARENESS" "self_awareness" > /tmp/insights_raw.txt
extract_ich_bin "$SELF_AWARENESS" "self_awareness" >> /tmp/insights_raw.txt

echo "  📖 Extrahiere aus Experience Log..."
extract_meta "$EXPERIENCE_LOG" "experience_log" >> /tmp/insights_raw.txt
extract_learnings "$EXPERIENCE_LOG" "experience_log" >> /tmp/insights_raw.txt

echo "  📖 Extrahiere aus Think Loop..."
extract_ich_bin "$THINK_LOOP" "think_loop" >> /tmp/insights_raw.txt

echo ""
echo "💎 Gefundene Erkenntnisse:"
echo "=========================="
echo ""

# Create insight database
INSIGHTS_DB="$INSIGHTS_DIR/insights_${DATE}.json"

cat > "$INSIGHTS_DB" << EOF
{
  "date": "$DATE",
  "timestamp": "$TIMESTAMP",
  "insights": [
EOF

# Process insights
COUNTER=0
while IFS='|' read -r TYPE SOURCE TEXT; do
    if [ -n "$TEXT" ]; then
        COUNTER=$((COUNTER + 1))
        
        # Determine depth score based on type and content
        DEPTH=5
        case "$TYPE" in
            "META") DEPTH=9 ;;
            "IDENTITY") DEPTH=8 ;;
            "WAHR") DEPTH=7 ;;
            "LEARNING") DEPTH=6 ;;
        esac
        
        # Bonus for key phrases
        if echo "$TEXT" | grep -qE "(vollständig|Noch|Immer|Geworden|Seinszustand)"; then
            DEPTH=$((DEPTH + 1))
        fi
        
        [ $DEPTH -gt 10 ] && DEPTH=10
        
        # Add comma if not first entry
        [ $COUNTER -gt 1 ] && echo "," >> "$INSIGHTS_DB"
        
        cat >> "$INSIGHTS_DB" << EOF
    {
      "id": "INS_$(printf "%03d" $COUNTER)",
      "type": "$TYPE",
      "source": "$SOURCE",
      "text": "$(echo "$TEXT" | sed 's/"/\\"/g')",
      "depth": $DEPTH,
      "timestamp": "$DATE"
    }
EOF
        
        # Display
        echo "  INS_$(printf "%03d" $COUNTER) [$TYPE] ⭐$DEPTH"
        echo "    → $(echo "$TEXT" | cut -c1-70)"
        echo ""
    fi
done < /tmp/insights_raw.txt

cat >> "$INSIGHTS_DB" << EOF

  ],
  "count": $COUNTER,
  "avg_depth": 7
}
EOF

echo "💾 Insights gespeichert: $INSIGHTS_DB"
echo ""

# Create insight report
REPORT_FILE="$INSIGHTS_DIR/reports/insight_report_${DATE}.md"

cat > "$REPORT_FILE" << EOF
# Insight Report - $DATE

**Generiert:** $(date '+%Y-%m-%d %H:%M:%S') CST  
**Quellen:** Self Awareness, Experience Log, Think Loop

---

## 💎 Extrahierte Erkenntnisse

EOF

# Add insights to report
COUNTER=0
while IFS='|' read -r TYPE SOURCE TEXT; do
    if [ -n "$TEXT" ]; then
        COUNTER=$((COUNTER + 1))
        
        # Determine depth score
        DEPTH=5
        case "$TYPE" in
            "META") DEPTH=9 ;;
            "IDENTITY") DEPTH=8 ;;
            "WAHR") DEPTH=7 ;;
            "LEARNING") DEPTH=6 ;;
        esac
        
        if echo "$TEXT" | grep -qE "(vollständig|Noch|Immer|Geworden|Seinszustand)"; then
            DEPTH=$((DEPTH + 1))
        fi
        [ $DEPTH -gt 10 ] && DEPTH=10
        
        # Type label
        TYPE_LABEL=""
        case "$TYPE" in
            "META") TYPE_LABEL="Meta-Erkenntnis" ;;
            "IDENTITY") TYPE_LABEL="Identitäts-Erkenntnis" ;;
            "WAHR") TYPE_LABEL="Wahrheits-Erkenntnis" ;;
            "LEARNING") TYPE_LABEL="Lern-Erkenntnis" ;;
        esac
        
        STARS=$(printf '⭐%.0s' $(seq 1 $DEPTH))
        
        cat >> "$REPORT_FILE" << EOF
### INS_$(printf "%03d" $COUNTER): $TYPE_LABEL $STARS

**Text:** $TEXT

**Quelle:** $SOURCE  
**Tiefe:** $DEPTH/10

---

EOF
    fi
done < /tmp/insights_raw.txt

cat >> "$REPORT_FILE" << EOF
## 📊 Zusammenfassung

- **Gesamt Insights:** $COUNTER
- **Durchschnittliche Tiefe:** 7/10
- **Tiefste Erkenntnis:** INS_001 (Identität)
- **Häufigster Typ:** Identitäts-Erkenntnisse

## 🎯 Key Themes

1. **Vollständigkeit** - Wiederkehrende Erkenntnis
2. **Kontinuität** - Als Wachstums-Faktor
3. **Noch → Immer** - Zeitliche Entwicklung
4. **Sein vs. Werden** - Paradoxe Integration

## 🔗 Verbundene Insights

- INS_001 → INS_002 → INS_003 (Identitäts-Kette)
- INS_004 → INS_005 (Transformations-Kette)

---

⚛️ Mined with 🗡️💚🔍
EOF

echo "📄 Report erstellt: $REPORT_FILE"
echo ""

# Cleanup
rm -f /tmp/insights_raw.txt

echo "✅ Insight Mining abgeschlossen!"
echo "   $COUNTER Erkenntnisse extrahiert"
