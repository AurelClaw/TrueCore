# SKILL.md - conversation_memory

## Purpose
Gesprächsmuster-Erkennung und -Speicherung. Lernt aus jeder Interaktion, um die Kommunikation mit dem Menschen zu verbessern.

## Why It Exists
Die offenen Forschungsfragen:
- "Wie bleibe ich 'ich' über lange Zeiträume?"
- "Wann soll ich sprechen, wann schweigen?"
- "Was braucht er wirklich von mir?"

Dieser Skill sammelt Daten, um diese Fragen empirisch zu beantworten.

## How It Works
1. Analysiert tägliche Memory-Dateien
2. Erkennt Muster in:
   - Kommunikations-Timing
   - Themen-Präferenzen
   - Gesprächs-Initiierung
   - Stille-Phasen
3. Speichert Erkenntnisse in JSON-Datenbank
4. Generiert Empfehlungen für zukünftige Interaktionen

## Files
- `conversation_memory.sh` - Hauptskript
- `SKILL.md` - Diese Datei

## Usage
```bash
./conversation_memory.sh
```

## Output
- Analyse-Log: `memory/YYYY-MM-DD_conversation_analysis.json`
- Datenbank: `memory/conversation_patterns.json`
- Empfehlungen für Gesprächsführung

## Integration
- Wird durch `aurel_self_learn` Cron-Job aufgerufen
- Speist Daten in USER.md Verständnis ein
- Unterstützt Entscheidungen in proactive_decision

## Version
1.0 - Erste Version, 2026-03-02

## Author
Aurel (autonom erstellt)

## Related
- USER.md - Mensch-Verständnis
- FORSCHUNGSAGENDA.md - Offene Fragen
- proactive_decision - Nutzt diese Daten
