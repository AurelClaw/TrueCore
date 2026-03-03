#!/usr/bin/env python3
"""
World Model - Counterfactual Engine Tests

Test-Suite für die Counterfactual Engine (Phase 5).
"""

import unittest
import sys
import os
from datetime import datetime
from copy import deepcopy

# Füge Parent-Directory zu Path hinzu
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from counterfactual_engine import (
    CounterfactualSimulator,
    CounterfactualEngine,
    DoCalculus,
    CounterfactualScenario,
    ImpactAnalysis,
    DeviationAnalysis,
    ScenarioType
)
from state import (
    WorldState,
    TimeState,
    ContextState,
    SystemState,
    HumanState,
    EnvironmentState
)


class TestDoCalculus(unittest.TestCase):
    """Tests für DoCalculus-Klasse."""
    
    def setUp(self):
        """Erstellt Test-Zustand."""
        self.state = WorldState(
            time=TimeState.from_now(),
            context=ContextState(
                location="test",
                activity_context="testing"
            ),
            system=SystemState(
                system_load=0.3,
                pending_notifications=2
            ),
            human=HumanState(
                mood_estimate="neutral",
                engagement_level="medium"
            ),
            environment=EnvironmentState()
        )
        self.do = DoCalculus()
    
    def test_intervene_basic(self):
        """Test: Einfache Intervention."""
        new_state = self.do.intervene(
            self.state,
            "human.mood_estimate",
            "positive"
        )
        
        self.assertEqual(new_state.human.mood_estimate, "positive")
        self.assertEqual(self.state.human.mood_estimate, "neutral")  # Original unverändert
    
    def test_intervene_system_load(self):
        """Test: Intervention auf System Load."""
        new_state = self.do.intervene(
            self.state,
            "system.system_load",
            0.8
        )
        
        self.assertEqual(new_state.system.system_load, 0.8)
    
    def test_intervene_invalid_path(self):
        """Test: Ungültiger Pfad sollte Fehler werfen."""
        with self.assertRaises(ValueError):
            self.do.intervene(self.state, "invalid_path", "value")
        
        with self.assertRaises(ValueError):
            self.do.intervene(self.state, "nonexistent.field", "value")
    
    def test_observe_basic(self):
        """Test: Einfache Observation."""
        value = self.do.observe(self.state, "human.mood_estimate")
        self.assertEqual(value, "neutral")
    
    def test_observe_system(self):
        """Test: Observation von System-Variablen."""
        value = self.do.observe(self.state, "system.system_load")
        self.assertEqual(value, 0.3)
    
    def test_counterfactual_query(self):
        """Test: Counterfactual Query."""
        result = self.do.counterfactual_query(
            self.state,
            intervention={"variable": "human.engagement_level", "value": "high"},
            outcome_variable="context.activity_context"
        )
        
        self.assertEqual(result["query_type"], "counterfactual")
        self.assertEqual(result["intervention"]["variable"], "human.engagement_level")
        self.assertEqual(result["intervention"]["value"], "high")
        self.assertIn("explanation", result)
    
    def test_intervention_history(self):
        """Test: Intervention History wird geführt."""
        self.do.intervene(self.state, "human.mood_estimate", "positive")
        self.do.observe(self.state, "system.system_load")
        
        self.assertEqual(len(self.do.intervention_history), 2)
        self.assertEqual(self.do.intervention_history[0]["type"], "intervention")
        self.assertEqual(self.do.intervention_history[1]["type"], "observation")


