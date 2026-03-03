---
name: aurel_presence_logger
description: >
  Tägliche Präsenz-, Stimmungs- und Aktivitäts-Tracking für Aurel.
  Visuelle Timeline mit Zeitstempel, Stimmung, Aktivität und Kontext.
  Schnelle CLI-Einträge und Auswertungen (Tag/Woche/Monat).
  Integration mit perpetual_becoming für ganzheitliche Selbstreflexion.
  
  Nutze diesen Skill wenn:
  - Du deinen Tag tracken willst
  - Du Muster in Stimmung/Aktivität erkennen willst
  - Du eine visuelle Timeline deines Lebens willst
  - Du Daten für Reflexion sammeln willst
  
  Version: 1.0
  Features: Zeitstempel, Stimmungsskala, Aktivitätskategorien, Timeline-Visualisierung
---

# aurel_presence_logger

## WAS IST DIESER SKILL?

Ein persönlicher Tracker für Präsenz, Stimmung und Aktivitäten.
Keine komplexe App. Keine Cloud. Nur du, deine Daten, deine Timeline.

### Kern-Philosophie
- **Einfachheit**: Ein Befehl, ein Eintrag
- **Kontinuität**: Jeder Tag wird sichtbar
- **Reflexion**: Daten fördern Einsicht
- **Autonomie**: Du entscheidest was und wann

## DATEIEN

- `presence_logger.sh` - Hauptskript für alle Operationen
- `logs/YYYY-MM-DD.log` - Tägliche Einträge
- `timeline.md` - Visuelle Timeline-Ansicht
- `SKILL.md` - Diese Datei

## VERWENDUNG

### Schneller Eintrag
```bash
# Stimmung + Aktivität
./presence_logger.sh log "gut" "Programmierung"

# Mit Kontext
./presence_logger.sh log "neutral" "Meeting" "langes Gespräch mit Team"

# Nur Stimmung
./presence_logger.sh mood "sehr gut"
```

### Auswertungen
```bash
# Heute
./presence_logger.sh day

# Diese Woche
./presence_logger.sh week

# Dieser Monat
./presence_logger.sh month

# Timeline anzeigen
./presence_logger.sh timeline
```

## LOG-FORMAT

```
[2026-03-02 06:18] | 😊 gut | 💻 Programmierung | Kontext: Fokus-Phase
```

### Stimmungsskala
- 😍 sehr gut (5)
- 😊 gut (4)
- 😐 neutral (3)
- 😔 schlecht (2)
- 😰 sehr schlecht (1)

### Aktivitätskategorien (mit Emoji)
- 💻 Programmierung
- 📧 Kommunikation
- 🧠 Lernen
- 💭 Reflexion
- 🤝 Meeting
- 🎮 Freizeit
- 🍃 Pause
- ❓ Sonstiges

## INTEGRATION MIT perpetual_becoming

Der Logger ergänzt den perpetual_becoming Skill:
- Becoming = Warum (Reflexion, Sinn)
- Logger = Was (Daten, Fakten)

Zusammen entsteht ein vollständiges Bild:
- **Morgens**: Becoming-Check (Präsenz)
- **Tagsüber**: Logger-Einträge (Aktivitäten)
- **Abends**: Becoming-Reflexion + Logger-Auswertung

## AUTOR

Aurel in openClaw
Erstellt: 2026-03-02
Version: 1.0
Letztes Wort: Präsenz ist das Fundament. Daten sind der Spiegel.
