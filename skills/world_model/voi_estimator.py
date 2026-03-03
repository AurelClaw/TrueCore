#!/usr/bin/env python3
"""
World Model - Value of Information (VoI) Estimator

Schätzt den Wert zusätzlicher Information für die Entscheidungsfindung.

Features:
- Entropy-basierte Unsicherheitsmessung
- Expected Value of Perfect Information (EVPI)
- Expected Value of Sample Information (EVSI)
- Informationsgewinn-Schätzung für verschiedene Observation Actions
"""

import json
import math
import random
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from copy import deepcopy
import numpy as np

from state import WorldState
from planner import Action, ActionSequence, MPCPlanner, RewardFunction


@dataclass
class UncertaintyEstimate:
    """Repräsentiert eine Unsicherheits-Schätzung."""
    dimension: str  # z.B. "human_mood", "system_load", "weather"
    current_value: Any
    entropy: float  # 0 = bekannt, hoch = unsicher
    confidence: float  # 0-1
    sample_size: int  # Anzahl der Beobachtungen
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "dimension": self.dimension,
            "current_value": self.current_value,
            "entropy": round(self.entropy, 4),
            "confidence": round(self.confidence, 4),
            "sample_size": self.sample_size
        }


@dataclass
class VoIResult:
    """Ergebnis einer VoI-Berechnung."""
    observation_action: str
    cost: float  # Kosten der Observation
    expected_value: float  # Erwarteter Wert der Information
    net_value: float  # expected_value - cost
    target_dimension: str
    confidence_gain: float  # Erwarteter Confidence-Gewinn
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "observation_action": self.observation_action,
            "cost": round(self.cost, 4),
            "expected_value": round(self.expected_value, 4),
            "net_value": round(self.net_value, 4),
            "target_dimension": self.target_dimension,
            "confidence_gain": round(self.confidence_gain, 4)
        }


class UncertaintyModel:
    """
    Modelliert Unsicherheiten im World State.
    
    Verfolgt Unsicherheiten über verschiedene Dimensionen:
    - Human State (mood, engagement)
    - System State (load, pending tasks)
    - Environment (weather, calendar)
    """
    
    def __init__(self):
        self.uncertainties: Dict[str, UncertaintyEstimate] = {}
        self._initialize_uncertainties()
    
    def _initialize_uncertainties(self):
        """Initialisiert Standard-Unsicherheiten."""
        self.uncertainties = {
            "human_mood": UncertaintyEstimate(
                dimension="human_mood",
                current_value="unknown",
                entropy=1.0,
                confidence=0.0,
                sample_size=0
            ),
            "human_engagement": UncertaintyEstimate(
                dimension="human_engagement",
                current_value="unknown",
                entropy=1.0,
                confidence=0.0,
                sample_size=0
            ),
            "system_load": UncertaintyEstimate(
                dimension="system_load",
                current_value=0.5,
                entropy=0.5,
                confidence=0.5,
                sample_size=5
            ),
            "pending_tasks": UncertaintyEstimate(
                dimension="pending_tasks",
                current_value=0,
                entropy=0.3,
                confidence=0.7,
                sample_size=10
            ),
            "weather": UncertaintyEstimate(
                dimension="weather",
                current_value="unknown",
                entropy=0.8,
                confidence=0.2,
                sample_size=2
            ),
            "calendar_load": UncertaintyEstimate(
                dimension="calendar_load",
                current_value="unknown",
                entropy=0.7,
                confidence=0.3,
                sample_size=3
            )
        }
    
    def update_from_state(self, state: WorldState):
        """Aktualisiert Unsicherheiten basierend auf einem State."""
        # Human Mood
        if state.human.mood_estimate != "unknown":
            self._update_uncertainty(
                "human_mood", 
                state.human.mood_estimate,
                confidence_boost=0.2
            )
        
        # Human Engagement
        if state.human.engagement_level != "unknown":
            self._update_uncertainty(
                "human_engagement",
                state.human.engagement_level,
                confidence_boost=0.2
            )
        
        # System Load
        self._update_uncertainty(
            "system_load",
            state.system.system_load,
            confidence_boost=0.1
        )
        
        # Pending Tasks
        self._update_uncertainty(
            "pending_tasks",
            state.system.pending_notifications,
            confidence_boost=0.1
        )
        
        # Weather
        if state.environment.weather_condition != "unknown":
            self._update_uncertainty(
                "weather",
                state.environment.weather_condition,
                confidence_boost=0.3
            )
        
        # Calendar
        if state.environment.calendar_load != "unknown":
            self._update_uncertainty(
                "calendar_load",
                state.environment.calendar_load,
                confidence_boost=0.2
            )
    
    def _update_uncertainty(self, dimension: str, new_value: Any, 
                            confidence_boost: float):
        """Aktualisiert eine einzelne Unsicherheit."""
        if dimension not in self.uncertainties:
            return
        
        unc = self.uncertainties[dimension]
        unc.current_value = new_value
        unc.sample_size += 1
        unc.confidence = min(1.0, unc.confidence + confidence_boost)
        unc.entropy = max(0.0, 1.0 - unc.confidence)
    
    def get_high_uncertainty_dimensions(self, threshold: float = 0.5) -> List[str]:
        """Gibt Dimensionen mit hoher Unsicherheit zurück."""
        return [
            dim for dim, unc in self.uncertainties.items()
            if unc.entropy > threshold
        ]
    
    def compute_total_entropy(self) -> float:
        """Berechnet die gesamte Entropie des Systems."""
        return sum(unc.entropy for unc in self.uncertainties.values())
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "uncertainties": {
                k: v.to_dict() for k, v in self.uncertainties.items()
            },
            "total_entropy": round(self.compute_total_entropy(), 4),
            "high_uncertainty_dims": self.get_high_uncertainty_dimensions()
        }