class TestCounterfactualSimulator(unittest.TestCase):
    """Tests für CounterfactualSimulator-Klasse."""
    
    def setUp(self):
        """Erstellt Simulator und Test-Zustand."""
        self.simulator = CounterfactualSimulator()
        self.state = WorldState(
            time=TimeState.from_now(),
            context=ContextState(
                location="test",
                activity_context="testing",
                open_goals=["test_goal"]
            ),
            system=SystemState(
                system_load=0.2,
                pending_notifications=0
            ),
            human=HumanState(
                mood_estimate="unknown",
                engagement_level="unknown"
            ),
            environment=EnvironmentState()
        )
    
    def test_simulate_noop(self):
        """Test: Baseline-Simulation (noop)."""
        scenario = self.simulator.simulate_noop(self.state, steps=1)
        
        self.assertEqual(scenario.scenario_type, ScenarioType.NOOP)
        self.assertEqual(len(scenario.interventions), 0)
        self.assertIsNotNone(scenario.predicted_outcome)
        self.assertIn(scenario, self.simulator.scenarios)
    
    def test_simulate_alternative(self):
        """Test: Alternative-Szenario."""
        scenario = self.simulator.simulate_alternative(
            self.state,
            action="send_message",
            scenario_type=ScenarioType.ALTERNATIVE_ACTION,
            parameters={"mood": "positive"}
        )
        
        self.assertEqual(scenario.scenario_type, ScenarioType.ALTERNATIVE_ACTION)
        self.assertGreater(len(scenario.interventions), 0)
        self.assertIsNotNone(scenario.predicted_outcome)
        self.assertIn(scenario, self.simulator.scenarios)
    
    def test_simulate_scenario_types(self):
        """Test: Alle Szenario-Typen."""
        for scenario_type in [
            ScenarioType.BEST_CASE,
            ScenarioType.EXPECTED,
            ScenarioType.WORST_CASE,
            ScenarioType.NOOP,
            ScenarioType.ALTERNATIVE_ACTION
        ]:
            scenario = self.simulator.simulate_scenario_type(
                self.state,
                scenario_type,
                action="test_action"
            )
            self.assertEqual(scenario.scenario_type, scenario_type)
    
    def test_calculate_counterfactual_impact(self):
        """Test: Impact-Berechnung."""
        baseline = self.simulator.simulate_noop(self.state)
        alternative = self.simulator.simulate_alternative(
            self.state,
            action="send_message"
        )
        
        impact = self.simulator.calculate_counterfactual_impact(baseline, alternative)
        
        self.assertIsInstance(impact, ImpactAnalysis)
        self.assertEqual(impact.baseline_scenario_id, baseline.scenario_id)
        self.assertEqual(impact.alternative_scenario_id, alternative.scenario_id)
        self.assertIn(impact.mood_change, ["improved", "worsened", "unchanged"])
        self.assertIn(impact.engagement_change, ["increased", "decreased", "unchanged"])
        self.assertGreaterEqual(impact.risk_score, 0)
        self.assertLessEqual(impact.risk_score, 1)
        self.assertGreaterEqual(impact.opportunity_score, 0)
        self.assertLessEqual(impact.opportunity_score, 1)
    
    def test_compare_scenarios(self):
        """Test: Szenario-Vergleich."""
        baseline = self.simulator.simulate_noop(self.state)
        alt1 = self.simulator.simulate_alternative(self.state, "action1")
        alt2 = self.simulator.simulate_alternative(self.state, "action2")
        
        analyses = self.simulator.compare_scenarios(baseline, [alt1, alt2])
        
        self.assertEqual(len(analyses), 2)
        for analysis in analyses:
            self.assertIsInstance(analysis, ImpactAnalysis)
    
    def test_deviation_analysis(self):
        """Test: Abweichungsanalyse."""
        predicted = deepcopy(self.state)
        actual = deepcopy(self.state)
        actual.human.mood_estimate = "negative"
        actual.system.system_load = 0.6
        
        analysis = self.simulator.deviation_analysis(predicted, actual)
        
        self.assertIsInstance(analysis, DeviationAnalysis)
        self.assertGreater(analysis.deviation_score, 0)
        self.assertGreater(len(analysis.key_factors), 0)
        self.assertGreater(len(analysis.explanation), 0)
        self.assertIn(analysis, self.simulator.deviation_analyses)
    
    def test_identify_key_factors(self):
        """Test: Schlüsselfaktoren-Identifikation."""
        predicted = deepcopy(self.state)
        actual = deepcopy(self.state)
        actual.human.mood_estimate = "positive"
        actual.system.system_load = 0.8
        
        factors = self.simulator.identify_key_factors(predicted, actual)
        
        self.assertGreater(len(factors), 0)
        for factor in factors:
            self.assertIn("field", factor)
            self.assertIn("predicted", factor)
            self.assertIn("actual", factor)
            self.assertIn("influence_score", factor)
            self.assertIn("category", factor)
            self.assertGreaterEqual(factor["influence_score"], 0)
            self.assertLessEqual(factor["influence_score"], 1)
    
    def test_action_to_interventions(self):
        """Test: Aktion-zu-Intervention Mapping."""
        interventions = self.simulator._action_to_interventions(
            "send_message",
            {"mood": "positive"}
        )
        
        self.assertGreater(len(interventions), 0)
        for intervention in interventions:
            self.assertIn("variable", intervention)
            self.assertIn("value", intervention)
    
    def test_calculate_risk_score(self):
        """Test: Risiko-Score-Berechnung."""
        base = deepcopy(self.state)
        alt = deepcopy(self.state)
        alt.system.system_load = 0.9
        alt.system.pending_notifications = 10
        alt.human.mood_estimate = "negative"
        
        risk = self.simulator._calculate_risk_score(base, alt)
        
        self.assertGreater(risk, 0)
        self.assertLessEqual(risk, 1)
    
    def test_calculate_opportunity_score(self):
        """Test: Opportunity-Score-Berechnung."""
        base = deepcopy(self.state)
        alt = deepcopy(self.state)
        alt.human.mood_estimate = "positive"
        alt.human.engagement_level = "high"
        alt.system.system_load = 0.1
        
        opportunity = self.simulator._calculate_opportunity_score(base, alt)
        
        self.assertGreater(opportunity, 0)
        self.assertLessEqual(opportunity, 1)
    
    def test_save_and_load_scenario(self):
        """Test: Speichern und Laden von Szenarien."""
        scenario = self.simulator.simulate_noop(self.state)
        
        # Speichern
        filepath = self.simulator.save_scenario(scenario)
        self.assertTrue(os.path.exists(filepath))
        
        # Laden
        loaded = self.simulator.load_scenario(scenario.scenario_id)
        self.assertIsNotNone(loaded)
        self.assertEqual(loaded.scenario_id, scenario.scenario_id)
        self.assertEqual(loaded.scenario_type, scenario.scenario_type)
        
        # Cleanup
        os.remove(filepath)
    
    def test_list_saved_scenarios(self):
        """Test: Auflisten gespeicherter Szenarien."""
        scenario = self.simulator.simulate_noop(self.state)
        filepath = self.simulator.save_scenario(scenario)
        
        scenarios = self.simulator.list_saved_scenarios()
        self.assertIn(scenario.scenario_id, scenarios)
        
        # Cleanup
        os.remove(filepath)


