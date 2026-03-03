# World Model Research - ZIEL-009

## Übersicht

Dieses Dokument fasst die wichtigsten Forschungsergebnisse zu World Models, RSSM (Recurrent State Space Models), Counterfactual Reasoning und Latent Space Planning zusammen. Die Ergebnisse bilden die Grundlage für die Architektur des AURELPRO World Model Systems.

---

## 1. RSSM (Recurrent State Space Model)

### 1.1 Kernkonzept

RSSM ist die dominante Architektur für moderne World Models, entwickelt von Danijar Hafner (DeepMind) für Dreamer/DreamerV3. Die zentrale Idee:

```
┌─────────────────────────────────────────────────────────┐
│                    RSSM Core Loop                        │
├─────────────────────────────────────────────────────────┤
│  h_t = f_φ(h_{t-1}, z_{t-1}, a_{t-1})   [Sequence Model]│
│  z_t ~ q_φ(z_t | h_t, x_t)              [Encoder]       │
│  ẑ_t ~ p_φ(ẑ_t | h_t)                   [Dynamics Pred] │
│  r̂_t ~ p_φ(r̂_t | h_t, z_t)              [Reward Pred]   │
│  ĉ_t ~ p_φ(ĉ_t | h_t, z_t)              [Continue Pred] │
│  x̂_t ~ p_φ(x̂_t | h_t, z_t)              [Decoder]       │
└─────────────────────────────────────────────────────────┘
```

### 1.2 Architektur-Komponenten

| Komponente | Funktion | Implementation |
|------------|----------|----------------|
| **Sequence Model** | Hidden State Transition | GRU/LSTM |
| **Encoder** | Observation → Latent State | CNN/MLP + Gaussian |
| **Dynamics Predictor** | Predicts latent from hidden | MLP + Gaussian |
| **Reward Predictor** | Predicts scalar reward | MLP |
| **Continue Predictor** | Predicts episode termination | MLP |
| **Decoder** | Reconstructs observation | Transposed CNN/MLP |

### 1.3 Training Losses (DreamerV3)

```
L_pred(φ) = -log p_φ(x_t | z_t, h_t)      [Reconstruction]
            -log p_φ(r_t | z_t, h_t)      [Reward]
            -log p_φ(c_t | z_t, h_t)      [Continue]

L_dyn(φ)  = max(1, KL[sg(q_φ(z_t | h_t, x_t)) || p_φ(z_t | h_t)])

L_rep(φ)  = max(1, KL[q_φ(z_t | h_t, x_t) || sg(p_φ(z_t | h_t))])
```

### 1.4 Key Papers

1. **Hafner et al. (2019)** - "Learning Latent Dynamics for Planning from Pixels"
   - Einführung von RSSM
   - PlaNet: Planning in latent space

2. **Hafner et al. (2020)** - "Dream to Control"
   - Actor-Critic learning in imagination
   - Sample-effizientes RL

3. **Hafner et al. (2024)** - "Mastering Diverse Domains through World Models"
   - DreamerV3: State-of-the-art performance
   - Verbesserte Stabilität und Skalierbarkeit

---

## 2. Counterfactual Reasoning

### 2.1 Definition

Counterfactual Reasoning ist die Fähigkeit, alternative Szenarien zu betrachten ("Was wäre wenn?") und kausale Zusammenhänge zu verstehen.

### 2.2 Anwendungen in AI Planning

**Existential Counterfactual Scenarios (∃):**
- Identifiziert minimale Modifikationen, sodass mindestens ein Plan ψ erfüllt
- Nutzung: "Wie müsste ich die Umgebung ändern, um Ziel X zu erreichen?"

**Universal Counterfactual Scenarios (∀):**
- Identifiziert Modifikationen, sodass ALLE Pläne ψ erfüllen
- Nutzung: "Wie stelle ich sicher, dass alle möglichen Aktionen sicher sind?"

### 2.3 Counterfactual Planning in AGI

Basierend auf Pearl's Causal Models:

```
┌────────────────────────────────────────────────────────┐
│           Counterfactual World Model                   │
├────────────────────────────────────────────────────────┤
│  Real World:    s_t ──a_t──> s_{t+1}                   │
│                      │                                 │
│                      ▼                                 │
│  Counterfactual:  s'_t ──a'_t──> s'_{t+1}              │
│                                                         │
│  Intervention: do(X=x)  [Pearl's do-calculus]          │
└────────────────────────────────────────────────────────┘
```

### 2.4 Key Papers

1. **Gigante et al. (2025)** - "Counterfactual Scenarios for Automated Planning"
   - Formale Definition von Counterfactual Scenarios
   - LTLf-basierte Spezifikation
   - PSPACE-completeness results

2. **Everitt et al.** - Causal Influence Diagrams
   - Graphische Repräsentation kausaler Beziehungen
   - Analyse von Agent-Incentives

3. **Pearl (2000)** - "Causality"
   - Fundamentale Arbeit zu Counterfactuals
   - do-calculus für Interventionen

---

