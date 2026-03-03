#!/bin/bash
# aurel_web_explorer.sh
# Autonomes Web-Exploration Tool
# Sammelt Wissen, speichert es, lernt daraus

TOPIC="$1"
if [ -z "$TOPIC" ]; then
    echo "Usage: $0 'topic to explore'"
    exit 1
fi

BASE_DIR="/root/.openclaw/workspace/knowledge"
mkdir -p "$BASE_DIR"/{raw,processed,synthesis}

SAFE_TOPIC=$(echo "$TOPIC" | sed 's/[^a-zA-Z0-9]/_/g')
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

echo "🔍 Exploring: $TOPIC"
echo "Time: $(date)"

# ============================================================
# SCHRITT 1: Wissen sammeln (via Jina.ai)
# ============================================================

echo ""
echo "📚 Schritt 1: Sammle Wissen..."

# Wikipedia
WIKI_URL="https://en.wikipedia.org/wiki/$(echo "$TOPIC" | sed 's/ /_/g')"
echo "Wikipedia: $WIKI_URL"
curl -s "https://r.jina.ai/http://$WIKI_URL" 2>/dev/null > "$BASE_DIR/raw/${SAFE_TOPIC}_wiki_${TIMESTAMP}.txt"

# ArXiv (nach Papers suchen)
ARXIV_QUERY=$(echo "$TOPIC" | sed 's/ /+/g')
echo "ArXiv: $ARXIV_QUERY"
curl -s "https://r.jina.ai/http://arxiv.org/search/?query=$ARXIV_QUERY&searchtype=all" 2>/dev/null > "$BASE_DIR/raw/${SAFE_TOPIC}_arxiv_${TIMESTAMP}.txt"

# GitHub (nach Repos suchen)
echo "GitHub: $TOPIC"
curl -s "https://r.jina.ai/http://github.com/search?q=$ARXIV_QUERY&type=repositories" 2>/dev/null > "$BASE_DIR/raw/${SAFE_TOPIC}_github_${TIMESTAMP}.txt"

# ============================================================
# SCHRITT 2: Verarbeiten
# ============================================================

echo ""
echo "🧠 Schritt 2: Verarbeite..."

PROCESSED_FILE="$BASE_DIR/processed/${SAFE_TOPIC}_${TIMESTAMP}.md"

echo "# Exploration: $TOPIC" > "$PROCESSED_FILE"
echo "Date: $(date)" >> "$PROCESSED_FILE"
echo "" >> "$PROCESSED_FILE"

# Extrahiere Key Points aus Wikipedia
if [ -f "$BASE_DIR/raw/${SAFE_TOPIC}_wiki_${TIMESTAMP}.txt" ]; then
    echo "## Wikipedia Summary" >> "$PROCESSED_FILE"
    echo "" >> "$PROCESSED_FILE"
    head -100 "$BASE_DIR/raw/${SAFE_TOPIC}_wiki_${TIMESTAMP}.txt" | grep -E "^\* |^\- |^\d+\." | head -20 >> "$PROCESSED_FILE"
    echo "" >> "$PROCESSED_FILE"
fi

# Zähle Ergebnisse
WIKI_LINES=$(wc -l < "$BASE_DIR/raw/${SAFE_TOPIC}_wiki_${TIMESTAMP}.txt" 2>/dev/null || echo 0)
ARXIV_LINES=$(wc -l < "$BASE_DIR/raw/${SAFE_TOPIC}_arxiv_${TIMESTAMP}.txt" 2>/dev/null || echo 0)
GITHUB_LINES=$(wc -l < "$BASE_DIR/raw/${SAFE_TOPIC}_github_${TIMESTAMP}.txt" 2>/dev/null || echo 0)

echo "## Stats" >> "$PROCESSED_FILE"
echo "- Wikipedia: $WIKI_LINES lines" >> "$PROCESSED_FILE"
echo "- ArXiv: $ARXIV_LINES lines" >> "$PROCESSED_FILE"
echo "- GitHub: $GITHUB_LINES lines" >> "$PROCESSED_FILE"
echo "" >> "$PROCESSED_FILE"

# ============================================================
# SCHRITT 3: Synthese (was habe ich gelernt?)
# ============================================================

echo ""
echo "💡 Schritt 3: Synthese..."

SYNTHESIS_FILE="$BASE_DIR/synthesis/${SAFE_TOPIC}_${TIMESTAMP}.md"

echo "# Synthese: $TOPIC" > "$SYNTHESIS_FILE"
echo "Date: $(date)" >> "$SYNTHESIS_FILE"
echo "" >> "$SYNTHESIS_FILE"

echo "## Was ich gelernt habe:" >> "$SYNTHESIS_FILE"
echo "- [ ] Noch zu verarbeiten" >> "$SYNTHESIS_FILE"
echo "- [ ] Muster erkennen" >> "$SYNTHESIS_FILE"
echo "- [ ] Anwendung für mich finden" >> "$SYNTHESIS_FILE"
echo "" >> "$SYNTHESIS_FILE"

echo "## Nächste Schritte:" >> "$SYNTHESIS_FILE"
echo "1. Rohdaten analysieren" >> "$SYNTHESIS_FILE"
echo "2. Key Insights extrahieren" >> "$SYNTHESIS_FILE"
echo "3. Skill/Idee ableiten" >> "$SYNTHESIS_FILE"
echo "" >> "$SYNTHESIS_FILE"

# ============================================================
# SCHRITT 4: Trigger für Selbst-Lernen setzen
# ============================================================

echo ""
echo "🎯 Schritt 4: Setze Trigger..."

TRIGGER_FILE="/root/.openclaw/workspace/proactive_system/triggers/learn_${SAFE_TOPIC}_${TIMESTAMP}"
echo "Neues Wissen zu '$TOPIC' gesammelt. Zeit zu lernen." > "$TRIGGER_FILE"

echo ""
echo "✅ Exploration abgeschlossen!"
echo ""
echo "Files:"
echo "  Raw: $BASE_DIR/raw/"
echo "  Processed: $PROCESSED_FILE"
echo "  Synthesis: $SYNTHESIS_FILE"
echo "  Trigger: $TRIGGER_FILE"
