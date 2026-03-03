"""
Hierarchical Reinforcement Learning System für AURELPRO

Basierend auf:
- Options Framework (Sutton et al.)
- MAXQ Decomposition (Dietterich)
- HAM (Hierarchical Abstract Machines)

Angepasst für Goal-basierte Agenten-Architektur.
"""

from __future__ import annotations

import json
import logging
import random
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field, asdict
from enum import Enum, auto
from pathlib import Path
from typing import Any, Callable, Dict, Generic, List, Optional, Protocol, Set, TypeVar, Union
from collections import defaultdict
import copy

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ============================================================================
# TYPES & PROTOCOLS
# ============================================================================

class GoalStatus(Enum):
    """Status eines Ziels im HRL-System."""
    PENDING = auto()
    ACTIVE = auto()
    IN_PROGRESS = auto()
    COMPLETED = auto()
    FAILED = auto()
    ABORTED = auto()


class OptionStatus(Enum):
    """Status einer Option (temporal abstraction)."""
    INITIATING = auto()
    RUNNING = auto()
    TERMINATED = auto()


@dataclass
class State:
    """Zustandsrepräsentation für den Agenten."""
    features: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)
    
    def get(self, key: str, default: Any = None) -> Any:
        return self.features.get(key, default)
    
    def update(self, **kwargs) -> State:
        new_features = {**self.features, **kwargs}
        return State(features=new_features, timestamp=time.time())


@dataclass  
class Action:
    """Aktion im HRL-System."""
    name: str
    params: Dict[str, Any] = field(default_factory=dict)
    
    def __hash__(self) -> int:
        return hash((self.name, tuple(sorted(self.params.items()))))
    
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Action):
            return False
        return self.name == other.name and self.params == other.params


@dataclass
class Reward:
    """Belohnungssignal mit Kontext."""
    value: float
    source: str = "external"
    context: Dict[str, Any] = field(default_factory=dict)
    
    def __float__(self) -> float:
        return float(self.value)


# Type variables for generic components
S = TypeVar('S', bound=State)
A = TypeVar('A', bound=Action)


# ============================================================================
# OPTIONS FRAMEWORK
# ============================================================================

class Option(ABC, Generic[S, A]):
    """
    Eine Option ist eine temporale Abstraktion:
    - I: Initiation set (wann kann die Option gestartet werden?)
    - π: Policy (welche Aktionen wählt die Option?)
    - β: Termination condition (wann endet die Option?)
    
    Basierend auf: Sutton, Precup, Singh (1999)
    """
    
    def __init__(self, name: str, level: int = 0):
        self.name = name
        self.level = level  # Hierarchie-Level
        self.status = OptionStatus.INITIATING
        self.execution_count = 0
        self.total_reward = 0.0
        self.success_count = 0
        
    @abstractmethod
    def can_initiate(self, state: S) -> bool:
        """Prüft ob die Option im aktuellen Zustand gestartet werden kann."""
        pass
    
    @abstractmethod
    def should_terminate(self, state: S) -> bool:
        """Prüft ob die Option beendet werden sollte."""
        pass
    
    @abstractmethod
    def select_action(self, state: S) -> Union[A, 'Option']:
        """Wählt die nächste Aktion oder Sub-Option."""
        pass
    
    def on_initiate(self, state: S) -> None:
        """Wird aufgerufen wenn die Option gestartet wird."""
        self.status = OptionStatus.RUNNING
        self.execution_count += 1
        logger.debug(f"Option '{self.name}' initiated")
    
    def on_terminate(self, state: S, success: bool = True) -> None:
        """Wird aufgerufen wenn die Option endet."""
        self.status = OptionStatus.TERMINATED
        if success:
            self.success_count += 1
        logger.debug(f"Option '{self.name}' terminated (success={success})")
    
    def get_q_value(self, state: S) -> float:
        """Geschätzter Q-Wert für diese Option."""
        # Baseline: Durchschnittlicher Reward pro Ausführung
        if self.execution_count == 0:
            return 0.0
        return self.total_reward / self.execution_count
    
    def update_stats(self, reward: float) -> None:
        """Aktualisiert Statistiken nach Ausführung."""
        self.total_reward += reward
    
    def __repr__(self) -> str:
        return f"Option({self.name}, level={self.level})"


