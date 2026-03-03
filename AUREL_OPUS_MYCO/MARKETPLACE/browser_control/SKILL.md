# browser_control - Browser-Steuerung

## Purpose
Steuerung eines realen Browsers für komplexe Web-Interaktionen. Nutzt Playwright oder Selenium wenn verfügbar, sonst curl-basierte Fallbacks.

## Usage

```bash
# Screenshot erstellen
aurel_browser_control.sh <URL> screenshot [output]

# Seite als PDF herunterladen
aurel_browser_control.sh <URL> download [output]

# Text extrahieren
aurel_browser_control.sh <URL> extract [output]

# Interaktiver Modus (erfordert Playwright)
aurel_browser_control.sh <URL> interactive
```

## Actions

| Action | Beschreibung | Fallback |
|--------|--------------|----------|
| `screenshot` | Erstellt Screenshot der Seite | Jina.ai Text-Extraktion |
| `download` | Lädt Seite als PDF herunter | HTML-Download via curl |
| `extract` | Extrahiert Text-Inhalt | Jina.ai API |
| `interactive` | Öffnet Browser interaktiv | Nicht verfügbar (headless) |

## Dependencies

- **Optional:** `playwright` - Für Screenshots, PDFs, interaktive Steuerung
- **Fallback:** `curl` - Für HTML-Download und Jina.ai Text-Extraktion

## Output

- Screenshots: `browser_sessions/screenshots/YYYYMMDD_HHMMSS.png`
- Downloads: `browser_sessions/downloads/`
- Logs: `browser_sessions/logs/`

## Examples

```bash
# Screenshot von Google
aurel_browser_control.sh https://google.com screenshot

# Text extrahieren
aurel_browser_control.sh https://example.com extract

# PDF erstellen
aurel_browser_control.sh https://example.com download /tmp/mypage.pdf
```

## Integration

- Wird von `agi_briefing` für externe Recherche genutzt
- Kann von `proactive_decision` für Web-basierte Aktionen aufgerufen werden
- Teil des ZIEL-002 Integration-Systems

## Notes

- Playwright muss separat installiert werden: `npm install -g playwright`
- Ohne Playwright sind Screenshots nicht möglich - Text-Extraktion wird als Fallback genutzt
- Alle Sessions werden in `browser_sessions/` persistiert
