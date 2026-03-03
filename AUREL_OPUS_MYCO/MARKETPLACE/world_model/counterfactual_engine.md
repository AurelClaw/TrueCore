# Counterfactual Engine - Dokumentation

## Übersicht

Die Counterfactual Engine ist Phase 5 des AURELPRO World Model Systems (ZIEL-009). Sie ermöglicht "Was wäre wenn"-Analysen und implementiert Pearl's Do-Calculus (vereinfacht) für kausale Inferenz.

## Architektur

```
┌─────────────────────────────────────────────────────────────────┐
│                    Counterfactual Engine                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │              CounterfactualSimulator                     │   │
│  │                                                          │   │
│  │  • simulate_alternative()    → "Was wäre wenn..."       │   │
│  │  • simulate_noop()           → Baseline                 │   │
│  │  • compare_scenarios()       → Szenario-Vergleich       │   │
│  │  • calculate_impact()        → Quantifizierung          │   │
│  │                                                          │   │
│  └─────────────────────────────────────────────────────────┘   │
│                            │                                     │
│  ┌─────────────────────────▼─────────────────────────────────┐   │
│  │                    DoCalculus                              │   │
│  │  (Pearl's Do-Calculus - vereinfacht)                       │   │
│  │                                                          │   │
│  │  • intervene()    → Do(X=x)    Setze Variable            │   │
│  │  • observe()      → P(Y|X=x)   Beobachte                 │   │
│  │  • counterfactual_query() → P(Y_x|X=x',Y=y') CF Query    │   │
│  │                                                          │   │
│  └─────────────────────────────────────────────────────────┘   │
│                            │                                     │
│  ┌─────────────────────────▼─────────────────────────────────┐   │
│  │              Deviation Analysis                            │   │
│  │                                                          │   │
│  │  • deviation_analysis()      → Prediction vs Actual      │   │
│  │  • identify_key_factors()    → Einflussfaktoren          │   │
│  │                                                          │   │
│  └─────────────────────────────────────────────────────────┘   │
│                            │                                     │
│  ┌─────────────────────────▼─────────────────────────────────┐   │
│  │              CounterfactualEngine (High-Level API)         │   │
│  │                                                          │   │
│  │  • what_if()                 → Einfache CF-Abfrage       │   │
│  │  • compare_actions()         → Aktions-Vergleich         │   │
│  │  • analyze_prediction_error()→ Fehleranalyse             │   │
│  │                                                          │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## Hauptkomponenten

### 1. CounterfactualSimulator

Die Hauptklasse für Counterfactual-Simulationen.

#### Methoden

##### `simulate_alternative(state, action, scenario_type, parameters)`
Simuliert ein alternatives Szenario.

```python
scenario = simulator.simulate_alternative(
    state=current_state,
    action="delay_morning_greeting",
    scenario_type=ScenarioType.ALTERNATIVE_ACTION,
    parameters={"delay": "1h"}
)
```

**Parameter:**
- `state`: Ausgangszustand (WorldState)
- `action`: Auszuführende Aktion
- `scenario_type`: Typ des Szenarios (ScenarioType Enum)
- `parameters`: Zusätzliche Parameter als Dict

**Returns:** `CounterfactualScenario`

##### `simulate_noop(state, steps)`
Simuliert Baseline-Szenario (keine Aktion).

```python
baseline = simulator.simulate_noop(current_state, steps=1)
```

##### `compare_scenarios(baseline, alternatives)`
Vergleicht mehrere Szenarien mit einer Baseline.

```python
analyses = simulator.compare_scenarios(baseline, [alternative1, alternative2])
```

##### `calculate_counterfactual_impact(baseline, counterfactual)`
Quantifiziert den Unterschied zwischen zwei Szenarien.

```python
impact = simulator.calculate_counterfactual_impact(baseline, alternative)
# impact.overall_impact → -1 bis +1
# impact.risk_score → 0 bis 1
# impact.opportunity_score → 0 bis 1
```

### 2. DoCalculus

Implementierung von Pearl's Do-Calculus (vereinfacht).

#### Methoden

##### `intervene(state, variable_path, value)`
Führt eine Intervention durch (Do-Operator).

```python
new_state = do_calculus.intervene(
    state=current_state,
    variable_path="human.mood_estimate",
    value="positive"
)
```

##### `observe(state, variable_path)`
Beobachtet eine Variable ohne Intervention.

```python
mood = do_calculus.observe(current_state, "human.mood_estimate")
```

##### `counterfactual_query(state, intervention, outcome_variable)`
Führt eine Counterfactual Query durch.

```python
result = do_calculus.counterfactual_query(
    state=observed_state,
    intervention={"variable": "human.engagement_level", "value": "high"},
    outcome_variable="context.activity_context"
)
# result["explanation"] → "Wäre human.engagement_level = high gewesen, ..."
```

### 3. Deviation Analysis

Analyse der Abweichung zwischen Vorhersage und Realität.

#### Methoden

##### `deviation_analysis(predicted, actual, prediction_id)`
Analysiert Abweichung zwischen Vorhersage und Realität.

```python
analysis = simulator.deviation_analysis(
    predicted=predicted_state,
    actual=actual_state,
    prediction_id="pred_001"
)
# analysis.deviation_score → 0-1
# analysis.explanation → Menschenlesbare Erklärung
# analysis.key_factors → Einflussfaktoren
# analysis.lessons_learned → Gelernte Lektionen
```

##### `identify_key_factors(predicted, actual)`
Identifiziert welche Faktoren die größten Abweichungen verursacht haben.

```python
factors = simulator.identify_key_factors(predicted, actual)
# factors[0] → {"field": "human.mood_estimate", "influence_score": 0.85, ...}
```

### 4. CounterfactualEngine (High-Level API)

Vereinfachte Schnittstelle für häufige Use Cases.

#### Methoden

##### `what_if(state, action, parameters)`
Einfache "Was wäre wenn"-Abfrage.

```python
result = engine.what_if(
    state=current_state,
    action="send_message",
    parameters={"mood": "positive"}
)
# result["impact"] → ImpactAnalysis
# result["recommendation"] → "proceed" oder "reconsider"
```

##### `compare_actions(state, actions, parameters)`
Vergleicht mehrere mögliche Aktionen.

```python
comparison = engine.compare_actions(
    state=current_state,
    actions=["send_message", "wait", "execute_skill"],
    parameters={"send_message": {"mood": "positive"}}
)
# comparison["recommended_action"] → Beste Aktion
# comparison["impacts"] → Impact für jede Aktion
```

##### `analyze_prediction_error(predicted, actual)`
Analysiert warum eine Vorhersage falsch war.

```python
error_analysis = engine.analyze_prediction_error(predicted, actual)
# error_analysis["explanation"] → Warum war die Vorhersage falsch?
# error_analysis["lessons_learned"] → Was können wir lernen?
```

## Scenario Types

| Typ | Beschreibung | Verwendung |
|-----|--------------|------------|
| `BEST_CASE` | Optimistisches Szenario | Upper bound schätzen |
| `EXPECTED` | Baseline-Erwartung | Standard-Vorhersage |
| `WORST_CASE` | Pessimistisches Szenario | Risiko-Assessment |
| `NOOP` | Keine Aktion | Baseline für Vergleiche |
| `ALTERNATIVE_ACTION` | Andere Aktion | Aktionen vergleichen |

## Datenstrukturen

### CounterfactualScenario

```python
@dataclass
class CounterfactualScenario:
    scenario_id: str
    scenario_type: ScenarioType
    name: str
    base_state: WorldState
    interventions: List[Dict[str, Any]]
    predicted_outcome: Optional[WorldState]
    confidence: float
    metadata: Dict[str, Any]