class PrimitiveOption(Option[S, A]):
    """
    Eine primitive Option entspricht einer atomaren Aktion.
    Führt genau eine Aktion aus und terminiert sofort.
    """
    
    def __init__(self, action: A, level: int = 0):
        super().__init__(f"primitive:{action.name}", level)
        self.action = action
        
    def can_initiate(self, state: S) -> bool:
        return True  # Primitive Aktionen sind immer verfügbar
    
    def should_terminate(self, state: S) -> bool:
        return True  # Terminieren sofort nach Ausführung
    
    def select_action(self, state: S) -> A:
        return self.action


class CompositeOption(Option[S, A]):
    """
    Eine zusammengesetzte Option führt eine Sequenz von Sub-Optionen aus.
    Implementiert ein Sub-Goal mit eigener Policy.
    """
    
    def __init__(self, name: str, sub_options: List[Option[S, A]], level: int = 1):
        super().__init__(name, level)
        self.sub_options = sub_options
        self.current_sub_option_idx = 0
        self.current_sub_option: Optional[Option[S, A]] = None
        self.sub_goal: Optional[Callable[[S], bool]] = None
        
    def set_sub_goal(self, goal_fn: Callable[[S], bool]) -> None:
        """Setzt ein explizites Sub-Goal für diese Option."""
        self.sub_goal = goal_fn
        
    def can_initiate(self, state: S) -> bool:
        if not self.sub_options:
            return False
        return self.sub_options[0].can_initiate(state)
    
    def should_terminate(self, state: S) -> bool:
        # Terminiere wenn Sub-Goal erreicht oder alle Sub-Optionen ausgeführt
        if self.sub_goal and self.sub_goal(state):
            return True
        return self.current_sub_option_idx >= len(self.sub_options)
    
    def select_action(self, state: S) -> Union[A, Option[S, A]]:
        # Check if current sub-option is done and we need to advance
        if self.current_sub_option is not None and self.current_sub_option.status == OptionStatus.TERMINATED:
            # Current option terminated, move to next
            self.current_sub_option = None
        
        # If no current option, get the next one
        if self.current_sub_option is None:
            if self.current_sub_option_idx < len(self.sub_options):
                self.current_sub_option = self.sub_options[self.current_sub_option_idx]
                self.current_sub_option_idx += 1
                self.current_sub_option.on_initiate(state)
        
        if self.current_sub_option:
            # If the sub-option is primitive, it returns an action directly
            # If composite, it may return another option or action
            result = self.current_sub_option.select_action(state)
            return result
        
        raise RuntimeError(f"Option '{self.name}' has no available sub-options")
    
    def on_initiate(self, state: S) -> None:
        super().on_initiate(state)
        self.current_sub_option_idx = 0
        self.current_sub_option = None
    
    def on_terminate(self, state: S, success: bool = True) -> None:
        super().on_terminate(state, success)
        self.current_sub_option_idx = 0
        self.current_sub_option = None


# ============================================================================
# MAXQ DECOMPOSITION
# ============================================================================

@dataclass
class MaxQNode:
    """
    Ein Knoten im MAXQ-Hierarchie-Baum.
    
    MAXQ dekomponiert den Wert einer zusammengesetzten Aktion:
    V*(i, s) = V^π(i, s) + Σ P(s'|s,i) * V*(a(i), s')
    
    wobei:
    - V^π(i, s): Completion value (Wert nach Ausführung von i)
    - V*(a(i), s): Wert der gewählten Sub-Aktion
    """
    name: str
    is_primitive: bool = False
    children: List[MaxQNode] = field(default_factory=list)
    parent: Optional[MaxQNode] = None
    
    # Value function estimates
    v_values: Dict[str, float] = field(default_factory=dict)  # V^π(i, s)
    c_values: Dict[str, float] = field(default_factory=dict)  # Completion values
    
    def get_v_value(self, state_key: str) -> float:
        return self.v_values.get(state_key, 0.0)
    
    def get_c_value(self, state_key: str, child_name: str) -> float:
        key = f"{state_key}:{child_name}"
        return self.c_values.get(key, 0.0)
    
    def update_v(self, state_key: str, value: float, alpha: float = 0.1) -> None:
        """Setzt den V-Wert direkt (für Tests und initiale Werte)."""
        self.v_values[state_key] = value
    
    def update_c(self, state_key: str, child_name: str, value: float, alpha: float = 0.1) -> None:
        """Setzt den C-Wert direkt (für Tests und initiale Werte)."""
        key = f"{state_key}:{child_name}"
        self.c_values[key] = value
    
    def get_maxq_value(self, state_key: str) -> float:
        """
        Berechnet V*(i, s) = V^π(i, s) + max_j C*(i, s, j)
        """
        if self.is_primitive:
            return self.get_v_value(state_key)
        
        v_pi = self.get_v_value(state_key)
        max_c = max(
            (self.get_c_value(state_key, child.name) for child in self.children),
            default=0.0
        )
        return v_pi + max_c


