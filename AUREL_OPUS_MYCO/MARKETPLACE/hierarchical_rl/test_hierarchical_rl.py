"""
Unit Tests für das Hierarchical Reinforcement Learning System.

Testabdeckung:
- Options Framework
- MAXQ Decomposition
- Goal Hierarchy
- Meta-Controller & Sub-Controllers
- HRL System Integration
- AurelPRO Integration
"""

import json
import sys
import time
import unittest
from pathlib import Path
from typing import Any, Dict, List

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from hierarchical_rl import (
    # Core types
    State, Action, Reward, GoalStatus, OptionStatus,
    # Options
    Option, PrimitiveOption, CompositeOption,
    # MAXQ
    MaxQNode, MaxQHierarchy,
    # Goals
    Goal, GoalHierarchy,
    # Controllers
    Policy, EpsilonGreedyPolicy, UCBPolicy, SubController, MetaController,
    # Environment
    Environment, SimulatedEnvironment,
    # System
    HRLSystem, AurelHRLAdapter,
    # Utils
    create_default_hrl_system,
)


# ============================================================================
# FIXTURES
# ============================================================================

class MockEnvironment(Environment):
    """Mock-Umgebung für deterministische Tests."""
    
    def __init__(self, reward_sequence: List[float] = None):
        self.state = State(features={"step": 0, "test": True})
        self.reward_sequence = reward_sequence or [1.0, 0.5, -0.5, 1.0]
        self.reward_idx = 0
        self.action_history: List[Action] = []
        
    def get_state(self) -> State:
        return self.state
    
    def execute(self, action: Action) -> Reward:
        self.action_history.append(action)
        reward = self.reward_sequence[self.reward_idx % len(self.reward_sequence)]
        self.reward_idx += 1
        
        step = self.state.get("step", 0) + 1
        self.state = self.state.update(step=step)
        
        return Reward(value=reward, source="mock")
    
    def reset(self) -> State:
        self.reward_idx = 0
        self.action_history = []
        self.state = State(features={"step": 0, "test": True})
        return self.state


class CountingOption(Option):
    """Test-Option die nach N Schritten terminiert."""
    
    def __init__(self, name: str, max_steps: int = 3):
        super().__init__(name)
        self.max_steps = max_steps
        self.current_step = 0
        
    def can_initiate(self, state: State) -> bool:
        return True
    
    def should_terminate(self, state: State) -> bool:
        return self.current_step >= self.max_steps
    
    def select_action(self, state: State) -> Action:
        self.current_step += 1
        return Action(name=f"action_{self.current_step}")
    
    def on_initiate(self, state: State) -> None:
        super().on_initiate(state)
        self.current_step = 0


# ============================================================================
# TESTS: Core Types
# ============================================================================

class TestState(unittest.TestCase):
    """Tests für State Klasse."""
    
    def test_state_creation(self):
        state = State(features={"x": 1, "y": 2})
        self.assertEqual(state.get("x"), 1)
        self.assertEqual(state.get("y"), 2)
        self.assertIsNone(state.get("z"))
    
    def test_state_update(self):
        state = State(features={"x": 1})
        new_state = state.update(x=2, z=3)
        
        self.assertEqual(state.get("x"), 1)  # Original unchanged
        self.assertEqual(new_state.get("x"), 2)
        self.assertEqual(new_state.get("z"), 3)
    
    def test_state_default(self):
        state = State()
        self.assertEqual(state.get("missing", "default"), "default")


class TestAction(unittest.TestCase):
    """Tests für Action Klasse."""
    
    def test_action_equality(self):
        a1 = Action(name="move", params={"dir": "up"})
        a2 = Action(name="move", params={"dir": "up"})
        a3 = Action(name="move", params={"dir": "down"})
        
        self.assertEqual(a1, a2)
        self.assertNotEqual(a1, a3)
    
    def test_action_hash(self):
        a1 = Action(name="move", params={"dir": "up"})
        a2 = Action(name="move", params={"dir": "up"})
        
        self.assertEqual(hash(a1), hash(a2))


class TestReward(unittest.TestCase):
    """Tests für Reward Klasse."""
    
    def test_reward_value(self):
        r = Reward(value=5.0, source="test")
        self.assertEqual(float(r), 5.0)
    
    def test_reward_context(self):
        r = Reward(value=1.0, context={"reason": "success"})
        self.assertEqual(r.context["reason"], "success")