```

### ImpactAnalysis

```python
@dataclass
class ImpactAnalysis:
    baseline_scenario_id: str
    alternative_scenario_id: str
    system_load_delta: float
    notification_delta: int
    mood_change: str  # "improved", "worsened", "unchanged"
    engagement_change: str  # "increased", "decreased", "unchanged"
    risk_score: float  # 0-1
    opportunity_score: float  # 0-1
    overall_impact: float  # -1 bis +1
    key_differences: List[Dict[str, Any]]
    recommendations: List[str]
```

### DeviationAnalysis

```python
@dataclass
class DeviationAnalysis:
    prediction_id: str
    actual_state: WorldState
    predicted_state: WorldState
    deviation_score: float  # 0-1
    temporal_deviation: float
    context_deviation: float
    system_deviation: float
    human_deviation: float
    environment_deviation: float
    key_factors: List[Dict[str, Any]]
    explanation: str
    lessons_learned: List[str]
```

## Beispiel-Nutzung

### Beispiel 1: Morgengruß verschieben

```python
from counterfactual_engine import CounterfactualEngine
from state import WorldState, StateCollector

# Aktuellen Zustand laden
collector = StateCollector()
current_state = collector.collect()

# Engine initialisieren
engine = CounterfactualEngine()

# "Was wäre wenn ich den Morgengruß um 1h verschiebe?"
result = engine.what_if(
    current_state,
    action="delay_morning_greeting",
    parameters={"delay": "1h"}
)