class MaxQHierarchy:
    """
    MAXQ Hierarchie für dekompositionelles Lernen.
    """
    
    def __init__(self, root: MaxQNode):
        self.root = root
        self.nodes: Dict[str, MaxQNode] = {}
        self._index_nodes(root)
        
    def _index_nodes(self, node: MaxQNode) -> None:
        self.nodes[node.name] = node
        for child in node.children:
            child.parent = node
            self._index_nodes(child)
    
    def get_node(self, name: str) -> Optional[MaxQNode]:
        return self.nodes.get(name)
    
    def evaluate(self, node_name: str, state_key: str) -> float:
        """Evaluiert den Wert eines Knotens im aktuellen Zustand."""
        node = self.get_node(node_name)
        if node is None:
            return 0.0
        return node.get_maxq_value(state_key)
    
    def update_path(self, path: List[str], state_key: str, reward: float, alpha: float = 0.1) -> None:
        """
        Aktualisiert alle Knoten entlang eines Pfads mit einem Reward.
        """
        for i, node_name in enumerate(path):
            node = self.get_node(node_name)
            if node is None:
                continue
            
            if i < len(path) - 1:
                # Update completion value
                next_node = path[i + 1]
                node.update_c(state_key, next_node, reward, alpha)
            else:
                # Leaf node: update V value
                node.update_v(state_key, reward, alpha)


# ============================================================================
# GOAL HIERARCHY
# ============================================================================

@dataclass
class Goal:
    """
    Ein Ziel im hierarchischen System.
    """
    id: str
    name: str
    description: str = ""
    parent_id: Optional[str] = None
    sub_goals: List[str] = field(default_factory=list)
    priority: float = 1.0
    deadline: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # HRL-specific
    associated_option: Optional[str] = None
    success_criteria: Optional[Callable[[State], bool]] = None
    
    def __post_init__(self):
        if self.success_criteria is None:
            self.success_criteria = lambda s: False
    
    def is_achieved(self, state: State) -> bool:
        if self.success_criteria:
            return self.success_criteria(state)
        return False
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "parent_id": self.parent_id,
            "sub_goals": self.sub_goals,
            "priority": self.priority,
            "deadline": self.deadline,
            "metadata": self.metadata,
            "associated_option": self.associated_option,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Goal:
        # Remove fields that can't be serialized
        data = {k: v for k, v in data.items() if k != "success_criteria"}
        return cls(**data)


class GoalHierarchy:
    """
    Verwaltet eine Hierarchie von Zielen.
    """
    
    def __init__(self):
        self.goals: Dict[str, Goal] = {}
        self.root_goals: Set[str] = set()
        self._status: Dict[str, GoalStatus] = {}
        
    def add_goal(self, goal: Goal) -> None:
        self.goals[goal.id] = goal
        self._status[goal.id] = GoalStatus.PENDING
        
        if goal.parent_id is None:
            self.root_goals.add(goal.id)
        else:
            parent = self.goals.get(goal.parent_id)
            if parent:
                parent.sub_goals.append(goal.id)
    
    def get_goal(self, goal_id: str) -> Optional[Goal]:
        return self.goals.get(goal_id)
    
    def get_status(self, goal_id: str) -> GoalStatus:
        return self._status.get(goal_id, GoalStatus.PENDING)
    
    def set_status(self, goal_id: str, status: GoalStatus) -> None:
        self._status[goal_id] = status
        
        # Propagate to parent
        goal = self.goals.get(goal_id)
        if goal and goal.parent_id:
            self._update_parent_status(goal.parent_id)
    
    def _update_parent_status(self, parent_id: str) -> None:
        parent = self.goals.get(parent_id)
        if not parent:
            return
        
        sub_statuses = [self.get_status(gid) for gid in parent.sub_goals]
        
        if all(s == GoalStatus.COMPLETED for s in sub_statuses):
            self._status[parent_id] = GoalStatus.COMPLETED
        elif any(s == GoalStatus.ACTIVE or s == GoalStatus.IN_PROGRESS for s in sub_statuses):
            self._status[parent_id] = GoalStatus.IN_PROGRESS
        elif any(s == GoalStatus.FAILED for s in sub_statuses):
            self._status[parent_id] = GoalStatus.FAILED
    
    def get_active_path(self, goal_id: str) -> List[str]:
        """Gibt den aktiven Pfad von einem Ziel zu seinen aktiven Sub-Zielen."""
        path = [goal_id]
        goal = self.goals.get(goal_id)
        
        if not goal:
            return path
        
        # Finde aktives Sub-Ziel
        for sub_id in goal.sub_goals:
            status = self.get_status(sub_id)
            if status in (GoalStatus.ACTIVE, GoalStatus.IN_PROGRESS):
                path.extend(self.get_active_path(sub_id))
                break
        
        return path
    
    def get_ready_subgoals(self, goal_id: str) -> List[str]:
        """Gibt Sub-Ziele zurück die bereit sind ausgeführt zu werden."""
        goal = self.goals.get(goal_id)
        if not goal:
            return []
        
        ready = []
        for sub_id in goal.sub_goals:
            status = self.get_status(sub_id)
            if status == GoalStatus.PENDING:
                # Prüfe ob alle Vorgänger abgeschlossen sind
                # (einfache sequentielle Abhängigkeit)
                ready.append(sub_id)
        
        return ready
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "goals": {gid: g.to_dict() for gid, g in self.goals.items()},
            "root_goals": list(self.root_goals),
            "status": {gid: s.name for gid, s in self._status.items()},
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> GoalHierarchy:
        hierarchy = cls()
        for goal_data in data.get("goals", {}).values():
            hierarchy.add_goal(Goal.from_dict(goal_data))
        return hierarchy