# ============================================================================
# TESTS: Options Framework
# ============================================================================

class TestPrimitiveOption(unittest.TestCase):
    """Tests für PrimitiveOption."""
    
    def test_primitive_always_available(self):
        action = Action(name="test")
        option = PrimitiveOption(action)
        state = State()
        
        self.assertTrue(option.can_initiate(state))
        self.assertTrue(option.should_terminate(state))
    
    def test_primitive_returns_action(self):
        action = Action(name="test_action")
        option = PrimitiveOption(action)
        state = State()
        
        result = option.select_action(state)
        self.assertEqual(result, action)
    
    def test_primitive_stats(self):
        action = Action(name="test")
        option = PrimitiveOption(action)
        
        self.assertEqual(option.execution_count, 0)
        option.on_initiate(State())
        self.assertEqual(option.execution_count, 1)
        
        option.update_stats(5.0)
        self.assertEqual(option.total_reward, 5.0)
        self.assertEqual(option.get_q_value(State()), 5.0)


class TestCompositeOption(unittest.TestCase):
    """Tests für CompositeOption."""
    
    def test_composite_sequential_execution(self):
        """Test that composite options correctly sequence through sub-options.
        
        Note: Primitive options return their action immediately but stay RUNNING
        until on_terminate is called. The composite tracks this and advances
        when the sub-option terminates.
        """
        a1 = Action(name="step1")
        a2 = Action(name="step2")
        
        opt1 = PrimitiveOption(a1)
        opt2 = PrimitiveOption(a2)
        
        composite = CompositeOption("test_composite", [opt1, opt2])
        state = State()
        
        # Init
        composite.on_initiate(state)
        self.assertEqual(composite.status, OptionStatus.RUNNING)
        
        # First call should return first action
        result1 = composite.select_action(state)
        self.assertEqual(result1, a1)
        self.assertEqual(composite.current_sub_option_idx, 1)
        
        # Manually terminate the first option (simulating execution completion)
        opt1.on_terminate(state, success=True)
        self.assertEqual(opt1.status, OptionStatus.TERMINATED)
        
        # Now the composite should advance to the second option
        result2 = composite.select_action(state)
        self.assertEqual(result2, a2)
    
    def test_composite_termination(self):
        a1 = Action(name="step1")
        opt1 = PrimitiveOption(a1)
        composite = CompositeOption("test", [opt1])
        
        state = State()
        composite.on_initiate(state)
        
        self.assertFalse(composite.should_terminate(state))
        
        # Execute the only sub-option
        composite.select_action(state)
        
        # After execution, should terminate
        self.assertTrue(composite.should_terminate(state))


class TestCountingOption(unittest.TestCase):
    """Tests für CountingOption (Custom Option)."""
    
    def test_counting_option(self):
        option = CountingOption("counter", max_steps=3)
        state = State()
        
        option.on_initiate(state)
        
        self.assertFalse(option.should_terminate(state))
        option.select_action(state)  # step 1
        
        self.assertFalse(option.should_terminate(state))
        option.select_action(state)  # step 2
        
        self.assertFalse(option.should_terminate(state))
        option.select_action(state)  # step 3
        
        self.assertTrue(option.should_terminate(state))


# ============================================================================
# TESTS: MAXQ Decomposition
# ============================================================================

class TestMaxQNode(unittest.TestCase):
    """Tests für MaxQNode."""
    
    def test_primitive_node(self):
        node = MaxQNode(name="primitive_action", is_primitive=True)
        
        node.update_v("state1", 5.0)
        self.assertEqual(node.get_v_value("state1"), 5.0)
        
        # Primitive node: maxq = v_value
        self.assertEqual(node.get_maxq_value("state1"), 5.0)
    
    def test_composite_node(self):
        child1 = MaxQNode(name="child1", is_primitive=True)
        child2 = MaxQNode(name="child2", is_primitive=True)
        
        parent = MaxQNode(name="parent", is_primitive=False, children=[child1, child2])
        
        # Set completion values
        parent.update_c("state1", "child1", 10.0)
        parent.update_c("state1", "child2", 5.0)
        
        # MAXQ = V^π + max(C)
        self.assertEqual(parent.get_maxq_value("state1"), 10.0)
    
    def test_maxq_updates(self):
        node = MaxQNode(name="test", is_primitive=True)
        
        # Direct value update (simplified for testing)
        node.update_v("s1", 5.0, alpha=0.5)
        self.assertEqual(node.get_v_value("s1"), 5.0)
        
        node.update_v("s1", 10.0, alpha=0.5)
        self.assertEqual(node.get_v_value("s1"), 10.0)