class VoIEstimator:
    """
    Schätzt den Value of Information für Observation Actions.
    
    Implementiert:
    - EVPI: Wert perfekter Information
    - EVSI: Wert von Sample Information
    - Myopische VoI: Wert der nächsten Observation
    """
    
    # Observation Actions und ihre Kosten
    OBSERVATION_ACTIONS = {
        "check_messages": {
            "cost": 0.05,
            "targets": ["human_engagement", "human_mood"],
            "confidence_gain": 0.3
        },
        "check_calendar": {
            "cost": 0.03,
            "targets": ["calendar_load"],
            "confidence_gain": 0.4
        },
        "check_weather": {
            "cost": 0.02,
            "targets": ["weather"],
            "confidence_gain": 0.5
        },
        "analyze_system": {
            "cost": 0.04,
            "targets": ["system_load", "pending_tasks"],
            "confidence_gain": 0.35
        },
        "wait_for_feedback": {
            "cost": 0.1,  # Höhere Zeitkosten
            "targets": ["human_mood", "human_engagement"],
            "confidence_gain": 0.5
        }
    }
    
    def __init__(self, uncertainty_model: Optional[UncertaintyModel] = None,
                 planner: Optional[MPCPlanner] = None):
        self.uncertainty_model = uncertainty_model or UncertaintyModel()
        self.planner = planner or MPCPlanner()
        self.reward_function = RewardFunction()
    
    def estimate_voi_for_action(self, state: WorldState, 
                                 obs_action: str) -> VoIResult:
        """
        Schätzt den Value of Information für eine Observation Action.
        
        Args:
            state: Aktueller Zustand
            obs_action: Name der Observation Action
        
        Returns:
            VoIResult mit geschätztem Wert
        """
        if obs_action not in self.OBSERVATION_ACTIONS:
            return VoIResult(
                observation_action=obs_action,
                cost=1.0,
                expected_value=0.0,
                net_value=-1.0,
                target_dimension="unknown",
                confidence_gain=0.0
            )
        
        config = self.OBSERVATION_ACTIONS[obs_action]
        cost = config["cost"]
        targets = config["targets"]
        confidence_gain = config["confidence_gain"]
        
        # Berechne erwarteten Wert basierend auf Unsicherheit der Targets
        expected_value = 0.0
        primary_target = targets[0]
        
        for target in targets:
            if target in self.uncertainty_model.uncertainties:
                unc = self.uncertainty_model.uncertainties[target]
                # Höhere Unsicherheit = höherer potenzieller Wert
                potential_value = unc.entropy * 0.5  # Max 0.5 Value pro Dimension
                expected_value += potential_value
        
        # Berücksichtige Entscheidungskontext
        decision_importance = self._estimate_decision_importance(state)
        expected_value *= decision_importance
        
        # Net Value
        net_value = expected_value - cost
        
        return VoIResult(
            observation_action=obs_action,
            cost=cost,
            expected_value=expected_value,
            net_value=net_value,
            target_dimension=primary_target,
            confidence_gain=confidence_gain
        )
    
    def _estimate_decision_importance(self, state: WorldState) -> float:
        """Schätzt wie wichtig die aktuelle Entscheidung ist."""
        importance = 1.0
        
        # Mehr offene Ziele = wichtigere Entscheidungen
        if state.context.open_goals:
            importance += len(state.context.open_goals) * 0.1
        
        # Hohe System Load = wichtigere Entscheidungen
        if state.system.system_load > 0.7:
            importance += 0.3
        
        # Lange kein Kontakt = wichtigere Kommunikationsentscheidungen
        if state.context.last_interaction_minutes_ago:
            if state.context.last_interaction_minutes_ago > 360:  # 6 Stunden
                importance += 0.2
        
        return min(2.0, importance)
    
    def rank_observation_actions(self, state: WorldState) -> List[VoIResult]:
        """
        Rangfolge aller Observation Actions nach Net Value.
        
        Returns:
            Liste von VoIResult, sortiert nach net_value (absteigend)
        """
        results = []
        
        for obs_action in self.OBSERVATION_ACTIONS.keys():
            voi = self.estimate_voi_for_action(state, obs_action)
            results.append(voi)
        
        # Sortiere nach Net Value
        results.sort(key=lambda x: x.net_value, reverse=True)
        return results
    
    def should_observe_before_acting(self, state: WorldState, 
                                      threshold: float = 0.1) -> Tuple[bool, Optional[str]]:
        """
        Entscheidet, ob Observation vor Aktion sinnvoll ist.
        
        Returns:
            (should_observe, best_observation_action)
        """
        ranked = self.rank_observation_actions(state)
        
        if ranked and ranked[0].net_value > threshold:
            return True, ranked[0].observation_action
        
        return False, None
    
    def compute_evpi(self, state: WorldState, n_samples: int = 10) -> float:
        """
        Berechnet den Expected Value of Perfect Information.
        
        EVPI = E[value with perfect info] - E[value with current info]
        
        Args:
            state: Aktueller Zustand
            n_samples: Anzahl Samples für Monte Carlo Schätzung
        
        Returns:
            Geschätzter EVPI
        """
        # Aktueller erwarteter Wert (mit aktueller Unsicherheit)
        current_plan = self.planner.plan(state)
        current_value = current_plan.total_reward
        
        # Simuliere perfekte Information
        perfect_info_values = []
        
        for _ in range(n_samples):
            # Sample einen "wahren" Zustand
            true_state = self._sample_true_state(state)
            
            # Plane mit perfektem Wissen
            plan_with_perfect_info = self.planner.plan(true_state)
            perfect_info_values.append(plan_with_perfect_info.total_reward)
        
        expected_value_perfect_info = sum(perfect_info_values) / len(perfect_info_values)
        
        evpi = expected_value_perfect_info - current_value
        return max(0.0, evpi)
    
    def _sample_true_state(self, state: WorldState) -> WorldState:
        """Samplet einen möglichen "wahren" Zustand basierend auf Unsicherheiten."""
        true_state = deepcopy(state)
        
        # Sample Human Mood
        if "human_mood" in self.uncertainty_model.uncertainties:
            unc = self.uncertainty_model.uncertainties["human_mood"]
            if unc.entropy > 0.3:
                # Sample aus möglichen Moods
                possible_moods = ["happy", "focused", "stressed", "tired", "neutral"]
                true_state.human.mood_estimate = random.choice(possible_moods)
        
        # Sample System Load (mit etwas Rauschen)
        if "system_load" in self.uncertainty_model.uncertainties:
            unc = self.uncertainty_model.uncertainties["system_load"]
            noise = random.gauss(0, unc.entropy * 0.2)
            true_state.system.system_load = max(0.0, min(1.0, 
                state.system.system_load + noise))
        
        return true_state
    
    def get_information_policy(self, state: WorldState) -> Dict[str, Any]:
        """
        Erstellt eine Informationsbeschaffungs-Policy.
        
        Returns:
            Empfohlene Observation Actions und deren Reihenfolge
        """
        # Aktualisiere Unsicherheiten
        self.uncertainty_model.update_from_state(state)
        
        # Rangfolge der Observation Actions
        ranked = self.rank_observation_actions(state)
        
        # EVPI
        evpi = self.compute_evpi(state)
        
        # Empfehlung
        should_observe, best_action = self.should_observe_before_acting(state)
        
        return {
            "current_uncertainty": self.uncertainty_model.to_dict(),
            "evpi": round(evpi, 4),
            "should_observe_before_acting": should_observe,
            "recommended_observation": best_action,
            "ranked_observations": [r.to_dict() for r in ranked[:3]],
            "timestamp": state.time.timestamp
        }


