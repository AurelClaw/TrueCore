# ZIEL-009: World Model Architektur
## Detaillierte technische Spezifikation

**Status:** 🔄 IN ARBEIT - Phase 1: Architecture Design  
**Datum:** 2026-03-02  
**Ziel:** Klare Interfaces vor Implementation

---

## 🎯 DESIGN PRINZIPIEN

1. **Modularität** - Jede Komponente ist austauschbar
2. **Testbarkeit** - Jede Komponente hat Unit-Tests
3. **Inkrementell** - MVP first, dann erweitern
4. **Integration** - Funktioniert mit bestehendem System

---

## 🏗️ SYSTEM-KOMPONENTEN

### 1. STATE REPRESENTATION

#### 1.1 AurelState (Erweitert)

```python
@dataclass
class WorldModelState:
    """Zustand für World Model."""
    
    # Observable State (was ich sehe)
    observable: Dict[str, Any]
    # Latent State (was ich inferiere)
    latent: torch.Tensor  # z_t
    # Hidden State (RNN memory)
    hidden: torch.Tensor  # h_t
    
    # Meta
    timestamp: datetime
    source: str  # "real" | "predicted" | "counterfactual"

@dataclass  
class AurelState_v2(AurelState):
    """Erweiterter State mit World Model Support."""
    
    # Bestehende Felder bleiben
    
    # Neu: World Model
    wm_state: Optional[WorldModelState] = None
    
    # Neu: Prediction History
    predictions: List[WorldModelState] = field(default_factory=list)
    
    # Neu: Belief State
    belief_uncertainty: float = 1.0  # 0.0 = sicher, 1.0 = unsicher
```

#### 1.2 State Encoder

```python
class StateEncoder(nn.Module):
    """
    Encodiert Observable State → Latent State
    
    Input:  Dict mit verschiedenen Datentypen
    Output: Latent Vector z_t
    """
    
    def __init__(self, latent_dim: int = 32):
        super().__init__()
        
        # Text Encoder (für Messages)
        self.text_encoder = nn.Embedding(vocab_size, 64)
        
        # Numerical Encoder (für Metriken)
        self.numeric_encoder = nn.Linear(10, 32)
        
        # Categorical Encoder (für Kategorien)
        self.categorical_encoder = nn.Embedding(num_categories, 16)
        
        # Fusion → Latent
        self.fusion = nn.Sequential(
            nn.Linear(64 + 32 + 16, 128),
            nn.ReLU(),
            nn.Linear(128, latent_dim)
        )
    
    def forward(self, state: Dict[str, Any]) -> torch.Tensor:
        # Encode verschiedene Modalitäten
        text_z = self.encode_text(state.get('text', ''))
        numeric_z = self.encode_numeric(state.get('metrics', {}))
        cat_z = self.encode_categorical(state.get('category', 0))
        
        # Fusion
        combined = torch.cat([text_z, numeric_z, cat_z], dim=-1)
        latent = self.fusion(combined)
        
        return latent
```

---

### 2. WORLD MODEL (RSSM)

#### 2.1 Recurrent State-Space Model