class TestMaxQHierarchy(unittest.TestCase):
    """Tests für MaxQHierarchy."""
    
    def test_hierarchy_indexing(self):
        root = MaxQNode(name="root")
        child = MaxQNode(name="child", is_primitive=True)
        root.children.append(child)
        
        hierarchy = MaxQHierarchy(root)
        
        self.assertIsNotNone(hierarchy.get_node("root"))
        self.assertIsNotNone(hierarchy.get_node("child"))
        self.assertIsNone(hierarchy.get_node("missing"))
    
    def test_path_update(self):
        root = MaxQNode(name="root")
        child = MaxQNode(name="child", is_primitive=True)
        root.children.append(child)
        
        hierarchy = MaxQHierarchy(root)
        
        # Update path
        hierarchy.update_path(["root", "child"], "state1", 5.0)
        
        # Child should have V updated
        self.assertEqual(hierarchy.get_node("child").get_v_value("state1"), 5.0)
        
        # Root should have C updated
        self.assertEqual(hierarchy.get_node("root").get_c_value("state1", "child"), 5.0)


# ============================================================================
# TESTS: Goal Hierarchy
# ============================================================================

class TestGoal(unittest.TestCase):
    """Tests für Goal Klasse."""
    
    def test_goal_creation(self):
        goal = Goal(
            id="test_1",
            name="Test Goal",
            description="A test goal",
            priority=2.0
        )
        
        self.assertEqual(goal.id, "test_1")
        self.assertEqual(goal.name, "Test Goal")
        self.assertEqual(goal.priority, 2.0)
    
    def test_goal_achievement(self):
        goal = Goal(
            id="test",
            name="Position Goal",
            success_criteria=lambda s: s.get("position", 0) >= 10
        )
        
        state_fail = State(features={"position": 5})
        state_success = State(features={"position": 10})
        
        self.assertFalse(goal.is_achieved(state_fail))
        self.assertTrue(goal.is_achieved(state_success))
    
    def test_goal_serialization(self):
        goal = Goal(id="test", name="Test", priority=1.5)
        data = goal.to_dict()
        
        restored = Goal.from_dict(data)
        self.assertEqual(restored.id, goal.id)
        self.assertEqual(restored.name, goal.name)
        self.assertEqual(restored.priority, goal.priority)


class TestGoalHierarchy(unittest.TestCase):
    """Tests für GoalHierarchy."""
    
    def test_add_goal(self):
        hierarchy = GoalHierarchy()
        goal = Goal(id="g1", name="Goal 1")
        
        hierarchy.add_goal(goal)
        
        self.assertEqual(len(hierarchy.goals), 1)
        self.assertIn("g1", hierarchy.root_goals)
    
    def test_goal_hierarchy(self):
        hierarchy = GoalHierarchy()
        
        parent = Goal(id="parent", name="Parent")
        child = Goal(id="child", name="Child", parent_id="parent")
        
        hierarchy.add_goal(parent)
        hierarchy.add_goal(child)
        
        self.assertIn("child", parent.sub_goals)
        self.assertNotIn("child", hierarchy.root_goals)
    
    def test_status_propagation(self):
        hierarchy = GoalHierarchy()
        
        parent = Goal(id="parent", name="Parent")
        child1 = Goal(id="child1", name="Child 1", parent_id="parent")
        child2 = Goal(id="child2", name="Child 2", parent_id="parent")
        
        hierarchy.add_goal(parent)
        hierarchy.add_goal(child1)
        hierarchy.add_goal(child2)
        
        # Initially pending
        self.assertEqual(hierarchy.get_status("parent"), GoalStatus.PENDING)
        
        # One child active
        hierarchy.set_status("child1", GoalStatus.ACTIVE)
        self.assertEqual(hierarchy.get_status("parent"), GoalStatus.IN_PROGRESS)
        
        # All children completed
        hierarchy.set_status("child1", GoalStatus.COMPLETED)
        hierarchy.set_status("child2", GoalStatus.COMPLETED)
        self.assertEqual(hierarchy.get_status("parent"), GoalStatus.COMPLETED)
    
    def test_active_path(self):
        hierarchy = GoalHierarchy()
        
        root = Goal(id="root", name="Root")
        child = Goal(id="child", name="Child", parent_id="root")
        grandchild = Goal(id="grandchild", name="Grandchild", parent_id="child")
        
        hierarchy.add_goal(root)
        hierarchy.add_goal(child)
        hierarchy.add_goal(grandchild)
        
        hierarchy.set_status("grandchild", GoalStatus.ACTIVE)
        
        path = hierarchy.get_active_path("root")
        self.assertEqual(path, ["root", "child", "grandchild"])