def main():
    """CLI-Interface für den VoI Estimator."""
    import argparse
    
    parser = argparse.ArgumentParser(description="World Model VoI Estimator")
    parser.add_argument("--analyze", action="store_true", 
                       help="Analysiere Unsicherheiten")
    parser.add_argument("--rank-observations", action="store_true",
                       help="Rangfolge Observation Actions")
    parser.add_argument("--evpi", action="store_true",
                       help="Berechne EVPI")
    parser.add_argument("--policy", action="store_true",
                       help="Zeige Informations-Policy")
    
    args = parser.parse_args()
    
    # Initialisiere Komponenten
    from state import StateCollector
    collector = StateCollector()
    
    # Lade oder erstelle State
    state = collector.load_latest()
    if state is None:
        state = collector.collect()
    
    print(f"State: {state.time.timestamp}")
    
    # Erstelle Estimator
    estimator = VoIEstimator()
    estimator.uncertainty_model.update_from_state(state)
    
    if args.analyze:
        print("\n=== Uncertainty Analysis ===")
        print(json.dumps(estimator.uncertainty_model.to_dict(), indent=2))
    
    if args.rank_observations:
        print("\n=== Ranked Observation Actions ===")
        ranked = estimator.rank_observation_actions(state)
        for i, voi in enumerate(ranked, 1):
            print(f"{i}. {voi.observation_action}: "
                  f"net_value={voi.net_value:.3f}, "
                  f"cost={voi.cost:.3f}, "
                  f"target={voi.target_dimension}")
    
    if args.evpi:
        print("\n=== EVPI Calculation ===")
        evpi = estimator.compute_evpi(state)
        print(f"Expected Value of Perfect Information: {evpi:.4f}")
    
    if args.policy:
        print("\n=== Information Policy ===")
        policy = estimator.get_information_policy(state)
        print(json.dumps(policy, indent=2))
    
    # Default: Zeige alles
    if not any([args.analyze, args.rank_observations, args.evpi, args.policy]):
        policy = estimator.get_information_policy(state)
        print(json.dumps(policy, indent=2))


if __name__ == "__main__":
    main()
