# World Model - Planning Module

Dokumentation für das MPC-basierte Planning Module mit CEM Action Sampling.

## Übersicht

Das Planning Module implementiert Model Predictive Control (MPC) mit Cross-Entropy Method (CEM) für effiziente Aktionsplanung im World Model System.

## Komponenten

### 1. planner.py - MPC Planner

Hauptplanungsmodul mit folgenden Features:

#### ActionSpace
Definiert den verfügbaren Aktionsraum:
- **Communication**: `send_message`, `react_to_message`, `remain_silent`, `schedule_reminder`
- **Task Execution**: `execute_skill`, `schedule_task`, `delegate_task`
- **Learning**: `research_topic`, `update_model`, `explore_new_skill`
- **Self Improvement**: `refactor_skill`, `optimize_pipeline`, `analyze_performance`

#### RewardFunction
Multi-Objective Reward Function mit:
- **Goal Alignment** (30%): Wie gut unterstützt die Aktion aktuelle Ziele?
- **Context Appropriateness** (30%): Zeit- und kontextabhängige Angemessenheit
- **Resource Efficiency** (20%): Effiziente Ressourcennutzung
- **Learning** (20%): Langfristiger Lernwert

#### MPCPlanner
CEM-basierter Planner:
```python
planner = MPCPlanner(
    horizon=3,           # Planungshorizont (Actions)
    n_candidates=20,     # Kandidaten pro Iteration
    n_elite=5,          # Elite-Kandidaten
    n_iterations=5      # CEM Iterationen
)

plan = planner.plan(current_state)
```

**CEM Algorithmus:**
1. Sample zufällige Action-Sequenzen
2. Simuliere jede Sequenz mit Transition Model
3. Bewerte mit Reward Function
4. Selektiere Top-K (Elite)
5. Resample basierend auf Elite-Verteilung
6. Wiederhole für N Iterationen

### 2. voi_estimator.py - Value of Information

Schätzt den Wert zusätzlicher Information:

#### UncertaintyModel
Verfolgt Unsicherheiten über:
- `human_mood`, `human_engagement`
- `system_load`, `pending_tasks`
- `weather`, `calendar_load`

#### VoIEstimator
Berechnet:
- **EVPI**: Expected Value of Perfect Information
- **EVSI**: Expected Value of Sample Information
- **Myopische VoI**: Wert der nächsten Observation

**Observation Actions:**
| Action | Cost | Targets | Confidence Gain |
|--------|------|---------|-----------------|
| check_messages | 0.05 | human_mood, engagement | 0.3 |
| check_calendar | 0.03 | calendar_load | 0.4 |
| check_weather | 0.02 | weather | 0.5 |
| analyze_system | 0.04 | system_load, tasks | 0.35 |
| wait_for_feedback | 0.10 | human_mood, engagement | 0.5 |

## Integration

### Mit Transition Model
```python
from transition_model import TransitionModel
from planner import MPCPlanner

transition_model = TransitionModel()
planner = MPCPlanner(transition_model=transition_model)

# Planung mit Forward Simulation
plan = planner.plan(state)
```

### Mit State Representation
```python
from state import StateCollector, WorldState

collector = StateCollector()
state = collector.collect()

planner = MPCPlanner()
plan = planner.plan(state)
```

### Counterfactual Planning
```python
# Mit Szenario-Analyse
result = planner.plan_with_counterfactuals(state, n_scenarios=3)
# Enthält: best_case, expected, worst_case Pläne
```

## API Reference

### MPCPlanner

#### `__init__(horizon, n_candidates, n_elite, n_iterations, transition_model, reward_function)`

#### `plan(initial_state, context_hints) -> ActionSequence`
Erstellt optimalen Aktionsplan.

**Returns:**
- `actions`: Liste von Action-Objekten
- `total_reward`: Geschätzter Gesamt-Reward
- `trajectory`: Vorhergesagte Zustands-Trajektorie
- `predicted_final_state`: Erwarteter Endzustand

#### `plan_with_counterfactuals(initial_state, n_scenarios) -> Dict`
Planung mit Szenario-Analyse.

### VoIEstimator

#### `estimate_voi_for_action(state, obs_action) -> VoIResult`
Schätzt VoI für eine Observation Action.

#### `rank_observation_actions(state) -> List[VoIResult]`
Rangfolge aller Observation Actions.

#### `should_observe_before_acting(state, threshold) -> (bool, str)`
Entscheidet, ob Observation vor Aktion sinnvoll ist.

#### `compute_evpi(state, n_samples) -> float`
Berechnet Expected Value of Perfect Information.

#### `get_information_policy(state) -> Dict`
Vollständige Informations-Policy.

## CLI Usage

### Planner
```bash
# Einfache Planung
python planner.py --plan --horizon 3

# Mit Counterfactuals
python planner.py --plan --counterfactual

# Mit Trajektorie
python planner.py --plan --show-trajectory
```

### VoI Estimator
```bash
# Unsicherheits-Analyse
python voi_estimator.py --analyze

# Observation Ranking
python voi_estimator.py --rank-observations

# EVPI Berechnung
python voi_estimator.py --evpi

# Komplette Policy
python voi_estimator.py --policy
```

## Beispiel: Komplette Planungspipeline

```python
from state import StateCollector
from transition_model import TransitionModel
from planner import MPCPlanner
from voi_estimator import VoIEstimator

# 1. State sammeln
collector = StateCollector()
state = collector.collect()

# 2. Prüfe, ob Observation sinnvoll ist
voi_estimator = VoIEstimator()
should_observe, obs_action = voi_estimator.should_observe_before_acting(state)

if should_observe:
    print(f"Empfohlene Observation: {obs_action}")
    # Führe Observation durch...

# 3. Erstelle Plan
planner = MPCPlanner(horizon=3, n_iterations=5)
plan = planner.plan(state)

print(f"Plan mit Reward {plan.total_reward:.3f}:")
for i, action in enumerate(plan.actions, 1):
    print(f"  {i}. {action.name} ({action.category})")

# 4. Counterfactual Analyse
result = planner.plan_with_counterfactuals(state)
print(f"Plan Robustheit: {result['comparison']['robustness']:.2f}")
```

## Konfiguration

### Reward Weights anpassen
```python
reward_fn = RewardFunction(goal_weights={
    "productivity": 0.4,
    "learning": 0.3,
    "harmony": 0.2,
    "efficiency": 0.1
})

planner = MPCPlanner(reward_function=reward_fn)
```

### CEM Parameter
- **horizon**: Mehr Schritte = bessere Planung, aber langsamer
- **n_candidates**: Mehr Kandidaten = bessere Exploration
- **n_elite**: Mehr Elite = stabilere Konvergenz
- **n_iterations**: Mehr Iterationen = bessere Optimierung

## Performance

Typische Laufzeiten (auf Standard-Hardware):
- Planung (horizon=3, n_candidates=20, n_iterations=5): ~100-200ms
- VoI Berechnung (n_samples=10): ~50-100ms
- Counterfactual Analysis (3 Szenarien): ~300-500ms

## Erweiterungsmöglichkeiten

1. **Neural Rewards**: Trainierte Reward Functions
2. **Hierarchical Planning**: Mehrstufige Planung
3. **Online Learning**: Adaptives CEM
4. **Multi-Agent**: Koordination mehrerer Agenten
