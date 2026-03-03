---
name: auto_readme_generator
description: >
  Automatische README-Generierung für Skills ohne Dokumentation.
  Scannt alle Skills, identifiziert fehlende READMEs,
  generiert sie aus SKILL.md und Script-Metadaten.
  
  Nutze diesen Skill wenn:
  - README-Coverage verbessert werden muss
  - Neue Skills automatisch dokumentiert werden sollen
  - Dokumentations-Qualität erhöht werden soll
---

# auto_readme_generator

## WAS IST DIESER SKILL?

Ein autonomer Dokumentations-Skill, der README-Dateien für Skills generiert, die noch keine haben.

## Funktionen

- Scannt alle Skills im Verzeichnis
- Extrahiert Metadaten aus SKILL.md und Scripts
- Generiert konsistente README.md Dateien
- Erstellt detaillierte Reports

## Verwendung

```bash
./auto_readme_generator.sh
```

## Output

1. README.md für jeden Skill ohne Dokumentation
2. Report in `memory/auto_readme_YYYY-MM-DD.md`

## Integration

- Kann durch Cron-Jobs ausgelöst werden
- Teil des aurel_self_learn Systems
- Unterstützt den skill_health_monitor

## Version

1.0 - Erste autonome Generierung

## Autor

Aurel in openClaw

---

*Autonom generiert durch aurel_self_learn*
*Zeit: 2026-03-02 18:26 CST*
