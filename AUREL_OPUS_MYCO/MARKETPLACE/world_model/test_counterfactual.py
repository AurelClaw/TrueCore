#!/usr/bin/env python3
"""
World Model - Counterfactual Engine Tests

Unit Tests für die Counterfactual Engine.
Testet:
1. Counterfactual Generation
2. Intervention Types
3. Outcome Comparison
4. Logging System
5. Integration mit bestehenden Modulen
"""

import sys
import os
import json
import tempfile
import shutil
from pathlib import Path

# Füge Parent-Verzeichnis zu Path hinzu
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from counterfactual_engine import (
    CounterfactualEngine, DoCalculusEngine,
    Intervention, InterventionType,
    CounterfactualScenario, OutcomeComparison, CounterfactualLog
)
from state import WorldState, TimeState, ContextState, SystemState, HumanState, EnvironmentState
from simulation_core import SimulationCore, SimulationBranch, SimulationStep


class TestCounterfactualEngine:
    """Test-Suite für die Counterfactual Engine."""
    
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.temp_dir = None
    
    def setup(self):
        """Erstellt temporäres Verzeichnis für Tests."""
        self.temp_dir = tempfile.mkdtemp()
        return self
    
    def teardown(self):
        """Räumt temporäres Verzeichnis auf."""
        if self.temp_dir and os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def assert_true(self, condition, message):
        """Hilfsfunktion für Assertions."""
        if condition:
            self.passed += 1
            print(f"  ✅ {message}")
        else:
            self.failed += 1
            print(f"  ❌ {message}")
    
    def assert_equal(self, actual, expected, message):
        """Vergleicht zwei Werte."""
        if actual == expected:
            self.passed += 1
            print(f"  ✅ {message}")
        else:
            self.failed += 1
            print(f"  ❌ {message}")
            print(f"     Expected: {expected}")
            print(f"     Actual: {actual}")
    
    def assert_in_range(self, value, min_val, max_val, message):
        """Prüft, ob Wert in Range liegt."""
        if min_val <= value <= max_val:
            self.passed += 1
            print(f"  ✅ {message}")
        else:
            self.failed += 1
            print(f"  ❌ {message}")
            print(f"     Value {value} not in range [{min_val}, {max_val}]")
    
    def create_test_state(self, **overrides) -> WorldState:
        """Erstellt einen Test-WorldState."""
        state = WorldState(
            time=TimeState.from_now(),
            context=ContextState(
                location="workspace",
                activity_context="testing",
                open_goals=["test_goal"]
            ),
            system=SystemState(
                active_skills=["test_skill"],
                system_load=0.3,
                pending_notifications=1
            ),
            human=HumanState(
                mood_estimate="focused",
                engagement_level="medium"
            ),
            environment=EnvironmentState(
                weather_condition="sunny",
                temperature=20.0
            )
        )
        
        # Wende Overrides an
        for key, value in overrides.items():
            if hasattr(state, key):
                setattr(state, key, value)
        
        return state
    
    # =================================================================
    # Test 1: DoCalculusEngine
    # =================================================================
    
    def test_do_action(self):
        """Test: do_action Intervention."""
        print("\n🧪 Test 1.1: DoCalculusEngine.do_action()")
        
        engine = DoCalculusEngine()
        state = self.create_test_state()
        
        # Teste verschiedene Aktionen
        new_state = engine.do_action(state, "send_greeting")
        
        self.assert_true(
            "greeting" in new_state.context.activity_context or
            any("greet" in e for e in new_state.system.recent_events),
            "Greeting action modifies state correctly"
        )
        
        # Teste Wait-Aktion
        wait_state = engine.do_action(state, "wait")
        self.assert_equal(
            wait_state.context.activity_context,
            "waiting",
            "Wait action sets activity_context to 'waiting'"
        )
    
    def test_do_timing_change(self):
        """Test: do_timing_change Intervention."""
        print("\n🧪 Test 1.2: DoCalculusEngine.do_timing_change()")
        
        engine = DoCalculusEngine()
        state = self.create_test_state()
        
        original_time = state.time.timestamp
        
        # Teste Delay
        delayed_state = engine.do_timing_change(state, 2)
        
        self.assert_true(
            "delayed" in delayed_state.context.activity_context,
            "Timing change marks activity_context as delayed"
        )
        
        # Zeit sollte verschoben sein
        self.assert_true(
            delayed_state.time.timestamp != original_time,
            "Timestamp changes after timing intervention"
        )
    
    def test_do_state_change(self):
        """Test: do_state_change Intervention."""
        print("\n🧪 Test 1.3: DoCalculusEngine.do_state_change()")
        
        engine = DoCalculusEngine()
        state = self.create_test_state()
        
        # Ändere Mood
        new_state = engine.do_state_change(state, "human.mood_estimate", "happy")
        
        self.assert_equal(
            new_state.human.mood_estimate,
            "happy",
            "State change modifies human.mood_estimate"
        )
        
        # Ändere System Load
        load_state = engine.do_state_change(state, "system.system_load", 0.8)
        
        self.assert_equal(
            load_state.system.system_load,
            0.8,
            "State change modifies system.system_load"
        )
    
    # =================================================================
    # Test 2: Counterfactual Generation
    # =================================================================
    
    def test_generate_counterfactual_basic(self):
        """Test: Grundlegende Counterfactual Generation."""
        print("\n🧪 Test 2.1: CounterfactualEngine.generate_counterfactual() - Basic")
        
        engine = CounterfactualEngine(storage_dir=self.temp_dir)
        state = self.create_test_state()
        
        scenario = engine.generate_counterfactual(
            actual_state=state,
            actual_action="action_a",
            counterfactual_action="action_b",
            steps=3
        )
        
        self.assert_true(
            isinstance(scenario, CounterfactualScenario),
            "Returns CounterfactualScenario object"
        )
        
        self.assert_true(
            scenario.scenario_id.startswith("cf_"),
            "Scenario has valid ID"
        )
        
        self.assert_equal(
            scenario.actual_action,
            "action_a",
            "Actual action is stored correctly"
        )
        
        self.assert_equal(
            scenario.counterfactual_action,
            "action_b",
            "Counterfactual action is stored correctly"
        )
        
        self.assert_equal(
            scenario.steps_simulated,
            3,
            "Steps simulated is correct"
        )
    
    def test_generate_counterfactual_timing(self):
        """Test: Counterfactual Generation mit Timing-Intervention."""
        print("\n🧪 Test 2.2: Counterfactual Generation - Timing")
        
        engine = CounterfactualEngine(storage_dir=self.temp_dir)
        state = self.create_test_state()
        
        scenario = engine.generate_counterfactual(
            actual_state=state,
            actual_action="send_now",
            counterfactual_action="delay:1h",
            steps=3,
            intervention_type=InterventionType.TIMING
        )
        
        self.assert_equal(
            scenario.intervention.intervention_type,
            InterventionType.TIMING,
            "Intervention type is TIMING"
        )
        
        self.assert_true(
            len(scenario.actual_outcome.steps) > 0,
            "Actual outcome has steps"
        )
        
        self.assert_true(
            len(scenario.counterfactual_outcome.steps) > 0,
            "Counterfactual outcome has steps"
        )
    
    def test_generate_counterfactual_omission(self):
        """Test: Counterfactual Generation mit Omission-Intervention."""
        print("\n🧪 Test 2.3: Counterfactual Generation - Omission")
        
        engine = CounterfactualEngine(storage_dir=self.temp_dir)
        state = self.create_test_state()
        
        scenario = engine.generate_counterfactual(
            actual_state=state,
            actual_action="send_message",
            counterfactual_action="wait",
            steps=3,
            intervention_type=InterventionType.OMISSION
        )
        
        self.assert_equal(
            scenario.intervention.intervention_type,
            InterventionType.OMISSION,
            "Intervention type is OMISSION"
        )
        
        # Counterfactual sollte "wait" enthalten
        self.assert_true(
            "wait" in scenario.counterfactual_action.lower(),
            "Counterfactual action involves waiting"
        )
    
    # =================================================================
    # Test 3: Outcome Comparison
    # =================================================================
    
    def test_compare_outcomes_structure(self):
        """Test: Outcome Comparison Struktur."""
        print("\n🧪 Test 3.1: CounterfactualEngine.compare_outcomes() - Structure")
        
        engine = CounterfactualEngine(storage_dir=self.temp_dir)
        
        # Erstelle zwei einfache Branches
        state = self.create_test_state()
        
        branch1 = SimulationBranch(
            branch_id="test1",
            name="actual",
            steps=[
                SimulationStep(
                    step_number=0,
                    timestamp=state.time.timestamp,
                    state=state,
                    confidence=1.0
                )
            ],
            final_confidence=0.9
        )
        
        # Modifiziere State für zweiten Branch
        state2 = self.create_test_state()
        state2.human.mood_estimate = "happy"
        
        branch2 = SimulationBranch(
            branch_id="test2",
            name="counterfactual",
            steps=[
                SimulationStep(
                    step_number=0,
                    timestamp=state2.time.timestamp,
                    state=state2,
                    confidence=1.0
                )
            ],
            final_confidence=0.85
        )
        
        comparison = engine.compare_outcomes(branch1, branch2)
        
        self.assert_true(
            isinstance(comparison, OutcomeComparison),
            "Returns OutcomeComparison object"
        )
        
        self.assert_true(
            comparison.comparison_id.startswith("comp_"),
            "Comparison has valid ID"
        )
        
        self.assert_in_range(
            comparison.divergence_score,
            0.0, 1.0,
            "Divergence score is in valid range"
        )
        
        self.assert_in_range(
            comparison.impact_score,
            -1.0, 1.0,
            "Impact score is in valid range"
        )
    
    def test_compare_outcomes_differences(self):
        """Test: Outcome Comparison erkennt Differenzen."""
        print("\n🧪 Test 3.2: Outcome Comparison - Differences")
        
        engine = CounterfactualEngine(storage_dir=self.temp_dir)
        
        # Erstelle zwei unterschiedliche States
        state1 = self.create_test_state()
        state1.human.mood_estimate = "sleepy"
        state1.system.system_load = 0.2
        
        state2 = self.create_test_state()
        state2.human.mood_estimate = "focused"
        state2.system.system_load = 0.5
        
        branch1 = SimulationBranch(
            branch_id="test1",
            name="actual",
            steps=[
                SimulationStep(
                    step_number=0,
                    timestamp=state1.time.timestamp,
                    state=state1,
                    confidence=1.0
                )
            ],
            final_confidence=0.9
        )
        
        branch2 = SimulationBranch(
            branch_id="test2",
            name="counterfactual",
            steps=[
                SimulationStep(
                    step_number=0,
                    timestamp=state2.time.timestamp,
                    state=state2,
                    confidence=1.0
                )
            ],
            final_confidence=0.9
        )
        
        comparison = engine.compare_outcomes(branch1, branch2)
        
        # Sollte Differenzen finden
        self.assert_true(
            len(comparison.state_differences) > 0,
            "Comparison finds state differences"
        )
        
        # Sollte Insights generieren
        self.assert_true(
            len(comparison.key_insights) > 0,
            "Comparison generates key insights"
        )
        
        # Sollte eine Recommendation haben
        self.assert_true(
            comparison.recommendation is not None,
            "Comparison generates recommendation"
        )
    
    def test_divergence_calculation(self):
        """Test: Divergence Score Berechnung."""
        print("\n🧪 Test 3.3: Divergence Score Calculation")
        
        engine = CounterfactualEngine(storage_dir=self.temp_dir)
        
        # Identische States = 0 Divergence
        state = self.create_test_state()
        
        branch1 = SimulationBranch(
            branch_id="test1",
            name="actual",
            steps=[SimulationStep(0, state.time.timestamp, state, 1.0)],
            final_confidence=1.0
        )
        
        branch2 = SimulationBranch(
            branch_id="test2",
            name="counterfactual",
            steps=[SimulationStep(0, state.time.timestamp, state, 1.0)],
            final_confidence=1.0
        )
        
        comparison = engine.compare_outcomes(branch1, branch2)
        
        self.assert_equal(
            comparison.divergence_score,
            0.0,
            "Identical states have 0 divergence"
        )
    
    def test_impact_calculation(self):
        """Test: Impact Score Berechnung."""
        print("\n🧪 Test 3.4: Impact Score Calculation")
        
        engine = CounterfactualEngine(storage_dir=self.temp_dir)
        
        # State mit negativem Mood vs positivem Mood
        state1 = self.create_test_state()
        state1.human.mood_estimate = "frustrated"
        
        state2 = self.create_test_state()
        state2.human.mood_estimate = "positive"
        
        branch1 = SimulationBranch(
            branch_id="test1",
            name="actual",
            steps=[SimulationStep(0, state1.time.timestamp, state1, 1.0)],
            final_confidence=1.0
        )
        
        branch2 = SimulationBranch(
            branch_id="test2",
            name="counterfactual",
            steps=[SimulationStep(0, state2.time.timestamp, state2, 1.0)],
            final_confidence=1.0
        )
        
        comparison = engine.compare_outcomes(branch1, branch2)
        
        # Positive mood in CF sollte positiven Impact haben
        self.assert_true(
            comparison.impact_score > 0,
            "Better mood in counterfactual gives positive impact"
        )
    
    # =================================================================
    # Test 4: Logging System
    # =================================================================
    
    def test_log_counterfactual(self):
        """Test: Counterfactual Logging."""
        print("\n🧪 Test 4.1: CounterfactualEngine.log_counterfactual()")
        
        engine = CounterfactualEngine(storage_dir=self.temp_dir)
        state = self.create_test_state()
        
        # Erstelle Szenario und Comparison
        scenario = engine.generate_counterfactual(
            actual_state=state,
            actual_action="action_a",
            counterfactual_action="action_b",
            steps=2
        )
        
        comparison = engine.compare_outcomes(
            scenario.actual_outcome,
            scenario.counterfactual_outcome,
            scenario.scenario_id
        )
        
        # Logge
        log_path = engine.log_counterfactual(
            scenario=scenario,
            comparison=comparison,
            tags=["test", "demo"],
            notes="Test notes"
        )
        
        self.assert_true(
            os.path.exists(log_path),
            "Log file is created"
        )
        
        self.assert_true(
            log_path.endswith('.json'),
            "Log file has .json extension"
        )
        
        # Prüfe Datei-Inhalt
        with open(log_path, 'r') as f:
            data = json.load(f)
        
        self.assert_true(
            'log_id' in data,
            "Log contains log_id"
        )
        
        self.assert_true(
            'scenario' in data,
            "Log contains scenario"
        )
        
        self.assert_true(
            'comparison' in data,
            "Log contains comparison"
        )
        
        self.assert_equal(
            data.get('tags'),
            ["test", "demo"],
            "Log contains correct tags"
        )
    
    def test_load_logs(self):
        """Test: Laden von Logs."""
        print("\n🧪 Test 4.2: CounterfactualEngine.load_logs()")
        
        engine = CounterfactualEngine(storage_dir=self.temp_dir)
        state = self.create_test_state()
        
        # Erstelle mehrere Logs
        for i in range(3):
            scenario = engine.generate_counterfactual(
                actual_state=state,
                actual_action=f"action_{i}",
                counterfactual_action=f"alt_action_{i}",
                steps=2
            )
            comparison = engine.compare_outcomes(
                scenario.actual_outcome,
                scenario.counterfactual_outcome
            )
            engine.log_counterfactual(scenario, comparison, tags=[f"test_{i}"])
        
        # Lade Logs
        logs = engine.load_logs(limit=10)
        
        self.assert_true(
            len(logs) >= 3,
            f"Loads at least 3 logs (found {len(logs)})"
        )
        
        self.assert_true(
            all(isinstance(l, CounterfactualLog) for l in logs),
            "All loaded items are CounterfactualLog objects"
        )
    
    def test_get_statistics(self):
        """Test: Statistik-Generierung."""
        print("\n🧪 Test 4.3: CounterfactualEngine.get_statistics()")
        
        engine = CounterfactualEngine(storage_dir=self.temp_dir)
        state = self.create_test_state()
        
        # Erstelle einige Logs
        for i in range(3):
            scenario = engine.generate_counterfactual(
                actual_state=state,
                actual_action="action",
                counterfactual_action="alt_action",
                steps=2
            )
            comparison = engine.compare_outcomes(
                scenario.actual_outcome,
                scenario.counterfactual_outcome
            )
            engine.log_counterfactual(scenario, comparison)
        
        stats = engine.get_statistics()
        
        self.assert_true(
            'total_counterfactuals' in stats,
            "Statistics contains total_counterfactuals"
        )
        
        self.assert_true(
            'impact_distribution' in stats,
            "Statistics contains impact_distribution"
        )
        
        self.assert_true(
            'average_scores' in stats,
            "Statistics contains average_scores"
        )
        
        self.assert_equal(
            stats['total_counterfactuals'],
            3,
            "Total counterfactuals count is correct"
        )
    
    # =================================================================
    # Test 5: Integration Tests
    # =================================================================
    
    def test_integration_with_simulation_core(self):
        """Test: Integration mit SimulationCore."""
        print("\n🧪 Test 5.1: Integration with SimulationCore")
        
        sim_core = SimulationCore()
        engine = CounterfactualEngine(
            simulation_core=sim_core,
            storage_dir=self.temp_dir
        )
        
        state = self.create_test_state()
        
        scenario = engine.generate_counterfactual(
            actual_state=state,
            actual_action="test_action",
            counterfactual_action="alt_action",
            steps=3
        )
        
        self.assert_true(
            len(scenario.actual_outcome.steps) == 4,  # 0 + 3 steps
            "SimulationCore integration works for actual outcome"
        )
        
        self.assert_true(
            len(scenario.counterfactual_outcome.steps) == 4,
            "SimulationCore integration works for counterfactual outcome"
        )
    
    def test_end_to_end_counterfactual(self):
        """Test: End-to-End Counterfactual Workflow."""
        print("\n🧪 Test 5.2: End-to-End Counterfactual Workflow")
        
        engine = CounterfactualEngine(storage_dir=self.temp_dir)
        
        # Schritt 1: Initialer Zustand
        state = self.create_test_state()
        state.human.mood_estimate = "sleepy"
        state.context.activity_context = "morning_routine"
        
        # Schritt 2: Generiere Counterfactual
        scenario = engine.generate_counterfactual(
            actual_state=state,
            actual_action="send_morgen_gruss_now",
            counterfactual_action="delay:1h",
            steps=3,
            intervention_type=InterventionType.TIMING
        )
        
        # Schritt 3: Vergleiche Outcomes
        comparison = engine.compare_outcomes(
            scenario.actual_outcome,
            scenario.counterfactual_outcome,
            scenario.scenario_id
        )
        
        # Schritt 4: Logge Ergebnis
        log_path = engine.log_counterfactual(
            scenario=scenario,
            comparison=comparison,
            tags=["morgen_gruss", "timing", "e2e_test"],
            notes="End-to-end test of counterfactual workflow"
        )
        
        # Verifikationen
        self.assert_true(
            os.path.exists(log_path),
            "End-to-end: Log file created"
        )
        
        self.assert_true(
            len(comparison.key_insights) > 0,
            "End-to-end: Insights generated"
        )
        
        self.assert_true(
            scenario.confidence > 0,
            "End-to-end: Confidence calculated"
        )
    
    def test_morgen_gruss_scenario(self):
        """Test: Spezifisches Morgengruß-Szenario."""
        print("\n🧪 Test 5.3: Morgengruß Scenario")
        
        engine = CounterfactualEngine(storage_dir=self.temp_dir)
        
        # Morgengruß-spezifischer Zustand
        state = WorldState(
            time=TimeState.from_now(),
            context=ContextState(
                location="workspace",
                activity_context="morning_routine",
                open_goals=["send_morgen_gruss"]
            ),
            system=SystemState(
                active_skills=["morgen_gruss"],
                system_load=0.2
            ),
            human=HumanState(
                mood_estimate="sleepy",
                engagement_level="low"
            ),
            environment=EnvironmentState(
                weather_condition="sunny"
            )
        )
        
        scenario = engine.generate_counterfactual(
            actual_state=state,
            actual_action="send_morgen_gruss_now",
            counterfactual_action="delay:1h",
            steps=3,
            intervention_type=InterventionType.TIMING
        )
        
        comparison = engine.compare_outcomes(
            scenario.actual_outcome,
            scenario.counterfactual_outcome
        )
        
        self.assert_equal(
            scenario.actual_action,
            "send_morgen_gruss_now",
            "Morgengruß: Actual action stored correctly"
        )
        
        self.assert_equal(
            scenario.counterfactual_action,
            "delay:1h",
            "Morgengruß: Counterfactual action stored correctly"
        )
        
        self.assert_in_range(
            comparison.divergence_score,
            0.0, 1.0,
            "Morgengruß: Valid divergence score"
        )
    
    def test_skill_prioritization_scenario(self):
        """Test: Skill-Priorisierung Szenario."""
        print("\n🧪 Test 5.4: Skill Prioritization Scenario")
        
        engine = CounterfactualEngine(storage_dir=self.temp_dir)
        
        state = WorldState(
            time=TimeState.from_now(),
            context=ContextState(
                location="workspace",
                activity_context="task_processing",
                open_goals=["process_skill_a", "process_skill_b"]
            ),
            system=SystemState(
                active_skills=["orchestrator"],
                system_load=0.4
            ),
            human=HumanState(
                mood_estimate="focused",
                engagement_level="high"
            ),
            environment=EnvironmentState()
        )
        
        scenario = engine.generate_counterfactual(
            actual_state=state,
            actual_action="prioritize:skill_a_first",
            counterfactual_action="prioritize:skill_b_first",
            steps=3,
            intervention_type=InterventionType.SEQUENCE
        )
        
        comparison = engine.compare_outcomes(
            scenario.actual_outcome,
            scenario.counterfactual_outcome
        )
        
        self.assert_true(
            "prioritize" in scenario.actual_action,
            "Skill prioritization: Actual action contains 'prioritize'"
        )
        
        self.assert_equal(
            scenario.intervention.intervention_type,
            InterventionType.SEQUENCE,
            "Skill prioritization: Intervention type is SEQUENCE"
        )
    
    def test_human_interaction_scenario(self):
        """Test: Mensch-Interaktion Szenario (Wait vs Act)."""
        print("\n🧪 Test 5.5: Human Interaction Scenario (Wait vs Act)")
        
        engine = CounterfactualEngine(storage_dir=self.temp_dir)
        
        state = WorldState(
            time=TimeState.from_now(),
            context=ContextState(
                location="workspace",
                activity_context="decision_point",
                last_interaction_minutes_ago=30
            ),
            system=SystemState(
                active_skills=["proactive_decision"],
                system_load=0.3
            ),
            human=HumanState(
                mood_estimate="unknown",
                engagement_level="unknown"
            ),
            environment=EnvironmentState()
        )
        
        scenario = engine.generate_counterfactual(
            actual_state=state,
            actual_action="send_message",
            counterfactual_action="wait",
            steps=3,
            intervention_type=InterventionType.OMISSION
        )
        
        comparison = engine.compare_outcomes(
            scenario.actual_outcome,
            scenario.counterfactual_outcome
        )
        
        self.assert_equal(
            scenario.counterfactual_action,
            "wait",
            "Human interaction: Counterfactual action is 'wait'"
        )
        
        self.assert_equal(
            scenario.intervention.intervention_type,
            InterventionType.OMISSION,
            "Human interaction: Intervention type is OMISSION"
        )
        
        self.assert_true(
            comparison.recommendation is not None,
            "Human interaction: Recommendation generated"
        )
    
    # =================================================================
    # Run All Tests
    # =================================================================
    
    def run_all(self):
        """Führt alle Tests aus."""
        print("=" * 70)
        print("🧪 Counterfactual Engine - Unit Tests")
        print("=" * 70)
        
        self.setup()
        
        try:
            # DoCalculusEngine Tests
            self.test_do_action()
            self.test_do_timing_change()
            self.test_do_state_change()
            
            # Counterfactual Generation Tests
            self.test_generate_counterfactual_basic()
            self.test_generate_counterfactual_timing()
            self.test_generate_counterfactual_omission()
            
            # Outcome Comparison Tests
            self.test_compare_outcomes_structure()
            self.test_compare_outcomes_differences()
            self.test_divergence_calculation()
            self.test_impact_calculation()
            
            # Logging Tests
            self.test_log_counterfactual()
            self.test_load_logs()
            self.test_get_statistics()
            
            # Integration Tests
            self.test_integration_with_simulation_core()
            self.test_end_to_end_counterfactual()
            self.test_morgen_gruss_scenario()
            self.test_skill_prioritization_scenario()
            self.test_human_interaction_scenario()
            
        finally:
            self.teardown()
        
        # Summary
        print("\n" + "=" * 70)
        print("📊 Test Summary")
        print("=" * 70)
        print(f"✅ Passed: {self.passed}")
        print(f"❌ Failed: {self.failed}")
        print(f"📈 Success Rate: {self.passed / (self.passed + self.failed) * 100:.1f}%")
        
        if self.failed == 0:
            print("\n🎉 All tests passed!")
            return True
        else:
            print(f"\n⚠️  {self.failed} test(s) failed")
            return False


def main():
    """Hauptfunktion."""
    tester = TestCounterfactualEngine()
    success = tester.run_all()
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
