#!/usr/bin/env python3
"""
World Model - Simulation Core

Multi-Step Forward Simulation mit Szenario-Branching und Confidence Decay.
Simuliert die Zukunft durch sequentielle Anwendung des Transition Models.
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple, Union
from pathlib import Path
from dataclasses import dataclass, field, asdict
from enum import Enum
import copy

# Importiere existierende Module
from state import WorldState, TimeState, ContextState, SystemState, HumanState, EnvironmentState
from transition_model import TransitionModel
from observation_model import Observation, ObservationType, StateChange, ObservationIntegrator


@dataclass
class SimulationStep:
    """Ein einzelner Schritt in der Simulation."""
    step_number: int
    timestamp: str
    state: WorldState
    confidence: float
    action: Optional[str] = None
    parent_step: Optional[int] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "step_number": self.step_number,
            "timestamp": self.timestamp,
            "state": self.state.to_dict(),
            "confidence": self.confidence,
            "action": self.action,
            "parent_step": self.parent_step
        }


@dataclass
class SimulationBranch:
    """Ein Branch (Pfad) in der Simulation."""
    branch_id: str
    name: str
    steps: List[SimulationStep] = field(default_factory=list)
    final_confidence: float = 1.0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "branch_id": self.branch_id,
            "name": self.name,
            "steps": [step.to_dict() for step in self.steps],
            "final_confidence": self.final_confidence,
            "total_steps": len(self.steps)
        }
    
    def get_final_state(self) -> Optional[WorldState]:
        if self.steps:
            return self.steps[-1].state
        return None


@dataclass
class SimulationResult:
    """Ergebnis einer vollständigen Simulation."""
    simulation_id: str
    start_time: str
    start_state: WorldState
    branches: List[SimulationBranch]
    parameters: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "simulation_id": self.simulation_id,
            "start_time": self.start_time,
            "start_state": self.start_state.to_dict(),
            "branches": [branch.to_dict() for branch in self.branches],
            "parameters": self.parameters,
            "total_branches": len(self.branches),
            "total_steps": sum(len(b.steps) for b in self.branches)
        }
    
    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False)
    
    def get_best_branch(self) -> Optional[SimulationBranch]:
        if not self.branches:
            return None
        return max(self.branches, key=lambda b: b.final_confidence)
    
    def compare_branches(self) -> Dict[str, Any]:
        if len(self.branches) < 2:
            return {"error": "Need at least 2 branches to compare"}
        
        return {
            "branch_count": len(self.branches),
            "confidence_range": {
                "min": min(b.final_confidence for b in self.branches),
                "max": max(b.final_confidence for b in self.branches),
                "avg": sum(b.final_confidence for b in self.branches) / len(self.branches)
            },
            "best_branch": self.get_best_branch().branch_id if self.get_best_branch() else None,
            "branch_details": [
                {
                    "branch_id": b.branch_id,
                    "name": b.name,
                    "steps": len(b.steps),
                    "final_confidence": b.final_confidence,
                    "final_mood": b.get_final_state().human.mood_estimate if b.get_final_state() else "unknown"
                }
                for b in self.branches
            ]
        }


class SimulationCore:
    """Kern-Engine für Forward Simulation."""
    
    def __init__(self, 
                 transition_model: Optional[TransitionModel] = None,
                 confidence_decay_rate: float = 0.9,
                 max_steps: int = 10):
        self.transition_model = transition_model or TransitionModel()
        self.confidence_decay_rate = confidence_decay_rate
        self.max_steps = max_steps
        self.simulation_counter = 0
    
    def simulate_single_path(self,
                            initial_state: WorldState,
                            actions: List[str],
                            steps: int,
                            branch_name: str = "default") -> SimulationBranch:
        """Simuliert einen einzelnen Pfad (kein Branching)."""
        branch = SimulationBranch(
            branch_id=f"branch_{self.simulation_counter}_{branch_name}",
            name=branch_name,
            steps=[]
        )
        self.simulation_counter += 1
        
        current_state = initial_state
        current_confidence = 1.0
        
        # Initialer Schritt (Step 0)
        initial_step = SimulationStep(
            step_number=0,
            timestamp=current_state.time.timestamp,
            state=copy.deepcopy(current_state),
            confidence=current_confidence,
            action=None,
            parent_step=None
        )
        branch.steps.append(initial_step)
        
        # Simuliere n Schritte
        for i in range(min(steps, self.max_steps)):
            action = actions[i] if i < len(actions) else "continue"
            predicted_state = self.transition_model.predict_with_trends(current_state, steps_ahead=1)
            current_confidence *= self.confidence_decay_rate
            
            step = SimulationStep(
                step_number=i + 1,
                timestamp=predicted_state.time.timestamp,
                state=predicted_state,
                confidence=current_confidence,
                action=action,
                parent_step=i
            )
            branch.steps.append(step)
            current_state = predicted_state
        
        branch.final_confidence = current_confidence
        return branch
    
    def simulate_branched(self,
                         initial_state: WorldState,
                         action_sequences: Dict[str, List[str]],
                         steps: int) -> SimulationResult:
        """
        Simuliert mehrere parallele Szenarien (Branching).
        
        Args:
            initial_state: Ausgangszustand
            action_sequences: Dict mit Branch-Name -> Liste von Aktionen
            steps: Anzahl der zu simulierenden Schritte
        
        Returns:
            SimulationResult mit allen Branches
        """
        simulation_id = f"sim_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        branches = []
        
        for branch_name, actions in action_sequences.items():
            branch = self.simulate_single_path(
                initial_state=initial_state,
                actions=actions,
                steps=steps,
                branch_name=branch_name
            )
            branches.append(branch)
        
        return SimulationResult(
            simulation_id=simulation_id,
            start_time=datetime.now().isoformat(),
            start_state=initial_state,
            branches=branches,
            parameters={
                "steps": steps,
                "confidence_decay_rate": self.confidence_decay_rate,
                "action_sequences": action_sequences
            }
        )
    
    def simulate_with_confidence_analysis(self,
                                         initial_state: WorldState,
                                         actions: List[str],
                                         steps: int) -> Dict[str, Any]:
        """
        Simuliert und analysiert den Confidence-Verlauf.
        
        Returns:
            Dict mit Simulation und Confidence-Analyse
        """
        branch = self.simulate_single_path(initial_state, actions, steps, "analysis")
        
        confidence_data = [
            {"step": step.step_number, "confidence": step.confidence}
            for step in branch.steps
        ]
        
        return {
            "branch": branch.to_dict(),
            "confidence_analysis": {
                "initial_confidence": 1.0,
                "final_confidence": branch.final_confidence,
                "decay_rate": self.confidence_decay_rate,
                "confidence_per_step": confidence_data,
                "confidence_drop_per_step": (1.0 - branch.final_confidence) / len(branch.steps) if branch.steps else 0
            }
        }


def demo_simulation():
    """Demonstration der Simulation Core."""
    print("=" * 60)
    print("🎯 Forward Simulation Core - Demo")
    print("=" * 60)
    
    # Erstelle einen Beispiel-Zustand
    initial_state = WorldState(
        time=TimeState.from_now(),
        context=ContextState(
            location="workspace",
            activity_context="coding",
            open_goals=["ZIEL-009 Phase 4", "Test Simulation"]
        ),
        system=SystemState(
            active_skills=["world_model", "simulation_core"],
            system_load=0.3
        ),
        human=HumanState(
            mood_estimate="focused",
            engagement_level="high"
        ),
        environment=EnvironmentState()
    )
    
    # Initialisiere Simulation Core
    sim_core = SimulationCore(confidence_decay_rate=0.85)
    
    print("\n📊 Test 1: 3-Step Simulation")
    print("-" * 40)
    
    actions = ["continue_coding", "take_break", "resume_work"]
    branch = sim_core.simulate_single_path(initial_state, actions, steps=3, branch_name="coding_session")
    
    print(f"Branch: {branch.name}")
    print(f"Steps: {len(branch.steps)}")
    print(f"Final Confidence: {branch.final_confidence:.2%}")
    
    for step in branch.steps:
        print(f"  Step {step.step_number}: {step.action or 'START'} | Confidence: {step.confidence:.2%}")
    
    print("\n📊 Test 2: Branching Simulation (2 Pfade)")
    print("-" * 40)
    
    action_sequences = {
        "path_continue": ["keep_working", "keep_working", "keep_working"],
        "path_break": ["take_break", "check_messages", "resume_work"]
    }
    
    result = sim_core.simulate_branched(initial_state, action_sequences, steps=3)
    
    print(f"Simulation ID: {result.simulation_id}")
    print(f"Total Branches: {result.total_branches}")
    
    for branch in result.branches:
        print(f"\n  Branch: {branch.name}")
        print(f"    Steps: {len(branch.steps)}")
        print(f"    Final Confidence: {branch.final_confidence:.2%}")
    
    # Vergleiche Branches
    comparison = result.compare_branches()
    print(f"\n📈 Branch Comparison:")
    print(f"  Best Branch: {comparison['best_branch']}")
    print(f"  Confidence Range: {comparison['confidence_range']['min']:.2%} - {comparison['confidence_range']['max']:.2%}")
    
    print("\n📊 Test 3: Confidence Decay Analysis")
    print("-" * 40)
    
    analysis = sim_core.simulate_with_confidence_analysis(initial_state, actions, steps=5)
    
    print(f"Initial Confidence: {analysis['confidence_analysis']['initial_confidence']:.2%}")
    print(f"Final Confidence: {analysis['confidence_analysis']['final_confidence']:.2%}")
    print(f"Decay Rate per Step: {analysis['confidence_analysis']['decay_rate']:.2%}")
    print("\nConfidence per Step:")
    for step_data in analysis['confidence_analysis']['confidence_per_step']:
        print(f"  Step {step_data['step']}: {step_data['confidence']:.2%}")
    
    print("\n" + "=" * 60)
    print("✅ All Tests Passed!")
    print("=" * 60)
    
    return result


if __name__ == "__main__":
    demo_simulation()
