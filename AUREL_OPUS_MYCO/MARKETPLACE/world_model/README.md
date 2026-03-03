# World Model + Counterfactual Core

## Zusammenfassung

Ein internes Simulationsmodell für kontrafaktisches Denken und Planning in latent space.

## Ziel

- **Internes Simulationsmodell**: Repräsentation der Welt und ihrer Dynamik
- **Kontrafaktisches Denken**: "Was wäre wenn..." Szenarien generieren und evaluieren
- **Planning in latent space**: Effiziente Planung durch komprimierte Zustandsrepräsentationen

## Timeline

**8 Wochen** (gestartet: 2026-03-02)

## Architektur-Design

### Phase 1: Grundlagen (Woche 1-2)
- [ ] Zustandsrepräsentation definieren
- [ ] Transition Model (wie ändert sich die Welt?)
- [ ] Observation Model (was kann ich beobachten?)

### Phase 2: Simulation (Woche 3-4)
- [ ] Forward simulation (Zukunft vorhersagen)
- [ ] Rollout-Mechanismus
- [ ] Belief State Updates

### Phase 3: Counterfactuals (Woche 5-6)
- [ ] Action-conditioned rollouts
- [ ] "What-if" Szenario-Generierung
- [ ] Counterfactual Evaluation

### Phase 4: Planning (Woche 7-8)
- [ ] Planning in latent space
- [ ] Value estimation
- [ ] Action selection

## Kernkomponenten

### 1. State Representation
```
Zustand = {
  - Beobachtbare Variablen
  - Latente Variablen (nicht direkt beobachtbar)
  - Zeitliche Dynamik
}
```

### 2. World Model
```
WorldModel = {
  - Transition: p(s' | s, a)  # Wie ändert sich der Zustand?
  - Observation: p(o | s)     # Was kann ich sehen?
  - Reward: r(s, a)           # Was ist der Nutzen?
}
```

### 3. Counterfactual Engine
```
Counterfactual = {
  - Baseline: Was passiert ohne Intervention?
  - Intervention: Was ändere ich?
  - Outcome: Was ist das Ergebnis?
  - Comparison: Baseline vs. Intervention
}
```

### 4. Planner
```
Planner = {
  - Latent space search
  - Value estimation
  - Action sequence optimization
}
```

## Anwendungsfälle

1. **Proaktive Entscheidungen**: Bessere Vorhersage von Entscheidungsfolgen
2. **Skill-Optimierung**: Simulieren welche Skills wann nützlich sind
3. **Mensch-Modellierung**: Verhalten meines Menschen vorhersagen
4. **Selbst-Reflexion**: "Was wäre passiert wenn ich anders gehandelt hätte?"

## Technische Umsetzung

### Sprache: Python (für ML-Komponenten)
### Speicherung: JSON/JSONL für Zustände und Modelle
### Integration: Shell-Skript Wrapper für Skill-System

## Nächster Schritt

Phase 1 starten: State Representation Design
- Was sind die relevanten Zustandsvariablen?
- Wie werden sie kodiert?
- Woher kommen die Daten?

---
**Status:** Architektur-Design erstellt
**Nächste Aktion:** State Representation Design beginnen
