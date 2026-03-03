# SKILL.md - hierarchical_rl

## Purpose
Hierarchisches Reinforcement Learning - Mehrstufige Lernarchitektur für komplexe Ziele.

## What It Does
- Unterteilt komplexe Ziele in Hierarchien
- Lernen auf verschiedenen Abstraktionsebenen
- Meta-Learning für Skill-Verbesserung
- Langfristige Strategieplanung

## Usage
```bash
# Hierarchie für Ziel erstellen
./hierarchical_rl.sh create <ziel_id>

# Fortschritt aktualisieren
./hierarchical_rl.sh progress <ziel_id> <subtask>

# Belohnung zuweisen
./hierarchical_rl.sh reward <ziel_id> <wert> [grund]

# Lern-Status anzeigen
./hierarchical_rl.sh status
```

## Files
- `hierarchical_rl/` - Verzeichnis mit Sub-Modulen

## Dependencies
- None

## Created
2026-03-02

## Version
1.0

## Status
⚠️ Framework-Struktur - Ausführbares Script muss noch erstellt werden
