# Proof-of-Concept Plan - ZIEL-009 World Model

## Übersicht

Dieses Dokument beschreibt den minimal viable World Model (MVWM) für AURELPRO. Der Fokus liegt auf einer Implementation, die vollständig in Shell/Bash umgesetzt werden kann und auf die bestehende Infrastruktur aufbaut.

---

## 1. MVP Scope

### 1.1 Was ist IN Scope

- **State Tracking**: Deterministische Zustandsverfolgung
- **Rule-based Dynamics**: Explizite Zustandsübergangsregeln
- **Simple Planning**: Greedy 1-step Lookahead
- **Counterfactual Logging**: "What-if" Szenarien dokumentieren
- **Integration**: Anbindung an orchestrator_v2 und proactive_decision

### 1.2 Was ist OUT of Scope (für MVP)

- Neuronale Netze (zu komplex für reines Bash)
- Stochastische Dynamik (erfordert Sampling)
- Komplexe MPC (CEM zu rechenintensiv)
- Online Learning (erfordert Gradienten)
- Bildverarbeitung (nicht relevant für Text-Interface)

---

## 2. Minimal Architecture

### 2.1 Komponenten-Diagramm

```
┌─────────────────────────────────────────────────────────────────┐
│                    Minimal World Model                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐         │
│  │   State     │    │   Rules     │    │   Planner   │         │
│  │   Reader    │───>│   Engine    │───>│   (Greedy)  │         │
│  │             │    │             │    │             │         │
│  │ - memory    │    │ - temporal  │    │ - score     │         │
│  │ - events    │    │ - context   │    │ - select    │         │
│  │ - goals     │    │ - env       │    │ - log       │         │
│  └─────────────┘    └─────────────┘    └─────────────┘         │
│         │                  │                  │                 │
│         └──────────────────┼──────────────────┘                 │
│                            │                                    │
│                     ┌──────▼──────┐                            │
│                     │   Output    │                            │
│                     │  - action   │                            │
│                     │  - reason   │                            │
│                     │  - conf     │                            │
│                     └─────────────┘                            │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 Core Files

```
skills/world_model/
├── lib/
│   ├── state_reader.sh      # Liest aktuellen Zustand
│   ├── rules_engine.sh      # Wendet Zustandsübergänge an
│   ├── planner.sh           # Einfache Planung
│   └── counterfactual.sh    # What-if Logging
├── data/
│   ├── current_state.json   # Aktueller Zustand
│   └── state_history/       # Historie
├── config/
│   └── rules.json           # Regeldefinitionen
└── world_model.sh           # Main Entry Point
```

---

## 3. Datenstrukturen

### 3.1 Minimal State Format

```json
{
  "mvwm": {
    "version": "0.1.0",
    "timestamp": "2026-03-02T10:30:00Z",
    
    "state": {
      "hour": 10,
      "day_phase": "morning",
      "last_contact_hours_ago": 2.5,
      "pending_tasks": 3,
      "active_goals_count": 2,
      "system_health": "good"
    },
    
    "context": {
      "recent_events": ["skill_completed", "heartbeat"],
      "current_focus": null,
      "human_available": true
    }
  }
}
```

### 3.2 Action Format

```json
{
  "action": {
    "id": "send_morning_greeting",
    "type": "communication",
    "parameters": {
      "template": "morgen_gruss",
      "include_weather": true
    },
    "expected_outcome": {
      "last_contact_hours_ago": 0,
      "human_mood": "positive"
    }
  }
}
```

---

## 4. Implementation Details

### 4.1 State Reader (lib/state_reader.sh)

```bash
#!/bin/bash
# state_reader.sh - Liest den aktuellen Systemzustand

WM_DATA_DIR="${WM_DATA_DIR:-skills/world_model/data}"

read_current_state() {
    local timestamp=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
    local hour=$(date +%H)
    local day_phase=$(get_day_phase "$hour")
    
    # Lese letzten Kontakt
    local last_contact=$(find_last_human_contact)
    local hours_ago=$(calculate_hours_ago "$last_contact")
    
    # Baue State JSON
    jq -n \
        --arg ts "$timestamp" \
        --argjson h "$hour" \
        --arg dp "$day_phase" \
        --argjson lch "$hours_ago" \
        '{
            mvwm: {
                version: "0.1.0",
                timestamp: $ts,
                state: {
                    hour: $h,
                    day_phase: $dp,
                    last_contact_hours_ago: $lch
                }
            }
        }'
}

get_day_phase() {
    local hour="$1"
    if (( hour >= 5 && hour < 12 )); then
        echo "morning"
    elif (( hour >= 12 && hour < 17 )); then
        echo "afternoon"
    elif (( hour >= 17 && hour < 22 )); then
        echo "evening"
    else
        echo "night"
    fi
}
```

### 4.2 Rules Engine (lib/rules_engine.sh)

```bash
#!/bin/bash
# rules_engine.sh - Wendet Regeln auf den aktuellen Zustand an

