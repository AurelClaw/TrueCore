# Implementation Recommendations for ZIEL-009

**World Model + Counterfactual Core - Phase 2: Transition Model**

---

## 1. MVP Architecture

### 1.1 Core Components

```
┌─────────────────────────────────────────────────────────────────┐
│                    ZIEL-009 WORLD MODEL                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────────────┐  │
│  │   Encoder   │───▶│    RSSM     │───▶│  Decoder (optional) │  │
│  │  (Simple)   │    │  (Core)     │    │                     │  │
│  └─────────────┘    └──────┬──────┘    └─────────────────────┘  │
│                            │                                     │
│              ┌─────────────┼─────────────┐                      │
│              ▼             ▼             ▼                      │
│  ┌───────────────┐ ┌─────────────┐ ┌──────────────┐            │
│  │ Reward Model  │ │ Actor       │ │ Critic       │            │
│  │ (for training)│ │ (Policy)    │ │ (Value)      │            │
│  └───────────────┘ └─────────────┘ └──────────────┘            │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 1.2 Simplified RSSM for MVP

```python
class SimplifiedRSSM(nn.Module):
    """
    Minimal RSSM für ZIEL-009 MVP
    - Discrete latents (DreamerV2 style)
    - KL balancing
    - Straight-through gradients
    """
    def __init__(
        self,
        action_dim: int = 4,
        hidden_dim: int = 256,
        num_categories: int = 32,
        num_classes: int = 32,
        embedding_dim: int = 512
    ):
        super().__init__()
        self.action_dim = action_dim
        self.hidden_dim = hidden_dim
        self.state_dim = num_categories * num_classes
        self.num_categories = num_categories
        self.num_classes = num_classes
        
        # Recurrent core
        self.gru = nn.GRUCell(self.state_dim + action_dim, hidden_dim)
        
        # Prior network
        self.prior_net = nn.Sequential(
            nn.Linear(hidden_dim, 256),
            nn.ReLU(),
            nn.Linear(256, self.state_dim)
        )
        
        # Posterior network (uses observation embedding)
        self.posterior_net = nn.Sequential(
            nn.Linear(hidden_dim + embedding_dim, 256),
            nn.ReLU(),
            nn.Linear(256, self.state_dim)
        )
        
        # Reward predictor (for training signal)
        self.reward_net = nn.Sequential(
            nn.Linear(hidden_dim + self.state_dim, 256),
            nn.ReLU(),
            nn.Linear(256, 1)
        )
    
    def forward(
        self,
        h_prev: torch.Tensor,
        z_prev: torch.Tensor,
        action: torch.Tensor,
        obs_embed: Optional[torch.Tensor] = None
    ):
        # Recurrent update
        h = self.gru(torch.cat([z_prev, action], dim=-1), h_prev)
        
        # Prior (for imagination)
        prior_logits = self.prior_net(h)
        prior_logits = prior_logits.view(-1, self.num_categories, self.num_classes)
        
        if obs_embed is not None:
            # Posterior (for training)
            post_input = torch.cat([h, obs_embed], dim=-1)
            post_logits = self.posterior_net(post_input)
            post_logits = post_logits.view(-1, self.num_categories, self.num_classes)
            
            # Sample with straight-through
            z = self.sample_straight_through(post_logits)
            
            # Predict reward
            reward = self.reward_net(torch.cat([h, z], dim=-1))
            
            return {
                'h': h,
                'z': z,
                'prior_logits': prior_logits,
                'post_logits': post_logits,
                'reward_pred': reward
            }
        else:
            # Imagination mode
            z = self.sample_straight_through(prior_logits)
            return {'h': h, 'z': z, 'prior_logits': prior_logits}
    
    def sample_straight_through(self, logits: torch.Tensor) -> torch.Tensor:
        """Straight-through gradient estimation for categorical sampling."""
        probs = F.softmax(logits, dim=-1)
        
        # One-hot sample (non-differentiable)
        sample = torch.multinomial(probs.view(-1, self.num_classes), 1)
        one_hot = F.one_hot(sample.squeeze(-1), self.num_classes).float()
        one_hot = one_hot.view(-1, self.num_categories, self.num_classes)
        
        # Straight-through: use probs for backward, one_hot for forward
        return one_hot + (probs - probs.detach())
    
    def compute_loss(
        self,
        outputs: Dict[str, torch.Tensor],
        target_reward: torch.Tensor,
        kl_balance_alpha: float = 0.8,
        kl_free_bits: float = 0.1
    ) -> Dict[str, torch.Tensor]:
        """Compute RSSM training losses."""
        
        # KL divergence with balancing
        prior_logits = outputs['prior_logits']
        post_logits = outputs['post_logits']
        
        prior_dist = torch.distributions.Categorical(logits=prior_logits)
        post_dist = torch.distributions.Categorical(logits=post_logits)
        
        # KL balancing
        kl_prior = torch.distributions.kl_divergence(
            torch.distributions.Categorical(logits=post_logits.detach()),
            prior_dist
        ).sum(dim=-1).mean()
        
        kl_post = torch.distributions.kl_divergence(
            post_dist,
            torch.distributions.Categorical(logits=prior_logits.detach())
        ).sum(dim=-1).mean()
        
        kl_loss = kl_balance_alpha * kl_prior + (1 - kl_balance_alpha) * kl_post
        
        # Free bits
        kl_loss = torch.maximum(kl_loss, torch.tensor(kl_free_bits))
        
        # Reward prediction loss
        reward_loss = F.mse_loss(outputs['reward_pred'], target_reward)
        
        return {
            'kl_loss': kl_loss,
            'reward_loss': reward_loss,
            'total_loss': kl_loss + reward_loss
        }