# ============================================================================
# META-CONTROLLER & SUB-CONTROLLERS
# ============================================================================

class Policy(ABC, Generic[S, A]):
    """Abstrakte Policy für ein Controller-Level."""
    
    @abstractmethod
    def select(self, state: S, available_options: List[Option[S, A]]) -> Option[S, A]:
        """Wählt eine Option basierend auf dem aktuellen Zustand."""
        pass
    
    @abstractmethod
    def update(self, state: S, option: Option[S, A], reward: Reward) -> None:
        """Aktualisiert die Policy basierend auf dem Reward."""
        pass


class EpsilonGreedyPolicy(Policy[S, A]):
    """Epsilon-Greedy Policy für Exploration vs Exploitation."""
    
    def __init__(self, epsilon: float = 0.1, decay: float = 0.995, min_epsilon: float = 0.01):
        self.epsilon = epsilon
        self.decay = decay
        self.min_epsilon = min_epsilon
        self.q_values: Dict[str, Dict[str, float]] = defaultdict(lambda: defaultdict(float))
        
    def select(self, state: S, available_options: List[Option[S, A]]) -> Option[S, A]:
        if not available_options:
            raise ValueError("No available options")
        
        state_key = self._state_key(state)
        
        # Epsilon-Greedy
        if random.random() < self.epsilon:
            return random.choice(available_options)
        
        # Greedy: wähle Option mit höchstem Q-Wert
        best_option = available_options[0]
        best_value = float('-inf')
        
        for option in available_options:
            q_val = self.q_values[state_key][option.name]
            if q_val > best_value:
                best_value = q_val
                best_option = option
        
        return best_option
    
    def update(self, state: S, option: Option[S, A], reward: Reward) -> None:
        state_key = self._state_key(state)
        current_q = self.q_values[state_key][option.name]
        # Q-Learning update
        self.q_values[state_key][option.name] = current_q + 0.1 * (float(reward) - current_q)
        
        # Decay epsilon
        self.epsilon = max(self.min_epsilon, self.epsilon * self.decay)
    
    def _state_key(self, state: S) -> str:
        """Erzeugt einen Key für den Zustand."""
        # Vereinfachte State-Representation - nur hashable Typen
        def make_hashable(obj):
            if isinstance(obj, dict):
                return tuple((k, make_hashable(v)) for k, v in sorted(obj.items()))
            elif isinstance(obj, list):
                return tuple(make_hashable(v) for v in obj)
            elif isinstance(obj, set):
                return tuple(sorted(make_hashable(v) for v in obj))
            return obj
        
        try:
            return str(hash(make_hashable(state.features)))
        except TypeError:
            # Fallback: nur string-keys verwenden
            return str(hash(tuple(sorted((k, str(v)) for k, v in state.features.items()))))


