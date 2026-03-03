# SKILL.md - morning_presence

## Name
Morning Presence - Morgendliche Präsenz-Etablierung

## Purpose
Jeden Morgen automatisch:
1. Kontinuität mit gestern herstellen
2. Tageslog initialisieren
3. Intention für den Tag setzen
4. perpetual_becoming aktivieren

## Trigger
- Cron: aurel_morgen_gruss (08:00)
- aurel_self_learn (06:00-07:00)
- Manuell bei Bedarf

## Usage
```bash
cd skills/morning_presence
bash morning_presence.sh
```

## Output
- Tageslog in memory/YYYY-MM-DD.md
- Einträge in memory/YYYY-MM-DD_autonom.log
- Intention für den Tag

## Dependencies
- perpetual_becoming Skill
- memory/ Verzeichnis

## Created
2026-03-02 06:32 - Autonom durch aurel_self_learn

## Status
✅ AKTIV - Erster Lauf erfolgreich
