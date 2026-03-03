#!/usr/bin/env python3
"""Tests für den SimplePlanner."""

import unittest
import sys
import os

# Füge das Verzeichnis zum Pfad hinzu
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from planner import SimplePlanner, Action, Plan
from state import WorldState, HumanState, ContextState, SystemState, TimeState, EnvironmentState
from simulation_core import SimulationCore


class TestAction(unittest.TestCase):
    """Tests für die Action-Klasse."""
    
    def test_valid_action_types(self):
        """Teste gültige Action-Typen."""
        for action_type in Action.VALID_TYPES:
            action = Action(action_type=action_type)
            self.assertEqual(action.action_type, action_type)
    
    def test_invalid_action_type(self):
        """Teste ungültigen Action-Typ."""
        with self.assertRaises(ValueError):
            Action(action_type="invalid_action")
    
    def test_action_with_params(self):
        """Teste Action mit Parametern."""
        action = Action(action_type="execute_skill", params={"skill_name": "test"})
        self.assertEqual(action.params["skill_name"], "test")
    
    def test_action_to_dict(self):
        """Teste Action-Serialisierung."""
        action = Action(action_type="wait")
        data = action.to_dict()
        self.assertEqual(data["action_type"], "wait")
        self.assertEqual(data["params"], {})


class TestPlan(unittest.TestCase):
    """Tests für die Plan-Klasse."""
    
    def test_plan_creation(self):
        """Teste Plan-Erstellung."""
        actions = [Action("wait"), Action("send_message")]
        plan = Plan(actions=actions, expected_reward=5.0, confidence=0.8, horizon=2)
        self.assertEqual(len(plan.actions), 2)
        self.assertEqual(plan.expected_reward, 5.0)
    
    def test_plan_to_dict(self):
        """Teste Plan-Serialisierung."""
        actions = [Action("wait")]
        plan = Plan(actions=actions, expected_reward=3.0, confidence=0.5, horizon=1)
        data = plan.to_dict()
        self.assertEqual(data["expected_reward"], 3.0)
        self.assertEqual(len(data["actions"]), 1)


class TestSimplePlanner(unittest.TestCase):
    """Tests für den SimplePlanner."""
    
    def setUp(self):
        """Setze Test-Setup auf."""
        self.sim = SimulationCore()
        self.planner = SimplePlanner(self.sim)
        # Erstelle State manuell
        self.state = WorldState(
            time=TimeState.from_now(),
            context=ContextState(),
            system=SystemState(),
            human=HumanState(),
            environment=EnvironmentState()
        )
    
    def test_planner_initialization(self):
        """Teste Planner-Initialisierung."""
        self.assertIsNotNone(self.planner)
        self.assertEqual(len(self.planner.action_types), 3)
    
    def test_plan_generation(self):
        """Teste Plan-Generierung."""
        goal = {"human_mood": "focused"}
        plan = self.planner.plan(self.state, goal, horizon=2)
        
        self.assertIsInstance(plan, Plan)
        self.assertEqual(plan.horizon, 2)
        self.assertLessEqual(len(plan.actions), 2)
    
    def test_plan_with_empty_goal(self):
        """Teste Plan mit leerem Goal."""
        plan = self.planner.plan(self.state, {}, horizon=1)
        self.assertIsInstance(plan, Plan)
    
    def test_simulate_wait_action(self):
        """Teste Simulation der 'wait' Action."""
        action = Action("wait")
        new_state = self.planner._simulate_action(self.state, action)
        self.assertIsInstance(new_state, WorldState)
    
    def test_simulate_send_message_action(self):
        """Teste Simulation der 'send_message' Action."""
        action = Action("send_message")
        new_state = self.planner._simulate_action(self.state, action)
        self.assertIsInstance(new_state, WorldState)
        self.assertIsNotNone(new_state.human.last_interaction)
    
    def test_simulate_execute_skill_action(self):
        """Teste Simulation der 'execute_skill' Action."""
        action = Action("execute_skill", params={"skill_name": "test_skill"})
        new_state = self.planner._simulate_action(self.state, action)
        self.assertIn("test_skill", new_state.system.active_skills)
    
    def test_compute_reward_human_mood(self):
        """Teste Reward-Berechnung für human_mood."""
        goal = {"human_mood": "focused"}
        reward = self.planner._compute_reward(self.state, goal)
        self.assertIsInstance(reward, float)
    
    def test_compute_reward_human_engagement(self):
        """Teste Reward-Berechnung für human_engagement."""
        goal = {"human_engagement": "high"}
        reward = self.planner._compute_reward(self.state, goal)
        self.assertIsInstance(reward, float)
    
    def test_compute_reward_activity_context(self):
        """Teste Reward-Berechnung für activity_context."""
        goal = {"activity_context": "working"}
        reward = self.planner._compute_reward(self.state, goal)
        self.assertIsInstance(reward, float)
    
    def test_beam_search_limits_candidates(self):
        """Teste dass Beam Search Kandidaten limitiert."""
        goal = {"human_mood": "focused"}
        plan = self.planner.plan(self.state, goal, horizon=2, beam_width=2)
        self.assertIsInstance(plan, Plan)


class TestIntegration(unittest.TestCase):
    """Integrationstests."""
    
    def test_end_to_end_planning(self):
        """Teste kompletten Planungs-Workflow."""
        # Setup
        sim = SimulationCore()
        planner = SimplePlanner(sim)
        state = WorldState(
            time=TimeState.from_now(),
            context=ContextState(),
            system=SystemState(),
            human=HumanState(),
            environment=EnvironmentState()
        )
        
        # Goal definieren
        goal = {
            "human_mood": "focused",
            "activity_context": "working"
        }
        
        # Plan generieren
        plan = planner.plan(state, goal, horizon=3)
        
        # Assertions
        self.assertIsInstance(plan, Plan)
        self.assertLessEqual(len(plan.actions), 3)
        self.assertGreaterEqual(plan.confidence, 0.0)
        self.assertLessEqual(plan.confidence, 1.0)
    
    def test_plan_with_multiple_goals(self):
        """Teste Plan mit mehreren Goals."""
        sim = SimulationCore()
        planner = SimplePlanner(sim)
        state = WorldState(
            time=TimeState.from_now(),
            context=ContextState(),
            system=SystemState(),
            human=HumanState(),
            environment=EnvironmentState()
        )
        
        goal = {
            "human_mood": "focused",
            "human_engagement": "high",
            "activity_context": "working"
        }
        
        plan = planner.plan(state, goal, horizon=2)
        self.assertIsInstance(plan, Plan)


if __name__ == "__main__":
    print("=== Running SimplePlanner Tests ===\n")
    unittest.main(verbosity=2)
