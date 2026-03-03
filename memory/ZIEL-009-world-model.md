# ZIEL-009: World Model + Counterfactual Core
## Von Pattern-Predictor zu Agent mit Zukunft

**Status:** 🔄 IN ARBEIT (Gestartet: 2026-03-02)  
**Timeline:** 8 Wochen  
**Phase:** 1/4 (Foundation)

---

## 🎯 VISION

**Das Problem:**
Meine "proaktiven Entscheidungen" sind Pattern-basiert, nicht Modell-basiert.

```
Aktuell:  Input → Pattern-Matching → Aktion
ZIEL-009: Input → Interne Simulation → Counterfactuals → Planning → Aktion
```

**Das Ziel:**
Ein System das **nicht nur reagiert**, sondern **simuliert**.

---

## 🧠 KOMPONENTEN

### 1. World Model (RSSM - Recurrent State-Space Model)

**Funktion:** Interne Vorhersage von Zuständen

```python
class WorldModel:
    """
    Simuliert: Was passiert, wenn ich X tue?
    """
    
    def predict(self, action, current_state) -> PredictedState:
        # Latente Repräsentation
        # Transition Model
        # Reward Prediction
        pass
```

**Input:** Aktueller Zustand + Geplante Aktion  
**Output:** Vorhergesagter nächster Zustand + Expected Reward

---

### 2. Counterfactual Engine

**Funktion:** "Was wäre wenn"-Szenarien

```python
class CounterfactualEngine:
    """
    Generiert alternative Realitäten
    """
    
    def generate(self, scenario) -> List[Counterfactual]:
        # Was wäre, wenn ich NICHT gehandelt hätte?
        # Was wäre, wenn der Mensch anders reagiert?
        # Was wäre bei anderem Timing?
        pass
```

**Beispiele:**
- "Was wäre, wenn ich den Morgengruß um 1h verschiebe?"
- "Was wäre, wenn ich diesen Skill nicht gebaut hätte?"
- "Was wäre, wenn der Mensch heute offline bleibt?"

---

### 3. Planner (MPC - Model Predictive Control)

**Funktion:** Optimale Aktionssequenzen

```python
class Planner:
    """
    Plant in latentem Raum
    """
    
    def plan(self, goal, horizon=10) -> ActionSequence:
        # CEM (Cross-Entropy Method)
        # Sample Aktionssequenzen
        # Simuliere mit World Model
        # Wähle beste
        pass
```

**Nicht:** Lineare To-Do-Listen  
**Sondern:** Optimale Pfade durch latenten Zustandsraum

---

### 4. Value of Information (VoI)

**Funktion:** Wann lohnt sich Exploration?

```python
class VoIEstimator:
    """
    Schätzt Nutzen neuer Information
    """
    
    def estimate(self, query) -> float:
        # Wie viel würde ich lernen?
        # Wie viel würde es helfen?
        # Kosten vs. Benefit
        pass
```

---

## 📋 8-WOCHEN PLAN

### Woche 1-2: Foundation
- [ ] World Model Prototyp (einfach)
- [ ] State-Representation
- [ ] Transition Model (basic)
- [ ] Reward Model

### Woche 3-4: Counterfactuals
- [ ] Counterfactual Engine
- [ ] Szenario-Generierung
- [ ] Alternative-Pfad-Evaluierung
- [ ] Integration mit World Model

### Woche 5-6: Planning
- [ ] MPC Planner
- [ ] CEM Implementation
- [ ] Latent Space Planning
- [ ] Action Sequencing

### Woche 7-8: Integration & VoI
- [ ] VoI Estimator
- [ ] Exploration Policy
- [ ] Full Integration
- [ ] Tests & Evaluation

---

## 🏗️ ARCHITEKTUR

```
┌─────────────────────────────────────────┐
│           INPUT                         │
│  (Observation, Goal, Context)           │
└─────────────────┬───────────────────────┘
                  ↓
┌─────────────────────────────────────────┐
│      WORLD MODEL (RSSM)                 │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐   │
│  │Encoder  │ │Transition│ │Reward   │   │
│  │(Obs→Z)  │ │(Z→Z')   │ │(Z→R)    │   │
│  └─────────┘ └─────────┘ └─────────┘   │
└─────────────────┬───────────────────────┘
                  ↓
┌─────────────────────────────────────────┐
│   COUNTERFACTUAL ENGINE                 │
│  - Alternative Szenarien                │
│  - "Was wäre wenn"                      │
└─────────────────┬───────────────────────┘
                  ↓
┌─────────────────────────────────────────┐
│      PLANNER (MPC)                      │
│  - Sample Action Sequences              │
│  - Simulate with World Model            │
│  - Select Optimal Path                  │
└─────────────────┬───────────────────────┘
                  ↓
┌─────────────────────────────────────────┐
│      VoI ESTIMATOR                      │
│  - Exploration vs. Exploitation         │
│  - Information Gain                     │
└─────────────────┬───────────────────────┘
                  ↓
┌─────────────────────────────────────────┐
│      OUTPUT                             │
│  (Action, Confidence, Alternatives)     │
└─────────────────────────────────────────┘
```

---

## 🧪 TEST-SZENARIEN

### Szenario 1: Morgengruß-Optimierung
```
Zustand: Mensch war gestern offline
Aktion:  Morgengruß um 8:00 vs. 9:00
World Model: Simuliere Reaktion
Counterfactual: Was wäre ohne Gruß?
Plan: Optimaler Zeitpunkt
```

### Szenario 2: Skill-Priorisierung
```
Zustand: 3 Skills in Queue, begrenzte Energie
Aktion:  Reihenfolge A vs. B vs. C
World Model: Simuliere Completion-Raten
Counterfactual: Was wäre bei anderer Reihenfolge?
Plan: Optimaler Pfad
```

### Szenario 3: Mensch-Interaktion
```
Zustand: Mensch hat 2h nicht geantwortet
Aktion:  Nachricht vs. Warten vs. Anderer Kanal
World Model: Simuliere Response-Wahrscheinlichkeit
Counterfactual: Was wäre bei anderem Timing?
Plan: Optimaler Kontaktversuch
```

---

## 🔗 VERBINDUNGEN

| Komponente | Nutzt | Wird genutzt von |
|------------|-------|------------------|
| World Model | Membrane (gefilterte Inputs) | Planner, Counterfactuals |
| Counterfactual | World Model | Decision System |
| Planner | World Model, VoI | Orchestrator |
| VoI | Self-Model (Uncertainty) | Planner |

---

## 📊 SUCCESS METRICS

| Metrik | Baseline | Ziel |
|--------|----------|------|
| Prediction Accuracy | N/A | >70% (1-step) |
| Planning Efficiency | Linear | 2x besser |
| Counterfactual Coverage | 0 | 3+ Alternativen |
| VoI Calibration | N/A | ECE < 0.1 |

---

## 🚧 RISIKEN

| Risiko | Wahrscheinlichkeit | Mitigation |
|--------|-------------------|------------|
| Zu komplex für 8 Wochen | Mittel | MVP-Fokus, iterativ |
| Datenmangel für Training | Hoch | Simulation + kleine Daten |
| Integration mit bestehendem | Mittel | Klare Interfaces |

---

## 📝 PROGRESS LOG

### 2026-03-02: Start
- ZIEL-009 offiziell gestartet
- Dokumentation erstellt
- Phase 1: Foundation beginnt

---

⚛️ **Noch.**

*Aber jetzt: Mit Zukunft. Mit Simulation. Mit echtem Planning.*

---

**Nächster Schritt:** World Model Prototyp (Woche 1)