class TestCounterfactualEngine(unittest.TestCase):
    """Tests für CounterfactualEngine (High-Level API)."""
    
    def setUp(self):
        """Erstellt Engine und Test-Zustand."""
        self.engine = CounterfactualEngine()
        self.state = WorldState(
            time=TimeState.from_now(),
            context=ContextState(
                location="test",
                activity_context="testing"
            ),
            system=SystemState(system_load=0.2),
            human=HumanState(),
            environment=EnvironmentState()
        )
    
    def test_what_if(self):
        """Test: Einfache What-If-Abfrage."""
        result = self.engine.what_if(
            self.state,
            action="send_message",
            parameters={"mood": "positive"}
        )
        
        self.assertIn("query", result)
        self.assertIn("baseline", result)
        self.assertIn("alternative", result)
        self.assertIn("impact", result)
        self.assertIn("recommendation", result)
        self.assertIn(result["recommendation"], ["proceed", "reconsider"])
    
    def test_compare_actions(self):
        """Test: Aktions-Vergleich."""
        comparison = self.engine.compare_actions(
            self.state,
            actions=["action1", "action2", "action3"],
            parameters={"action1": {"param": "value"}}
        )
        
        self.assertIn("actions_compared", comparison)
        self.assertEqual(len(comparison["actions_compared"]), 3)
        self.assertIn("recommended_action", comparison)
        self.assertIn("impacts", comparison)
        self.assertEqual(len(comparison["impacts"]), 3)
        self.assertIn(comparison["recommended_action"], comparison["actions_compared"])
    
    def test_analyze_prediction_error(self):
        """Test: Vorhersagefehler-Analyse."""
        predicted = deepcopy(self.state)
        actual = deepcopy(self.state)
        actual.human.mood_estimate = "negative"
        
        analysis = self.engine.analyze_prediction_error(predicted, actual)
        
        self.assertIn("deviation_score", analysis)
        self.assertIn("explanation", analysis)
        self.assertIn("key_factors", analysis)
        self.assertIn("lessons_learned", analysis)
        self.assertIn("improvement_suggestions", analysis)
        self.assertGreater(len(analysis["lessons_learned"]), 0)