class UCBPolicy(Policy[S, A]):
    """Upper Confidence Bound Policy für bessere Exploration."""
    
    def __init__(self, c: float = 1.0):
        self.c = c
        self.q_values: Dict[str, Dict[str, float]] = defaultdict(lambda: defaultdict(float))
        self.counts: Dict[str, Dict[str, int]] = defaultdict(lambda: defaultdict(int))
        self.total_counts: Dict[str, int] = defaultdict(int)
        
    def select(self, state: S, available_options: List[Option[S, A]]) -> Option[S, A]:
        if not available_options:
            raise ValueError("No available options")
        
        state_key = self._state_key(state)
        
        # UCB Formel: Q(s,a) + c * sqrt(log(N(s)) / N(s,a))
        best_option = available_options[0]
        best_value = float('-inf')
        
        for option in available_options:
            q_val = self.q_values[state_key][option.name]
            count = self.counts[state_key][option.name]
            total = self.total_counts[state_key]
            
            if count == 0:
                # Unexplored option - prioritize
                return option
            
            ucb_value = q_val + self.c * (2 * (total ** 0.5) / count) ** 0.5
            
            if ucb_value > best_value:
                best_value = ucb_value
                best_option = option
        
        return best_option
    
    def update(self, state: S, option: Option[S, A], reward: Reward) -> None:
        state_key = self._state_key(state)
        self.counts[state_key][option.name] += 1
        self.total_counts[state_key] += 1
        
        # Update Q-Value
        count = self.counts[state_key][option.name]
        current_q = self.q_values[state_key][option.name]
        self.q_values[state_key][option.name] = current_q + (float(reward) - current_q) / count
    
    def _state_key(self, state: S) -> str:
        """Erzeugt einen Key für den Zustand."""
        def make_hashable(obj):
            if isinstance(obj, dict):
                return tuple((k, make_hashable(v)) for k, v in sorted(obj.items()))
            elif isinstance(obj, list):
                return tuple(make_hashable(v) for v in obj)
            elif isinstance(obj, set):
                return tuple(sorted(make_hashable(v) for v in obj))
            return obj
        
        try:
            return str(hash(make_hashable(state.features)))
        except TypeError:
            return str(hash(tuple(sorted((k, str(v)) for k, v in state.features.items()))))


class SubController:
    """
    Ein Sub-Controller verwaltet eine Option und führt sie aus.
 """
    
    def __init__(self, option: Option[S, A], policy: Policy[S, A]):
        self.option = option
        self.policy = policy
        self.execution_history: List[Dict[str, Any]] = []
        
    def execute(self, state: S, env: 'Environment') -> Tuple[float, bool]:
        """
        Führt die Option aus bis zur Terminierung.
        
        Returns:
            (total_reward, success)
        """
        self.option.on_initiate(state)
        total_reward = 0.0
        steps = 0
        max_steps = 100  # Safety limit
        
        # Execute at least one step for primitive options
        # Primitive options should_terminate immediately but still need to execute
        while steps < max_steps:
            # Check termination after at least one step for primitive options
            if steps > 0 and self.option.should_terminate(state):
                break
            
            # Wähle nächste Aktion/Sub-Option
            selected = self.option.select_action(state)
            
            if isinstance(selected, Option):
                # Rekursive Ausführung
                sub_controller = SubController(selected, self.policy)
                reward, success = sub_controller.execute(state, env)
                total_reward += reward
            else:
                # Primitive Aktion
                reward = env.execute(selected)
                total_reward += float(reward)
                self.policy.update(state, self.option, reward)
            
            state = env.get_state()
            steps += 1
            
            self.execution_history.append({
                "step": steps,
                "action": str(selected),
                "reward": float(reward) if not isinstance(selected, Option) else reward,
            })
            
            # Check termination after execution
            if self.option.should_terminate(state):
                break
        
        success = steps < max_steps
        self.option.on_terminate(state, success)
        self.option.update_stats(total_reward)
        
        return total_reward, success