# ============================================================================
# TESTS: Policies
# ============================================================================

class TestEpsilonGreedyPolicy(unittest.TestCase):
    """Tests für EpsilonGreedyPolicy."""
    
    def test_policy_selection(self):
        policy = EpsilonGreedyPolicy(epsilon=0.0)  # Pure greedy
        
        action1 = Action(name="a1")
        action2 = Action(name="a2")
        option1 = PrimitiveOption(action1)
        option2 = PrimitiveOption(action2)
        
        state = State()
        
        # Train option1 to be better
        policy.update(state, option1, Reward(value=10.0))
        policy.update(state, option2, Reward(value=1.0))
        
        # Should select option1 (greedy)
        selected = policy.select(state, [option1, option2])
        self.assertEqual(selected, option1)
    
    def test_epsilon_decay(self):
        policy = EpsilonGreedyPolicy(epsilon=1.0, decay=0.5, min_epsilon=0.1)
        
        action = Action(name="test")
        option = PrimitiveOption(action)
        state = State()
        
        # Multiple updates should decay epsilon
        for _ in range(10):
            policy.update(state, option, Reward(value=1.0))
        
        self.assertLess(policy.epsilon, 1.0)
        self.assertGreaterEqual(policy.epsilon, 0.1)


class TestUCBPolicy(unittest.TestCase):
    """Tests für UCBPolicy."""
    
    def test_ucb_exploration(self):
        policy = UCBPolicy(c=1.0)
        
        action1 = Action(name="a1")
        action2 = Action(name="a2")
        option1 = PrimitiveOption(action1)
        option2 = PrimitiveOption(action2)
        
        state = State()
        
        # Train option1 many times
        for _ in range(10):
            policy.update(state, option1, Reward(value=5.0))
        
        # Option2 unexplored - should be selected due to UCB bonus
        selected = policy.select(state, [option1, option2])
        self.assertEqual(selected, option2)
    
    def test_ucb_convergence(self):
        policy = UCBPolicy(c=0.1)  # Low exploration
        
        action1 = Action(name="a1")
        action2 = Action(name="a2")
        option1 = PrimitiveOption(action1)
        option2 = PrimitiveOption(action2)
        
        state = State()
        
        # Train both options
        for _ in range(10):
            policy.update(state, option1, Reward(value=10.0))
            policy.update(state, option2, Reward(value=1.0))
        
        # Should converge to option1
        selections = [policy.select(state, [option1, option2]) for _ in range(10)]
        option1_selections = sum(1 for s in selections if s == option1)
        
        self.assertGreater(option1_selections, 5)  # Majority should be option1


# ============================================================================
# TESTS: Controllers
# ============================================================================

class TestSubController(unittest.TestCase):
    """Tests für SubController."""
    
    def test_controller_execution(self):
        env = MockEnvironment(reward_sequence=[1.0, 2.0, 3.0])
        policy = EpsilonGreedyPolicy(epsilon=0.0)
        
        # Create option that runs for 3 steps
        option = CountingOption("test", max_steps=3)
        controller = SubController(option, policy)
        
        state = env.get_state()
        reward, success = controller.execute(state, env)
        
        self.assertTrue(success)
        self.assertEqual(reward, 6.0)  # 1.0 + 2.0 + 3.0
        self.assertEqual(len(controller.execution_history), 3)