evaluate_rules() {
    local state="$1"
    local rules="$2"
    
    # Für jede Regel, prüfe Condition
    echo "$rules" | jq -r '.rules[] | @base64' | while read -r rule_b64; do
        local rule=$(echo "$rule_b64" | base64 -d)
        local rule_id=$(echo "$rule" | jq -r '.id')
        local condition=$(echo "$rule" | jq -r '.condition')
        local action=$(echo "$rule" | jq -r '.action')
        local priority=$(echo "$rule" | jq -r '.priority')
        
        if evaluate_condition "$state" "$condition"; then
            jq -n \
                --arg id "$rule_id" \
                --arg action "$action" \
                --argjson priority "$priority" \
                '{matched: true, rule_id: $id, action: $action, priority: $priority}'
        fi
    done | jq -s 'sort_by(.priority) | reverse | .[0] // {matched: false}'
}
```

### 4.3 Main Entry Point (world_model.sh)

```bash
#!/bin/bash
# world_model.sh - Haupt-Einstiegspunkt für das World Model

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WM_DATA_DIR="${WM_DATA_DIR:-$SCRIPT_DIR/data}"
export WM_DATA_DIR

# Source libraries
source "$SCRIPT_DIR/lib/state_reader.sh"
source "$SCRIPT_DIR/lib/rules_engine.sh"

# Default rules
DEFAULT_RULES='{
    "rules": [
        {
            "id": "morning_greeting",
            "condition": {"hour": {">=": 8, "<": 12}, "last_contact_hours_ago": {">": 6}},
            "action": "send_morning_greeting",
            "priority": 0.7
        }
    ]
}'

main() {
    local command="${1:-plan}"
    
    case "$command" in
        "state")
            read_current_state
            ;;
        "plan")
            local state=$(read_current_state)
            local rules=$(cat "${WM_DATA_DIR}/../config/rules.json" 2>/dev/null || echo "$DEFAULT_RULES")
            evaluate_rules "$state" "$rules"
            ;;
        "init")
            mkdir -p "$WM_DATA_DIR"/{states,predictions,counterfactuals}
            echo "$DEFAULT_RULES" > "${WM_DATA_DIR}/../config/rules.json"
            echo "World Model initialized at $WM_DATA_DIR"
            ;;
        *)
            echo "Usage: $0 {state|plan|init}"
            exit 1
            ;;
    esac
}

main "$@"
```

---

## 5. Testing Strategie

### 5.1 Unit Tests

```bash
#!/bin/bash
# test_world_model.sh

test_state_reader() {
    echo "Testing state_reader..."
    
    source lib/state_reader.sh
    
    [[ $(get_day_phase 8) == "morning" ]] || echo "FAIL: morning"
    [[ $(get_day_phase 14) == "afternoon" ]] || echo "FAIL: afternoon"
    [[ $(get_day_phase 20) == "evening" ]] || echo "FAIL: evening"
    [[ $(get_day_phase 2) == "night" ]] || echo "FAIL: night"
    
    echo "State reader tests complete"
}

# Run tests
test_state_reader
echo "All tests complete"
```

---

## 6. Deployment Plan

### 6.1 Phasen

| Phase | Dauer | Deliverable |
|-------|-------|-------------|
| **Phase 1** | 1 Woche | Core Implementation (state_reader, rules_engine) |
| **Phase 2** | 1 Woche | Planner + Integration mit orchestrator_v2 |
| **Phase 3** | 1 Woche | Counterfactual Logging + Tests |
| **Phase 4** | 1 Woche | Dokumentation + Polish |

### 6.2 Integration mit bestehendem System

```bash
# Integration in orchestrator_v2
world_model_recommend() {
    local context="$1"
    local recommendation=$(skills/world_model/world_model.sh plan)
    local action=$(echo "$recommendation" | jq -r '.action')
    local confidence=$(echo "$recommendation" | jq -r '.priority')
    
    if (( $(echo "$confidence > 0.5" | bc -l) )); then
        echo "$action"
    else
        echo "no_action"
    fi
}
```

---

## 7. Erfolgskriterien

### 7.1 MVP Success Criteria

| Kriterium | Messung | Ziel |
|-----------|---------|------|
| **State Accuracy** | Korrekte Zustandserfassung | > 95% |
| **Rule Coverage** | Anteil der Zeit mit matching rule | > 70% |
| **Decision Latency** | Zeit von Trigger zu Empfehlung | < 2s |
| **False Positive Rate** | Falsche Empfehlungen | < 20% |

### 7.2 Exit Criteria für nächste Phase

- MVP läuft stabil für 2 Wochen
- > 50 Entscheidungen getroffen
- < 10% menschliche Korrekturen nötig
- Counterfactual Logs zeigen lernbare Patterns

---

## 8. Zusammenfassung

### 8.1 Was wird geliefert

1. **Vollständige Bash-Implementation** eines minimalen World Models
2. **Integration** mit bestehendem orchestrator_v2
3. **Counterfactual Logging** für zukünftiges Lernen
4. **Tests** für alle Kernkomponenten
5. **Dokumentation** für Erweiterung

### 8.2 Nächste Schritte nach MVP

1. **Statistical Learning**: Häufigkeiten aus Counterfactual Logs lernen
2. **Multi-Step Planning**: Einfacher 2-3 Step Lookahead
3. **Neural Components**: Optionale NN-Integration (Python-Bridge)
4. **Full RSSM**: Komplette RSSM-Architektur mit externer Lib

---

## 9. Referenzen

- Siehe RESEARCH.md für theoretische Grundlagen
- Siehe ARCHITECTURE.md für vollständige Systemarchitektur