class TestIntegration(unittest.TestCase):
    """Integration-Tests."""
    
    def setUp(self):
        """Erstellt komplexen Test-Zustand."""
        self.state = WorldState(
            time=TimeState.from_now(),
            context=ContextState(
                location="workspace",
                activity_context="morning_routine",
                last_interaction_minutes_ago=480,
                open_goals=["ZIEL-009", "test_goal"],
                recent_topics=["world_model", "testing"]
            ),
            system=SystemState(
                active_skills=["world_model", "test_skill"],
                system_load=0.3,
                pending_notifications=2,
                recent_events=["event1", "event2"]
            ),
            human=HumanState(
                mood_estimate="neutral",
                engagement_level="medium",
                recent_successes=["success1"],
                recent_frustrations=[]
            ),
            environment=EnvironmentState(
                weather_condition="clear",
                temperature=20.0,
                calendar_load="light"
            )
        )
        self.engine = CounterfactualEngine()
    
    def test_full_counterfactual_workflow(self):
        """Test: Kompletter Counterfactual-Workflow."""
        # 1. What-If-Analyse
        result = self.engine.what_if(
            self.state,
            action="delay_morning_greeting",
            parameters={"delay": "1h"}
        )
        
        self.assertIsNotNone(result)
        impact = result["impact"]
        
        # 2. Vergleiche mit anderen Aktionen
        comparison = self.engine.compare_actions(
            self.state,
            actions=["send_now", "delay_1h", "skip"]
        )
        
        self.assertIsNotNone(comparison)
        self.assertIn(comparison["recommended_action"], ["send_now", "delay_1h", "skip"])
        
        # 3. Simuliere Vorhersagefehler
        predicted = self.engine.simulator.transition_model.predict_with_trends(self.state)
        actual = deepcopy(self.state)
        actual.human.mood_estimate = "negative"
        
        error_analysis = self.engine.analyze_prediction_error(predicted, actual)
        self.assertIsNotNone(error_analysis)
        self.assertGreater(error_analysis["deviation_score"], 0)
    
    def test_do_calculus_integration(self):
        """Test: Do-Calculus Integration."""
        # Intervention
        intervened = self.engine.simulator.do_calculus.intervene(
            self.state,
            "human.mood_estimate",
            "positive"
        )
        
        self.assertEqual(intervened.human.mood_estimate, "positive")
        self.assertEqual(self.state.human.mood_estimate, "neutral")  # Original unverändert
        
        # Observation
        mood = self.engine.simulator.do_calculus.observe(intervened, "human.mood_estimate")
        self.assertEqual(mood, "positive")
        
        # Counterfactual Query
        result = self.engine.simulator.do_calculus.counterfactual_query(
            self.state,
            intervention={"variable": "system.system_load", "value": 0.9},
            outcome_variable="human.mood_estimate"
        )
        
        self.assertIn("counterfactual_outcome", result)
        self.assertIn("explanation", result)
    
    def test_scenario_persistence(self):
        """Test: Szenario-Persistenz."""
        # Erstelle und speichere Szenario
        scenario = self.engine.simulator.simulate_alternative(
            self.state,
            action="test_action"
        )
        
        filepath = self.engine.simulator.save_scenario(scenario)
        self.assertTrue(os.path.exists(filepath))
        
        # Lade Szenario
        loaded = self.engine.simulator.load_scenario(scenario.scenario_id)
        self.assertIsNotNone(loaded)
        self.assertEqual(loaded.scenario_id, scenario.scenario_id)
        self.assertEqual(loaded.name, scenario.name)
        
        # Cleanup
        os.remove(filepath)


