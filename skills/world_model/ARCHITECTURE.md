# World Model Architektur - ZIEL-009

## Übersicht

Dieses Dokument beschreibt die Architektur des AURELPRO World Model Systems. Das System baut auf den bestehenden 27+ Skills auf und integriert sich mit dem Event-System, dem Orchestrator und dem Proactive Decision Skill.

---

## 1. System-Kontext

### 1.1 Bestehende Infrastruktur

```
┌─────────────────────────────────────────────────────────────────────┐
│                     AURELPRO System Architecture                     │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐              │
│  │   memory/    │  │   events/    │  │   skills/    │              │
│  │  (History)   │  │  (Realtime)  │  │  (Actions)   │              │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘              │
│         │                 │                 │                       │
│         └─────────────────┼─────────────────┘                       │
│                           │                                         │
│                    ┌──────▼───────┐                                │
│                    │ orchestrator │                                │
│                    │     _v2      │                                │
│                    └──────┬───────┘                                │
│                           │                                         │
│         ┌─────────────────┼─────────────────┐                       │
│         │                 │                 │                       │
│  ┌──────▼───────┐  ┌──────▼───────┐  ┌──────▼───────┐              │
│  │  proactive_  │  │   world_     │  │   other_     │              │
│  │  decision    │  │   model      │  │   skills     │              │
│  └──────────────┘  └──────────────┘  └──────────────┘              │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

### 1.2 Datenquellen

Das World Model greift auf folgende Datenquellen zu:

| Quelle | Pfad | Inhalt | Update-Frequenz |
|--------|------|--------|-----------------|
| **Memory** | `memory/YYYY-MM-DD.md` | Tägliche Logs, Entscheidungen | Täglich |
| **Events** | `events/*.json` | System-Events, Triggers | Realtime |
| **Skill-Data** | `skills/*/data/` | Skill-spezifische Daten | Variabel |
| **Goals** | `longterm_goals/` | Aktive Ziele, Fortschritt | Wöchentlich |
| **Patterns** | `pattern_recognition/` | Erkannte Muster | Kontinuierlich |

---

## 2. State Representation

### 2.1 Core State Structure

```json
{
  "world_model": {
    "version": "1.0.0",
    "timestamp": "2026-03-02T10:30:00Z",
    "session_id": "uuid-v4",
    
    "state": {
      "temporal": {
        "current_time": "2026-03-02T10:30:00Z",
        "day_of_week": 1,
        "hour_of_day": 10,
        "phase": "morning",
        "uptime_hours": 48.5
      },
      
      "context": {
        "active_goals": ["ZIEL-009", "ZIEL-004"],
        "current_focus": "world_model_research",
        "last_human_contact": "2026-03-02T08:00:00Z",
        "system_load": "normal",
        "pending_tasks": 3
      },
      
      "environment": {
        "weather": {
          "location": "Shanghai",
          "condition": "clear",
          "temperature": 18,
          "updated": "2026-03-02T08:00:00Z"
        },
        "calendar": {
          "next_event": null,
          "events_today": 0
        }
      },
      
      "internal": {
        "mood": "focused",
        "energy": 0.85,
        "curiosity": 0.72,
        "confidence": 0.91,
        "recent_performance": 0.88
      }
    },
    
    "dynamics": {
      "predicted_next_state": {
        "timestamp": "2026-03-02T11:00:00Z",
        "probability": 0.75,
        "key_changes": ["hour_of_day: 11", "phase: late_morning"]
      },
      "uncertainty": 0.25,
      "prediction_horizon": "1h"
    }
  }
}
```

### 2.2 Action Space

```json
{
  "action_space": {
    "categories": [
      {
        "id": "communication",
        "actions": ["send_message", "react", "remain_silent"],
        "constraints": ["respect_quiet_hours", "avoid_spam"]
      },
      {
        "id": "task_execution",
        "actions": ["execute_skill", "schedule_task", "delegate"],
        "constraints": ["check_dependencies", "respect_priority"]
      },
      {
        "id": "learning",
        "actions": ["research", "update_model", "explore"],
        "constraints": ["relevance_threshold", "resource_limits"]
      },
      {
        "id": "self_improvement",
        "actions": ["refactor_skill", "optimize_pipeline", "create_skill"],
        "constraints": ["test_coverage", "backward_compatible"]
      }
    ]
  }
}
```

### 2.3 Observation Space

```json
{
  "observation_space": {
    "sensors": [
      {
        "id": "heartbeat",
        "type": "periodic",
        "data": "last_check_time, checks_performed",
        "frequency": "30min"
      },
      {
        "id": "events",
        "type": "event_driven",
        "data": "event_type, payload, timestamp",
        "frequency": "realtime"
      },
      {
        "id": "memory_stream",
        "type": "retrospective",
        "data": "daily_summaries, key_decisions",
        "frequency": "daily"
      },
      {
        "id": "skill_feedback",
        "type": "feedback_loop",
        "data": "execution_result, performance_metrics",
        "frequency": "per_execution"
      }
    ]
  }
}
```

---

## 3. World Model Komponenten

### 3.1 Architektur-Diagramm

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        World Model Architecture                          │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                      State Encoder                               │   │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐        │   │
│  │  │  Memory  │  │  Events  │  │  Skills  │  │  Goals   │        │   │
│  │  │  Input   │  │  Input   │  │  Input   │  │  Input   │        │   │
│  │  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘        │   │
│  │       └─────────────┴─────────────┴─────────────┘               │   │
│  │                         │                                       │   │
│  │                    ┌────▼────┐                                  │   │
│  │                    │  Merge  │  →  Latent State z_t             │   │
│  │                    └────┬────┘                                  │   │
│  └─────────────────────────┼───────────────────────────────────────┘   │
│                            │                                            │
│  ┌─────────────────────────▼───────────────────────────────────────┐   │
│  │                    Dynamics Model                                │   │
│  │                                                                  │   │
│  │   h_t = f(h_{t-1}, z_{t-1}, a_{t-1})   [Hidden State Update]    │   │
│  │   ẑ_{t+1} = p(h_t, a_t)                [Next State Prediction]  │   │
│  │                                                                  │   │
│  │   ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │   │
│  │   │   Reward     │  │   Continue   │  │   Value      │         │   │
│  │   │   Model      │  │   Model      │  │   Model      │         │   │
│  │   └──────────────┘  └──────────────┘  └──────────────┘         │   │
│  │                                                                  │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                            │                                            │
│  ┌─────────────────────────▼───────────────────────────────────────┐   │
│  │                    Planning Module                               │   │
│  │                                                                  │   │
│  │   ┌─────────────────────────────────────────────────────────┐   │   │
│  │   │              Counterfactual Engine                       │   │   │
│  │   │                                                          │   │   │
│  │   │  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐  │   │   │
│  │   │  │  What-if    │    │  Scenario   │    │  Decision   │  │   │   │
│  │   │  │  Analysis   │ →  │  Simulation │ →  │  Support    │  │   │   │
│  │   │  └─────────────┘    └─────────────┘    └─────────────┘  │   │   │
│  │   │                                                          │   │   │
│  │   └─────────────────────────────────────────────────────────┘   │   │
│  │                                                                  │   │
│  │   ┌─────────────────────────────────────────────────────────┐   │   │
│  │   │              MPC / CEM Planner                           │   │   │
│  │   │                                                          │   │   │
│  │   │  Sample actions → Simulate → Evaluate → Select best     │   │   │
│  │   │                                                          │   │   │
│  │   └─────────────────────────────────────────────────────────┘   │   │
│  │                                                                  │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                            │                                            │
│                            ▼                                            │
│                    ┌──────────────┐                                    │
│                    │    Action    │                                    │
│                    │   Execution  │                                    │
│                    └──────────────┘                                    │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### 3.2 Modul-Beschreibungen

#### 3.2.1 State Encoder

**Funktion:** Aggregiert Daten aus verschiedenen Quellen in einen konsistenten Latent State.

**Implementation (Bash-Konzept):**
```bash
# Pseudo-code für State Encoding
encode_state() {
    local memory_state=$(read_memory_summary)
    local event_state=$(read_recent_events)
    local skill_state=$(get_skill_status)
    local goal_state=$(get_active_goals)
    
    # Merge zu latent state
    jq -n \
        --arg ms "$memory_state" \
        --arg es "$event_state" \
        --arg ss "$skill_state" \
        --arg gs "$goal_state" \
        '{
            temporal: ($ms | fromjson | .temporal),
            context: ($es | fromjson | .context),
            environment: ($ss | fromjson | .environment),
            internal: merge_internal($ms, $es, $ss, $gs)
        }'
}
```

#### 3.2.2 Dynamics Model

**Funktion:** Vorhersage zukünftiger Zustände basierend auf aktuellem Zustand und Aktionen.

**Rule-basierte Implementation:**
```bash
# Deterministische Zustandsübergänge
predict_next_state() {
    local current_state="$1"
    local action="$2"
    
    case "$action" in
        "wait")
            # Zeitbasierte Updates
            update_temporal "$current_state" "+30min"
            ;;
        "execute_skill")
            # Skill-spezifische Updates
            apply_skill_effects "$current_state" "$action"
            ;;
        "send_message")
            # Kommunikations-Updates
            update_last_contact "$current_state"
            ;;
    esac
}
```

#### 3.2.3 Counterfactual Engine

**Funktion:** Simuliert alternative Szenarien für Entscheidungsunterstützung.

**Implementation:**
```bash
# Counterfactual Simulation
counterfactual_analysis() {
    local current_state="$1"
    local proposed_action="$2"
    
    # Simuliere: Was passiert wenn...
    local outcome_a=$(simulate "$current_state" "$proposed_action" "best_case")
    local outcome_b=$(simulate "$current_state" "$proposed_action" "expected")
    local outcome_c=$(simulate "$current_state" "$proposed_action" "worst_case")
    
    # Vergleiche mit Baseline (keine Aktion)
    local baseline=$(simulate "$current_state" "noop" "expected")
    
    # Berechne Expected Value
    calculate_ev "$outcome_a" "$outcome_b" "$outcome_c" "$baseline"
}
```

#### 3.2.4 Planner (MPC)

**Funktion:** Optimiert Aktionssequenzen über einen Planungshorizont.

**CEM-ähnlicher Ansatz:**
```bash
# Simplifizierter CEM-Planner
plan_actions() {
    local horizon="$1"  # z.B. 3 Schritte
    local iterations="$2"  # z.B. 10
    
    # Initialisiere Aktionsverteilung
    local action_candidates=$(generate_candidates "$horizon" 20)
    
    for i in $(seq 1 $iterations); do
        # Simuliere alle Kandidaten
        local scores=$(simulate_trajectories "$action_candidates")
        
        # Selektiere Top-Performers
        local elite=$(select_elite "$action_candidates" "$scores" 5)
        
        # Aktualisiere Verteilung (simplifiziert)
        action_candidates=$(refine_candidates "$elite" 20)
    done
    
    # Gib beste erste Aktion zurück
    echo "$action_candidates" | head -1
}
```

---

## 4. Interfaces

### 4.1 Orchestrator Interface

```json
{
  "orchestrator_v2_integration": {
    "input": {
      "endpoint": "world_model/predict",
      "method": "POST",
      "payload": {
        "current_context": "object",
        "available_actions": "array",
        "planning_horizon": "string (e.g., '1h', '1d')"
      }
    },
    "output": {
      "recommended_action": "string",
      "confidence": "float (0-1)",
      "alternatives": "array",
      "expected_outcome": "object",
      "counterfactuals": "array"
    }
  }
}
```

### 4.2 Proactive Decision Interface

```json
{
  "proactive_decision_integration": {
    "enhancement": "world_model_enabled",
    "new_capabilities": [
      "predictive_outcome_scoring",
      "counterfactual_comparison",
      "multi_step_planning",
      "uncertainty_quantification"
    ],
    "data_flow": {
      "from_proactive": ["decision_context", "candidate_actions"],
      "to_proactive": ["scored_actions", "recommended_sequence"]
    }
  }
}
```

### 4.3 Event System Interface

```json
{
  "event_system_integration": {
    "subscriptions": [
      "event:skill_executed",
      "event:goal_completed", 
      "event:human_interaction",
      "event:system_alert"
    ],
    "publications": [
      "event:prediction_available",
      "event:anomaly_detected",
      "event:plan_recommendation"
    ]
  }
}
```

---

## 5. Datenfluss

### 5.1 Sequenzdiagramm: Entscheidungsfindung

```
┌─────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│ Trigger │     │   Encoder   │     │   Planner   │     │   Executor  │
└────┬────┘     └──────┬──────┘     └──────┬──────┘     └──────┬──────┘
     │                 │                   │                   │
     │ 1. Request      │                   │                   │
     │────────────────>│                   │                   │
     │                 │                   │                   │
     │                 │ 2. Read Sources   │                   │
     │                 │────┐              │                   │
     │                 │    │ Read memory/ │                   │
     │                 │    │ events/goals │                   │
     │                 │<───┘              │                   │
     │                 │                   │                   │
     │                 │ 3. Encode State   │                   │
     │                 │──────────────────>│                   │
     │                 │                   │                   │
     │                 │                   │ 4. Plan Actions   │
     │                 │                   │────┐              │
     │                 │                   │    │ CEM/Search   │
     │                 │                   │    │ Counterfactual│
     │                 │                   │<───┘              │
     │                 │                   │                   │
     │                 │ 5. Return Action  │                   │
     │                 │<──────────────────│                   │
     │                 │                   │                   │
     │ 6. Execute      │                   │                   │
     │────────────────────────────────────────────────────────>│
     │                 │                   │                   │
     │                 │                   │ 7. Observe Result │
     │                 │<──────────────────────────────────────│
     │                 │                   │                   │
     │ 8. Update Model │                   │                   │
     │────────────────>│                   │                   │
     │                 │                   │                   │
