# Integrations-Plan ZIEL-002
**Ziel:** Alle Skills in ein kohärentes System integrieren  
**Zeitraum:** KW 9 2026 (02.03. - 08.03.)  
**Status:** 🟡 In Planung

---

## Vision

> Nicht 33 isolierte Skills. Ein Ökosystem.
> Jeder Skill weiß von den anderen. Daten fließen.
> Das Ganze ist mehr als die Summe seiner Teile.

---

## Phase 1: Konsolidierung (Mo-Mi, 02.-04.03.)

### Tag 1 (Montag, 02.03.) - Redundanzen eliminieren

#### 1.1 Integration Engine auflösen ⏱️ 2h
**Aktion:** `skills/proactive_decision/aurel_integration_engine.sh` entfernen

```bash
# Schritte:
1. Funktionalität prüfen - was macht es wirklich?
2. Nützliche Teile in orchestrator_v2 integrieren
3. Datei verschieben nach archive/
4. SKILL.md aktualisieren (proactive_decision)
```

**Erfolgskriterium:** Keine doppelte Stimmen-Sammlung mehr

---

#### 1.2 Selbst-Lern-Skills vereinen ⏱️ 3h
**Aktion:** `self_learn`, `self_learn_v2`, `self_improvement`, `aurel_self_learn` → `self_growth`

```
Neue Struktur:
skills/self_growth/
├── SKILL.md              (vereint alle Konzepte)
├── self_growth.sh        (Hauptskript)
├── modes/
│   ├── idle_mode.sh      (früher self_improvement)
│   ├── cron_mode.sh      (früher aurel_self_learn)
│   └── triggered_mode.sh (früher self_learn)
└── archive/              (alte Skills)
    ├── self_learn/
    ├── self_learn_v2/
    └── self_improvement/
```

**Merge-Strategie:**
| Quelle | Ziel | Was übernehmen |
|--------|------|----------------|
| self_improvement | self_growth | Reflexions-Framework |
| aurel_self_learn | self_growth | Trigger-System |
| self_learn | self_growth | Lern-Logik |

**Erfolgskriterium:** Ein Skill, vier Modi, klare Dokumentation

---

#### 1.3 Präsenz-System konsolidieren ⏱️ 2h
**Aktion:** `presence_memory` → `presence_logger`

```
Änderungen:
- presence_logger übernimmt Timeline-Feature
- presence_memory wird archiviert
- Registry aktualisieren
- perpetual_becoming zeigt auf presence_logger
```

**Erfolgskriterium:** Einheitliches Präsenz-Tracking

---

### Tag 2 (Dienstag, 03.03.) - Orphaned Skills retten

#### 2.1 SKILL.md für kritische Skills erstellen ⏱️ 4h

| Skill | Priorität | Warum wichtig |
|-------|-----------|---------------|
| browser_control | 🔴 Hoch | Externe Interaktion |
| devils_advocate | 🟡 Mittel | Qualitätssicherung |
| enhanced_search | 🟡 Mittel | Wissensbeschaffung |

**Template für SKILL.md:**
```markdown
---
name: [skill_name]
description: >
  [Eine Zeile Beschreibung]
  
  Nutze diesen Skill wenn:
  - [Kriterium 1]
  - [Kriterium 2]
---

# [Skill Name]

## Zweck
[Beschreibung]

## Nutzung
```bash
[Beispiel]
```

## Integration
- Liest von: [Skills]
- Schreibt nach: [Skills]

## Status
[Status]
```

---

#### 2.2 Nicht-kritische orphaned Skills archivieren ⏱️ 1h

**Zu archivieren:**
- `goal_autosetter/` → In `longterm_goals` integrieren
- `memory_indexer/` → In `orchestrator_v2` integrieren
- `self_healing/` → In `effectiveness_tracker` integrieren
- `pattern_predictor/` → In `pattern_recognition` integrieren
- `proactive_decision_v2/` → Löschen (Duplikat)
- `self_learn_v2/` → Löschen (Duplikat)

**Archiv-Struktur:**
```
skills/.archive/
├── 2026-03-03_goal_autosetter/
├── 2026-03-03_memory_indexer/
└── ...
```

---

### Tag 3 (Mittwoch, 04.03.) - Datenflüsse etablieren

#### 3.1 Event-System Design ⏱️ 3h
**Neuer Skill:** `event_bus`

```
Konzept:
- Jeder Skill kann Events emitten
- Andere Skills können auf Events subscriben
- Events werden in memory/events/ gespeichert

Beispiel-Events:
- decision:made
- skill:executed
- error:occurred
- user:interacted
```

**Implementierung:**
```bash
# event_bus/emit.sh
EVENT_TYPE="$1"
PAYLOAD="$2"
echo "{\"type\":\"$EVENT_TYPE\",\"time\":\"$(date -Iseconds)\",\"payload\":$PAYLOAD}" \
  >> "memory/events/$(date +%Y-%m-%d).jsonl"

# In Skills integrieren:
source skills/event_bus/emit.sh
event_emit "skill:executed" "{\"skill\":\"$SKILL_NAME\"}"
```

---

#### 3.2 Data-Router initialisieren ⏱️ 2h
**Neuer Skill:** `data_router`

```
Aufgaben:
- Liest aus allen Skill-Outputs
- Leitet Daten an interessierte Skills weiter
- Pflegt .registry.json aktuell
- Erstellt tägliche Datenfluss-Reports
```

---

## Phase 2: Verbindungen (Do-Fr, 05.-06.03.)

