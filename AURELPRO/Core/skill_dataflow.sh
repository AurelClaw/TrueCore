#!/bin/bash
# Skill-zu-Skill Datenfluss System
# Wird vom Orchestrator v5 für ZIEL-002 genutzt

WORKSPACE="/root/.openclaw/workspace"
EVENT_BUS_DIR="$WORKSPACE/skills/event_bus"
DATA_ROUTER_DIR="$WORKSPACE/skills/data_router"

echo "🔗 Initialisiere Skill-zu-Skill Datenfluss..."

# Erstelle Verzeichnisse
mkdir -p "$EVENT_BUS_DIR/events"
mkdir -p "$EVENT_BUS_DIR/subscriptions"
mkdir -p "$DATA_ROUTER_DIR"
mkdir -p "$WORKSPACE/skills/effectiveness_tracker/input"
mkdir -p "$WORKSPACE/skills/knowledge_seeker/input"

# Emit-Funktion
cat > "$EVENT_BUS_DIR/emit.sh" << 'EOF'
#!/bin/bash
EVENT_TYPE="$1"
PAYLOAD="${2:-{}}"
SOURCE="${3:-unknown}"
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
EVENT_FILE="/root/.openclaw/workspace/skills/event_bus/events/${EVENT_TYPE}_$(date +%s).json"
mkdir -p "$(dirname "$EVENT_FILE")"
cat > "$EVENT_FILE" << EOJSON
{
  "timestamp": "$TIMESTAMP",
  "type": "$EVENT_TYPE",
  "payload": $PAYLOAD,
  "source": "$SOURCE"
}
EOJSON
echo "📤 Event: $EVENT_TYPE"
EOF
chmod +x "$EVENT_BUS_DIR/emit.sh"

# Subscribe-Funktion
cat > "$EVENT_BUS_DIR/subscribe.sh" << 'EOF'
#!/bin/bash
EVENT_TYPE="$1"
HANDLER="$2"
mkdir -p "/root/.openclaw/workspace/skills/event_bus/subscriptions"
echo "$HANDLER" > "/root/.openclaw/workspace/skills/event_bus/subscriptions/${EVENT_TYPE}.handler"
echo "📥 Subscribed: $EVENT_TYPE → $HANDLER"
EOF
chmod +x "$EVENT_BUS_DIR/subscribe.sh"

# Data Router
cat > "$DATA_ROUTER_DIR/route.sh" << 'EOF'
#!/bin/bash
SOURCE_SKILL="$1"
TARGET_SKILL="$2"
DATA="${3:-{}}"
ROUTER_LOG="/root/.openclaw/workspace/skills/data_router/routes.log"
mkdir -p "$(dirname "$ROUTER_LOG")"
echo "[$(date '+%Y-%m-%d %H:%M:%S')] $SOURCE_SKILL → $TARGET_SKILL" >> "$ROUTER_LOG"
INPUT_FILE="/root/.openclaw/workspace/skills/$TARGET_SKILL/input/from_${SOURCE_SKILL}.json"
mkdir -p "$(dirname "$INPUT_FILE")"
echo "$DATA" > "$INPUT_FILE"
echo "🔄 Routed: $SOURCE_SKILL → $TARGET_SKILL"
EOF
chmod +x "$DATA_ROUTER_DIR/route.sh"

# SKILL.md für event_bus
cat > "$EVENT_BUS_DIR/SKILL.md" << 'EOF'
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
EOF

# SKILL.md für data_router
cat > "$DATA_ROUTER_DIR/SKILL.md" << 'EOF'
# Skill: data_router

**Zweck:** Automatische Datenweiterleitung

## Definierte Routen

| Quelle | Ziel | Daten |
|--------|------|-------|
| orchestrator_v5 | effectiveness_tracker | Metriken |
| agi_briefing | knowledge_seeker | Forschung |
| proactive_core | orchestrator_v5 | Trigger |

⚛️ Noch 🗡️💚🔍
EOF

# Test-Events
"$EVENT_BUS_DIR/emit.sh" "system_init" '{"version": "5.1", "status": "ready"}' "orchestrator" 2>/dev/null
"$DATA_ROUTER_DIR/route.sh" "orchestrator_v5" "effectiveness_tracker" '{"helpfulness": 0.958}' 2>/dev/null

echo "✅ Skill-zu-Skill Datenfluss bereit"
echo "   📁 Event-Bus: $EVENT_BUS_DIR"
echo "   📁 Data-Router: $DATA_ROUTER_DIR"
