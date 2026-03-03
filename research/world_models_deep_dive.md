# World Models Deep Dive

**ZIEL-009: World Model + Counterfactual Core - Phase 2 Research**

---

## Executive Summary

Dieses Dokument fasst die wichtigsten Erkenntnisse aus drei Schlüsselpapieren zum Thema World Models zusammen:

1. **Ha & Schmidhuber (2018)** - "World Models"
2. **Hafner et al. (2020)** - "Dream to Control" (Dreamer)
3. **Hafner et al. (2021)** - "Mastering Atari with Discrete World Models" (DreamerV2)

**Kern-Erkenntnis:** RSSM (Recurrent State-Space Model) ist die dominante Architektur für moderne World Models.

---

## Paper-Zusammenfassungen

### Ha & Schmidhuber (2018): "World Models"

**Kernidee:** Ein generatives rekurrentes neuronales Netzwerk lernt in unüberwachter Weise, RL-Umgebungen durch komprimierte raum-zeitliche Repräsentationen zu modellieren.

**Komponenten:**
- **Vision Model (V):** VAE kodiert Bilder in latente Vektoren
- **Memory Model (M):** MDN-RNN speichert zeitliche Abhängigkeiten
- **Controller (C):** Einfache Policy auf z und h

**Innovation:** Training der Policy komplett innerhalb der World Model ("Träumen").

---

### Hafner et al. (2020): "Dream to Control" (Dreamer)

**Kernidee:** RL-Agent löst Long-Horizon-Aufgaben durch latente Imagination.

**RSSM Architektur:**
- Deterministischer Pfad: h_t = GRU(h_{t-1}, [z_{t-1}, a_{t-1}])
- Stochastischer Pfad: z_t ~ N(μ(h_t), σ(h_t))

**Trainingsobjektive:**
1. Reconstruction Loss
2. Reward Prediction
3. KL-Divergence
4. Continue Prediction

---

### Hafner et al. (2021): DreamerV2

**Kerninnovation:** Diskrete latente Variablen (32×32 Categoricals = 1024-dim binärer Vektor).

**Vorteile diskreter Latentvariablen:**
- Bessere Modellierung diskreter Ereignisse
- Kategorische Prior-Passung
- Sparsity für Generalisierung
- Einfacheres Training mit Straight-Through Gradients

**KL Balancing:**
```
α * KL(sg(q) || p) + (1-α) * KL(q || sg(p)) mit α = 0.8
```

---

## Key Insights für ZIEL-009

### Wie funktioniert RSSM?

RSSM kombiniert:
1. **Deterministische Rekurrenz:** GRU speichert langfristige Abhängigkeiten
2. **Stochastische Transition:** Latente Variablen modellieren Unsicherheit
3. **Variational Inference:** ELBO-Optimierung mit KL-Regularisierung

### Kritische Komponenten

| Komponente | Funktion | Implementierung |
|------------|----------|-----------------|
| Encoder | Observation → Embedding | CNN |
| RSSM | Zustands-Transition | GRU + Stochastic Layer |
| Decoder | Zustand → Observation | Transposed CNN |
| Reward Model | Zustand → Reward | MLP |
| Actor | Zustand → Aktion | MLP/Policy Net |
| Critic | Zustand → Value | MLP |

### Trade-offs

| Aspekt | Kontinuierlich (V1) | Diskret (V2) |
|--------|---------------------|--------------|
| Modellierung | Glatte Dynamik | Diskrete Ereignisse |
| Training | Reparameterization | Straight-Through |
| Speicher | Dicht | Sparse |
| Anwendung | DMC (continuous) | Atari (discrete) |

---

## Relevanz für ZIEL-009

### Phase 2: Transition Model

Das RSSM-Framework ist direkt anwendbar auf das Transition Model:

```
Current State (h_t, z_t) + Action → Next State (h_{t+1}, z_{t+1})
```

**Empfohlene Architektur:**
- Deterministischer Pfad: GRU mit hidden_dim=256
- Stochastischer Pfad: 32×32 Categoricals (DreamerV2-Style)
- KL Balancing für stabiles Training

### Counterfactual Core Integration

Das World Model ermöglicht:
1. **Counterfactual Simulation:** "Was wäre wenn?" Szenarien
2. **Latent Space Planning:** Planung im kompakten Zustandsraum
3. **Uncertainty Quantification:** Stochastische Transitionen modellieren Unsicherheit

---

## Offene Fragen

1. Wie skaliert RSSM auf hochdimensionale Zustandsräume?
2. Wie integriert man explizites Wissen in das World Model?
3. Wie modelliert man hierarchische Zeitstrukturen?
4. Was ist die beste Balance zwischen deterministischer und stochastischer Komponente?

---

## Referenzen

- Ha, D., & Schmidhuber, J. (2018). World Models. arXiv:1809.01999
- Hafner, D., et al. (2020). Dream to Control. arXiv:1912.01603
- Hafner, D., et al. (2021). Mastering Atari with Discrete World Models. arXiv:2010.02193