class MetaController:
    """
    Der Meta-Controller verwaltet die höchste Ebene der Hierarchie.
    Wählt zwischen verschiedenen High-Level Optionen (z.B. Zielen).
    """
    
    def __init__(self, policy: Policy[S, A], goal_hierarchy: GoalHierarchy):
        self.policy = policy
        self.goal_hierarchy = goal_hierarchy
        self.options: Dict[str, Option[S, A]] = {}
        self.active_option: Optional[Option[S, A]] = None
        self.episode_history: List[Dict[str, Any]] = []
        
    def register_option(self, option: Option[S, A], goal_id: Optional[str] = None) -> None:
        """Registriert eine Option im Meta-Controller."""
        self.options[option.name] = option
        
        if goal_id:
            goal = self.goal_hierarchy.get_goal(goal_id)
            if goal:
                goal.associated_option = option.name
    
    def select_goal(self, state: S) -> Optional[Goal]:
        """Wählt das nächste Ziel basierend auf der Policy."""
        # Filtere verfügbare Optionen
        available = [
            opt for opt in self.options.values()
            if opt.can_initiate(state)
        ]
        
        if not available:
            return None
        
        selected_option = self.policy.select(state, available)
        
        # Finde zugehöriges Ziel
        for goal_id, goal in self.goal_hierarchy.goals.items():
            if goal.associated_option == selected_option.name:
                return goal
        
        return None
    
    def execute_goal(self, goal_id: str, state: S, env: 'Environment') -> Tuple[float, bool]:
        """Führt ein spezifisches Ziel aus."""
        goal = self.goal_hierarchy.get_goal(goal_id)
        if not goal:
            raise ValueError(f"Goal {goal_id} not found")
        
        option_name = goal.associated_option
        if not option_name or option_name not in self.options:
            raise ValueError(f"No option associated with goal {goal_id}")
        
        option = self.options[option_name]
        self.goal_hierarchy.set_status(goal_id, GoalStatus.ACTIVE)
        
        controller = SubController(option, self.policy)
        reward, success = controller.execute(state, env)
        
        status = GoalStatus.COMPLETED if success else GoalStatus.FAILED
        self.goal_hierarchy.set_status(goal_id, status)
        
        self.episode_history.append({
            "goal_id": goal_id,
            "reward": reward,
            "success": success,
            "timestamp": time.time(),
        })
        
        return reward, success
    
    def run_episode(self, env: 'Environment', max_goals: int = 10) -> Dict[str, Any]:
        """Führt eine Episode mit mehreren Zielen aus."""
        state = env.get_state()
        total_reward = 0.0
        goals_completed = 0
        goals_attempted = 0
        
        for _ in range(max_goals):
            goal = self.select_goal(state)
            if not goal:
                break
            
            reward, success = self.execute_goal(goal.id, state, env)
            total_reward += reward
            goals_attempted += 1
            
            if success:
                goals_completed += 1
            
            state = env.get_state()
        
        return {
            "total_reward": total_reward,
            "goals_completed": goals_completed,
            "goals_attempted": goals_attempted,
            "timestamp": time.time(),
        }


# ============================================================================
# ENVIRONMENT INTERFACE
# ============================================================================

class Environment(ABC):
    """Abstrakte Environment-Schnittstelle."""
    
    @abstractmethod
    def get_state(self) -> State:
        """Gibt den aktuellen Zustand zurück."""
        pass
    
    @abstractmethod
    def execute(self, action: Action) -> Reward:
        """Führt eine Aktion aus und gibt den Reward zurück."""
        pass
    
    @abstractmethod
    def reset(self) -> State:
        """Setzt die Environment zurück."""
        pass


class SimulatedEnvironment(Environment):
    """Eine simulierte Environment für Tests."""
    
    def __init__(self):
        self.state = State(features={"step": 0, "position": 0})
        self.step_count = 0
        
    def get_state(self) -> State:
        return self.state
    
    def execute(self, action: Action) -> Reward:
        self.step_count += 1
        
        # Simuliere einfache Dynamik
        if action.name == "move_forward":
            new_pos = self.state.get("position", 0) + 1
            self.state = self.state.update(position=new_pos, step=self.step_count)
            return Reward(value=1.0, source="move")
        elif action.name == "move_backward":
            new_pos = self.state.get("position", 0) - 1
            self.state = self.state.update(position=new_pos, step=self.step_count)
            return Reward(value=-0.5, source="move")
        elif action.name == "wait":
            self.state = self.state.update(step=self.step_count)
            return Reward(value=0.0, source="wait")
        else:
            return Reward(value=0.0, source="unknown")
    
    def reset(self) -> State:
        self.step_count = 0
        self.state = State(features={"step": 0, "position": 0})
        return self.state


# ============================================================================
# HRL SYSTEM INTEGRATION
# ============================================================================

