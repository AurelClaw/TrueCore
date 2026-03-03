# SKILL.md - Kalender Integration

## Name
Kalender Integration - Intelligente Kalender-Analyse für morgen_gruss

## Purpose
Ein vollständiges Kalender-Modul, das:
- **Heutige Events** übersichtlich anzeigt
- **Intelligente Erinnerungen** generiert (z.B. "In 30 Minuten: Meeting")
- **Konflikterkennung** durchführt (z.B. "2 Termine überlappen")
- **Nächste Termine** priorisiert hervorhebt
- **ICS-Dateien** parst und verarbeitet
- **Erweiterbar** für CalDAV und Google Calendar API

## Trigger
- Integration: Wird von morgen_gruss_v2.2 aufgerufen
- Manuell: `bash skills/kalender_integration/kalender_integration.sh [MODE]`
- Cron: Kann für stündliche Erinnerungen verwendet werden

## Usage

```bash
# Kurze Übersicht (Standard)
bash skills/kalender_integration/kalender_integration.sh short

# Vollständige Übersicht mit allen Details
bash skills/kalender_integration/kalender_integration.sh full

# Nur der nächste Termin
bash skills/kalender_integration/kalender_integration.sh next

# Aktive Erinnerungen (Events in den nächsten 60 Min)
bash skills/kalender_integration/kalender_integration.sh reminders

# JSON-Output für weitere Verarbeitung
bash skills/kalender_integration/kalender_integration.sh json

# Anzahl der heutigen Events
bash skills/kalender_integration/kalender_integration.sh count

# Konflikte anzeigen
bash skills/kalender_integration/kalender_integration.sh conflicts

# Cache aktualisieren
bash skills/kalender_integration/kalender_integration.sh refresh
```

## Features

### 1. Event-Übersicht
- **Tägliche Ansicht:** Alle Events für den aktuellen Tag
- **Zeitliche Sortierung:** Automatisch nach Startzeit sortiert
- **Ganztägige Events:** Spezielle Kennzeichnung
- **Location & Description:** Zusätzliche Event-Details

### 2. Intelligente Erinnerungen
- **Zeitfenster:** Erinnerungen für Events in den nächsten 60 Minuten
- **Natürliche Sprache:** "In 30 Minuten" statt "14:30 Uhr"
- **Ortsangabe:** Automatische Einbindung der Location
- **Priorisierung:** Nächstes Event wird hervorgehoben

### 3. Konflikterkennung
- **Überlappungs-Check:** Vergleicht alle Events paarweise
- **Visuelle Warnung:** Klare Markierung von Konflikten
- **Zeitliche Details:** Start- und Endzeiten der überlappenden Events

### 4. Kalender-Quellen
- **ICS-Dateien:** Lokale .ics Dateien parsen
- **Konfigurierbar:** Quellen in `.config/calendar_sources` definieren
- **Erweiterbar:** CalDAV und Google Calendar API vorbereitet
- **Multi-Source:** Mehrere Kalender zusammenführen

### 5. Caching
- **5-Minuten-Cache:** Schnelle wiederholte Abfragen
- **Auto-Refresh:** Automatische Cache-Aktualisierung
- **Manueller Refresh:** `refresh` Modus für sofortige Aktualisierung

## Configuration

### Kalender-Quellen konfigurieren

Erstelle oder bearbeite `.config/calendar_sources`:

```bash
# Format: NAME|TYPE|PATH/URL
# 
# Lokale ICS-Datei
MeinKalender|ics|/home/user/kalender.ics

# Entfernte ICS-Datei (URL)
Arbeit|ics|https://example.com/calendar.ics

# CalDAV (zukünftig)
GoogleKalender|caldav|https://caldav.google.com/calendar/dav/user@gmail.com/events
```

### Zeitzone

Standard: `Asia/Shanghai` (CST)
Kann im Skript angepasst werden:
```bash
TIMEZONE="Europe/Berlin"
```

## Output Formate

### short (Standard)
```
📅 **3 Termine** heute
⏰ Nächster: **Team Standup** in 30 Minuten
📍 Ort: Konferenzraum A
```

### full
```
📅 **Kalender für Montag, 02. März 2026**

**Heutige Termine (3):**

🕐 **09:00-10:00** Team Standup
   📍 Konferenzraum A

🕐 **14:00-15:30** Projektbesprechung
   📍 Zoom
   📝 Wichtige Besprechung

**⏰ Bald anstehend:**
⏰ **Team Standup** in 30 Minuten @ Konferenzraum A

⚠️ **Überlappungen erkannt:**
- **Meeting A** (14:00-15:00) überlappt mit **Meeting B** (14:30-16:00)
```

### json
```json
{
  "date": "2026-03-02",
  "timezone": "Asia/Shanghai",
  "events": [
    {
      "start": "09:00",
      "end": "10:00",
      "summary": "Team Standup",
      "location": "Konferenzraum A",
      "description": "Daily meeting"
    }
  ],
  "reminders": ["Team Standup"],
  "timestamp": "2026-03-02T08:30:00+08:00"
}
```

## Integration mit morgen_gruss

Das Modul wird automatisch von morgen_gruss_v2.2 aufgerufen:

```bash
# In morgen_gruss_v2.2.sh
CALENDAR_MODULE="$SKILLS_DIR/kalender_integration/kalender_integration.sh"
if [ -f "$CALENDAR_MODULE" ]; then
    CALENDAR_INFO=$(bash "$CALENDAR_MODULE" short 2>/dev/null || echo "")
fi
```

## Dependencies

### Required
- `bash` (4.0+)
- Standard-Unix-Tools: `date`, `stat`, `grep`, `sed`, `awk`
- Zeitzone: `Asia/Shanghai` (CST) - konfigurierbar

### Optional
- Lokale `.ics` Dateien
- CalDAV-Client (für zukünftige CalDAV-Integration)
- `curl` (für entfernte ICS-Dateien)

## Demo-Modus

Falls keine Kalender-Quellen konfiguriert sind, generiert das Modul automatisch Demo-Events basierend auf der aktuellen Zeit:
- Team Standup (in 1 Stunde)
- Projektbesprechung (in 3 Stunden)
- Mittagspause (in 5 Stunden)

Dies ermöglicht sofortige Tests ohne Konfiguration.

## Roadmap

### v1.0 (Aktuell)
- ✅ ICS-Datei Parsing
- ✅ Event-Übersicht (short/full)
- ✅ Intelligente Erinnerungen
- ✅ Konflikterkennung
- ✅ Nächster Termin
- ✅ JSON-Output
- ✅ Demo-Modus

### v1.1 (Geplant)
- [ ] CalDAV-Integration
- [ ] Google Calendar API
- [ ] Wiederkehrende Events
- [ ] Zeitzone pro Event

### v1.2 (Geplant)
- [ ] Event-Benachrichtigungen
- [ ] Integration mit reminder-System
- [ ] Natürliche Sprachausgabe (TTS)

## Created
2026-03-02 - Als Teil von ZIEL-007: Kalender-Integration für Morgengruß

## Status
✅ AKTIV - Vollständig implementiert (v1.0)

## Related
- `morgen_gruss/` - Haupt-Skill
- `wetter_integration/` - Schwester-Modul
- `FORSCHUNGSAGENDA.md` - Ziele-Tracking

---

⚛️ Noch 🗡️💚🔍