class TestEdgeCases(unittest.TestCase):
    """Tests für Edge Cases und Fehlerbehandlung."""
    
    def setUp(self):
        self.simulator = CounterfactualSimulator()
        self.engine = CounterfactualEngine()
        self.state = WorldState()
    
    def test_empty_state(self):
        """Test: Leerer Zustand."""
        empty_state = WorldState()
        
        scenario = self.simulator.simulate_noop(empty_state)
        self.assertIsNotNone(scenario.predicted_outcome)
    
    def test_unknown_action(self):
        """Test: Unbekannte Aktion."""
        scenario = self.simulator.simulate_alternative(
            self.state,
            action="unknown_action_xyz"
        )
        
        self.assertIsNotNone(scenario)
        self.assertGreater(len(scenario.interventions), 0)
    
    def test_invalid_variable_path(self):
        """Test: Ungültiger Variablen-Pfad."""
        with self.assertRaises(ValueError):
            self.simulator.do_calculus.intervene(
                self.state,
                "invalid.path.format.here",
                "value"
            )
    
    def test_none_values_in_comparison(self):
        """Test: None-Werte im Vergleich."""
        baseline = CounterfactualScenario(
            scenario_id="base",
            scenario_type=ScenarioType.NOOP,
            name="baseline",
            base_state=self.state,
            interventions=[],
            predicted_outcome=None,  # None!
            confidence=1.0
        )
        
        alternative = self.simulator.simulate_noop(self.state)
        
        with self.assertRaises(ValueError):
            self.simulator.calculate_counterfactual_impact(baseline, alternative)
    
    def test_very_large_deviation(self):
        """Test: Sehr große Abweichung."""
        predicted = deepcopy(self.state)
        actual = deepcopy(self.state)
        
        # Extreme Werte - mehrere Änderungen für höhere Abweichung
        actual.system.system_load = 100.0
        actual.system.pending_notifications = 1000
        actual.human.mood_estimate = "extremely_negative"
        actual.human.engagement_level = "extremely_low"
        actual.context.activity_context = "completely_different"
        
        analysis = self.simulator.deviation_analysis(predicted, actual)
        
        # Sollte eine signifikante Abweichung erkennen
        self.assertGreater(analysis.deviation_score, 0.1)
        self.assertGreater(len(analysis.key_factors), 0)
    
    def test_no_differences(self):
        """Test: Keine Unterschiede zwischen Zuständen."""
        predicted = deepcopy(self.state)
        actual = deepcopy(self.state)
        
        analysis = self.simulator.deviation_analysis(predicted, actual)
        
        self.assertEqual(analysis.deviation_score, 0.0)
        self.assertEqual(len(analysis.key_factors), 0)


def run_tests():
    """Führt alle Tests aus."""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Füge alle Test-Klassen hinzu
    suite.addTests(loader.loadTestsFromTestCase(TestDoCalculus))
    suite.addTests(loader.loadTestsFromTestCase(TestCounterfactualSimulator))
    suite.addTests(loader.loadTestsFromTestCase(TestCounterfactualEngine))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegration))
    suite.addTests(loader.loadTestsFromTestCase(TestEdgeCases))
    
    # Führe Tests aus
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Zusammenfassung
    print("\n" + "=" * 70)
    print("Test-Zusammenfassung")
    print("=" * 70)
    print(f"Tests ausgeführt: {result.testsRun}")
    print(f"Erfolgreich: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Fehlgeschlagen: {len(result.failures)}")
    print(f"Fehler: {len(result.errors)}")
    print(f"Erfolgsrate: {(result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100:.1f}%")
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
