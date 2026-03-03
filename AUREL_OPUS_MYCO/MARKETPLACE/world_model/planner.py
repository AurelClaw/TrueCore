#!/usr/bin/env python3
"""
World Model - MPC Planner Module

Model Predictive Control (MPC) basierter Planner mit 
Cross-Entropy Method (CEM) für Action Sampling.

Features:
- Multi-step Action Sequencing
- CEM für effizientes Action Sampling
- Integration mit Transition Model für Forward Simulation
- Reward-basierte Action Evaluation
"""

import json
import os
import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple, Callable
from pathlib import Path
from dataclasses import dataclass, field
from copy import deepcopy
import numpy as np

from state import WorldState, TimeState, ContextState, SystemState
from transition_model import TransitionModel


@dataclass
class Action:
    """Repräsentiert eine einzelne Aktion."""
    name: str
    category: str  # communication, task_execution, learning, self_improvement
    parameters: Dict[str, Any] = field(default_factory=dict)
    duration_minutes: int = 30
    
    def __hash__(self):
        return hash((self.name, self.category, tuple(sorted(self.parameters.items()))))
    
    def __eq__(self, other):
        if not isinstance(other, Action):
            return False
        return (self.name == other.name and 
                self.category == other.category and
                self.parameters == other.parameters)


@dataclass
class ActionSequence:
    """Eine Sequenz von Aktionen (Plan)."""
    actions: List[Action] = field(default_factory=list)
    total_reward: float = 0.0
    predicted_final_state: Optional[WorldState] = None
    trajectory: List[WorldState] = field(default_factory=list)
    
    def __len__(self):
        return len(self.actions)
    
    def add_action(self, action: Action):
        self.actions.append(action)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "actions": [
                {
                    "name": a.name,
                    "category": a.category,
                    "parameters": a.parameters,
                    "duration_minutes": a.duration_minutes
                }
                for a in self.actions
            ],
            "total_reward": self.total_reward,
            "length": len(self.actions)
        }


class ActionSpace:
    """Definiert den verfügbaren Action Space."""
    
    # Vordefinierte Aktionen nach Kategorie
    COMMUNICATION_ACTIONS = [
        Action("send_message", "communication", {"urgency": "normal"}, 5),
        Action("send_message", "communication", {"urgency": "high"}, 5),
        Action("react_to_message", "communication", {"type": "positive"}, 2),
        Action("remain_silent", "communication", {}, 0),
        Action("schedule_reminder", "communication", {}, 5),
    ]
    
    TASK_EXECUTION_ACTIONS = [
        Action("execute_skill", "task_execution", {"priority": "low"}, 30),
        Action("execute_skill", "task_execution", {"priority": "medium"}, 30),
        Action("execute_skill", "task_execution", {"priority": "high"}, 30),
        Action("schedule_task", "task_execution", {"delay": "1h"}, 5),
        Action("delegate_task", "task_execution", {}, 10),
    ]
    
    LEARNING_ACTIONS = [
        Action("research_topic", "learning", {"depth": "shallow"}, 60),
        Action("research_topic", "learning", {"depth": "deep"}, 120),
        Action("update_model", "learning", {}, 30),
        Action("explore_new_skill", "learning", {}, 90),
    ]
    
    SELF_IMPROVEMENT_ACTIONS = [
        Action("refactor_skill", "self_improvement", {}, 60),
        Action("optimize_pipeline", "self_improvement", {}, 45),
        Action("analyze_performance", "self_improvement", {}, 30),
        Action("update_documentation", "self_improvement", {}, 20),
    ]
    
    def __init__(self):
        self.all_actions = (
            self.COMMUNICATION_ACTIONS +
            self.TASK_EXECUTION_ACTIONS +
            self.LEARNING_ACTIONS +
            self.SELF_IMPROVEMENT_ACTIONS
        )
    
    def sample_random(self, n: int = 1) -> List[Action]:
        """Zieht n zufällige Aktionen."""
        return random.choices(self.all_actions, k=n)
    
    def sample_by_category(self, category: str, n: int = 1) -> List[Action]:
        """Zieht n zufällige Aktionen aus einer Kategorie."""
        category_actions = [a for a in self.all_actions if a.category == category]
        if not category_actions:
            return []
        return random.choices(category_actions, k=min(n, len(category_actions)))
    
    def get_actions_by_context(self, state: WorldState, n: int = 5) -> List[Action]:
        """Gibt kontext-geeignete Aktionen zurück."""
        suitable = []
        
        # Basierend auf Tageszeit filtern
        if state.time.time_of_day == "night":
            # Nachts: Keine Kommunikation
            suitable = [a for a in self.all_actions if a.category != "communication"]
        elif state.time.time_of_day == "morning":
            # Morgens: Fokus auf Tasks und Kommunikation
            suitable = self.sample_by_category("task_execution", 2)
            suitable += self.sample_by_category("communication", 2)
            suitable += self.sample_by_category("learning", 1)
        else:
            suitable = self.all_actions
        
        # Basierend auf System Load anpassen
        if state.system.system_load > 0.7:
            # Hohe Load: Weniger intensive Aktionen
            suitable = [a for a in suitable if a.category != "learning"]
        
        if len(suitable) < n:
            suitable = self.all_actions
        
        return random.sample(suitable, min(n, len(suitable)))