```

---

## 2. Training Pipeline

### 2.1 Data Collection

```python
def collect_experiences(env, rssm, actor, buffer, num_episodes=1000):
    """Collect experiences for world model training."""
    for episode in range(num_episodes):
        obs = env.reset()
        h = torch.zeros(1, rssm.hidden_dim)
        z = torch.zeros(1, rssm.state_dim)
        
        done = False
        while not done:
            # Encode observation
            obs_embed = encoder(obs)
            
            # Get action from actor
            with torch.no_grad():
                state = torch.cat([h, z], dim=-1)
                action = actor(state).sample()
            
            # Step environment
            next_obs, reward, done, info = env.step(action)
            
            # Store transition
            buffer.add({
                'obs': obs,
                'action': action,
                'reward': reward,
                'next_obs': next_obs,
                'done': done
            })
            
            # Update RSSM state
            with torch.no_grad():
                outputs = rssm(h, z, action, obs_embed)
                h, z = outputs['h'], outputs['z']
            
            obs = next_obs
```

### 2.2 World Model Training

```python
def train_world_model(rssm, encoder, buffer, optimizer, batch_size=32):
    """Train RSSM on collected experiences."""
    rssm.train()
    
    # Sample batch
    batch = buffer.sample(batch_size)
    
    # Encode observations
    obs_embed = encoder(batch['obs'])
    
    # Initialize states
    h = torch.zeros(batch_size, rssm.hidden_dim)
    z = torch.zeros(batch_size, rssm.state_dim)
    
    total_loss = 0
    
    # Unroll through sequence
    for t in range(sequence_length):
        outputs = rssm(h, z, batch['actions'][t], obs_embed[t])
        losses = rssm.compute_loss(
            outputs,
            batch['rewards'][t],
            kl_balance_alpha=0.8,
            kl_free_bits=0.1
        )
        total_loss += losses['total_loss']
        
        h, z = outputs['h'], outputs['z']
    
    # Backprop
    optimizer.zero_grad()
    total_loss.backward()
    torch.nn.utils.clip_grad_norm_(rssm.parameters(), 100.0)
    optimizer.step()
    
    return total_loss.item()
```

### 2.3 Behavior Learning (Actor-Critic)

```python
def train_actor_critic(rssm, actor, critic, optimizer_actor, optimizer_critic, 
                       imagination_horizon=15, lambda_return=0.95):
    """Train actor-critic using imagined trajectories."""
    
    # Sample initial states from buffer
    initial_states = sample_initial_states(buffer)
    h, z = initial_states['h'], initial_states['z']
    
    # Imagine trajectories
    imagined_trajectory = []
    for t in range(imagination_horizon):
        state = torch.cat([h, z], dim=-1)
        action = actor(state).sample()
        
        # Predict next state (using prior)
        with torch.no_grad():
            outputs = rssm(h, z, action, obs_embed=None)
            h, z = outputs['h'], outputs['z']
            reward = rssm.reward_net(torch.cat([h, z], dim=-1))
        
        imagined_trajectory.append({
            'state': state,
            'action': action,
            'reward': reward,
            'h': h,
            'z': z
        })
    
    # Compute lambda-returns
    values = [critic(torch.cat([t['h'], t['z']], dim=-1)) 
              for t in imagined_trajectory]
    
    returns = compute_lambda_returns(
        rewards=[t['reward'] for t in imagined_trajectory],
        values=values,
        lambda_=lambda_return
    )
    
    # Critic loss
    critic_loss = sum((v - r.detach()) ** 2 for v, r in zip(values, returns))
    
    # Actor loss (policy gradient + dynamics backprop)
    actor_loss = -sum(returns)  # Simplified
    
    # Update
    optimizer_critic.zero_grad()
    critic_loss.backward()
    optimizer_critic.step()
    
    optimizer_actor.zero_grad()
    actor_loss.backward()
    optimizer_actor.step()
