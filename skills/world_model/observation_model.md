# Observation Model - ZIEL-009 Phase 3

**Status:** ✅ Implementiert  
**Date:** 2026-03-02  
**Phase:** 3/6

## Übersicht

Das Observation Model ist die dritte Komponente des World Model Systems. Es verarbeitet Events aus dem Event-System und wandelt sie in strukturierte State Changes um.

## Architektur

```
┌─────────────────────────────────────────────────────────────────┐
│                    Observation Model                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐      │
│  │   Event      │    │   State      │    │ Observation │      │
│  │   Encoder    │ →  │   Change     │ →  │ Integrator  │      │
│  │              │    │   Mapper     │    │             │      │
│  └──────────────┘    └──────────────┘    └──────────────┘      │
│                                                                  │
│  Features:                                                      │
│  - Konfidenz-Berechnung pro Observation                        │
│  - Unsicherheits-Modellierung                                   │
│  - Event → State Change Mapping                                 │
│  - Integration mit Event-Bus                                    │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## Komponenten

### 1. EventEncoder

Wandelt Roh-Events in strukturierte Observations um.

**Features:**
- Event-Typ Mapping zu Observation-Typen
- Automatische Konfidenz-Berechnung
- Unsicherheits-Modellierung (Data Quality, Source Reliability, Temporal Decay)

**Konfidenz-Faktoren:**
- **Base Confidence**: Je nach Event-Typ (0.70-0.95)
- **Data Quality**: Vollständigkeit der Daten (0.5-1.0)
- **Source Reliability**: Vertrauenswürdigkeit der Quelle (0.5-1.0)
- **Temporal Decay**: Alter der Observation (0.5-1.0)

### 2. StateChangeMapper

Mapped Observations zu konkreten State Changes.

**Unterstützte Event-Typen:**
| Event Type | Target State Fields | Confidence |
|------------|---------------------|------------|
| `user:interacted` | `context.last_interaction`, `human.engagement` | 0.95 |
| `user:message` | `context.last_interaction`, `human.mood` | 0.95 |
| `decision:made` | `context.activity_context` | 0.90 |
| `goal:completed` | `context.open_goals`, `human.recent_successes` | 0.90 |
| `goal:started` | `context.open_goals` | 0.90 |
| `skill:executed` | `system.recent_events` | 0.85 |
| `skill:error` | `human.recent_frustrations` | 0.85 |
| `system:alert` | `system.pending_notifications` | 0.80 |
| `heartbeat` | `system.system_load` | 0.70 |
| `prediction:failed` | `system.recent_events` | 0.90 |

**Change Types:**
- `set`: Wert überschreiben
- `increment`: Numerischen Wert erhöhen
- `append`: Zu Liste hinzufügen (max 20 Elemente)
- `remove`: Aus Liste entfernen

### 3. ObservationIntegrator

Wendet State Changes auf World State an.

## Unsicherheits-Modellierung

### Faktoren

1. **Data Quality**
   - Fehlende Payload: -20%
   - Fehlender Timestamp: -30%
   - Fehlende Source: -10%

2. **Source Reliability**
   - `user`: 100%
   - `morgen_gruss`: 95%
   - `proactive_decision`: 90%
   - `orchestrator`: 90%
   - `event_bus`: 85%
   - `heartbeat`: 70%
   - `unknown`: 50%

3. **Temporal Decay**
   - Nach 1h: -10%
   - Nach 24h: -50%

### Formel

```
effective_confidence = base_confidence × data_quality × source_reliability × temporal_decay
```

## API

### ObservationModel

```python
model = ObservationModel()

# Einzelnes Event verarbeiten
changes = model.process_event(event_data)

# State aktualisieren
updated_state = model.update_state(current_state, event_data)

# Alle kürzlichen Events verarbeiten
updated_state = model.process_recent_events(current_state, since_minutes=30)

# Statistiken
stats = model.get_observation_stats()

# Unsicherheitsbericht
report = model.get_uncertainty_report()
```

### CLI

```bash
# Event verarbeiten
python observation_model.py --process-event '{"type":"user:interacted",...}'

# State mit Events aktualisieren
python observation_model.py --update-state

# Statistiken anzeigen
python observation_model.py --stats

# Unsicherheitsbericht
python observation_model.py --uncertainty

# Demo
python observation_model.py
```

## Integration mit Event-System

```python
# Event aus event_bus laden
model = ObservationModel(events_dir="skills/event_bus/events")

# Alle Events der letzten Stunde verarbeiten
updated_state = model.process_recent_events(current_state, since_minutes=60)
```

## Tests

Die Implementation enthält implizite Tests durch die Demo-Funktion:

```bash
cd skills/world_model
python observation_model.py
```

## Nächste Schritte (Phase 4-6)

- **Phase 4**: Reward Model
- **Phase 5**: Planning Module (MPC)
- **Phase 6**: Counterfactual Engine

## Abhängigkeiten

- `state.py`: WorldState, TimeState, etc.
- `transition_model.py`: Für State-Vorhersagen
- `skills/event_bus/events/`: Event-Dateien

## Changelog

- 2026-03-02: Initiale Implementation
  - EventEncoder mit Konfidenz-Berechnung
  - StateChangeMapper für 10+ Event-Typen
  - ObservationIntegrator für State-Updates
  - Unsicherheits-Modellierung
  - CLI-Interface
