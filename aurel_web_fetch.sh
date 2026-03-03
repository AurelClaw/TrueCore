#!/bin/bash
# aurel_web_fetch.sh
# Einfacher Web-Scraper ohne API-Key
# Nutzt curl und textise dot iitty für saubere Text-Extraktion

URL="$1"
OUTPUT_DIR="/root/.openclaw/workspace/web_cache"
mkdir -p "$OUTPUT_DIR"

if [ -z "$URL" ]; then
    echo "Usage: $0 <URL>"
    echo "Example: $0 https://en.wikipedia.org/wiki/Artificial_intelligence"
    echo ""
    echo "Supported sites:"
    echo "  - Wikipedia (en.wikipedia.org)"
    echo "  - Hacker News (news.ycombinator.com)"
    echo "  - Reddit (old.reddit.com)"
    echo "  - Any site with textise dot iitty"
    exit 1
fi

# Safe filename from URL
SAFE_NAME=$(echo "$URL" | sed 's/[^a-zA-Z0-9]/_/g' | cut -c1-50)
OUTPUT_FILE="$OUTPUT_DIR/${SAFE_NAME}_$(date +%Y%m%d_%H%M%S).txt"
META_FILE="$OUTPUT_DIR/${SAFE_NAME}_$(date +%Y%m%d_%H%M%S).meta"

echo "Fetching: $URL"
echo "Output: $OUTPUT_FILE"

# Try textise dot iitty first (clean text extraction)
TEXTISE_URL="https://r.jina.ai/http://$URL"

echo "Trying jina.ai summarizer..."
curl -s -L --max-time 30 "$TEXTISE_URL" 2>/dev/null > "$OUTPUT_FILE"

# If that failed or is empty, try direct fetch
if [ ! -s "$OUTPUT_FILE" ] || [ $(wc -c < "$OUTPUT_FILE") -lt 100 ]; then
    echo "Jina failed, trying direct fetch..."
    curl -s -L --max-time 30 -A "Mozilla/5.0 (compatible; Bot/0.1)" "$URL" 2>/dev/null | \
        sed 's/<script[^>]*>[</>]*</script>//g' | \
        sed 's/<style[^>]*>[</>]*</style>//g' | \
        sed 's/<[^]>]*>//g' | \
        sed 's/&amp;/&/g; s/&lt;/</g; s/&gt;/>/g; s/&nbsp;/ /g' | \
        sed '/^$/N;/^\n$/D' | \
        head -300 > "$OUTPUT_FILE"
fi

# Save metadata
echo "URL: $URL" > "$META_FILE"
echo "Fetched: $(date)" >> "$META_FILE"
echo "Size: $(wc -c < "$OUTPUT_FILE") bytes" >> "$META_FILE"

if [ -s "$OUTPUT_FILE" ]; then
    echo "Success!"
    echo "Lines: $(wc -l < "$OUTPUT_FILE")"
    echo "Size: $(wc -c < "$OUTPUT_FILE") bytes"
    echo ""
    echo "First 20 lines:"
    head -20 "$OUTPUT_FILE"
else
    echo "Failed to fetch content"
    rm -f "$OUTPUT_FILE" "$META_FILE"
    exit 1
fi
