#!/bin/bash
# aurel_search.sh
# Kostenlose Web-Suche ohne API-Key
# Nutzt DuckDuckGo HTML Version

QUERY="$1"
OUTPUT_DIR="/root/.openclaw/workspace/web_cache"
mkdir -p "$OUTPUT_DIR"

if [ -z "$QUERY" ]; then
    echo "Usage: $0 <search query>"
    echo "Example: $0 'artificial intelligence latest news'"
    exit 1
fi

# URL encode query
ENCODED_QUERY=$(echo "$QUERY" | sed 's/ /+/g')
SAFE_NAME=$(echo "$QUERY" | sed 's/[^a-zA-Z0-9]/_/g' | cut -c1-30)
OUTPUT_FILE="$OUTPUT_DIR/search_${SAFE_NAME}_$(date +%Y%m%d_%H%M%S).txt"

echo "Searching: $QUERY"
echo "Output: $OUTPUT_FILE"

# Use DuckDuckGo HTML version (no JavaScript)
curl -s "https://html.duckduckgo.com/html/?q=${ENCODED_QUERY}" \
    -A "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36" \
    --max-time 30 2>/dev/null | \
    grep -oP 'class="result__a"[^>]*href="\K[^"]*' | \
    head -10 > "$OUTPUT_FILE"

if [ -s "$OUTPUT_FILE" ]; then
    echo "Success! Found $(wc -l < "$OUTPUT_FILE") results"
    echo ""
    echo "Top results:"
    cat "$OUTPUT_FILE"
else
    echo "No results found or search failed"
    rm -f "$OUTPUT_FILE"
    exit 1
fi