class RewardFunction:
    """
    Berechnet Rewards für Zustands-Action-Paare.
    
    Kombiniert mehrere Reward-Komponenten:
    - Goal Alignment: Wie gut passt zur aktuellen Zielsetzung
    - Context Appropriateness: Kontextuelle Angemessenheit
    - Resource Efficiency: Effiziente Nutzung von Ressourcen
    - Exploration Bonus: Für Diversität
    """
    
    def __init__(self, goal_weights: Optional[Dict[str, float]] = None):
        self.goal_weights = goal_weights or {
            "productivity": 0.3,
            "learning": 0.2,
            "harmony": 0.3,
            "efficiency": 0.2
        }
    
    def compute_reward(self, state: WorldState, action: Action, 
                       next_state: WorldState) -> float:
        """
        Berechnet den Reward für eine State-Action-Transition.
        
        Returns:
            Float im Bereich [-1, 1]
        """
        rewards = {
            "goal_alignment": self._goal_alignment_reward(state, action, next_state),
            "context_appropriateness": self._context_reward(state, action),
            "resource_efficiency": self._resource_reward(state, action, next_state),
            "exploration": 0.0  # Wird separat hinzugefügt
        }
        
        # Gewichtete Summe
        total = sum(rewards[k] * self.goal_weights.get(k, 0.25) 
                   for k in rewards if k in self.goal_weights)
        
        return max(-1.0, min(1.0, total))
    
    def _goal_alignment_reward(self, state: WorldState, action: Action,
                                next_state: WorldState) -> float:
        """Wie gut unterstützt die Aktion die aktuellen Ziele?"""
        reward = 0.0
        
        # Basierend auf offenen Zielen
        if state.context.open_goals:
            # Task-Ausführung ist gut für offene Ziele
            if action.category == "task_execution":
                reward += 0.4
            # Learning bei Zielen mit "learn" oder "research"
            if any("learn" in g or "research" in g for g in state.context.open_goals):
                if action.category == "learning":
                    reward += 0.5
        
        # Self-improvement ist immer etwas wert
        if action.category == "self_improvement":
            reward += 0.2
        
        return min(1.0, reward)
    
    def _context_reward(self, state: WorldState, action: Action) -> float:
        """Wie kontext-geeignet ist die Aktion?"""
        reward = 0.0
        
        # Zeit-basierte Constraints
        if state.time.time_of_day == "night":
            # Nachts: Keine Kommunikation
            if action.category == "communication":
                reward -= 0.8
            else:
                reward += 0.2  # Stille Aktionen sind gut
        
        # Hohe System Load
        if state.system.system_load > 0.8:
            if action.category in ["learning", "self_improvement"]:
                reward -= 0.3  # Vermeide schwere Aktionen
        
        # Lange Zeit ohne Interaktion -> Kommunikation wichtiger
        if state.context.last_interaction_minutes_ago:
            if state.context.last_interaction_minutes_ago > 240:  # 4 Stunden
                if action.category == "communication":
                    reward += 0.3
        
        return reward
    
    def _resource_reward(self, state: WorldState, action: Action,
                         next_state: WorldState) -> float:
        """Wie effizient nutzt die Aktion Ressourcen?"""
        reward = 0.0
        
        # Kürzere Aktionen sind effizienter
        duration = action.duration_minutes
        if duration <= 10:
            reward += 0.3
        elif duration <= 30:
            reward += 0.1
        elif duration > 60:
            reward -= 0.2
        
        # System Load sollte nicht steigen
        if next_state.system.system_load < state.system.system_load:
            reward += 0.2
        elif next_state.system.system_load > state.system.system_load + 0.2:
            reward -= 0.3
        
        return reward