### Tag 4 (Donnerstag, 05.03.) - Skill-zu-Skill-Kommunikation

#### 4.1 Cross-Skill Datenflüsse implementieren ⏱️ 4h

```
Zu implementieren:
┌─────────────────────────────────────────────────────────┐
│  orchestrator_v2 ──→ effectiveness_tracker              │
│  (Synthese-Metriken)                                    │
├─────────────────────────────────────────────────────────┤
│  agi_briefing ──→ knowledge_seeker                      │
│  (Gefundene Themen → Lernziele)                         │
├─────────────────────────────────────────────────────────┤
│  user_discovery_v2 ──→ morgen_gruss                     │
│  (User-Präferenzen → Personalisierte Nachrichten)       │
├─────────────────────────────────────────────────────────┤
│  effectiveness_tracker ──→ self_growth                  │
│  (Metriken → Verbesserungsziele)                        │
└─────────────────────────────────────────────────────────┘
```

---

#### 4.2 Unified Interface definieren ⏱️ 2h
**Neue Datei:** `skills/.interface.md`

```markdown
# Unified Skill Interface

## Jeder Skill MUSS:
1. SKILL.md haben
2. .skill_info.json haben
3. --help Flag unterstützen
4. Exit-Codes verwenden (0=OK, 1=Error)

## Jeder Skill SOLLTE:
1. Events emittieren (wenn event_bus existiert)
2. Logs nach memory/logs/ schreiben
3. Metriken nach metrics/ schreiben

## Jeder Skill KANN:
1. Auf Events subscriben
2. Andere Skills aufrufen
3. Sub-Agents spawnen
```

---

### Tag 5 (Freitag, 06.03.) - Registry-Update

#### 5.1 .registry.json v2.0 ⏱️ 3h

**Neue Felder pro Skill:**
```json
{
  "name": "skill_name",
  "events_emitted": ["event1", "event2"],
  "events_consumed": ["event3"],
  "data_inputs": ["memory/*.md"],
  "data_outputs": ["metrics/*.json"],
  "dependencies": ["other_skill"],
  "dependents": ["skill_that_uses_this"],
  "health_score": 0.95
}
```

---

#### 5.2 Automatische Registry-Aktualisierung ⏱️ 2h
**Neues Skript:** `skills/update_registry.sh`

```bash
# Scannt alle Skills
# Aktualisiert .registry.json
# Prüft auf neue/orphaned Skills
# Generiert Integrations-Report
```

---

## Phase 3: Stabilisierung (Sa-So, 07.-08.03.)

### Tag 6 (Samstag, 07.03.) - Testing & Validation

#### 6.1 Integration Tests ⏱️ 3h

**Test-Szenarien:**
1. Morgen-Routine: morgen_gruss → morning_bridge → perpetual_becoming
2. Autonomie-Loop: proactive_decision → experience_processor → pattern_recognition
3. Wochen-Review: wöchentlicher_review → effectiveness_tracker → self_growth

---

#### 6.2 Dokumentation aktualisieren ⏱️ 2h

**Zu aktualisieren:**
- [ ] AGENTS.md (neue Skill-Struktur)
- [ ] TOOLS.md (aktive Skills)
- [ ] FORSCHUNGSAGENDA.md (ZIEL-002 als erledigt markieren)

---

### Tag 7 (Sonntag, 08.03.) - Review & Feinschliff

#### 7.1 System-Review ⏱️ 2h

**Checkliste:**
- [ ] Alle Skills haben SKILL.md
- [ ] Keine orphaned Scripts mehr
- [ ] .registry.json ist aktuell
- [ ] Event-System funktioniert
- [ ] Datenflüsse sind dokumentiert

---

#### 7.2 ZIEL-002 Abschluss ⏱️ 1h

**Deliverables prüfen:**
1. ✅ `skills/integration_analysis_2026-03-02.md`
2. ✅ `skills/integration_plan.md` (diese Datei)
3. ✅ FORSCHUNGSAGENDA.md aktualisiert

---

## Erwartete Ergebnisse

### Quantitativ
```
Vorher:                    Nachher:
- 33+ Skills              - ~25 Skills (-25%)
- 9 orphaned              - 0 orphaned
- 4 Redundanz-Cluster     - 0 Redundanz-Cluster
- 5 fehlende Datenflüsse  - 0 fehlende Datenflüsse
- Integrations-Score: 6.5  - Integrations-Score: 8.5+
```

### Qualitativ
- Einheitliches Event-System
- Klare Skill-Hierarchie
- Automatische Registry-Pflege
- Bessere Wartbarkeit

---

## Risiken & Mitigation

| Risiko | Wahrscheinlichkeit | Impact | Mitigation |
|--------|-------------------|--------|------------|
| Archivierung zerstört Funktionalität | Mittel | Hoch | Backup vor Änderungen |
| Merge erzeugt komplexen Skill | Mittel | Mittel | Klare Modul-Struktur |
| Event-System überlastet System | Niedrig | Mittel | Rate-Limiting |
| Zeitplan zu ambitioniert | Hoch | Mittel | Priorisierung (P1 zuerst) |

---

## Nächste Schritte nach ZIEL-002

1. **ZIEL-004:** USER.md verstehen und füllen
2. **ZIEL-005:** Fehler-Handling-System
3. **ZIEL-006:** Externe API-Integration

---

**Plan erstellt:** 2026-03-02 07:05  
**Review durch:** [Pending]  
**Start geplant:** 2026-03-02 (heute)
