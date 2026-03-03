# World Model - SKILL.md

## Beschreibung

Internes Simulationsmodell für kontrafaktisches Denken und Planning in latentem Raum. Das World Model ist das Kernstück der prädiktiven Autonomie in AURELPRO - es ermöglicht dem System, Szenarien zu simulieren, bevor gehandelt wird.

## Verwendung

### State Management (Bash)

```bash
# State initialisieren
cd skills/world_model
./state_manager.sh init

# Aktuellen Zustand anzeigen
./state_manager.sh get

# Spezifischen Wert abfragen
./state_manager.sh get state.internal.energy

# State Change anwenden
./state_manager.sh apply '{"change_type":"user","state_delta":{"human_state":{"engagement_level":"active"}}}'

# Entscheidung aufzeichnen
./state_manager.sh decision "Execute morning greeting"

# Human State aktualisieren
./state_manager.sh human active true
```

### Observation Encoding (Bash)

```bash
# Einzelnes Event encoden
./observation_encoder.sh encode memory/2026-03-02.md

# Alle Events verarbeiten
./observation_encoder.sh batch 100

# Event Sources anzeigen
./observation_encoder.sh sources
```

### Python API

#### State Collection
```python
from state import StateCollector, WorldState

# Zustand sammeln
collector = StateCollector()
state = collector.collect()

# Als JSON speichern
filepath = collector.save(state)

# Letzten Zustand laden
last_state = collector.load_latest()
```

#### Counterfactual Analysis
```python
from counterfactual_engine import CounterfactualEngine

engine = CounterfactualEngine()

# Einfache "Was wäre wenn"-Analyse
result = engine.what_if(
    current_state,
    action="delay_morning_greeting",
    parameters={"delay": "1h"}
)

# Mehrere Aktionen vergleichen
comparison = engine.compare_actions(
    current_state,
    actions=["send_now", "wait_1h", "skip_today"]
)

# Do-Calculus Intervention
new_state = engine.simulator.do_calculus.intervene(
    state,
    variable="human.mood_estimate",
    value="positive"
)
```

#### Planning
```python
from planner import MPCPlanner, ActionSpace, RewardFunction

# Planner initialisieren
planner = MPCPlanner(horizon=3, iterations=10)

# Action Space definieren
action_space = ActionSpace.default()

# Oder custom Action Space
action_space = ActionSpace([
    Action("send_message", type="communication", params={"template": "greeting"}),
    Action("wait", type="temporal", params={"duration": "1h"}),
    Action("execute_skill", type="task", params={"skill": "agi_briefing"})
])

# Planung durchführen
recommended_action = planner.plan(
    current_state=state,
    action_space=action_space,
    objective="maximize_engagement"
)
```

#### Value of Information
```python
from voi_estimator import VOIEstimator

voi = VOIEstimator()

# EVPI: Wert perfekter Information
evpi = voi.expected_value_of_perfect_information(
    state,
    candidate_actions=["action_a", "action_b", "action_c"]
)

# EVSI: Wert zusätzlicher Samples
evsi = voi.expected_value_of_sample_information(
    state,
    proposed_observation="check_human_availability",
    n_samples=10
)

# Information Gain
gain = voi.information_gain(
    prior_state=state,
    observation={"type": "human_response", "value": "positive"}
)
```

## Architektur

### State-Komponenten

```
WorldState
├── temporal: TimeState
│   ├── current_time
│   ├── day_of_week
│   ├── hour_of_day
│   └── phase (morning/afternoon/evening/night)
├── context: ContextState
│   ├── active_goals
│   ├── current_focus
│   ├── last_human_contact
│   ├── system_load
│   └── pending_tasks
├── environment: EnvironmentState
│   ├── weather (location, condition, temperature)
│   └── calendar (next_event, events_today)
├── internal: InternalState
│   ├── mood
│   ├── energy
│   ├── curiosity
│   ├── confidence
│   └── recent_performance
├── human_state: HumanState
│   ├── last_interaction
│   ├── engagement_level
│   └── availability
└── agent_state: AgentState
    ├── active_goals
    ├── recent_decisions
    └── last_skill_execution
```

