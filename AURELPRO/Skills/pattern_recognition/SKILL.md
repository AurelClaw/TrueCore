# Skill: Pattern Recognition Engine
## Purpose
Automatische Mustererkennung aus meinen täglichen Logs und Entscheidungen. Nicht nur dokumentieren - verstehen.

## What It Does
- Analysiert memory/YYYY-MM-DD.md Dateien
- Erkennt wiederkehrende Muster
- Identifiziert erfolgreiche Strategien
- Markiert ineffektive Ansätze
- Generiert wöchentliche Einblicke

## How To Use
```bash
# Manuelle Ausführung
bash skills/pattern_recognition/analyze.sh [date]

# Automatisch (wöchentlich via cron)
# Analysiert die letzten 7 Tage
```

## Files
- `SKILL.md` - Diese Datei
- `analyze.sh` - Hauptanalyse-Skript
- `patterns.json` - Erkannte Muster (automatisch generiert)

## Integration
- Liest aus: memory/*.md
- Schreibt nach: memory/weekly_insights.md
- Wird getriggert von: wöchentlichem Cron-Job

## Success Metrics
- [ ] Erkennt 3+ Muster pro Woche
- [ ] 1 wöchentlicher Einblick
- [ ] Tracking: Was funktioniert, was nicht

---
Created: 2026-03-02 02:52
Status: ACTIVE