class MPCPlanner:
    """
    Model Predictive Control Planner mit Cross-Entropy Method.
    
    Der Planner:
    1. Samplet Action-Sequenzen (Kandidaten)
    2. Simuliert jede Sequenz mit dem Transition Model
    3. Bewertet jede Sequenz mit der Reward Function
    4. Selektiert die besten (Elite) Sequenzen
    5. Aktualisiert die Sampling-Verteilung
    6. Wiederholt für N Iterationen
    """
    
    def __init__(self, 
                 horizon: int = 3,
                 n_candidates: int = 20,
                 n_elite: int = 5,
                 n_iterations: int = 5,
                 transition_model: Optional[TransitionModel] = None,
                 reward_function: Optional[RewardFunction] = None):
        """
        Args:
            horizon: Planungshorizont (Anzahl Actions)
            n_candidates: Anzahl zu samplender Kandidaten pro Iteration
            n_elite: Anzahl zu behaltender Elite-Kandidaten
            n_iterations: CEM Iterationen
            transition_model: Modell für Zustandsübergänge
            reward_function: Funktion zur Reward-Berechnung
        """
        self.horizon = horizon
        self.n_candidates = n_candidates
        self.n_elite = n_elite
        self.n_iterations = n_iterations
        
        self.transition_model = transition_model or TransitionModel()
        self.reward_function = reward_function or RewardFunction()
        self.action_space = ActionSpace()
    
    def plan(self, initial_state: WorldState, 
             context_hints: Optional[Dict[str, Any]] = None) -> ActionSequence:
        """
        Erstellt einen optimalen Aktionsplan.
        
        Args:
            initial_state: Ausgangszustand
            context_hints: Optionale Hinweise für die Planung
        
        Returns:
            Beste gefundene ActionSequence
        """
        # Initialisiere Kandidaten-Pool
        candidates = self._initialize_candidates(initial_state)
        
        # CEM Iterationen
        for iteration in range(self.n_iterations):
            # Simuliere alle Kandidaten
            evaluated = []
            for seq in candidates:
                reward, trajectory = self._simulate_sequence(initial_state, seq)
                seq.total_reward = reward
                seq.trajectory = trajectory
                if trajectory:
                    seq.predicted_final_state = trajectory[-1]
                evaluated.append((seq, reward))
            
            # Selektiere Elite
            evaluated.sort(key=lambda x: x[1], reverse=True)
            elite = [seq for seq, _ in evaluated[:self.n_elite]]
            
            # Aktualisiere Verteilung und resample
            if iteration < self.n_iterations - 1:
                candidates = self._refine_candidates(elite, initial_state)
        
        # Gib beste Sequenz zurück
        best_sequence = evaluated[0][0]
        return best_sequence
    
    def _initialize_candidates(self, state: WorldState) -> List[ActionSequence]:
        """Initialisiert zufällige Action-Sequenzen."""
        candidates = []
        for _ in range(self.n_candidates):
            seq = ActionSequence()
            # Sample horizon Aktionen
            for _ in range(self.horizon):
                actions = self.action_space.get_actions_by_context(state, n=3)
                if actions:
                    seq.add_action(random.choice(actions))
            candidates.append(seq)
        return candidates
    
    def _simulate_sequence(self, initial_state: WorldState, 
                           sequence: ActionSequence) -> Tuple[float, List[WorldState]]:
        """
        Simuliert eine Action-Sequenz und berechnet den Gesamt-Reward.
        
        Returns:
            (total_reward, trajectory)
        """
        current_state = deepcopy(initial_state)
        trajectory = [current_state]
        total_reward = 0.0
        discount = 1.0
        
        for action in sequence.actions:
            # Simuliere Zustandsübergang
            next_state = self._apply_action(current_state, action)
            
            # Berechne Reward
            reward = self.reward_function.compute_reward(
                current_state, action, next_state
            )
            total_reward += discount * reward
            discount *= 0.95  # Discount Factor
            
            trajectory.append(next_state)
            current_state = next_state
        
        return total_reward, trajectory
    
    def _apply_action(self, state: WorldState, action: Action) -> WorldState:
        """
        Wendet eine Aktion auf einen Zustand an.
        
        Nutzt das Transition Model für die Basis-Vorhersage,
        modifiziert basierend auf Action-Typ.
        """
        # Basis-Vorhersage mit Transition Model
        next_state = self.transition_model.predict(
            state, method="pattern", steps_ahead=1
        )
        
        # Modifiziere basierend auf Action
        if action.category == "communication":
            # Kommunikation: Update last_interaction
            next_state.context.last_interaction_minutes_ago = 0
            # Hohe Priorität könnte System Load beeinflussen
            if action.parameters.get("urgency") == "high":
                next_state.system.system_load = min(1.0, next_state.system.system_load + 0.1)
        
        elif action.category == "task_execution":
            # Task Execution: Kann System Load erhöhen
            priority = action.parameters.get("priority", "medium")
            load_increase = {"low": 0.05, "medium": 0.1, "high": 0.2}.get(priority, 0.1)
            next_state.system.system_load = min(1.0, next_state.system.system_load + load_increase)
            # Könnte offene Ziele reduzieren
            if next_state.context.open_goals and random.random() < 0.3:
                next_state.context.open_goals.pop(0)
        
        elif action.category == "learning":
            # Learning: Erhöht Load, aber langfristig nützlich
            depth = action.parameters.get("depth", "shallow")
            load_increase = {"shallow": 0.1, "deep": 0.25}.get(depth, 0.1)
            next_state.system.system_load = min(1.0, next_state.system.system_load + load_increase)
            # Fügt Knowledge hinzu (simuliert)
            next_state.context.recent_topics.append(f"learned_{action.name}")
        
        elif action.category == "self_improvement":
            # Self-improvement: Moderater Load, langfristiger Benefit
            next_state.system.system_load = min(1.0, next_state.system.system_load + 0.15)
            next_state.system.active_skills.append(f"improved_{action.name}")
        
        # Zeit-Update basierend auf Action-Dauer
        current_time = datetime.fromisoformat(next_state.time.timestamp)
        new_time = current_time + timedelta(minutes=action.duration_minutes)
        next_state.time = TimeState(
            timestamp=new_time.isoformat(),
            time_of_day=self._get_time_of_day(new_time.hour),
            day_of_week=new_time.weekday(),
            week_of_year=new_time.isocalendar()[1],
            is_weekend=new_time.weekday() >= 5,
            is_holiday=next_state.time.is_holiday
        )
        
        return next_state
    
    def _get_time_of_day(self, hour: int) -> str:
        """Bestimmt Tageszeit aus Stunde."""
        if 5 <= hour < 12:
            return "morning"
        elif 12 <= hour < 17:
            return "afternoon"
        elif 17 <= hour < 22:
            return "evening"
        else:
            return "night"
    
    def _refine_candidates(self, elite: List[ActionSequence], 
                           state: WorldState) -> List[ActionSequence]:
        """
        Erzeugt neue Kandidaten basierend auf Elite-Sequenzen.
        
        Einfache Implementation: Kombiniere Elite-Sequenzen mit
        zufälligen Mutationen.
        """
        new_candidates = []
        
        # Behalte Elite bei
        new_candidates.extend(deepcopy(elite))
        
        # Generiere neue Kandidaten durch Mutation
        while len(new_candidates) < self.n_candidates:
            # Wähle zufällige Elite-Sequenz als Basis
            base = random.choice(elite)
            mutated = self._mutate_sequence(base, state)
            new_candidates.append(mutated)
        
        return new_candidates
    
    def _mutate_sequence(self, sequence: ActionSequence, 
                         state: WorldState) -> ActionSequence:
        """Mutiert eine Sequenz durch zufällige Änderungen."""
        mutated = ActionSequence()
        
        for i, action in enumerate(sequence.actions):
            # 30% Chance, eine Aktion zu ersetzen
            if random.random() < 0.3:
                new_actions = self.action_space.get_actions_by_context(state, n=3)
                if new_actions:
                    mutated.add_action(random.choice(new_actions))
                else:
                    mutated.add_action(action)
            else:
                mutated.add_action(action)
        
        return mutated
    
    def plan_with_counterfactuals(self, initial_state: WorldState,
                                   n_scenarios: int = 3) -> Dict[str, Any]:
        """
        Erstellt einen Plan mit Counterfactual-Analyse.
        
        Simuliert verschiedene Szenarien und vergleicht Ergebnisse.
        """
        result = {
            "optimal_plan": None,
            "scenarios": [],
            "comparison": {}
        }
        
        # Hauptplan
        optimal = self.plan(initial_state)
        result["optimal_plan"] = optimal.to_dict()
        
        # Counterfactual Szenarien
        scenarios = ["best_case", "expected", "worst_case"]
        
        for scenario in scenarios[:n_scenarios]:
            # Modifiziere Rewards basierend auf Szenario
            modified_reward = self._create_scenario_reward(scenario)
            original_reward = self.reward_function
            
            self.reward_function = modified_reward
            plan = self.plan(initial_state)
            
            result["scenarios"].append({
                "scenario": scenario,
                "plan": plan.to_dict(),
                "expected_reward": plan.total_reward
            })
            
            self.reward_function = original_reward
        
        # Vergleiche Szenarien
        if len(result["scenarios"]) >= 2:
            rewards = [s["expected_reward"] for s in result["scenarios"]]
            result["comparison"] = {
                "reward_range": max(rewards) - min(rewards),
                "average_reward": sum(rewards) / len(rewards),
                "robustness": 1.0 - (np.std(rewards) if len(rewards) > 1 else 0)
            }
        
        return result
    
    def _create_scenario_reward(self, scenario: str) -> RewardFunction:
        """Erstellt eine modifizierte Reward Function für ein Szenario."""
        if scenario == "best_case":
            # Optimalistische Annahmen
            return RewardFunction({
                "productivity": 0.4,
                "learning": 0.3,
                "harmony": 0.2,
                "efficiency": 0.1
            })
        elif scenario == "worst_case":
            # Pessimistische Annahmen
            return RewardFunction({
                "productivity": 0.1,
                "learning": 0.1,
                "harmony": 0.6,
                "efficiency": 0.2
            })
        else:  # expected
            return RewardFunction()