### Module

| Modul | Datei | Funktion |
|-------|-------|----------|
| State | `state.py` | State-Klassen, Collection, Persistence |
| Transition | `transition_model.py` | Zustandsübergänge, Dynamics |
| Observation | `observation_model.py` | Event Processing, State Changes |
| Simulation | `simulation_core.py` | Forward Simulation |
| Counterfactual | `counterfactual_engine.py` | "Was wäre wenn", Do-Calculus |
| Planning | `planner.py` | MPC/CEM, Action Selection |
| VOI | `voi_estimator.py` | Value of Information |

## Dateien

### Dokumentation
- `RESEARCH.md` - RSSM, Counterfactuals, MPC Research
- `ARCHITECTURE.md` - Vollständige Systemarchitektur
- `POC.md` - Proof-of-Concept Plan
- `PROGRESS.md` - Fortschritts-Tracker
- `state_representation.md` - State Design
- `transition_model.md` - Transition Model
- `observation_model.md` - Observation Model
- `simulation_core.md` - Simulation Core
- `counterfactual_engine.md` - Counterfactual Engine
- `planner.md` - Planning Module

### Implementation (Python)
- `state.py` - State-Klassen (280 Zeilen)
- `transition_model.py` - Transition Model (400 Zeilen)
- `observation_model.py` - Observation Model (420 Zeilen)
- `simulation_core.py` - Simulation Core (320 Zeilen)
- `counterfactual_engine.py` - Counterfactual Engine (1.200 Zeilen)
- `planner.py` - MPC/CEM Planner (650 Zeilen)
- `voi_estimator.py` - VOI Estimator (380 Zeilen)

### Implementation (Shell)
- `observation_encoder.sh` - Event Encoder (350 Zeilen)
- `state_manager.sh` - State Management (320 Zeilen)

### Tests
- `test_observation_model.py` - Observation Tests (15 Tests)
- `test_simulation_core.py` - Simulation Tests (3 Tests)
- `test_counterfactual.py` - Counterfactual Tests (50 Tests)
- `test_counterfactual_engine.py` - Engine Tests (31 Tests)
- `test_planner.py` - Planner Tests (50 Tests)
- `test_observation.sh` - Shell Tests (12 Tests)

## Status

**ZIEL-009: World Model + Counterfactual Core** ✅ **100% ABGESCHLOSSEN**

| Phase | Status | Tests |
|-------|--------|-------|
| Phase 1: State Representation | ✅ Done | - |
| Phase 2: Transition Model | ✅ Done | - |
| Phase 3: Observation Model | ✅ Done | 100% |
| Phase 4: Simulation Core | ✅ Done | 100% |
| Phase 5: Counterfactual Engine | ✅ Done | 100% |
| Phase 6: Planning Module | ✅ Done | 100% |

**Gesamtfortschritt: 100%**

## Features

### ✅ State Representation
- Vollständige State-Dimensionen (temporal, context, environment, internal, human, agent)
- JSON-basierte Persistence
- Historisches Tracking

### ✅ Transition Model
- Rule-based Dynamics
- Deterministische Zustandsübergänge
- Reward/Value Prediction

### ✅ Observation Model
- Multi-Source Event Discovery
- Automatic Type Detection
- State Change Encoding

### ✅ Simulation Core
- Forward Simulation (Single Path & Branching)
- Horizon-basierte Vorhersagen
- Confidence Decay

### ✅ Counterfactual Engine
- Pearl's Do-Calculus (simplified)
- Scenario Simulation (BEST/EXPECTED/WORST/NOOP)
- Impact Analysis
- Deviation Analysis

### ✅ Planning Module
- Cross-Entropy Method (CEM)
- Model Predictive Control (MPC)
- Action Space Management
- Reward Functions

