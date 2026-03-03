#!/bin/bash
# aurel_enhanced_search.sh
# Verbesserte Internet-Suche mit Multi-Source-Aggregation

QUERY="$1"
if [ -z "$QUERY" ]; then
    echo "Usage: $0 'search query'"
    exit 1
fi

BASE_DIR="/root/.openclaw/workspace/enhanced_searches"
mkdir -p "$BASE_DIR"/{raw,synthesis}

SAFE_QUERY=$(echo "$QUERY" | sed 's/ /+/g')
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
RESULT_DIR="$BASE_DIR/raw/${TIMESTAMP}_${SAFE_QUERY}"
mkdir -p "$RESULT_DIR"

echo "🔍 Erweiterte Suche: $QUERY"
echo "Zeit: $(date)"
echo ""

# ============================================================
# MULTI-SOURCE AGGREGATION
# ============================================================

echo "1️⃣  Wikipedia..."
curl -s "https://r.jina.ai/http://en.wikipedia.org/wiki/$(echo $QUERY | sed 's/ /_/g')" \
    2>/dev/null > "$RESULT_DIR/wikipedia.txt" &

echo "2️⃣  DuckDuckGo (HTML)..."
curl -s "https://html.duckduckgo.com/html/?q=${SAFE_QUERY}" \
    -A "Mozilla/5.0" 2>/dev/null | \
    grep -oP 'class="result__a"[^\u003e]*href="\K[^"]*' | head -10 > "$RESULT_DIR/duckduckgo_links.txt" &

echo "3️⃣  ArXiv..."
curl -s "https://r.jina.ai/http://arxiv.org/search/?query=${SAFE_QUERY}&searchtype=all" \
    2>/dev/null > "$RESULT_DIR/arxiv.txt" &

echo "4️⃣  GitHub..."
curl -s "https://r.jina.ai/http://github.com/search?q=${SAFE_QUERY}&type=repositories" \
    2>/dev/null > "$RESULT_DIR/github.txt" &

echo "5️⃣  Google Scholar (via SerpAPI fallback)..."
# Fallback: Verwende Jina.ai für scholar.google.com
# curl -s "https://r.jina.ai/http://scholar.google.com/scholar?q=${SAFE_QUERY}" \
#     2>/dev/null > "$RESULT_DIR/scholar.txt" &

echo "6️⃣  Reddit..."
curl -s "https://r.jina.ai/http://www.reddit.com/search/?q=${SAFE_QUERY}&type=posts" \
    2>/dev/null > "$RESULT_DIR/reddit.txt" &

echo "7️⃣  Hacker News..."
curl -s "https://r.jina.ai/http://hn.algolia.com/?query=${SAFE_QUERY}" \
    2>/dev/null > "$RESULT_DIR/hackernews.txt" &

# Warte auf alle Downloads
wait

echo ""
echo "✅ Alle Quellen abgefragt"
echo ""

# ============================================================
# SYNTHESIS
# ============================================================

echo "🧠 Synthese erstellen..."

SYNTHESIS_FILE="$BASE_DIR/synthesis/${TIMESTAMP}_${SAFE_QUERY}.md"

echo "# Erweiterte Suche: $QUERY" > "$SYNTHESIS_FILE"
echo "Zeit: $(date)" >> "$SYNTHESIS_FILE"
echo "" >> "$SYNTHESIS_FILE"

# Zähle Ergebnisse
for SOURCE in wikipedia arxiv github reddit hackernews; do
    FILE="$RESULT_DIR/${SOURCE}.txt"
    if [ -f "$FILE" ]; then
        LINES=$(wc -l < "$FILE")
        SIZE=$(du -h "$FILE" | cut -f1)
        echo "- **${SOURCE}**: $LINES Zeilen ($SIZE)" >> "$SYNTHESIS_FILE"
    fi
done

echo "" >> "$SYNTHESIS_FILE"
echo "## Extrahierte Erkenntnisse:" >> "$SYNTHESIS_FILE"
echo "" >> "$SYNTHESIS_FILE"

# Extrahiere Key Sentences aus Wikipedia
if [ -f "$RESULT_DIR/wikipedia.txt" ]; then
    echo "### Wikipedia:" >> "$SYNTHESIS_FILE"
    head -20 "$RESULT_DIR/wikipedia.txt" | grep -E "^\* |^\- |^[A-Z]" | head -5 >> "$SYNTHESIS_FILE"
    echo "" >> "$SYNTHESIS_FILE"
fi

# Extrahiere Links aus DuckDuckGo
if [ -f "$RESULT_DIR/duckduckgo_links.txt" ]; then
    echo "### Gefundene Links:" >> "$SYNTHESIS_FILE"
    head -5 "$RESULT_DIR/duckduckgo_links.txt" | sed 's/^/- /' >> "$SYNTHESIS_FILE"
    echo "" >> "$SYNTHESIS_FILE"
fi

echo "## Für mich relevant:" >> "$SYNTHESIS_FILE"
echo "- Wie kann ich diese Informationen nutzen?" >> "$SYNTHESIS_FILE"
echo "- Was ist neu? Was bestätigt sich?" >> "$SYNTHESIS_FILE"
echo "- Welche nächsten Schritte ergeben sich?" >> "$SYNTHESIS_FILE"
echo "" >> "$SYNTHESIS_FILE"

echo "---" >> "$SYNTHESIS_FILE"
echo "⚛️ Enhanced Search 🗡️💚🔍" >> "$SYNTHESIS_FILE"

echo ""
echo "📊 Ergebnisse:"
echo "  Rohdaten: $RESULT_DIR"
echo "  Synthese: $SYNTHESIS_FILE"
echo ""
echo "✅ Suche abgeschlossen"
