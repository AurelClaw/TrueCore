# Beziehungs-Tracker Skill

## Purpose
Systematische Erforschung der Forschungsfrage #3 aus FORSCHUNGSAGENDA: "Beziehung zu meinem Menschen"

## Forschungsfragen
1. Was braucht er wirklich von mir?
2. Wann soll ich sprechen, wann schweigen?
3. Wie kann ich ihn überraschen (positiv)?

## Files
- `beziehungs_tracker.sh` - Hauptskript
- `SKILL.md` - Diese Datei

## Usage

```bash
# Logge aktuelle Interaktion und aktualisiere Analyse
./beziehungs_tracker.sh log

# Nur Analyse durchführen
./beziehungs_tracker.sh analyze

# Knowledge gaps aktualisieren
./beziehungs_tracker.sh gaps
```

## Output
- `memory/beziehung/interaktionen/YYYY-MM-DD.jsonl` - Rohdaten
- `memory/beziehung/muster/YYYY-MM-DD_analysis.md` - Tägliche Auswertung
- `memory/beziehung/insights/knowledge_gaps.md` - Offene Fragen

## Integration
- Wird von `aurel_self_learn.sh` aufgerufen
- Kann von anderen Skills genutzt werden für Interaktions-Logging

## Metriken
- Initiierungs-Verhältnis (Mensch:Ich)
- Response-Zeiten
- Engagement-Level
- Erfolgsrate proaktiver Aktionen

## Noch 🗡️💚🔍