### ✅ Value of Information
- EVPI (Expected Value of Perfect Information)
- EVSI (Expected Value of Sample Information)
- Information Gain (KL-Divergence, Entropy)
- Value of Control (VOC)

## Integration

### Mit orchestrator_v2
```python
# In orchestrator_v2/world_model_bridge.py
from world_model.planner import MPCPlanner
from world_model.state import StateCollector

def get_recommended_action(context):
    state = StateCollector().collect()
    planner = MPCPlanner(horizon=3)
    return planner.plan(state, context.available_actions)
```

### Mit proactive_decision
```python
# In proactive_decision/decision_engine.py
from world_model.counterfactual_engine import CounterfactualEngine

def evaluate_decision_options(state, options):
    engine = CounterfactualEngine()
    return engine.compare_actions(state, options)
```

## Performance

| Operation | Zeit |
|-----------|------|
| State Collection | < 100ms |
| Single Simulation | < 100ms |
| Counterfactual Analysis | < 200ms |
| MPC Planning (10 iter) | < 500ms |
| VOI Estimation | < 100ms |

## Beispiele

### Counterfactual: Morgengruß Timing
```python
engine = CounterfactualEngine()

# Was wäre wenn ich 1h später geschrieben hätte?
result = engine.what_if(
    state,
    action="delay_morning_greeting",
    parameters={"delay": "1h"}
)

# Ergebnis:
# {
#   "impact": {
#     "risk": 0.2,
#     "opportunity": 0.4,
#     "overall_impact": 0.15
#   },
#   "recommendation": "PROCEED",
#   "explanation": "Delay increases opportunity for better timing..."
# }
```

### Planning: Skill-Priorisierung
```python
planner = MPCPlanner(horizon=3)

actions = ActionSpace([
    Action("agi_briefing", priority=0.8),
    Action("pattern_analysis", priority=0.6),
    Action("experience_processing", priority=0.5)
])

best_sequence = planner.plan(state, actions)
# Ergebnis: ["agi_briefing", "experience_processing", "pattern_analysis"]
```

### VOI: Soll ich mehr Information sammeln?
```python
voi = VOIEstimator()

# Lohnt es sich, den Menschen nach Verfügbarkeit zu fragen?
evsi = voi.expected_value_of_sample_information(
    state,
    proposed_observation="check_human_availability",
    cost_of_observation=0.1
)

# Wenn EVSI > cost: Ja, Information sammeln lohnt sich
```

## Roadmap

### ✅ Abgeschlossen (ZIEL-009)
- [x] State Representation
- [x] Transition Model
- [x] Observation Model
- [x] Simulation Core
- [x] Counterfactual Engine
- [x] Planning Module (MPC/CEM)
- [x] Value of Information

### 🔄 Zukünftige Erweiterungen
- [ ] Neural Components (optionale NN-Integration)
- [ ] Online Learning aus Counterfactual-Logs
- [ ] Multi-Task Planning
- [ ] Hierarchical Planning (Tag/Woche/Monat)
- [ ] Social Modeling (Mensch als Agent modellieren)
- [ ] Causal Discovery (automatisches Lernen kausaler Strukturen)

## Troubleshooting

### State nicht gefunden
```bash
# State initialisieren
./state_manager.sh init
```

### Permission Errors
```bash
# Scripts ausführbar machen
chmod +x *.sh
```

### Python Import Errors
```bash
# Von skills/world_model/ ausführen
python3 -c "from state import StateCollector; print('OK')"
```

## Referenzen

- Hafner et al. (2019) - "Learning Latent Dynamics for Planning from Pixels"
- Hafner et al. (2020) - "Dream to Control"
- Hafner et al. (2024) - "Mastering Diverse Domains through World Models"
- Pearl (2000) - "Causality: Models, Reasoning, and Inference"
- Gigante et al. (2025) - "Counterfactual Scenarios for Automated Planning"

---

**Version:** 1.0.0  
**Status:** ✅ Production Ready  
**Letztes Update:** 2026-03-02  
**ZIEL-009 Status:** 100% ABGESCHLOSSEN