class TestMetaController(unittest.TestCase):
    """Tests für MetaController."""
    
    def test_goal_selection(self):
        hierarchy = GoalHierarchy()
        policy = EpsilonGreedyPolicy(epsilon=0.0)
        controller = MetaController(policy, hierarchy)
        
        # Add goal with option
        goal = Goal(id="g1", name="Goal 1")
        action = Action(name="action1")
        option = PrimitiveOption(action)
        
        hierarchy.add_goal(goal)
        controller.register_option(option, goal.id)
        
        state = State()
        selected = controller.select_goal(state)
        
        self.assertIsNotNone(selected)
        self.assertEqual(selected.id, "g1")
    
    def test_episode_execution(self):
        hierarchy = GoalHierarchy()
        policy = EpsilonGreedyPolicy(epsilon=0.0)
        controller = MetaController(policy, hierarchy)
        env = MockEnvironment(reward_sequence=[1.0])
        
        # Add goals
        for i in range(3):
            goal = Goal(id=f"g{i}", name=f"Goal {i}")
            action = Action(name=f"action{i}")
            option = PrimitiveOption(action)
            hierarchy.add_goal(goal)
            controller.register_option(option, goal.id)
        
        result = controller.run_episode(env, max_goals=2)
        
        # With primitive options that terminate immediately, we should complete goals
        self.assertEqual(result["goals_completed"], 2)
        self.assertEqual(result["goals_attempted"], 2)
        # Each goal execution returns the reward from the environment
        # Note: PrimitiveOption returns action immediately, but SubController
        # executes the action in the environment and gets reward
        # The total_reward should be 2.0 (1.0 per goal)
        self.assertEqual(result["total_reward"], 2.0, 
                        f"Expected total_reward=2.0, got {result['total_reward']}")


# ============================================================================
# TESTS: HRL System Integration
# ============================================================================

class TestHRLSystem(unittest.TestCase):
    """Tests für HRLSystem."""
    
    def test_system_initialization(self):
        system = HRLSystem()
        system.initialize()
        
        self.assertIsNotNone(system.meta_controller)
        self.assertIsNotNone(system.maxq_hierarchy)
        self.assertIsNotNone(system.goal_hierarchy)
    
    def test_add_goal(self):
        system = HRLSystem()
        system.initialize()
        
        goal = Goal(id="test", name="Test Goal")
        system.add_goal(goal)
        
        self.assertEqual(len(system.goal_hierarchy.goals), 1)
        self.assertIsNotNone(system.goal_hierarchy.get_goal("test"))
    
    def test_add_goal_with_option(self):
        system = HRLSystem()
        system.initialize()
        
        goal = Goal(id="test", name="Test Goal")
        action = Action(name="test_action")
        option = PrimitiveOption(action)
        
        system.add_goal(goal, option)
        
        self.assertEqual(len(system.meta_controller.options), 1)
    
    def test_training(self):
        system = HRLSystem()
        system.initialize()
        
        # Add some goals
        for i in range(2):
            goal = Goal(id=f"g{i}", name=f"Goal {i}")
            action = Action(name=f"action{i}")
            option = PrimitiveOption(action)
            system.add_goal(goal, option)
        
        env = MockEnvironment(reward_sequence=[1.0])
        result = system.train(episodes=5, env=env)
        
        self.assertEqual(result["episodes"], 5)
        self.assertIn("avg_reward", result)
    
    def test_save_load(self):
        import tempfile
        import os
        
        with tempfile.TemporaryDirectory() as tmpdir:
            system = HRLSystem(storage_path=Path(tmpdir))
            system.initialize()
            
            goal = Goal(id="test", name="Test Goal")
            system.add_goal(goal)
            
            filepath = system.save("test_state.json")
            
            # Verify file exists
            self.assertTrue(filepath.exists())
            
            # Load into new system
            new_system = HRLSystem(storage_path=Path(tmpdir))
            new_system.load(filepath)
            
            self.assertEqual(len(new_system.goal_hierarchy.goals), 1)
            self.assertIsNotNone(new_system.goal_hierarchy.get_goal("test"))
    
    def test_get_stats(self):
        system = HRLSystem()
        system.initialize()
        
        # Add goals
        for i in range(3):
            goal = Goal(id=f"g{i}", name=f"Goal {i}")
            system.add_goal(goal)
        
        stats = system.get_stats()
        
        self.assertEqual(stats["num_goals"], 3)
        self.assertEqual(stats["num_root_goals"], 3)
        self.assertEqual(stats["training_episodes"], 0)


# ============================================================================
# TESTS: AurelPRO Integration
# ============================================================================