# Ergebnis auswerten
impact = result["impact"]
print(f"Overall Impact: {impact['overall_impact']:+.2f}")
print(f"Risk: {impact['risk_score']:.2f}")
print(f"Opportunity: {impact['opportunity_score']:.2f}")
print(f"Recommendation: {result['recommendation']}")

# Ausgabe:
# Overall Impact: -0.15
# Risk: 0.25
# Opportunity: 0.10
# Recommendation: reconsider
```

### Beispiel 2: Aktionen vergleichen

```python
# Verschiedene Kommunikationsstrategien vergleichen
comparison = engine.compare_actions(
    current_state,
    actions=["send_immediate", "wait_for_response", "send_later"],
    parameters={
        "send_immediate": {"mood": "neutral"},
        "send_later": {"delay": "2h", "mood": "positive"}
    }
)

print(f"Best action: {comparison['recommended_action']}")
for i, action in enumerate(comparison['actions_compared']):
    impact = comparison['impacts'][i]
    print(f"  {action}: impact={impact['overall_impact']:+.2f}")
```

### Beispiel 3: Do-Calculus

```python
from counterfactual_engine import DoCalculus

do = DoCalculus()

# Intervention: Setze Stimmung auf "positive"
intervened_state = do.intervene(
    current_state,
    "human.mood_estimate",
    "positive"
)

# Counterfactual Query
result = do.counterfactual_query(
    current_state,
    intervention={"variable": "context.activity_context", "value": "break"},
    outcome_variable="human.engagement_level"
)

print(result["explanation"])
# Ausgabe: "Wäre context.activity_context = break gewesen, 
#          dann wäre human.engagement_level = low"
```

### Beispiel 4: Abweichungsanalyse

```python
# Vorhersage vs Realität
predicted = transition_model.predict(current_state)
actual = collector.collect()  # Aktueller Zustand

analysis = engine.analyze_prediction_error(predicted, actual)

print(f"Deviation Score: {analysis['deviation_score']:.2f}")
print(f"Explanation: {analysis['explanation']}")
print("\nKey Factors:")
for factor in analysis['key_factors'][:3]:
    print(f"  - {factor['field']} (influence: {factor['influence_score']:.2f})")
```

## Integration

### Mit Transition Model

```python
from transition_model import TransitionModel
from counterfactual_engine import CounterfactualSimulator

transition_model = TransitionModel()
simulator = CounterfactualSimulator(transition_model=transition_model)
```

### Mit Simulation Core

```python
from simulation_core import SimulationCore
from counterfactual_engine import CounterfactualSimulator

sim_core = SimulationCore()
simulator = CounterfactualSimulator(simulation_core=sim_core)
```

### Speicherung

Counterfactuals werden automatisch in `states/counterfactuals/` gespeichert:

```python
# Szenario speichern
filepath = simulator.save_scenario(scenario)

# Szenario laden
scenario = simulator.load_scenario("cf_20260302_123000_abc123")

# Alle gespeicherten Szenarien auflisten
scenarios = simulator.list_saved_scenarios()
```

## Fehlerbehandlung

Die Engine implementiert umfassende Fehlerbehandlung:

```python
try:
    result = engine.what_if(state, action)
except ValueError as e:
    # Ungültige Parameter
    print(f"Invalid parameter: {e}")
except KeyError as e:
    # Ungültiger Variablen-Pfad
    print(f"Invalid path: {e}")
```

## Metriken

### Impact Scoring

Der `overall_impact` wird berechnet als:

```
overall_impact = opportunity_score - risk_score
                + mood_adjustment
                + engagement_adjustment
```

- `+0.2` für verbesserte Stimmung
- `-0.2` für verschlechterte Stimmung
- `+0.15` für erhöhtes Engagement
- `-0.15` für verringertes Engagement

### Deviation Scoring

Der `deviation_score` ist gewichtet:

```
deviation_score = temporal * 0.1
                + context * 0.25
                + system * 0.25
                + human * 0.3
                + environment * 0.1
```

Menschliches Verhalten hat den höchsten Einfluss (30%).

## CLI-Nutzung

```bash
# Demo ausführen
cd skills/world_model
python counterfactual_engine.py

# Tests ausführen
python test_counterfactual_engine.py
```

## Zukünftige Erweiterungen

1. **Komplexere Do-Calculus**: Mehrstufige Interventionen
2. **Lernen von Abweichungen**: Automatische Modell-Anpassung
3. **Mehr Szenario-Typen**: Monte Carlo Simulationen
4. **Visualisierung**: Grafische Darstellung von Counterfactuals

## Referenzen

- Pearl, J. (2009). Causality: Models, Reasoning, and Inference
- World Model Architecture: `ARCHITECTURE.md`
- Phase 1-4: `state.py`, `transition_model.py`, `observation_model.py`, `simulation_core.py`