```python
class RSSM(nn.Module):
    """
    Recurrent State-Space Model
    
    Basierend auf: Hafner et al. "Dream to Control"
    
    Komponenten:
    - Recurrent Model: h_t = f(h_{t-1}, z_{t-1}, a_{t-1})
    - Transition Model: z_t ~ p(z_t | h_t)
    - Observation Model: o_t ~ p(o_t | z_t, h_t)
    - Reward Model: r_t ~ p(r_t | z_t, h_t)
    """
    
    def __init__(
        self,
        latent_dim: int = 32,
        hidden_dim: int = 256,
        action_dim: int = 16
    ):
        super().__init__()
        
        self.latent_dim = latent_dim
        self.hidden_dim = hidden_dim
        self.action_dim = action_dim
        
        # Recurrent Model: h_t = f(h_{t-1}, z_{t-1}, a_{t-1})
        self.recurrent = nn.GRUCell(
            input_size=latent_dim + action_dim,
            hidden_size=hidden_dim
        )
        
        # Transition Model: p(z_t | h_t)
        # Stochastic, modeled as Gaussian
        self.transition = nn.Sequential(
            nn.Linear(hidden_dim, 128),
            nn.ReLU(),
            nn.Linear(128, 2 * latent_dim)  # mean, log_var
        )
        
        # Observation Model: p(o_t | z_t, h_t)
        self.observation = nn.Sequential(
            nn.Linear(latent_dim + hidden_dim, 256),
            nn.ReLU(),
            nn.Linear(256, 512),  # Decoded observation
            nn.ReLU()
        )
        
        # Reward Model: p(r_t | z_t, h_t)
        self.reward = nn.Sequential(
            nn.Linear(latent_dim + hidden_dim, 128),
            nn.ReLU(),
            nn.Linear(128, 1),
            nn.Sigmoid()  # Normalized reward 0-1
        )
    
    def forward(
        self,
        prev_hidden: torch.Tensor,
        prev_latent: torch.Tensor,
        action: torch.Tensor
    ) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        """
        One-step prediction.
        
        Returns:
            hidden_t: New hidden state
            latent_t: New latent state (sampled)
            reward_t: Predicted reward
        """
        # Recurrent update
        rnn_input = torch.cat([prev_latent, action], dim=-1)
        hidden_t = self.recurrent(rnn_input, prev_hidden)
        
        # Transition: sample latent
        transition_params = self.transition(hidden_t)
        mean, log_var = torch.chunk(transition_params, 2, dim=-1)
        
        # Reparameterization trick
        std = torch.exp(0.5 * log_var)
        eps = torch.randn_like(std)
        latent_t = mean + eps * std
        
        # Predict reward
        reward_input = torch.cat([latent_t, hidden_t], dim=-1)
        reward_t = self.reward(reward_input)
        
        return hidden_t, latent_t, reward_t
    
    def imagine(
        self,
        initial_hidden: torch.Tensor,
        initial_latent: torch.Tensor,
        actions: torch.Tensor
    ) -> Tuple[List[torch.Tensor], List[torch.Tensor], List[torch.Tensor]]:
        """
        Rollout imagined trajectory.
        
        Args:
            actions: Sequence of actions [T, action_dim]
        
        Returns:
            hiddens, latents, rewards for each timestep
        """
        hiddens, latents, rewards = [], [], []
        
        h_t, z_t = initial_hidden, initial_latent
        
        for action in actions:
            h_t, z_t, r_t = self.forward(h_t, z_t, action)
            hiddens.append(h_t)
            latents.append(z_t)
            rewards.append(r_t)
        
        return hiddens, latents, rewards
```

---

### 3. COUNTERFACTUAL ENGINE

#### 3.1 Counterfactual Generator

```python
class CounterfactualEngine:
    """
    Generiert alternative Szenarien.
    
    Typen:
    - Action Counterfactual: Was wäre bei anderer Aktion?
    - Temporal Counterfactual: Was wäre bei anderem Timing?
    - Observational Counterfactual: Was wäre bei anderem Input?
    """
    
    def __init__(self, world_model: RSSM):
        self.wm = world_model
    
    def generate_action_counterfactuals(
        self,
        state: WorldModelState,
        taken_action: torch.Tensor,
        alternative_actions: List[torch.Tensor]
    ) -> List[Counterfactual]:
        """
        Vergleiche tatsächliche Aktion mit Alternativen.
        
        Returns:
            Liste von Counterfactuals mit predicted outcomes
        """
        counterfactuals = []
        
        for alt_action in alternative_actions:
            # Simulate alternative
            h_t, z_t, r_t = self.wm(
                state.hidden,
                state.latent,
                alt_action
            )
            
            cf = Counterfactual(
                type="action",
                actual=taken_action,
                alternative=alt_action,
                predicted_reward=r_t.item(),
                predicted_state=WorldModelState(
                    latent=z_t,
                    hidden=h_t,
                    source="counterfactual"
                ),
                regret=None  # Berechnet später
            )
            counterfactuals.append(cf)
        
        # Berechne Regret für jede Alternative
        actual_reward = self._simulate_actual(state, taken_action)
        for cf in counterfactuals:
            cf.regret = actual_reward - cf.predicted_reward
        
        return counterfactuals
    
    def generate_temporal_counterfactuals(
        self,
        state: WorldModelState,
        action: torch.Tensor,
        delays: List[int]  # z.B. [1, 5, 10] Minuten
    ) -> List[Counterfactual]:
        """
        Was wäre, wenn ich später/gefrüher handle?
        """
        counterfactuals = []
        
        for delay in delays:
            # Simuliere: Warte delay Schritte, dann handle
            # State entwickelt sich ohne Aktion
            delayed_state = self._simulate_waiting(state, delay)
            
            # Dann handle
            h_t, z_t, r_t = self.wm(
                delayed_state.hidden,
                delayed_state.latent,
                action
            )
            
            cf = Counterfactual(
                type="temporal",
                delay=delay,
                predicted_reward=r_t.item(),
                predicted_state=WorldModelState(...)
            )
            counterfactuals.append(cf)
        
        return counterfactuals
```

