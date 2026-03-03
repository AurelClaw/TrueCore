# RSSM Architecture Deep Dive

**ZIEL-009: Phase 2 - Transition Model Architecture**

---

## 1. RSSM Overview

RSSM (Recurrent State-Space Model) ist ein latentes Variablenmodell, das deterministische Rekurrenz mit stochastischen Zustandsübergängen kombiniert.

### 1.1 Core Equations

```
# Deterministic Path (Memory)
h_t = f_θ(h_{t-1}, z_{t-1}, a_{t-1})
    = GRU(h_{t-1}, concat[z_{t-1}, a_{t-1}])

# Stochastic Prior (Prediction)
p(z_t | h_t) = N(μ_prior(h_t), σ_prior(h_t))

# Stochastic Posterior (Inference)
q(z_t | h_t, e_t) = N(μ_post(h_t, e_t), σ_post(h_t, e_t))

# Observation Model
p(o_t | h_t, z_t) = Decoder(h_t, z_t)

# Reward Model  
p(r_t | h_t, z_t) = MLP(h_t, z_t)
```

### 1.2 State Representation

Der RSSM-Zustand besteht aus zwei Komponenten:
- **Deterministisch (h_t):** GRU-Zustand, speichert langfristige Abhängigkeiten
- **Stochastisch (z_t):** Latente Variable, modelliert Unsicherheit

---

## 2. Training Objectives

### 2.1 ELBO (Evidence Lower Bound)

```
L_RSSM = Σ_t [ E_q(z_t)[log p(o_t | h_t, z_t)]          // Reconstruction
              + E_q(z_t)[log p(r_t | h_t, z_t)]          // Reward
              - KL(q(z_t | h_t, e_t) || p(z_t | h_t)) ]  // Regularization
```

### 2.2 KL Balancing (DreamerV2)

```
alpha = 0.8
KL_balanced = alpha * KL(stop_grad(q) || p) + (1-alpha) * KL(q || stop_grad(p))
```

**Intuition:**
- Erster Term: Trainiere Prior Richtung Posterior (mehr Gewicht)
- Zweiter Term: Regularisiere Posterior Richtung Prior

---

## 3. Network Architectures

### 3.1 Encoder (Observation → Embedding)

```python
class Encoder(nn.Module):
    def __init__(self, input_shape, embedding_dim=1024):
        super().__init__()
        self.conv1 = nn.Conv2d(3, 32, 4, stride=2)
        self.conv2 = nn.Conv2d(32, 64, 4, stride=2)
        self.conv3 = nn.Conv2d(64, 128, 4, stride=2)
        self.conv4 = nn.Conv2d(128, 256, 4, stride=2)
        self.fc = nn.Linear(256*2*2, embedding_dim)
    
    def forward(self, obs):
        x = F.relu(self.conv1(obs))
        x = F.relu(self.conv2(x))
        x = F.relu(self.conv3(x))
        x = F.relu(self.conv4(x))
        x = x.reshape(x.size(0), -1)
        return self.fc(x)
```

### 3.2 RSSM Core (Continuous)

```python
class RSSM(nn.Module):
    def __init__(self, hidden_dim=256, state_dim=32, action_dim=4):
        super().__init__()
        self.gru = nn.GRUCell(state_dim + action_dim, hidden_dim)
        
        # Prior p(z_t | h_t)
        self.prior_mean = nn.Linear(hidden_dim, state_dim)
        self.prior_std = nn.Linear(hidden_dim, state_dim)
        
        # Posterior q(z_t | h_t, e_t)
        self.posterior_mean = nn.Linear(hidden_dim + embed_dim, state_dim)
        self.posterior_std = nn.Linear(hidden_dim + embed_dim, state_dim)
    
    def forward(self, h_prev, z_prev, a_prev, obs_embed=None):
        h = self.gru(torch.cat([z_prev, a_prev], dim=-1), h_prev)
        
        prior_mean = self.prior_mean(h)
        prior_std = F.softplus(self.prior_std(h)) + 0.1
        
        if obs_embed is not None:
            posterior_input = torch.cat([h, obs_embed], dim=-1)
            post_mean = self.posterior_mean(posterior_input)
            post_std = F.softplus(self.posterior_std(posterior_input)) + 0.1
            z = post_mean + post_std * torch.randn_like(post_std)
            return h, z, (prior_mean, prior_std), (post_mean, post_std)
        else:
            z = prior_mean + prior_std * torch.randn_like(prior_std)
            return h, z, (prior_mean, prior_std), None
```

### 3.3 Discrete RSSM (DreamerV2)

```python
class DiscreteRSSM(nn.Module):
    def __init__(self, hidden_dim=256, num_categories=32, num_classes=32):
        super().__init__()
        self.state_dim = num_categories * num_classes
        self.gru = nn.GRUCell(self.state_dim + action_dim, hidden_dim)
        
        self.prior_logits = nn.Linear(hidden_dim, self.state_dim)
        self.posterior_logits = nn.Linear(hidden_dim + embed_dim, self.state_dim)
    
    def sample_categorical(self, logits):
        # Straight-Through Gradient Estimation
        probs = F.softmax(logits, dim=-1)
        sample = torch.multinomial(probs.view(-1, num_classes), 1)
        one_hot = F.one_hot(sample, num_classes).float()
        # STE: Forward: one_hot, Backward: softmax gradient
        return one_hot + (probs - probs.detach())
```

---

## 4. Imagination Loop

```python
def imagine_trajectory(rssm, actor, initial_state, horizon=15):
    h, z = initial_state
    trajectory = []
    
    for t in range(horizon):
        # Actor predicts action
        action = actor(torch.cat([h, z], dim=-1))
        
        # RSSM predicts next state (using prior)
        h, z, prior, _ = rssm(h, z, action, obs_embed=None)
        
        # Predict reward
        reward = reward_model(h, z)
        
        trajectory.append({
            'h': h, 'z': z, 'action': action, 'reward': reward
        })
    
    return trajectory
```

---

## 5. Hyperparameters

| Parameter | DreamerV1 | DreamerV2 | Empfohlen |
|-----------|-----------|-----------|-----------|
| hidden_dim | 200 | 600 | 256-512 |
| state_dim | 30 | 1024 (32×32) | 32×32 |
| embedding_dim | 1024 | 1024 | 512-1024 |
| KL balance α | - | 0.8 | 0.8 |
| KL free bits | 3.0 | 1.0 | 0.1-1.0 |
| Imagination horizon | 15 | 15 | 15-50 |
| Learning rate | 1e-3 | 1e-4 | 1e-4 |

---

## 6. Key Design Decisions

### 6.1 Continuous vs Discrete Latents

**Continuous (Gaussian):**
- Vorteil: Glatte Interpolation, einfache Gradienten
- Nachteil: Unimodal, schwierig bei diskreten Ereignissen

**Discrete (Categorical):**
- Vorteil: Multimodal, sparsity, bessere Modellierung diskreter Ereignisse
- Nachteil: Straight-Through Gradienten sind biased

### 6.2 Deterministic vs Stochastic Ratio

- **Mehr Determinismus:** Bessere Langzeit-Prädiktion
- **Mehr Stochastizität:** Bessere Unsicherheitsmodellierung
- **Balance:** Typisch 50/50 oder 70/30 (det/stoch)

### 6.3 KL Regularization

- **Zu stark:** Posterior kollabiert zu Prior
- **Zu schwach:** Keine sinnvolle Latentstruktur