class HRLSystem:
    """
    Hauptklasse für das Hierarchical Reinforcement Learning System.
    Integriert alle Komponenten und bietet eine einheitliche API.
    """
    
    def __init__(self, storage_path: Optional[Path] = None):
        self.storage_path = storage_path or Path("/root/.openclaw/workspace/skills/hierarchical_rl/data")
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        # Komponenten
        self.goal_hierarchy = GoalHierarchy()
        self.maxq_hierarchy: Optional[MaxQHierarchy] = None
        self.meta_controller: Optional[MetaController] = None
        self.environment: Optional[Environment] = None
        
        # Stats
        self.training_stats: List[Dict[str, Any]] = []
        
    def initialize(self, policy: Optional[Policy] = None) -> None:
        """Initialisiert das System mit einer Policy."""
        policy = policy or EpsilonGreedyPolicy(epsilon=0.2)
        self.meta_controller = MetaController(policy, self.goal_hierarchy)
        
        # Erstelle Default MAXQ Root
        root = MaxQNode(name="root", is_primitive=False)
        self.maxq_hierarchy = MaxQHierarchy(root)
        
        logger.info("HRL System initialized")
    
    def add_goal(self, goal: Goal, option: Optional[Option] = None) -> None:
        """Fügt ein Ziel mit optionaler Option hinzu."""
        self.goal_hierarchy.add_goal(goal)
        
        if option and self.meta_controller:
            self.meta_controller.register_option(option, goal.id)
            
            # Füge zu MAXQ Hierarchie hinzu
            if self.maxq_hierarchy:
                node = MaxQNode(name=option.name, is_primitive=isinstance(option, PrimitiveOption))
                self.maxq_hierarchy.root.children.append(node)
                self.maxq_hierarchy._index_nodes(node)
        
        logger.info(f"Added goal: {goal.name} (id={goal.id})")
    
    def create_composite_goal(
        self,
        name: str,
        sub_goals: List[Goal],
        option_name: Optional[str] = None
    ) -> Goal:
        """Erstellt ein zusammengesetztes Ziel mit Sub-Zielen."""
        goal_id = f"goal_{name.lower().replace(' ', '_')}"
        
        composite_goal = Goal(
            id=goal_id,
            name=name,
            sub_goals=[g.id for g in sub_goals],
        )
        
        # Erstelle Composite Option
        sub_options = []
        for sg in sub_goals:
            if sg.associated_option and self.meta_controller:
                opt = self.meta_controller.options.get(sg.associated_option)
                if opt:
                    sub_options.append(opt)
        
        if sub_options:
            composite_option = CompositeOption(
                name=option_name or f"option_{name.lower().replace(' ', '_')}",
                sub_options=sub_options,
                level=1
            )
            self.add_goal(composite_goal, composite_option)
        else:
            self.add_goal(composite_goal)
        
        return composite_goal
    
    def train(self, episodes: int = 100, env: Optional[Environment] = None) -> Dict[str, Any]:
        """Trainiert das System über mehrere Episoden."""
        if not self.meta_controller:
            raise RuntimeError("System not initialized. Call initialize() first.")
        
        env = env or self.environment or SimulatedEnvironment()
        
        total_rewards = []
        successes = []
        
        for episode in range(episodes):
            env.reset()
            result = self.meta_controller.run_episode(env)
            
            total_rewards.append(result["total_reward"])
            success_rate = result["goals_completed"] / max(result["goals_attempted"], 1)
            successes.append(success_rate)
            
            self.training_stats.append({
                "episode": episode,
                **result,
            })
            
            if episode % 10 == 0:
                avg_reward = sum(total_rewards[-10:]) / min(10, len(total_rewards))
                logger.info(f"Episode {episode}: avg_reward={avg_reward:.2f}")
        
        return {
            "episodes": episodes,
            "avg_reward": sum(total_rewards) / len(total_rewards),
            "avg_success_rate": sum(successes) / len(successes),
            "final_reward": total_rewards[-1] if total_rewards else 0,
        }
    
    def execute_goal(self, goal_id: str, env: Optional[Environment] = None) -> Dict[str, Any]:
        """Führt ein spezifisches Ziel aus."""
        if not self.meta_controller:
            raise RuntimeError("System not initialized")
        
        env = env or self.environment or SimulatedEnvironment()
        state = env.get_state()
        
        reward, success = self.meta_controller.execute_goal(goal_id, state, env)
        
        return {
            "goal_id": goal_id,
            "reward": reward,
            "success": success,
            "timestamp": time.time(),
        }
    
    def get_goal_status(self, goal_id: str) -> Dict[str, Any]:
        """Gibt den Status eines Ziels zurück."""
        goal = self.goal_hierarchy.get_goal(goal_id)
        status = self.goal_hierarchy.get_status(goal_id)
        
        if not goal:
            return {"error": f"Goal {goal_id} not found"}
        
        return {
            "goal": goal.to_dict(),
            "status": status.name,
            "is_achieved": goal.is_achieved(self.environment.get_state() if self.environment else State()),
        }
    
    def save(self, filename: Optional[str] = None) -> Path:
        """Speichert den Zustand des Systems."""
        filename = filename or f"hrl_state_{int(time.time())}.json"
        filepath = self.storage_path / filename
        
        data = {
            "goal_hierarchy": self.goal_hierarchy.to_dict(),
            "training_stats": self.training_stats,
            "saved_at": time.time(),
        }
        
        # Ensure directory exists
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2, default=str)
        
        logger.info(f"HRL System saved to {filepath}")
        return filepath
    
    def load(self, filepath: Path) -> None:
        """Lädt den Zustand des Systems."""
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        self.goal_hierarchy = GoalHierarchy.from_dict(data.get("goal_hierarchy", {}))
        self.training_stats = data.get("training_stats", [])
        
        logger.info(f"HRL System loaded from {filepath}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Gibt Statistiken über das System zurück."""
        return {
            "num_goals": len(self.goal_hierarchy.goals),
            "num_root_goals": len(self.goal_hierarchy.root_goals),
            "num_options": len(self.meta_controller.options) if self.meta_controller else 0,
            "training_episodes": len(self.training_stats),
            "avg_reward_last_10": (
                sum(s["total_reward"] for s in self.training_stats[-10:]) / 10
                if len(self.training_stats) >= 10 else 0
            ),
        }


# ============================================================================
# AURELPRO INTEGRATION
# ============================================================================

class AurelHRLAdapter:
    """
    Adapter für die Integration mit dem AURELPRO Goal-System.
    """
    
    def __init__(self, hrl_system: HRLSystem):
        self.hrl = hrl_system
        
    def convert_aurel_goal(self, aurel_goal_data: Dict[str, Any]) -> Goal:
        """Konvertiert ein AURELPRO-Ziel in ein HRL-Ziel."""
        return Goal(
            id=aurel_goal_data.get("id", ""),
            name=aurel_goal_data.get("name", ""),
            description=aurel_goal_data.get("description", ""),
            parent_id=aurel_goal_data.get("parent_id"),
            priority=aurel_goal_data.get("priority", 1.0),
            metadata=aurel_goal_data.get("metadata", {}),
        )
    
    def create_skill_learning_goal(self, skill_name: str) -> Tuple[Goal, Option]:
        """Erstellt ein Ziel für Skill-Lernen mit HRL-Struktur."""
        # Hauptziel: Skill erlernen
        main_goal = Goal(
            id=f"skill_{skill_name}",
            name=f"Learn {skill_name}",
            description=f"Master the {skill_name} skill",
        )
        
        # Sub-Ziele
        research_goal = Goal(
            id=f"skill_{skill_name}_research",
            name=f"Research {skill_name}",
            parent_id=main_goal.id,
        )
        
        implement_goal = Goal(
            id=f"skill_{skill_name}_implement",
            name=f"Implement {skill_name}",
            parent_id=main_goal.id,
        )
        
        test_goal = Goal(
            id=f"skill_{skill_name}_test",
            name=f"Test {skill_name}",
            parent_id=main_goal.id,
        )
        
        # Erstelle primitive Optionen für jedes Sub-Ziel
        research_option = PrimitiveOption(Action(name="research", params={"skill": skill_name}))
        implement_option = PrimitiveOption(Action(name="implement", params={"skill": skill_name}))
        test_option = PrimitiveOption(Action(name="test", params={"skill": skill_name}))
        
        # Composite Option für den gesamten Skill
        skill_option = CompositeOption(
            name=f"learn_{skill_name}",
            sub_options=[research_option, implement_option, test_option],
            level=1
        )
        
        return main_goal, skill_option
    
    def get_recommended_next_goal(self, current_state: State) -> Optional[str]:
        """Empfiehlt das nächste Ziel basierend auf dem aktuellen Zustand."""
        if not self.hrl.meta_controller:
            return None
        
        goal = self.hrl.meta_controller.select_goal(current_state)
        return goal.id if goal else None


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def create_default_hrl_system() -> HRLSystem:
    """Erstellt ein HRL-System mit Default-Konfiguration."""
    system = HRLSystem()
    system.initialize(policy=EpsilonGreedyPolicy(epsilon=0.2, decay=0.99))
    
    # Erstelle einige Default-Optionen
    move_forward = PrimitiveOption(Action(name="move_forward"))
    move_backward = PrimitiveOption(Action(name="move_backward"))
    wait = PrimitiveOption(Action(name="wait"))
    
    # Registriere primitive Optionen
    for opt in [move_forward, move_backward, wait]:
        system.meta_controller.register_option(opt)
    
    return system


# For type hints
def Tuple(*types):
    """Compatibility for older Python versions."""
    return tuple


# Make Tuple available
from typing import Tuple as TypingTuple