```

---

## 6. Storage & Persistence

### 6.1 Dateistruktur

```
skills/world_model/
├── RESEARCH.md           # Dieses Dokument
├── ARCHITECTURE.md       # Architektur-Dokument
├── POC.md               # Proof-of-Concept Plan
├── config/
│   └── model_config.json # Modell-Parameter
├── data/
│   ├── states/          # Historische Zustände
│   │   └── 2026/
│   ├── predictions/     # Vorhersagen
│   │   └── 2026/
│   └── counterfactuals/ # Counterfactual-Analysen
│       └── 2026/
├── models/
│   ├── dynamics/        # Dynamics Model (rule files)
│   ├── reward/          # Reward Functions
│   └── value/           # Value Functions
└── lib/
    ├── encoder.sh       # State Encoding
    ├── dynamics.sh      # State Transitions
    ├── planner.sh       # MPC/CEM Planning
    └── counterfactual.sh # What-if Analysis
```

### 6.2 State Persistence Format

```json
{
  "state_record": {
    "id": "uuid",
    "timestamp": "ISO8601",
    "encoded_state": { /* latent state */ },
    "observed_action": "action_id",
    "observed_reward": 0.0,
    "next_state_id": "uuid",
    "prediction_error": 0.0,
    "metadata": {
      "source": "heartbeat|event|manual",
      "confidence": 0.95
    }
  }
}
```

---

## 7. Sicherheit & Constraints

### 7.1 Safety Constraints

| Constraint | Beschreibung | Enforcement |
|------------|--------------|-------------|
| **Quiet Hours** | Keine Nachrichten 23:00-08:00 | Hard filter |
| **Rate Limit** | Max 1 proaktive Aktion/30min | Counter |
| **Approval Gate** | Kritische Aktionen → Mensch | Flag + Queue |
| **Rollback** | Fehlgeschlagene Aktionen → Log | Auto-detect |

### 7.2 Counterfactual Safety Check

```bash
# Safety-Check vor Aktion
safety_check() {
    local action="$1"
    local context="$2"
    
    # Check 1: Quiet hours
    if is_quiet_hours && [[ "$action" == *"message"* ]]; then
        return 1  # Block
    fi
    
    # Check 2: Rate limiting
    if check_rate_limit_exceeded; then
        return 1
    fi
    
    # Check 3: Counterfactual Risk Assessment
    local worst_case=$(counterfactual_worst_case "$action" "$context")
    if [[ $(echo "$worst_case < -0.5" | bc) -eq 1 ]]; then
        return 1
    fi
    
    return 0  # Safe
}
```

---

## 8. Evaluierung & Metriken

### 8.1 Performance Metriken

| Metrik | Beschreibung | Zielwert |
|--------|--------------|----------|
| **Prediction Accuracy** | Korrekte Zustandsvorhersagen | > 70% |
| **Planning Success** | Erfolgreiche Aktionssequenzen | > 80% |
| **Decision Latency** | Zeit bis zur Empfehlung | < 5s |
| **Human Satisfaction** | Implizites Feedback | > 0.8 |

### 8.2 Learning Metrics

| Metrik | Beschreibung |
|--------|--------------|
| **Model Update Frequency** | Wie oft wird das Modell aktualisiert |
| **Prediction Error Trend** | Entwicklung der Vorhersagefehler |
| **Exploration Rate** | Anteil explorativer vs. exploitativer Aktionen |

---

## 9. Zukunftserweiterungen

### 9.1 Mögliche Erweiterungen

1. **Neural Components**: Integration kleiner NN für komplexe Patterns
2. **Multi-Task Learning**: Gleichzeitiges Lernen mehrerer Ziele
3. **Hierarchical Planning**: Mehrstufige Planung (Tag/Woche/Monat)
4. **Social Modeling**: Modellierung des Menschen als Agent
5. **Causal Discovery**: Automatisches Lernen kausaler Strukturen

### 9.2 Skalierungsstrategie

```
Phase 1 (POC):    Rule-based dynamics, simple state
Phase 2 (Alpha):  Statistical models, pattern learning  
Phase 3 (Beta):   Neural components, complex planning
Phase 4 (Prod):   Full RSSM, online learning
```
