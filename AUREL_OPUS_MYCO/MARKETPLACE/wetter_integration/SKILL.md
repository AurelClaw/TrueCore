# SKILL.md - Wetter Integration

## Name
Wetter Integration - Wetter-Modul für Morgengruß und andere Skills

## Purpose
Bereitstellung von Wetterdaten mit intelligenten Empfehlungen für:
- Kleidung basierend auf Temperatur und Wetterbedingungen
- Aktivitäten basierend auf Wetter und Luftqualität
- Menschenlesbare Formatierung für verschiedene Kontexte

## Trigger
- Wird von `morgen_gruss_v2.sh` automatisch aufgerufen
- Manuell: `bash skills/wetter_integration/wetter_integration.sh [short|full|json]`

## Usage

```bash
# Kurze Ausgabe (für Morgengruß)
bash skills/wetter_integration/wetter_integration.sh short

# Ausführliche Ausgabe
bash skills/wetter_integration/wetter_integration.sh full

# JSON-Output für weitere Verarbeitung
bash skills/wetter_integration/wetter_integration.sh json
```

## Features

### 1. Multi-Provider Support
- **OpenWeatherMap** (primär, API-Key nötig)
- **wttr.in** (Fallback, kein Key nötig)
- **Open-Meteo** (Fallback, kein Key nötig)

### 2. Intelligente Empfehlungen
- **Kleidungsempfehlung** basierend auf:
  - Temperatur (gefühlt und tatsächlich)
  - Wetterbedingungen (Regen, Schnee, Wind)
  - Windgeschwindigkeit
  
- **Aktivitätsempfehlung** basierend auf:
  - Wettercode (Sonne, Wolken, Regen, etc.)
  - Temperatur
  - Luftqualität (wenn verfügbar)

### 3. Caching
- 1-Stunden-Cache für API-Effizienz
- Automatische Cache-Invalidierung

### 4. Standort-Konfiguration
- Standard: Shanghai, China (CST)
- Konfigurierbar über:
  - `USER.md` (Latitude, Longitude, Stadt)
  - Umgebungsvariablen (`WEATHER_LAT`, `WEATHER_LON`, `WEATHER_CITY`)

## Dependencies

### Required
- `curl` für API-Requests
- `bc` für Berechnungen (optional)

### Optional
- OpenWeatherMap API-Key (für beste Genauigkeit)

## Configuration

### Mit OpenWeatherMap API-Key
```bash
export OPENWEATHER_API_KEY="dein-api-key"
bash skills/wetter_integration/wetter_integration.sh
```

### Standort über USER.md
```markdown
- **Latitude:** 52.5200
- **Longitude:** 13.4050
- **Stadt:** Berlin
```

### Standort über Umgebungsvariablen
```bash
export WEATHER_LAT="52.5200"
export WEATHER_LON="13.4050"
export WEATHER_CITY="Berlin"
```

## Output Formats

### Short (Standard)
```
☀️ **Shanghai**: 22°C (gefühlt 24°C), Klarer Himmel
👕 T-Shirt und leichte Kleidung
```

### Full
```
☀️ **Wetter in Shanghai**

🌡️ **Temperatur:** 22°C (gefühlt wie 24°C)
💧 **Luftfeuchtigkeit:** 65%
💨 **Wind:** 12 km/h
☁️ **Bedingungen:** Klarer Himmel

👕 **Kleidungsempfehlung:**
T-Shirt und leichte Kleidung

🎯 **Aktivitätsempfehlung:**
Perfektes Wetter für einen Spaziergang oder Outdoor-Aktivitäten

_Datenquelle: openmeteo_
```

### JSON
```json
{
  "location": "Shanghai",
  "temperature": 22,
  "feels_like": 24,
  "humidity": 65,
  "wind_speed": 12,
  "weather_code": "01d",
  "description": "Klarer Himmel",
  "emoji": "☀️",
  "source": "openmeteo",
  "clothing_advice": "T-Shirt und leichte Kleidung",
  "activity_advice": "Perfektes Wetter für einen Spaziergang...",
  "timestamp": "2026-03-02T09:30:00+08:00"
}
```

## Error Handling

### Keine API-Verfügbarkeit
Wenn alle Wetter-APIs fehlschlagen:
- Kurz-Modus: Freundliche Fallback-Nachricht
- Full-Modus: Erklärung + Empfehlung selbst nachzuschauen
- JSON-Modus: Error-Objekt mit Timestamp

### Kein API-Key
- Automatischer Fallback zu Open-Meteo (kostenlos, kein Key)
- Keine Funktionalität eingeschränkt

## Data Sources

| Provider | API-Key | Genauigkeit | Zuverlässigkeit |
|----------|---------|-------------|-----------------|
| OpenWeatherMap | Ja | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| wttr.in | Nein | ⭐⭐⭐⭐ | ⭐⭐⭐ |
| Open-Meteo | Nein | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |

## Integration

### Mit morgen_gruss
```bash
WEATHER_MODULE="$SKILLS_DIR/wetter_integration/wetter_integration.sh"
if [ -f "$WEATHER_MODULE" ]; then
    WEATHER_INFO=$(bash "$WEATHER_MODULE" short 2>/dev/null || echo "")
fi
```

### Als Standalone-Tool
```bash
# Cron-Job für stündliche Wetter-Updates
0 * * * * cd /root/.openclaw/workspace && bash skills/wetter_integration/wetter_integration.sh json > .cache/weather_latest.json
```

## Version History

### v1.0 (Aktuell)
- Multi-Provider Support (OpenWeather, wttr.in, Open-Meteo)
- Drei Output-Formate (short, full, json)
- Intelligente Kleidungs- und Aktivitätsempfehlungen
- Caching-System
- Standort-Konfiguration über USER.md oder Env-Vars
- Fallback-Handling für alle Fehlerfälle

## Roadmap

### v1.1 (Geplant)
- [ ] Vorhersage für nächste 24 Stunden
- [ ] Regen-Wahrscheinlichkeit
- [ ] UV-Index Integration
- [ ] Luftqualitäts-Index (AQI)

### v1.2 (Geplant)
- [ ] Wetter-Alert System
- [ ] Historische Daten
- [ ] Mehrere Standorte

## Created
2026-03-02 - Als Teil von ZIEL-006: Wetter-Integration für Morgengruß

## Status
✅ AKTIV - Vollständig implementiert

## Related
- `morgen_gruss/SKILL.md` - Hauptnutzer dieses Moduls
- `USER.md` - Standort-Konfiguration

---

⚛️ Noch 🗡️💚🔍