class TestAurelHRLAdapter(unittest.TestCase):
    """Tests für AurelHRLAdapter."""
    
    def test_convert_aurel_goal(self):
        system = HRLSystem()
        adapter = AurelHRLAdapter(system)
        
        aurel_data = {
            "id": "ziel_001",
            "name": "Learn Skill",
            "description": "Learn a new skill",
            "priority": 2.5,
            "metadata": {"category": "learning"}
        }
        
        goal = adapter.convert_aurel_goal(aurel_data)
        
        self.assertEqual(goal.id, "ziel_001")
        self.assertEqual(goal.name, "Learn Skill")
        self.assertEqual(goal.priority, 2.5)
    
    def test_create_skill_learning_goal(self):
        system = HRLSystem()
        system.initialize()
        adapter = AurelHRLAdapter(system)
        
        goal, option = adapter.create_skill_learning_goal("TestSkill")
        
        self.assertEqual(goal.id, "skill_TestSkill")
        self.assertEqual(goal.name, "Learn TestSkill")
        self.assertEqual(option.name, "learn_TestSkill")
        self.assertEqual(len(option.sub_options), 3)  # research, implement, test
    
    def test_recommended_goal(self):
        system = HRLSystem()
        system.initialize()
        adapter = AurelHRLAdapter(system)
        
        # Add a goal
        goal = Goal(id="test", name="Test")
        action = Action(name="test_action")
        option = PrimitiveOption(action)
        system.add_goal(goal, option)
        
        state = State()
        recommended = adapter.get_recommended_next_goal(state)
        
        self.assertEqual(recommended, "test")


# ============================================================================
# TESTS: Default System
# ============================================================================

class TestDefaultSystem(unittest.TestCase):
    """Tests für create_default_hrl_system."""
    
    def test_default_system_creation(self):
        system = create_default_hrl_system()
        
        self.assertIsNotNone(system.meta_controller)
        self.assertGreaterEqual(len(system.meta_controller.options), 3)
    
    def test_default_system_runs(self):
        system = create_default_hrl_system()
        
        # Add a goal using default options
        goal = Goal(id="test", name="Test Goal")
        system.add_goal(goal)
        
        # Should be able to train
        result = system.train(episodes=2)
        self.assertEqual(result["episodes"], 2)


# ============================================================================
# TESTS: SimulatedEnvironment
# ============================================================================

class TestSimulatedEnvironment(unittest.TestCase):
    """Tests für SimulatedEnvironment."""
    
    def test_environment_basics(self):
        env = SimulatedEnvironment()
        
        state = env.get_state()
        self.assertEqual(state.get("step"), 0)
        self.assertEqual(state.get("position"), 0)
    
    def test_move_actions(self):
        env = SimulatedEnvironment()
        
        # Move forward
        reward = env.execute(Action(name="move_forward"))
        self.assertEqual(float(reward), 1.0)
        self.assertEqual(env.get_state().get("position"), 1)
        
        # Move backward
        reward = env.execute(Action(name="move_backward"))
        self.assertEqual(float(reward), -0.5)
        self.assertEqual(env.get_state().get("position"), 0)
    
    def test_reset(self):
        env = SimulatedEnvironment()
        
        env.execute(Action(name="move_forward"))
        env.reset()
        
        self.assertEqual(env.get_state().get("position"), 0)
        self.assertEqual(env.get_state().get("step"), 0)


# ============================================================================
# MAIN
# ============================================================================

def run_tests():
    """Führt alle Tests aus und gibt Coverage-Informationen aus."""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    test_classes = [
        # Core types
        TestState, TestAction, TestReward,
        # Options
        TestPrimitiveOption, TestCompositeOption, TestCountingOption,
        # MAXQ
        TestMaxQNode, TestMaxQHierarchy,
        # Goals
        TestGoal, TestGoalHierarchy,
        # Policies
        TestEpsilonGreedyPolicy, TestUCBPolicy,
        # Controllers
        TestSubController, TestMetaController,
        # System
        TestHRLSystem, TestAurelHRLAdapter, TestDefaultSystem,
        # Environment
        TestSimulatedEnvironment,
    ]
    
    for test_class in test_classes:
        tests = loader.loadTestsFromTestCase(test_class)
        suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    coverage = ((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100) if result.testsRun > 0 else 0
    print(f"Success Rate: {coverage:.1f}%")
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