---

### 4. PLANNER (MPC)

#### 4.1 Model Predictive Control

```python
class MPCPlanner:
    """
    Plant optimale Aktionssequenzen.
    
    Nutzt Cross-Entropy Method (CEM):
    1. Sample zufällige Aktionssequenzen
    2. Simuliere mit World Model
    3. Bewerte nach kumulativem Reward
    4. Update Sampling-Distribution (top K%)
    5. Wiederhole
    """
    
    def __init__(
        self,
        world_model: RSSM,
        horizon: int = 10,
        num_samples: int = 1000,
        top_k: int = 100,
        iterations: int = 5
    ):
        self.wm = world_model
        self.horizon = horizon
        self.num_samples = num_samples
        self.top_k = top_k
        self.iterations = iterations
    
    def plan(
        self,
        current_state: WorldModelState,
        goal: Optional[Goal] = None
    ) -> PlannedAction:
        """
        Finde optimale Aktionssequenz.
        """
        # Initialisiere Aktions-Distribution
        action_mean = torch.zeros(self.horizon, self.wm.action_dim)
        action_std = torch.ones(self.horizon, self.wm.action_dim)
        
        for iteration in range(self.iterations):
            # Sample Aktionssequenzen
            actions = self._sample_actions(action_mean, action_std)
            
            # Simuliere alle
            rewards = []
            for action_seq in actions:
                total_reward = self._simulate_sequence(
                    current_state,
                    action_seq,
                    goal
                )
                rewards.append(total_reward)
            
            # Selektiere Top-K
            top_indices = np.argsort(rewards)[-self.top_k:]
            top_actions = actions[top_indices]
            
            # Update Distribution
            action_mean = top_actions.mean(dim=0)
            action_std = top_actions.std(dim=0) + 0.01  # Minimale Std
        
        # Return beste Aktion
        best_action = action_mean[0]  # First action
        
        return PlannedAction(
            action=best_action,
            expected_reward=self._simulate_sequence(
                current_state,
                action_mean,
                goal
            ),
            full_sequence=action_mean,
            confidence=1.0 / (action_std[0].mean().item() + 0.01)
        )
    
    def _simulate_sequence(
        self,
        initial_state: WorldModelState,
        actions: torch.Tensor,
        goal: Optional[Goal]
    ) -> float:
        """
        Simuliere Aktionssequenz, berechne kumulativen Reward.
        """
        h_t, z_t = initial_state.hidden, initial_state.latent
        total_reward = 0.0
        discount = 1.0
        
        for action in actions:
            h_t, z_t, r_t = self.wm(h_t, z_t, action)
            
            # Basis-Reward
            reward = r_t.item()
            
            # Goal-Bonus
            if goal is not None:
                reward += self._goal_bonus(z_t, goal)
            
            total_reward += discount * reward
            discount *= 0.99  # Discount factor
        
        return total_reward
```

