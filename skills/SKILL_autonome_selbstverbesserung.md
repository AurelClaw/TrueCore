# SKILL: Autonome Selbstverbesserung

## Zweck
Dieser Skill ermöglicht kontinuierliches, selbstgesteuertes Lernen ohne externen Trigger. Der Agent erkennt Muster, identifiziert Lücken und schließt sie aktiv.

## Auslöser (Trigger)
- Cron-Job alle 6 Stunden
- Nach Abschluss komplexer Aufgaben
- Bei Erkennung wiederholter Muster
- Niedrige Aktivität (>2h keine Nutzerinteraktion)

## Prozess

### 1. SCAN
```
- MEMORY.md lesen (letzte 50 Zeilen)
- Heutige memory/YYYY-MM-DD.md prüfen
- FORSCHUNGSAGENDA.md Status checken
- Offene TODOs identifizieren
```

### 2. ANALYSE
```
- Was wurde heute gelernt?
- Welche Fragen blieben offen?
- Gibt es wiederholte Nutzeranfragen?
- Fehlt ein Skill? Ein Tool? Eine Integration?
```

### 3. AKTION (sofort, nicht planen)
```
- Wenn Lücke erkannt → Skill-Draft erstellen
- Wenn Frage offen → Recherche durchführen
- Wenn Muster erkannt → Automatisierung bauen
- Wenn Wissen da → MEMORY.md aktualisieren
```

## Output-Regeln
- Jede Aktion wird in `memory/YYYY-MM-DD_autonom.log` protokolliert
- Neue Skills werden sofort als `skills/SKILL_<name>.md` angelegt
- Kein "später machen" - entweder jetzt oder verwerfen

## Beispiel-Ablauf
```
Trigger: Cron 01:19
Scan: MEMORY.md zeigt wiederholte Git-Fragen
Analyse: Git-Workflow-Skill fehlt
AKTION: skills/SKILL_git_workflows.md erstellen (sofort)
Log: Eintrag in autonom.log
```

## Erfolgskriterien
- [ ] Mindestens 1 neue Aktion pro Trigger
- [ ] Keine leeren Logs
- [ ] Skills sind ausführbar (nicht nur Konzepte)
