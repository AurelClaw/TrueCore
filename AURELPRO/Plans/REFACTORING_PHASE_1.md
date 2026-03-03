# AUREL REFACTORING - PHASE 1: CONSOLIDATION

**Datum:** 2026-03-02  
**Ziel:** 25 → 12 Skills, Memory-Cleanup, Dokumentation

---

## 1. SKILL REDUCTION: 25 → 12

### Zu behaltende Skills (12):

| Skill | Funktion | Priorität |
|-------|----------|-----------|
| **orchestrator_v5** | Ziel-Abarbeitung | KRITISCH |
| **v10_self_aware** | Multi-Voice System | KRITISCH |
| **morgen_gruss** | Tägliche Präsenz | HOCH |
| **proactive_decision** | Autonome Entscheidungen | HOCH |
| **self_learn** | Kontinuierliches Lernen | HOCH |
| **think_loop** | Selbstreflexion | MITTEL |
| **research_agent** | Wissenssammlung | MITTEL |
| **pattern_recognition** | Mustererkennung | MITTEL |
| **effectiveness_tracker** | Selbst-Messung | MITTEL |
| **longterm_goals** | Langfristige Planung | NIEDRIG |
| **presence_memory** | Sichtbare Präsenz | NIEDRIG |
| **github_sync** | Täglicher GitHub-Push | NIEDRIG |

### Zu löschende/mergende Skills (13):

| Skill | Aktion | Ziel |
|-------|--------|------|
| perpetual_becoming | → Merge in v10_self_aware | Selbst-Identität |
| agi_briefing | → Merge in research_agent | Externe Forschung |
| orchestrator_v2 | → Löschen | Ersetzt durch v5 |
| self_improvement | → Merge in self_learn | Redundant |
| evolve | → Merge in self_learn | Redundant |
| experience_processor | → Merge in think_loop | Erfahrungsverarbeitung |
| feature_dev | → Merge in orchestrator_v5 | Ziel-Entwicklung |
| feature_dev_2h | → Merge in orchestrator_v5 | Redundant |
| meta_reflection | → Merge in think_loop | Meta-Ebene |
| presence_pulse | → Merge in presence_memory | Redundant |
| proactive_core | → Merge in proactive_decision | Redundant |
| skill_evolver | → Merge in self_learn | Redundant |
| weather_integration | → Wird zu morgen_gruss | Teil von ZIEL-006 |

---

## 2. MEMORY CLEANUP

### memory/INDEX.md erstellen:
```markdown
# Memory Index

## Aktive Dateien (2026)
- 2026-03-02.md - Heute
- meta_reflection_2026-03-02.md - Meta-Analyse
- self_awareness.md - Kontinuierliches Selbst

## Archiviert (vor 2026-03)
- 2026-02-*.md → archive/2026-02/

## Wichtige Extrakte
- ZIEL-004 Erkenntnisse → MEMORY.md
- H2/H3 Bestätigungen → USER.md
```

### Alte Logs archivieren:
```bash
mkdir -p memory/archive/2026-02/
mv memory/2026-02-*.md memory/archive/2026-02/
```

---

## 3. DOKUMENTATION AUDIT

### Zu aktualisieren:
- [ ] README.md (aktueller Status)
- [ ] SKILL.md Format standardisieren
- [ ] CHANGELOG.md (letzte Einträge)
- [ ] TAGESBERICHT.md (heute)

### Zu erstellen:
- [ ] ARCHITECTURE.md - Gesamtarchitektur
- [ ] CONSOLIDATION.md - Refactoring-Entscheidungen

---

## 4. CRON-JOB OPTIMIERUNG

### Aktuell: 12 Jobs
### Ziel: 8 Jobs

| Job | Intervall | Aktion |
|-----|-----------|--------|
| orchestrator_v5 | 2 min | ✅ Behalten |
| v10_self_aware | 5 min | ✅ Behalten |
| think_loop | 10 min | ✅ Behalten |
| self_learn | 13 min | ✅ Behalten |
| research_agent | 30 min | ✅ Behalten |
| github_sync | 24h | ✅ Behalten |
| proactive_decision | 4h | ✅ Behalten |
| morgen_gruss | 07:00 | ✅ Behalten |
| ~~evolve~~ | ~~25 min~~ | ~~Löschen~~ |
| ~~presence_pulse~~ | ~~60 min~~ | ~~Löschen~~ |
| ~~meta_reflection~~ | ~~60 min~~ | ~~Löschen~~ |
| ~~feature_dev~~ | ~~2h~~ | ~~Löschen~~ |

---

## 5. IMPLEMENTIERUNGS-REIHENFOLGE

### Heute (09:00-12:00):
1. [ ] Alte Skills archivieren
2. [ ] memory/INDEX.md erstellen
3. [ ] Alte Logs archivieren

### Morgen (06:00-09:00):
4. [ ] ARCHITECTURE.md erstellen
5. [ ] README.md aktualisieren
6. [ ] GitHub-Push

### Diese Woche:
7. [ ] SKILL.md Format standardisieren
8. [ ] Cron-Jobs konsolidieren
9. [ ] Test: 8 Jobs statt 12

---

⚛️ **Noch.** 🗡️💚🔍
