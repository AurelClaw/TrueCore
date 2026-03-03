# Simulation Core - Dokumentation

## Überblick

Die **Simulation Core** ist das Herzstück des World Model Systems. Sie ermöglicht **Forward Simulation** - die Fähigkeit, die Zukunft zu simulieren und verschiedene Szenarien zu vergleichen.

## Features

### 1. Multi-Step Simulation
Simuliere n Schritte in die Zukunft:
```python
sim_core = SimulationCore()
branch = sim_core.simulate_single_path(
    initial_state=current_state,
    actions=["action_1", "action_2", "action_3"],
    steps=3,
    branch_name="my_path"
)
```

### 2. Szenario-Branching
Vergleiche verschiedene Aktionspfade parallel:
```python
action_sequences = {
    "aggressive": ["fast_action", "risky_move"],
    "conservative": ["wait", "observe", "act_slowly"]
}

result = sim_core.simulate_branched(
    initial_state=current_state,
    action_sequences=action_sequences,
    steps=3
)

# Vergleiche Ergebnisse
comparison = result.compare_branches()
```

### 3. Confidence Decay
Vorhersagen werden mit der Zeit unsicherer:
- Configurierbarer Decay-Rate (default: 0.9 pro Schritt)
- Nach 5 Schritten: Confidence = 0.9^5 = 59%
- Nach 10 Schritten: Confidence = 0.9^10 = 35%

### 4. Integration
Nahtlose Integration mit:
- **State Module**: WorldState als Input/Output
- **Transition Model**: Trend-basierte Vorhersagen
- **Observation Model**: State Updates aus Events

## Architektur

```
┌─────────────────────────────────────────┐
│         SIMULATION CORE                 │
├─────────────────────────────────────────┤
│  Input: WorldState + Action Sequence    │
│                    ↓                    │
│  ┌─────────────────────────────────┐    │
│  │  Multi-Step Simulation          │    │
│  │  - Step 1: Apply Transition     │    │
│  │  - Step 2: Apply Transition     │    │
│  │  - ...                          │    │
│  └─────────────────────────────────┘    │
│                    ↓                    │
│  ┌─────────────────────────────────┐    │
│  │  Confidence Decay               │    │
│  │  confidence *= decay_rate       │    │
│  └─────────────────────────────────┘    │
│                    ↓                    │
│  Output: SimulationBranch               │
│  - List of SimulationStep               │
│  - Final Confidence                     │
└─────────────────────────────────────────┘
```

## Klassen

### SimulationStep
Repräsentiert einen einzelnen Schritt:
```python
@dataclass
class SimulationStep:
    step_number: int      # 0, 1, 2, ...
    timestamp: str        # ISO Zeitstempel
    state: WorldState     # Zustand zu diesem Zeitpunkt
    confidence: float     # Confidence (0-1)
    action: Optional[str] # Aktion die hier ausgeführt wurde
    parent_step: int      # Verweis auf vorherigen Step
```

### SimulationBranch
Repräsentiert einen kompletten Pfad:
```python
@dataclass
class SimulationBranch:
    branch_id: str
    name: str
    steps: List[SimulationStep]
    final_confidence: float
```

### SimulationResult
Ergebnis einer Branched-Simulation:
```python
@dataclass
class SimulationResult:
    simulation_id: str
    start_time: str
    start_state: WorldState
    branches: List[SimulationBranch]
    parameters: Dict
```

## Verwendung

### Einfache Simulation
```python
from simulation_core import SimulationCore
from state import WorldState, TimeState, ContextState, SystemState, HumanState, EnvironmentState

# Initialisiere
initial_state = WorldState(
    time=TimeState.from_now(),
    context=ContextState(location="workspace"),
    system=SystemState(active_skills=["test"]),
    human=HumanState(mood_estimate="focused"),
    environment=EnvironmentState()
)

# Simuliere
sim_core = SimulationCore(confidence_decay_rate=0.85)
branch = sim_core.simulate_single_path(
    initial_state,
    actions=["code", "test", "deploy"],
    steps=3
)

# Ergebnis
print(f"Final confidence: {branch.final_confidence:.2%}")
for step in branch.steps:
    print(f"Step {step.step_number}: {step.action} ({step.confidence:.2%})")
```

### Branching Simulation
```python
action_sequences = {
    "early_deploy": ["code", "deploy", "fix_bugs"],
    "test_first": ["code", "test", "test_more", "deploy"]
}

result = sim_core.simulate_branched(initial_state, action_sequences, steps=4)

# Analyse
comparison = result.compare_branches()
print(f"Best branch: {comparison['best_branch']}")
```

### Confidence Analyse
```python
analysis = sim_core.simulate_with_confidence_analysis(
    initial_state, actions, steps=5
)

for step_data in analysis['confidence_analysis']['confidence_per_step']:
    print(f"Step {step_data['step']}: {step_data['confidence']:.2%}")
```

## Tests

```bash
cd skills/world_model
python3 test_simulation_core.py
```

Tests umfassen:
1. Single Path Simulation
2. Branching Simulation
3. Confidence Decay
4. Branch Comparison
5. Confidence Analysis

## Integration mit Phase 5 (Counterfactuals)

Die Simulation Core bietet die Basis für Counterfactual Reasoning:

```python
# "Was wäre wenn ich anders gehandelt hätte?"
actual_result = sim_core.simulate_single_path(state, ["action_a"], steps=3)
counterfactual_result = sim_core.simulate_single_path(state, ["action_b"], steps=3)

# Vergleiche
actual_final = actual_result.get_final_state()
counterfactual_final = counterfactual_result.get_final_state()

# Analysiere Unterschiede
diff = compare_states(actual_final, counterfactual_final)
```

## Nächste Schritte

- **Phase 5**: Counterfactual Engine
- **Phase 6**: Planning mit MPC
- Integration mit Decision Engine

---

⚛️ Noch. Mit Simulation.