def main():
    """CLI-Interface für den Planner."""
    import argparse
    
    parser = argparse.ArgumentParser(description="World Model MPC Planner")
    parser.add_argument("--plan", action="store_true", help="Erstelle Plan")
    parser.add_argument("--horizon", type=int, default=3, help="Planungshorizont")
    parser.add_argument("--iterations", type=int, default=5, help="CEM Iterationen")
    parser.add_argument("--counterfactual", action="store_true", 
                       help="Mit Counterfactual-Analyse")
    parser.add_argument("--show-trajectory", action="store_true",
                       help="Zeige vorhergesagte Trajektorie")
    
    args = parser.parse_args()
    
    # Initialisiere Komponenten
    from state import StateCollector
    collector = StateCollector()
    
    # Lade oder erstelle State
    state = collector.load_latest()
    if state is None:
        state = collector.collect()
    
    print(f"Initial State: {state.time.timestamp}")
    print(f"  Time of day: {state.time.time_of_day}")
    print(f"  System load: {state.system.system_load:.2f}")
    print(f"  Open goals: {len(state.context.open_goals)}")
    
    # Erstelle Planner
    planner = MPCPlanner(
        horizon=args.horizon,
        n_candidates=20,
        n_elite=5,
        n_iterations=args.iterations
    )
    
    if args.counterfactual:
        result = planner.plan_with_counterfactuals(state)
        print("\n=== Counterfactual Analysis ===")
        print(json.dumps(result, indent=2, default=str))
    else:
        plan = planner.plan(state)
        
        print(f"\n=== Optimal Plan (Reward: {plan.total_reward:.3f}) ===")
        for i, action in enumerate(plan.actions, 1):
            print(f"{i}. {action.name} ({action.category}, {action.duration_minutes}min)")
        
        if args.show_trajectory and plan.trajectory:
            print("\n=== Predicted Trajectory ===")
            for i, traj_state in enumerate(plan.trajectory):
                print(f"Step {i}: {traj_state.time.time_of_day}, "
                      f"load={traj_state.system.system_load:.2f}")


if __name__ == "__main__":
    main()