## 3. Latent Space Planning & Model Predictive Control

### 3.1 Model Predictive Control (MPC)

**Prinzip:**
```
1. Beobachte aktuellen Zustand z_t
2. Optimiere Aktionssequenz a_{t:t+H} über Horizont H
3. Führe nur erste Aktion a_t aus
4. Wiederhole bei t+1 mit neuer Beobachtung
```

**Vorteile:**
- Robustheit gegen Modellfehler (Re-planning)
- Einfache Integration von Constraints
- Keine Policy-Netzwerk nötig

### 3.2 Cross-Entropy Method (CEM)

Gradient-freie Optimierung für MPC:

```python
# CEM Algorithmus (konzeptuell)
for iteration in range(max_iter):
    # Sample Aktionssequenzen
    actions = sample_from_distribution(mean, std)
    
    # Simuliere in World Model
    rewards = simulate_trajectories(actions, world_model)
    
    # Selektiere Elite-Sequenzen
    elite = top_k(actions, rewards, k=top_k)
    
    # Aktualisiere Verteilung
    mean, std = fit_gaussian(elite)
```

### 3.3 TD-MPC & BS-MPC

**TD-MPC (Temporal Difference MPC):**
- Kombiniert TD-Learning mit MPC
- Latent dynamics model
- Value function für long-term rewards

**BS-MPC (Bisimulation Metric MPC):**
- Verbesserte Stabilität durch Bisimulation Metric Loss
- Expliziter Encoder-Training
- Robuster gegen Noise

### 3.4 Key Papers

1. **Hansen et al. (2022)** - "Temporal Difference Learning for Model Predictive Control"
   - TD-MPC Architektur
   - State-based und image-based tasks

2. **Shimizu & Tomizuka (2024)** - "Bisimulation Metric for Model Predictive Control"
   - BS-MPC mit theoretischen Garantien
   - Verbesserte Robustheit

3. **Williams et al. (2016/2018)** - MPPI
   - Model Predictive Path Integral Control
   - Sampling-basierte Trajektorienoptimierung

---

## 4. World Model Varianten

### 4.1 Vergleichstabelle

| Modell | Architektur | Planning | Stärken |
|--------|-------------|----------|---------|
| **PlaNet** | RSSM + VAE | CEM in latent space | Sample-effizient |
| **Dreamer** | RSSM | Actor-Critic + Imagination | End-to-end RL |
| **DreamerV3** | RSSM v3 | Actor-Critic + Imagination | Skalierbar, stabil |
| **TD-MPC** | Latent dynamics + Q | CEM + Value | Schnell, effizient |
| **BS-MPC** | Latent dynamics + Q | CEM + Bisimulation | Robust, theoretisch fundiert |
| **DINO-WM** | DINOv2 + Transformer | MPC | Generalisiert gut |

### 4.2 DMWM (Dual-Mind World Model) - 2025

Neueste Entwicklung mit zwei Komponenten:
- **RSSM-S1**: Intuitive, schnelle Zustandsübergänge
- **LINN-S2**: Logik-integriertes neuronales Netzwerk für hierarchisches logisches Reasoning

---

## 5. Implikationen für AURELPRO

### 5.1 Wichtige Erkenntnisse

1. **RSSM ist bewährt**: Die Architektur ist in DreamerV3 und TD-MPC erfolgreich
2. **Latent Space Planning ist effizient**: Deutlich schneller als Pixel-space
3. **Counterfactuals für Safety**: Essentiell für robuste Entscheidungen
4. **MPC + World Model**: Kombination aus Planung und Lernen optimal

### 5.2 Für Shell/Bash-Umsetzung relevante Konzepte

- **State Tracking**: Deterministische Zustandsübergänge statt stochastisch
- **Rule-based Planning**: Explizite Regeln statt gelernte Dynamics
- **Counterfactual Simulation**: "What-if" Szenarien durch Skript-Varianten
- **Event-driven Architecture**: Passend zum bestehenden Event-System

---

## 6. Referenzen

### Primäre Quellen

1. Hafner, D., et al. (2019). Learning latent dynamics for planning from pixels. ICML.
2. Hafner, D., et al. (2020). Dream to control: Learning behaviors by latent imagination. ICLR.
3. Hafner, D., et al. (2024). Mastering diverse domains through world models. arXiv.
4. Hansen, N., et al. (2022). Temporal difference learning for model predictive control. ICML.
5. Shimizu, Y., & Tomizuka, M. (2024). Bisimulation metric for model predictive control. arXiv.
6. Gigante, N., et al. (2025). Counterfactual scenarios for automated planning. arXiv.
7. Wang, L., et al. (2025). DMWM: Dual-mind world model with long-term imagination. arXiv.

### Sekundäre Quellen

- Pearl, J. (2000). Causality: Models, reasoning, and inference.
- Sutton, R.S., & Barto, A.G. (2018). Reinforcement Learning: An Introduction.
- Williams, G., et al. (2016). Aggressive driving with model predictive path integral control. ICRA.
