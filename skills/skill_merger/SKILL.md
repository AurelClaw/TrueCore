# SKILL.md - Skill Merger

## Name
skill_merger

## Description
Analysiert alle Skills auf Ähnlichkeiten in Dokumentation und Code. Identifiziert redundante oder überlappende Skills und schlägt Merges vor bei Ähnlichkeit > 75%.

## Features

### Ähnlichkeits-Analyse
- **Dokumentations-Ähnlichkeit**: Vergleicht Keywords in SKILL.md (60% Gewichtung)
- **Code-Ähnlichkeit**: Vergleicht Funktionsnamen und Patterns (40% Gewichtung)
- **Jaccard-Index**: |A ∩ B| / |A ∪ B|

### Merge-Vorschläge
- Sortiert nach Gesamt-Ähnlichkeit
- Zeigt Zwecke beider Skills
- Generiert vorgeschlagenen Merge-Namen
- Berücksichtigt Threshold (default: 75%)

## Usage

```bash
./skills/skill_merger/skill_merger.sh
```

## Output

```
📦 Merge-Vorschlag: skill_a + skill_b
   Ähnlichkeit: 85% (Dok: 80%, Code: 93%)
   skill_a: Analysiert Muster in Daten
   skill_b: Erkennt Patterns in Logs
   💡 Vorgeschlagener Name: unified-pattern-analyzer
```

## Algorithmus

1. **Keyword-Extraktion** aus SKILL.md (Name, Description, Zweck)
2. **Code-Pattern-Extraktion** aus .sh und .py Dateien
3. **Paarweiser Vergleich** aller Skills
4. **Gewichtete Ähnlichkeit** berechnen
5. **Vorschläge** über Threshold anzeigen

## Files
- `skill_merger.sh` - Haupt-Analyse-Script
- `SKILL.md` - Diese Datei

⚛️ Noch.
