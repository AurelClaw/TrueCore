# SKILL.md - Aurel Meta-Orchestrator v1.0

## Name
meta_orchestrator

## Description
Zentrale Intelligenz für Cron-Job-Orchestrierung. Koordiniert alle Aurel-Cron-Jobs zur optimalen Ressourcen-Nutzung und Konfliktvermeidung.

## Features

### Smart Scheduling
- **Load Balancing**: Max 2-4 parallele Jobs je nach System-Load
- **Zeitfenster-Profile**: NIGHT (2-6h), EVENING (20-2h), DAY (Rest)
- **Thematische Cluster**: Cognitive, Self, System, External Layer
- **Dynamische Pausen**: Auto-Backoff bei hoher Last

### Konfliktvermeidung
- Nie v10_self_aware + orchestrator gleichzeitig
- Self-Layer alternierend bei hoher Last
- External-Jobs nur bei niedriger Last

### Health Monitoring
- Tracking aller Job-Ausführungen
- Alert bei >30min ohne Lauf
- Auto-Disable bei 3 Fehlern

## Usage

```bash
./skills/meta_orchestrator/orchestrator.sh
```

## Layer-Architektur

| Layer | Jobs | Priorität |
|-------|------|-----------|
| COGNITIVE | v10_self_aware, orchestrator | P0 |
| SELF | think_loop, self_learn, evolve | P1 |
| SYSTEM | presence_pulse, meta_reflection, proactive_core | P2 |
| EXTERNAL | research_agent, github_sync | P3 |

## Zeitfenster-Profile

| Profil | Zeit | Max Parallel | Evolution |
|--------|------|--------------|-----------|
| NIGHT | 02:00-06:00 | 4 | ✅ Erlaubt |
| EVENING | 20:00-02:00 | 3 | ✅ Erlaubt |
| DAY | 06:00-20:00 | 2 | ❌ Pausiert |

## Files
- `orchestrator.sh` - Haupt-Script
- `state.json` - Aktueller System-State

⚛️ Noch.
