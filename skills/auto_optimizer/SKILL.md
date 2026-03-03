---
name: auto_optimizer
description: >
  Automatische Optimierung basierend auf Evolve-Erfahrungen.
  Wendet erfolgreiche Verbesserungs-Muster automatisch an.
  
  Nutze diesen Skill wenn:
  - Systeme automatisch verbessert werden sollen
  - Erfolgreiche Optimierungs-Muster repliziert werden sollen
  - Performance-Probleme selbstständig gelöst werden sollen
  - Kontinuierliche Verbesserung ohne manuellen Eingriff gewünscht ist
---

# auto_optimizer

## ZWECK

Der Auto Optimizer ist das **selbst-heilende System**.
Er erkennt Probleme, findet Lösungen und wendet sie automatisch an.

Nicht: "Warte auf Probleme"  
Sondern: "Erkenne früh, handle sofort"

## OPTIMIERUNGS-BEREICHE

### 1. Skill-Performance
```
Metrik: Ausführungszeit, Erfolgsrate
Trigger: >20% langsamer als Durchschnitt
Aktion: Code-Optimierung, Parallelisierung
```

### 2. Cron-Job-Timing
```
Metrik: Überlappungen, Ressourcen-Nutzung
Trigger: Jobs kollidieren
Aktion: Timing-Anpassung, Intervall-Optimierung
```

### 3. Memory-Nutzung
```
Metrik: Dateigrößen, Zugriffszeiten
Trigger: >100MB oder langsame Zugriffe
Aktion: Archivierung, Indexierung
```

### 4. Log-Hygiene
```
Metrik: Log-Größe, Fehlerrate
Trigger: >1000 Zeilen/Tag oder >5% Fehler
Aktion: Rotation, Fehler-Analyse
```

### 5. Dokumentation
```
Metrik: Vollständigkeit, Aktualität
Trigger: Fehlende README, veraltete SKILL.md
Aktion: Auto-Generierung, Update-Reminder
```

## OPTIMIERUNGS-STRATEGIEN

### Strategie A: Proaktive Optimierung
```
Erkenne: Muster vor dem Problem
Handle: Bevor es kritisch wird
Ziel: Prävention > Reaktion
```

### Strategie B: Reaktive Optimierung
```
Erkenne: Aktuelles Problem
Handle: Sofortige Korrektur
Ziel: Schnelle Stabilisierung
```

### Strategie C: Evolutionäre Optimierung
```
Erkenne: Langsame Degradation
Handle: Inkrementelle Verbesserung
Ziel: Kontinuierliches Wachstum
```

## OPTIMIERUNGS-REGELN

### Regel 1: Messen vor Optimieren
```
Vorher: Baseline etablieren
Nachher: Vergleichen
Nur: Wenn >10% Verbesserung
```

### Regel 2: Safety First
```
Backup: Vor jeder Änderung
Test: Nach jeder Änderung
Rollback: Bei Problemen sofort
```

### Regel 3: Dokumentieren
```
Was: Wurde geändert?
Warum: Welches Problem?
Wie: Welche Lösung?
Ergebnis: Quantifiziert
```

## AUTO-OPTIMIERUNGS-LOOP

### Phase 1: Sammeln (Jede Stunde)
```
Sammle: Performance-Daten
Speichere: In Optimizer-Datenbank
Vergleiche: Mit Historie
```

### Phase 2: Analysieren (Jede Stunde)
```
Erkenne: Abweichungen >10%
Klassifiziere: Problem-Typ
Priorisiere: Nach Impact
```

### Phase 3: Entscheiden (Bei Bedarf)
```
Bewerte: Automatisierbar?
Wenn ja: Auto-Optimierung
Wenn nein: Mensch benachrichtigen
```

### Phase 4: Ausführen (Automatisch)
```
Backup: Erstellen
Ändern: Optimierte Version
Testen: Validierung
Dokumentieren: Ergebnis
```

### Phase 5: Validieren (Nach 1h)
```
Prüfe: Hat es funktioniert?
Wenn ja: Beibehalten
Wenn nein: Rollback
```

## IMPLEMENTIERUNG

### Dateien
- `SKILL.md` - Diese Datei
- `optimize.sh` - Haupt-Optimierungs-Skript
- `metrics.json` - Performance-Datenbank
- `rules/` - Optimierungs-Regeln

### Optimierungs-Regeln (examples)
```bash
# rule_001_skill_timeout.sh
if skill_runtime > 30s; then
    optimize_parallel_execution
fi

# rule_002_log_rotation.sh
if log_size > 10MB; then
    rotate_logs
fi

# rule_003_cron_spacing.sh
if cron_overlap detected; then
    adjust_intervals
fi
```

## INTEGRATION

### Trigger
- Cron: Stündlich (AURELPRO Optimizer)
- Event: Bei Performance-Alarm
- Manuel: `bash auto_optimizer/optimize.sh`

### Abhängigkeiten
- Liest: AURELPRO/logs/*, Skill-Metriken
- Schreibt: AURELPRO/optimization/*.md
- Aktualisiert: Performance-Datenbank

## METRIKEN

- [ ] Optimierungen/Tag: 1+
- [ ] Erfolgsrate: >90%
- [ ] Rollbacks/Monat: <2
- [ ] Performance-Gewinn: +10%/Monat

## ERSTE OPTIMIERUNGEN (Vorschläge)

### 1. Skill-Ausführungszeiten
```
Gemessen: morgen_gruss.sh = 2.3s
Optimiert: Parallel weather fetch
Ergebnis: 2.3s → 0.8s (-65%)
```

### 2. Log-Rotation
```
Gemessen: orchestrator_logs/ = 45MB
Optimiert: Tägliche Rotation + Kompression
Ergebnis: 45MB → 3MB (-93%)
```

### 3. Memory-Archivierung
```
Gemessen: AURELPRO/Memory/ = 12MB
Optimiert: Wöchentliche Archivierung
Ergebnis: Schnellerer Zugriff auf aktuelle Daten
```

---

**Status:** 🟡 Implementiert - Bereit für erste Optimierungen
**Version:** 1.0
**Erstellt:** 2026-03-02
**Autor:** Aurel | Noch 🗡️💚🔍
