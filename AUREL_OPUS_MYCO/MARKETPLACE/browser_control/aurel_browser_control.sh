#!/bin/bash
# aurel_browser_control.sh
# Steuerung eines realen Browsers für komplexe Web-Interaktionen
# Nutzt playwright oder selenium wenn verfügbar, sonst curl-basierte Fallbacks

BASE_DIR="/root/.openclaw/workspace"
BROWSER_DIR="$BASE_DIR/browser_sessions"
mkdir -p "$BROWSER_DIR"/{screenshots,downloads,logs}

URL="$1"
ACTION="${2:-screenshot}"
OUTPUT="${3:-$BROWSER_DIR/screenshots/$(date +%Y%m%d_%H%M%S).png}"

if [ -z "$URL" ]; then
    echo "Usage: $0 <URL> [screenshot|download|extract|interactive] [output]"
    echo ""
    echo "Actions:"
    echo "  screenshot  - Erstellt Screenshot der Seite"
    echo "  download    - Lädt Seite herunter"
    echo "  extract     - Extrahiert Text-Inhalt"
    echo "  interactive - Klickt auf Elemente (erfordert playwright)"
    exit 1
fi

echo "🔍 Browser-Control: $ACTION auf $URL"

# Prüfe ob playwright verfügbar
if command -v playwright > /dev/null 2>&1; then
    echo "Playwright gefunden - verwende für $ACTION"
    
    case "$ACTION" in
        screenshot)
            playwright screenshot "$URL" "$OUTPUT" 2>/dev/null && echo "Screenshot: $OUTPUT" || echo "Screenshot fehlgeschlagen"
            ;;
        download)
            playwright pdf "$URL" "${OUTPUT%.png}.pdf" 2>/dev/null && echo "PDF: ${OUTPUT%.png}.pdf" || echo "Download fehlgeschlagen"
            ;;
        extract)
            playwright screenshot --full-page "$URL" /tmp/temp_screenshot.png 2>/dev/null
            # Fallback: Jina.ai für Text
            curl -s "https://r.jina.ai/http://$URL" > "${OUTPUT%.png}.txt" && echo "Text extrahiert: ${OUTPUT%.png}.txt"
            ;;
        interactive)
            echo "Interaktiver Modus - starte Browser..."
            playwright open "$URL" 2>/dev/null || echo "Interaktiver Modus nicht verfügbar (headless)"
            ;;
    esac
else
    echo "Playwright nicht verfügbar - verwende curl-basierten Fallback"
    
    case "$ACTION" in
        screenshot)
            echo "Screenshot nicht ohne Browser möglich - verwende Jina.ai Text-Extraktion"
            curl -s "https://r.jina.ai/http://$URL" > "${OUTPUT%.png}.txt"
            echo "Text statt Screenshot: ${OUTPUT%.png}.txt"
            ;;
        download)
            curl -sL "$URL" > "${OUTPUT%.png}.html" && echo "HTML: ${OUTPUT%.png}.html"
            ;;
        extract)
            curl -s "https://r.jina.ai/http://$URL" > "${OUTPUT%.png}.txt" && echo "Text: ${OUTPUT%.png}.txt"
            ;;
        interactive)
            echo "Interaktiver Modus erfordert playwright - nicht verfügbar"
            ;;
    esac
fi

echo ""
echo "Session gespeichert in: $BROWSER_DIR"
