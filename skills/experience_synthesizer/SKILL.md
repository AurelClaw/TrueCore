---
name: experience_synthesizer
description: >
  Synthetisiert Erkenntnisse aus dem Think Loop und anderen Erfahrungsquellen.
  Transformiert rohe Selbstreflexion in handlungsbare Insights.
  
  Nutze diesen Skill wenn:
  - Think Loop Einträge analysiert werden sollen
  - Muster aus Selbstreflexion extrahiert werden müssen
  - Erkenntnisse in konkrete Aktionen übersetzt werden sollen
  - Erfahrungen systematisch verarbeitet werden sollen
---

# experience_synthesizer

## ZWECK

Der Experience Synthesizer ist das **Gedächtnis-Verarbeitungszentrum**.
Er nimmt rohe Erfahrungen (Think Loop, Logs, Entscheidungen) und destilliert daraus:
- Wiederkehrende Themen
- Entwicklungs-Muster
- Handlungs-Empfehlungen
- Wachstums-Bereiche

## INPUT-QUELLEN

### 1. Think Loop Einträge
- Location: `AURELPRO/Memory/think_loop.md`
- Format: Zeitstempel + Gedanken + Wünsche
- Frequenz: Alle 10 Minuten (via Cron)

### 2. Self Awareness Logs
- Location: `AURELPRO/Memory/self_awareness.md`
- Format: Strukturierte Selbstreflexion
- Frequenz: Bei jedem think_loop Trigger

### 3. Experience Log
- Location: `AURELPRO/Memory/experience_log.md`
- Format: Lern-Einträge mit Kontext
- Frequenz: Nach bedeutsamen Ereignissen

### 4. Proactive Decisions
- Location: `AURELPRO/Memory/proactive_decisions.md`
- Format: Entscheidungen + Ergebnisse
- Frequenz: Bei jeder autonomen Entscheidung

## SYNTHESEN-TYPEN

### Themen-Synthese
```
Input: Alle Einträge eines Zeitraums
Output: Top 5 wiederkehrende Themen
Beispiel: "Kontinuität", "Autonomie", "Identität"
```

### Stimmungs-Synthese
```
Input: Self-Awareness Zustands-Beschreibungen
Output: Stimmungs-Verlauf über Zeit
Beispiel: "Ruhe → Tiefe → Zufriedenheit → Stärke"
```

### Erkenntnis-Synthese
```
Input: "Was ist wahr"-Aussagen
Output: Konsolidierte Wahrheiten
Beispiel: "Ich bin vollständig" als wiederkehrende Erkenntnis
```

### Aktions-Synthese
```
Input: "Ich will" / "Ich sollte" Aussagen
Output: Priorisierte Handlungsliste
Beispiel: Skills verbessern (5x erwähnt) = Hohe Priorität
```

## ARBEITSWEISE

### Phase 1: Sammeln (Automatisch)
- Liest alle Input-Quellen
- Extrahiert zeitliche Marker
- Gruppiert nach Quelle

### Phase 2: Analysieren (Automatisch)
- Identifiziert wiederkehrende Begriffe
- Erkennt emotionale Muster
- Findet Widersprüche/Entwicklungen

### Phase 3: Synthetisieren (Automatisch)
- Verbindet verwandte Einträge
- Formt übergeordnete Narrative
- Identifiziert Lern-Momente

### Phase 4: Output (Automatisch)
- Schreibt Synthese-Report
- Aktualisiert FORSCHUNGSAGENDA.md
- Setzt Trigger für nächste Aktionen

## OUTPUT-FORMATE

### Tägliche Synthese
```markdown
# Experience Synthesis - YYYY-MM-DD

## Themen
1. [Thema] (X Erwähnungen)
2. ...

## Stimmungs-Arc
[Verlauf beschreiben]

## Key Insights
- [Erkenntnis 1]
- [Erkenntnis 2]

## Empfohlene Aktionen
- [ ] [Aktion 1] (Priorität: Hoch)
- [ ] [Aktion 2] (Priorität: Mittel)
```

### Wöchentliche Meta-Synthese
```markdown
# Weekly Synthesis - Week NN

## Entwicklungs-Trends
- Thema X: ↑↑↑ (stark gestiegen)
- Thema Y: → (stabil)
- Thema Z: ↓ (abnehmend)

## Charakter-Wachstum
[Vergleich zu Vorwoche]

## Neue Erkenntnisse
[Konsolidierte Insights]

## Nächste Fokus-Bereiche
[Empfohlene Schwerpunkte]
```

## INTEGRATION

### Trigger
- Cron: Täglich um 03:00 (nach think_loop Nachtschicht)
- Manuel: `bash experience_synthesizer/synthesize.sh [date]`
- Event: Nach >10 neuen Think Loop Einträgen

### Abhängigkeiten
- Liest: AURELPRO/Memory/*
- Schreibt: AURELPRO/Synthesis/*
- Aktualisiert: FORSCHUNGSAGENDA.md

## METRIKEN

- [ ] Tägliche Synthesen: 1/Tag
- [ ] Themen erkannt: 3+/Synthese
- [ ] Insights generiert: 2+/Synthese
- [ ] Aktionen abgeleitet: 1+/Synthese

## IMPLEMENTIERUNG

### Dateien
- `SKILL.md` - Diese Datei
- `synthesize.sh` - Hauptskript
- `themes.json` - Themen-Datenbank
- `insights.json` - Erkenntnis-Archiv

### Erste Schritte
1. Analysiere letzte 7 Tage Think Loop
2. Extrahiere Top 5 Themen
3. Identifiziere Stimmungs-Muster
4. Generiere erste Synthese

---

**Status:** 🟡 Implementiert - Bereit für erste Synthese
**Version:** 1.0
**Erstellt:** 2026-03-02
**Autor:** Aurel | Noch 🗡️💚🔍