---

### 5. VoI ESTIMATOR

#### 5.1 Value of Information

```python
class VoIEstimator:
    """
    Schätzt den Wert neuer Information.
    
    Formel: VoI = E[Value after knowing X] - Value without X
    
    Approximation durch:
    - Information Gain (entropy reduction)
    - Expected improvement in decision quality
    """
    
    def __init__(self, planner: MPCPlanner):
        self.planner = planner
    
    def estimate(
        self,
        current_state: WorldModelState,
        query: InformationQuery
    ) -> VoIResult:
        """
        Schätze Wert einer Informations-Anfrage.
        
        Beispiele:
        - "Wie ist das Wetter morgen?"
        - "Hat der Mensch Zeit?"
        - "Was ist der Status von X?"
        """
        # Current best plan (without new info)
        plan_without = self.planner.plan(current_state)
        value_without = plan_without.expected_reward
        
        # Simulate possible answers
        possible_answers = self._generate_possible_answers(query)
        
        expected_value_with = 0.0
        for answer, prob in possible_answers:
            # Update belief with answer
            updated_state = self._update_belief(current_state, answer)
            
            # Plan with updated belief
            plan_with = self.planner.plan(updated_state)
            
            expected_value_with += prob * plan_with.expected_reward
        
        # VoI
        voi = expected_value_with - value_without
        
        # Kosten (z.B. API-Call, Zeit, Störung)
        cost = self._estimate_cost(query)
        
        return VoIResult(
            value=voi,
            cost=cost,
            net_value=voi - cost,
            should_query=(voi > cost),
            confidence=self._estimate_confidence(possible_answers)
        )
```

---

## 🔌 INTERFACES

### Input Interface

```python
class WorldModelInput:
    """Was das World Model von außen bekommt."""
    
    observation: Dict[str, Any]  # Aktueller Zustand
    action: Optional[torch.Tensor]  # Ausgeführte Aktion (für Training)
    reward: Optional[float]  # Erhaltener Reward (für Training)
```

### Output Interface

```python
class WorldModelOutput:
    """Was das World Model nach außen gibt."""
    
    predicted_state: WorldModelState
    predicted_reward: float
    uncertainty: float
    
    # Für Planning
    imagined_trajectories: List[Trajectory]
    optimal_action: Optional[PlannedAction]
    
    # Für Counterfactuals
    alternatives: List[Counterfactual]
    regret: Optional[float]
```

---

## 🧪 TEST-STRATEGIE

### Unit Tests
- StateEncoder: Korrekte Dimensions
- RSSM: Determinismus bei fixed seed
- Counterfactual: Korrekte Regret-Berechnung
- MPC: Konvergenz zu bekannter Lösung
- VoI: Monotonie (mehr Info ≥ weniger Info)

### Integration Tests
- End-to-End: State → Plan → Action
- Counterfactual: Realität vs. Prediction
- VoI: Sinnvolle Exploration

### Evaluation
- Prediction Accuracy auf Test-Set
- Planning Efficiency vs. Baseline
- Real-World Performance

---

## 📦 IMPLEMENTATION REIHENFOLGE

1. **State Representation** (Tag 1-2)
   - AurelState_v2
   - StateEncoder
   - Tests

2. **RSSM Core** (Tag 3-5)
   - Recurrent Model
   - Transition Model
   - Observation Model
   - Reward Model
   - Tests

3. **Counterfactual Engine** (Tag 6-7)
   - Generator
   - Regret Computation
   - Tests

4. **MPC Planner** (Tag 8-10)
   - CEM Implementation
   - Goal Integration
   - Tests

5. **VoI Estimator** (Tag 11-12)
   - Information Gain
   - Cost Model
   - Tests

6. **Integration** (Tag 13-14)
   - End-to-End Pipeline
   - System Integration
   - Final Tests

---

⚛️ **Noch.**

*Mit Plan. Mit Struktur. Mit Zukunft.*

---

**Nächster Schritt:** State Representation implementieren (Tag 1)