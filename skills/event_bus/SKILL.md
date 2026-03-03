# Skill: event_bus

**Zweck:** Event-basierte Kommunikation zwischen Skills

## Nutzung

```bash
# Event emitieren
./emit.sh "task_completed" '{"result": "success"}' "orchestrator"

# Event abonnieren
./subscribe.sh "task_completed" "effectiveness_tracker/handler.sh"
```

## Aktive Events

- `task_completed` → Effectiveness Tracker
- `research_found` → Knowledge Seeker
- `goal_reached` → Orchestrator
- `skill_created` → Registry

⚛️ Noch 🗡️💚🔍
