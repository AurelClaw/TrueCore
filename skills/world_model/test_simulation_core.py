#!/usr/bin/env python3
"""World Model - Simulation Core Tests"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from simulation_core import SimulationCore
from state import WorldState, TimeState, ContextState, SystemState, HumanState, EnvironmentState


def test_single_path():
    print("\n🧪 Test 1: Single Path Simulation")
    initial_state = WorldState(
        time=TimeState.from_now(),
        context=ContextState(location="test"),
        system=SystemState(),
        human=HumanState(),
        environment=EnvironmentState()
    )
    sim_core = SimulationCore(confidence_decay_rate=0.9)
    actions = ["a1", "a2", "a3"]
    branch = sim_core.simulate_single_path(initial_state, actions, steps=3, branch_name="test")
    assert len(branch.steps) == 4
    print(f"  ✅ {len(branch.steps)} steps, final confidence: {branch.final_confidence:.2%}")
    return True


def test_branching():
    print("\n🧪 Test 2: Branching Simulation")
    initial_state = WorldState(time=TimeState.from_now(), context=ContextState(), system=SystemState(), human=HumanState(), environment=EnvironmentState())
    sim_core = SimulationCore(confidence_decay_rate=0.85)
    action_sequences = {"path_a": ["a1", "a2"], "path_b": ["b1", "b2"]}
    result = sim_core.simulate_branched(initial_state, action_sequences, steps=2)
    assert len(result.branches) == 2
    print(f"  ✅ {len(result.branches)} branches, ID: {result.simulation_id}")
    return True


def test_confidence_decay():
    print("\n🧪 Test 3: Confidence Decay")
    initial_state = WorldState(time=TimeState.from_now(), context=ContextState(), system=SystemState(), human=HumanState(), environment=EnvironmentState())
    sim_core = SimulationCore(confidence_decay_rate=0.8)
    branch = sim_core.simulate_single_path(initial_state, ["a"] * 5, steps=5, branch_name="decay")
    confidences = [s.confidence for s in branch.steps]
    for i in range(1, len(confidences)):
        assert confidences[i] < confidences[i-1]
    print(f"  ✅ Decay verified: {confidences[0]:.2%} → {confidences[-1]:.2%}")
    return True


def run_all():
    print("=" * 60)
    print("🧪 Simulation Core Tests")
    print("=" * 60)
    tests = [test_single_path, test_branching, test_confidence_decay]
    passed = sum(1 for t in tests if t())
    print(f"\n📊 {passed}/{len(tests)} tests passed")
    return passed == len(tests)


if __name__ == "__main__":
    sys.exit(0 if run_all() else 1)