```

---

## 3. Integration mit Counterfactual Core

### 3.1 Counterfactual Simulation

```python
class CounterfactualSimulator:
    """Generate counterfactual trajectories using RSSM."""
    
    def __init__(self, rssm, actor):
        self.rssm = rssm
        self.actor = actor
    
    def simulate_counterfactual(
        self,
        initial_state: Tuple[torch.Tensor, torch.Tensor],
        alternative_action_fn: Callable,
        horizon: int = 15
    ) -> List[Dict]:
        """
        Simulate: "What would happen if I took different actions?"
        """
        h, z = initial_state
        trajectory = []
        
        for t in range(horizon):
            state = torch.cat([h, z], dim=-1)
            
            # Alternative action (counterfactual)
            action = alternative_action_fn(state, t)
            
            # Predict outcome
            with torch.no_grad():
                outputs = self.rssm(h, z, action, obs_embed=None)
                h, z = outputs['h'], outputs['z']
                reward = self.rssm.reward_net(torch.cat([h, z], dim=-1))
            
            trajectory.append({
                'state': state,
                'action': action,
                'predicted_reward': reward,
                'h': h,
                'z': z
            })
        
        return trajectory
    
    def compare_strategies(
        self,
        initial_state: Tuple[torch.Tensor, torch.Tensor],
        strategies: List[Callable],
        horizon: int = 15
    ) -> Dict:
        """Compare multiple counterfactual strategies."""
        results = {}
        
        for i, strategy in enumerate(strategies):
            traj = self.simulate_counterfactual(initial_state, strategy, horizon)
            total_reward = sum(t['predicted_reward'] for t in traj)
            results[f'strategy_{i}'] = {
                'trajectory': traj,
                'expected_return': total_reward
            }
        
        return results
```

---

## 4. Empfohlene Hyperparameter

### 4.1 MVP Configuration

```python
CONFIG = {
    # RSSM
    'hidden_dim': 256,
    'num_categories': 32,
    'num_classes': 32,
    'embedding_dim': 512,
    
    # Training
    'batch_size': 32,
    'sequence_length': 50,
    'learning_rate': 1e-4,
    'grad_clip': 100.0,
    
    # KL
    'kl_balance_alpha': 0.8,
    'kl_free_bits': 0.1,
    
    # Imagination
    'imagination_horizon': 15,
    'lambda_return': 0.95,
    
    # Actor-Critic
    'actor_lr': 8e-5,
    'critic_lr': 8e-5,
    'discount': 0.99,
}
```

---

## 5. Evaluation Metrics

### 5.1 World Model Quality

```python
def evaluate_world_model(rssm, encoder, test_data):
    """Evaluate RSSM prediction quality."""
    metrics = {}
    
    # 1. Reconstruction accuracy (if decoder exists)
    # 2. Reward prediction MSE
    # 3. KL divergence between prior and posterior
    # 4. State consistency over time
    
    return metrics
```

### 5.2 Counterfactual Quality

```python
def evaluate_counterfactuals(simulator, ground_truth_data):
    """Evaluate counterfactual simulation accuracy."""
    metrics = {}
    
    # 1. Prediction accuracy vs actual outcomes
    # 2. Diversity of generated trajectories
    # 3. Computational efficiency
    
    return metrics
```

---

## 6. Next Steps

1. **Implement MVP:** Start mit simplified RSSM
2. **Test auf einfacher Umgebung:** z.B. CartPole oder einfaches Gridworld
3. **Erweitere auf Counterfactuals:** Integriere alternative Aktionen
4. **Skaliere:** Erhöhe Komplexität schrittweise
