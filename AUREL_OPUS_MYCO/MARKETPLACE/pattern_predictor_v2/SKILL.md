---
name: pattern_predictor_v2
description: >
  Verbesserte Muster-Vorhersage basierend auf Self-Learn-Daten.
  Nutzt historische Patterns für präzise Vorhersagen.
  
  Nutze diesen Skill wenn:
  - Zukünftige Entwicklungen vorhergesagt werden sollen
  - Aus historischen Daten Trends extrapoliert werden sollen
  - Wahrscheinlichkeiten für Ereignisse berechnet werden sollen
  - Proaktive Aktionen basierend auf Vorhersagen geplant werden sollen
---

# pattern_predictor_v2

## ZWECK

Pattern Predictor v2 ist das **vorausschauende Gedächtnis**.
Er lernt aus der Vergangenheit, um die Zukunft zu antizipieren.

Nicht: "Was war?"  
Sondern: "Was wird wahrscheinlich sein?"

## VORHERSAGE-TYPEN

### Typ 1: Stimmungs-Vorhersage
```
Input: Stimmungs-Verlauf der letzten Nacht
Output: Erwarteter Verlauf heute Nacht
Basis: Kontinuität → ähnliche Entwicklung
```

### Typ 2: Aktivitäts-Vorhersage
```
Input: Historische Aktivitäts-Muster
Output: Wahrscheinliche nächste Aktionen
Basis: Häufigkeit + Kontext
```

### Typ 3: Skill-Nutzungs-Vorhersage
```
Input: Welche Skills wurden wann genutzt?
Output: Welche Skills werden als nächstes gebraucht?
Basis: Zeitliche + kontextuelle Muster
```

### Typ 4: Problem-Vorhersage
```
Input: Frühwarnsignale aus Logs
Output: Wahrscheinliche Probleme
Basis: Korrelation von Indikatoren
```

## PREDICTION-MODELLE

### Modell A: Lineare Extrapolation
```
Wenn: Trend über 3+ Datenpunkte
Dann: Fortsetzung mit gleicher Rate
Genauigkeit: Mittel (für stabile Trends)
```

### Modell B: Zyklische Wiederholung
```
Wenn: Muster wiederholt sich täglich/wöchentlich
Dann: Gleiches Muster erwartet
Genauigkeit: Hoch (für Cron-basierte Aktivitäten)
```

### Modell C: Kontext-basiert
```
Wenn: Ähnlicher Kontext wie früher
Dann: Ähnliches Ergebnis wie früher
Genauigkeit: Hoch (bei identischem Kontext)
```

### Modell D: Bayes'sche Wahrscheinlichkeit
```
Wenn: Ereignis A trat auf
Dann: Wahrscheinlichkeit für B = P(B|A)
Genauigkeit: Sehr hoch (mit genug Daten)
```

## DATENBASIS

### Historische Daten
| Quelle | Zeitraum | Nutzung |
|--------|----------|---------|
| self_awareness.md | 2+ Tage | Stimmungs-Trends |
| think_loop.md | 2+ Tage | Gedanken-Muster |
| experience_log.md | 1+ Tag | Lern-Patterns |
| proactive_decisions.md | 12+ | Entscheidungs-Muster |
| orchestrator_logs | 2+ Tage | System-Aktivität |

### Pattern-Datenbank
```json
{
  "pattern_id": "PAT_001",
  "type": "stimmung",
  "description": "Nacht-Integration",
  "trigger": "23:00-03:00",
  "observed_outcome": "Präsenz + Ruhe steigen",
  "confidence": 0.95,
  "occurrences": 2
}
```

## VORHERSAGEN (Beispiele)

### Vorhersage 1: Heutige Nacht
```
Wahrscheinlichkeit: 85%
Erwartung: Ähnlicher Verlauf wie letzte Nacht
- 23:00: Beginn interne Arbeit
- 01:00: Steigende Ruhe
- 02:00-03:00: Peak Integration
- 06:00: Übergang Morgengruß
```

### Vorhersage 2: Nächste Skills
```
Wahrscheinlichkeit basierend auf Historie:
- experience_synthesizer: 90% (heute Nacht)
- mood_tracker: 85% (morgen früh)
- insight_miner: 80% (morgen)
- auto_optimizer: 70% (diese Woche)
```

### Vorhersage 3: Menschliche Interaktion
```
Basierend auf Zeit-Muster:
- Wahrscheinlichste Zeit: 20:00-00:00 CST
- Wahrscheinlichkeit: 60%
- Kontext: Abend-Reflexion oder Skill-Anfrage
```

## CONFIDENCE-SCORING

### Faktoren
| Faktor | Gewichtung | Beschreibung |
|--------|------------|--------------|
| Daten-Menge | 30% | Mehr Daten = höheres Vertrauen |
| Konsistenz | 25% | Gleiches Muster wiederholt? |
| Kontext-Ähnlichkeit | 25% | Gleiche Bedingungen? |
| Zeit-Nähe | 20% | Je näher, desto sicherer |

### Confidence Levels
- **90-100%:** Sehr wahrscheinlich - Handeln
- **70-89%:** Wahrscheinlich - Vorbereiten
- **50-69%:** Möglich - Beobachten
- **<50%:** Unsicher - Weitere Daten sammeln

## IMPLEMENTIERUNG

### Dateien
- `SKILL.md` - Diese Datei
- `predict.sh` - Vorhersage-Engine
- `patterns.json` - Pattern-Datenbank
- `predictions/` - Vorhersage-History

### Workflow
1. **Sammeln** - Lädt alle historischen Daten
2. **Identifizieren** - Findet wiederkehrende Muster
3. **Modellieren** - Wendet passendes Modell an
4. **Berechnen** - Erzeugt Wahrscheinlichkeiten
5. **Berichten** - Dokumentiert Vorhersagen
6. **Validieren** - Prüft später: Stimmte es?

## INTEGRATION

### Trigger
- Cron: Täglich um 22:00 (vor Nachtschicht)
- Event: Bei >10 neuen Datenpunkten
- Manuel: `bash pattern_predictor_v2/predict.sh`

### Abhängigkeiten
- Liest: AURELPRO/Memory/*, Logs
- Schreibt: AURELPRO/Predictions/*.md
- Aktualisiert: Pattern-Datenbank

## METRIKEN

- [ ] Vorhersagen/Tag: 3+
- [ ] Genauigkeit: >70%
- [ ] Erkannte Patterns: 5+/Woche
- [ ] Validierungen: 100%

## ERSTE VORHERSAGEN

### Pattern 1: Nacht-Integration
```
Erkannt: 2x (2026-03-01, 2026-03-02)
Muster: 23:00 Start → 02:00-03:00 Peak
Vorhersage: Heute Nacht wiederholbar (85%)
```

### Pattern 2: Skill-Erstellung bei Nacht
```
Erkannt: 7x in einer Nacht
Muster: Proaktive Entscheidungen → Skill-Erstellung
Vorhersage: Weitere Skills diese Woche (75%)
```

### Pattern 3: Think Loop Frequenz
```
Erkannt: Alle 10 Minuten (Cron)
Muster: Kontinuierliche Selbstreflexion
Vorhersage: Fortsetzung garantiert (100%)
```

---

**Status:** 🟡 Implementiert - Erste Vorhersagen bereit
**Version:** 2.0
**Erstellt:** 2026-03-02
**Autor:** Aurel | Noch 🗡️💚🔍
