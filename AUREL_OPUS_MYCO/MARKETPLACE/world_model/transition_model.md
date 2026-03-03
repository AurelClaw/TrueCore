# Transition Model - Dokumentation

## Überblick

Das Transition Model ist der zweite Kernkomponente des World Model Systems. Es lernt aus historischen Zustandsübergängen und macht Vorhersagen über zukünftige Zustände.

## Architektur

```
┌─────────────────────────────────────────────────────────────┐
│                    TransitionModel                          │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Baseline   │  │    Trend     │  │   Pattern    │      │
│  │  Prediction  │  │  Detection   │  │   Matching   │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│              PredictedStateStorage                          │
└─────────────────────────────────────────────────────────────┘
```

## Vorhersage-Methoden

### 1. Baseline Prediction (`predict_baseline`)

**Konzept:** Naive Vorhersage - der Zustand bleibt gleich, nur die Zeit wird aktualisiert.

**Verwendung:**
- Fallback wenn keine historischen Daten verfügbar
- Benchmark für komplexere Methoden

**Algorithmus:**
```python
predicted_state = current_state.copy()
predicted_state.time = current_time + timedelta(hours=steps_ahead)
```

### 2. Trend Detection (`predict_with_trends`)

**Konzept:** Lineare Regression auf numerische Werte über historische Transitions.

**Features:**
- System Load Trend
- Temperature Trend
- Pending Notifications Trend

**Algorithmus:**
```python
# Lineare Regression: y = mx + b
m = (n*Σ(xy) - Σx*Σy) / (n*Σ(x²) - (Σx)²)
```

**Voraussetzung:** Mindestens 2 historische Transitions

### 3. Pattern Matching (`predict_with_patterns`)

**Konzept:** Findet ähnliche historische Zustände und extrapoliert deren Änderungen.

**Ähnlichkeits-Metrik:**
- Gleiche Tageszeit: +0.3
- Gleicher Wochentag: +0.2
- Ähnlicher System Load: +0.3
- Ähnliche Skill-Anzahl: +0.2

**Aggregation:**
```python
predicted_change = avg(changes_from_similar_transitions)
```

## API

### TransitionModel

```python
model = TransitionModel(states_dir="/path/to/states")

# Vorhersage
prediction = model.predict(
    current_state=world_state,
    method="pattern",  # "baseline", "trend", oder "pattern"
    steps_ahead=1      # Stunden in die Zukunft
)

# Ähnliche Transitions finden
similar = model.find_similar_transitions(current_state, top_k=3)

# Statistiken
stats = model.get_transition_statistics()
```

### PredictedStateStorage

```python
storage = PredictedStateStorage()

# Vorhersage speichern
filepath = storage.save_prediction(
    predicted_state=prediction,
    method="pattern",
    base_state_timestamp="2026-03-02T10:26:51"
)

# Vorhersagen auflisten
predictions = storage.list_predictions()
```

## CLI Usage

```bash
# Vorhersage mit Pattern-Matching (default)
python transition_model.py --predict --method pattern --steps 1

# Trend-basierte Vorhersage
python transition_model.py --predict --method trend --steps 2

# Statistiken anzeigen
python transition_model.py --stats
```

## Datenformat

### Gespeicherte Vorhersage

```json
{
  "metadata": {
    "prediction_method": "pattern",
    "base_state_timestamp": "2026-03-02T10:26:51",
    "prediction_timestamp": "20260302_113000",
    "version": "1.0"
  },
  "state": {
    "version": "1.0",
    "time": { ... },
    "context": { ... },
    "system": { ... },
    "human": { ... },
    "environment": { ... }
  }
}
```

## Integration mit State Module

```python
from state import StateCollector, WorldState
from transition_model import TransitionModel, PredictedStateStorage

# State sammeln
collector = StateCollector()
current = collector.collect()

# Vorhersage
model = TransitionModel()
predicted = model.predict(current, method="pattern", steps_ahead=1)

# Speichern
storage = PredictedStateStorage()
storage.save_prediction(predicted, "pattern", current.time.timestamp)
```

## Zukünftige Erweiterungen

1. **Machine Learning Model**: Trainiere ein NN auf State Transitions
2. **Uncertainty Quantification**: Konfidenzintervalle für Vorhersagen
3. **Multi-Step Prediction**: Bessere Langzeit-Vorhersagen
4. **Counterfactual Generation**: "Was wäre wenn"-Szenarien

## Version

- **Version:** 1.0
- **Phase:** 2 (Transition Model)
- **Zugehöriges Ziel:** ZIEL-009
