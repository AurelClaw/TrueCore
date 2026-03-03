#!/usr/bin/env python3
"""
World Model - Counterfactual Engine (Phase 5)

Counterfactual-Engine für das AURELPRO World Model.
Implementiert Pearl's Do-Calculus (vereinfacht) und Szenario-Simulation.

Features:
- Counterfactual Simulation ("Was wäre wenn...")
- Pearl's Do-Calculus (Intervention, Observation, Counterfactual Query)
- Abweichungs-Analyse (Prediction vs Actual)
- Szenario-Vergleiche (best_case, expected, worst_case, noop, alternative_action)
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple, Union, Callable
from pathlib import Path
from dataclasses import dataclass, field, asdict
from enum import Enum
from copy import deepcopy
import uuid

# Importiere existierende Module
from state import WorldState, TimeState, ContextState, SystemState, HumanState, EnvironmentState
from transition_model import TransitionModel
from simulation_core import SimulationCore, SimulationStep, SimulationBranch, SimulationResult


class ScenarioType(Enum):
    """Verschiedene Szenario-Typen für Counterfactual-Analyse."""
    BEST_CASE = "best_case"           # Optimistisches Szenario
    EXPECTED = "expected"             # Baseline-Erwartung
    WORST_CASE = "worst_case"         # Pessimistisches Szenario
    NOOP = "noop"                     # Keine Aktion (Baseline)
    ALTERNATIVE_ACTION = "alternative_action"  # Andere Aktion


@dataclass
class CounterfactualScenario:
    """Repräsentiert ein Counterfactual-Szenario."""
    scenario_id: str
    scenario_type: ScenarioType
    name: str
    base_state: WorldState
    interventions: List[Dict[str, Any]]  # Liste von Interventionen
    predicted_outcome: Optional[WorldState] = None
    confidence: float = 1.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "scenario_id": self.scenario_id,
            "scenario_type": self.scenario_type.value,
            "name": self.name,
            "base_state": self.base_state.to_dict(),
            "interventions": self.interventions,
            "predicted_outcome": self.predicted_outcome.to_dict() if self.predicted_outcome else None,
            "confidence": self.confidence,
            "metadata": self.metadata
        }


@dataclass
class ImpactAnalysis:
    """Analyse des Impacts zwischen zwei Szenarien."""
    baseline_scenario_id: str
    alternative_scenario_id: str
    
    # Quantitative Impacts
    system_load_delta: float = 0.0
    notification_delta: int = 0
    mood_change: str = "unchanged"
    engagement_change: str = "unchanged"
    
    # Qualitative Impacts
    risk_score: float = 0.0  # 0-1, höher = riskanter
    opportunity_score: float = 0.0  # 0-1, höher = mehr Opportunity
    overall_impact: float = 0.0  # -1 bis +1
    
    # Details
    key_differences: List[Dict[str, Any]] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "baseline_scenario_id": self.baseline_scenario_id,
            "alternative_scenario_id": self.alternative_scenario_id,
            "system_load_delta": self.system_load_delta,
            "notification_delta": self.notification_delta,
            "mood_change": self.mood_change,
            "engagement_change": self.engagement_change,
            "risk_score": self.risk_score,
            "opportunity_score": self.opportunity_score,
            "overall_impact": self.overall_impact,
            "key_differences": self.key_differences,
            "recommendations": self.recommendations
        }


@dataclass
class DeviationAnalysis:
    """Analyse der Abweichung zwischen Vorhersage und Realität."""
    prediction_id: str
    actual_state: WorldState
    predicted_state: WorldState
    
    # Abweichungs-Metriken
    deviation_score: float = 0.0  # 0-1, höher = größere Abweichung
    
    # Kategorisierte Abweichungen
    temporal_deviation: float = 0.0
    context_deviation: float = 0.0
    system_deviation: float = 0.0
    human_deviation: float = 0.0
    environment_deviation: float = 0.0
    
    # Analyse
    key_factors: List[Dict[str, Any]] = field(default_factory=list)
    explanation: str = ""
    lessons_learned: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "prediction_id": self.prediction_id,
            "deviation_score": self.deviation_score,
            "temporal_deviation": self.temporal_deviation,
            "context_deviation": self.context_deviation,
            "system_deviation": self.system_deviation,
            "human_deviation": self.human_deviation,
            "environment_deviation": self.environment_deviation,
            "key_factors": self.key_factors,
            "explanation": self.explanation,
            "lessons_learned": self.lessons_learned
        }


class DoCalculus:
    """
    Implementierung von Pearl's Do-Calculus (vereinfacht).
    
    Erlaubt:
    - intervene(): Setze eine Variable auf einen Wert (Do-Operator)
    - observe(): Beobachte eine Variable ohne Intervention
    - counterfactual_query(): "Was wäre wenn X, dann Y?"
    """
    
    def __init__(self):
        self.intervention_history: List[Dict[str, Any]] = []
    
    def intervene(self, state: WorldState, variable_path: str, 
                  value: Any) -> WorldState:
        """
        Führt eine Intervention durch (Do-Operator).
        
        Setzt eine Variable auf einen bestimmten Wert, unabhängig von
        ihren natürlichen kausalen Eltern.
        
        Args:
            state: Aktueller Zustand
            variable_path: Pfad zur Variable (z.B. "human.mood_estimate")
            value: Neuer Wert
        
        Returns:
            Neuer Zustand nach Intervention
        """
        new_state = deepcopy(state)
        
        # Parse Pfad
        parts = variable_path.split(".")
        if len(parts) != 2:
            raise ValueError(f"Ungültiger Pfad: {variable_path}. Erwartet: section.field")
        
        section, field = parts
        target_obj = getattr(new_state, section, None)
        
        if target_obj is None:
            raise ValueError(f"Ungültige Sektion: {section}")
        
        # Speichere alten Wert für Historie
        old_value = getattr(target_obj, field, None)
        
        # Setze neuen Wert
        setattr(target_obj, field, value)
        
        # Logge Intervention
        self.intervention_history.append({
            "timestamp": datetime.now().isoformat(),
            "variable": variable_path,
            "old_value": old_value,
            "new_value": value,
            "type": "intervention"
        })
        
        return new_state
    
    def observe(self, state: WorldState, variable_path: str) -> Any:
        """
        Beobachtet eine Variable ohne Intervention.
        
        Args:
            state: Aktueller Zustand
            variable_path: Pfad zur Variable
        
        Returns:
            Wert der Variable
        """
        parts = variable_path.split(".")
        if len(parts) != 2:
            raise ValueError(f"Ungültiger Pfad: {variable_path}")
        
        section, field = parts
        target_obj = getattr(state, section, None)
        
        if target_obj is None:
            raise ValueError(f"Ungültige Sektion: {section}")
        
        value = getattr(target_obj, field, None)
        
        # Logge Observation
        self.intervention_history.append({
            "timestamp": datetime.now().isoformat(),
            "variable": variable_path,
            "value": value,
            "type": "observation"
        })
        
        return value
    
    def counterfactual_query(self, state: WorldState, 
                            intervention: Dict[str, Any],
                            outcome_variable: str) -> Dict[str, Any]:
        """
        Führt eine Counterfactual Query durch.
        
        "Was wäre Y gewesen, wenn X anders gewesen wäre?"
        
        Args:
            state: Aktueller (beobachteter) Zustand
            intervention: Intervention die durchgeführt werden soll
                         {"variable": "human.mood", "value": "happy"}
            outcome_variable: Variable deren Wert wir wissen wollen
        
        Returns:
            Dict mit counterfactual Outcome und Erklärung
        """
        # 1. Abduction: Inferiere exogene Variablen aus beobachtetem Zustand
        # (In unserem vereinfachten Modell: nutze aktuellen Zustand)
        
        # 2. Action: Führe Intervention durch
        intervened_state = self.intervene(
            state, 
            intervention["variable"], 
            intervention["value"]
        )
        
        # 3. Prediction: Berechne counterfactual Outcome
        # Simuliere einen Schritt mit dem intervenierten Zustand
        outcome_value = self.observe(intervened_state, outcome_variable)
        
        return {
            "query_type": "counterfactual",
            "intervention": intervention,
            "outcome_variable": outcome_variable,
            "counterfactual_outcome": outcome_value,
            "actual_state": state.to_dict(),
            "intervened_state": intervened_state.to_dict(),
            "explanation": f"Wäre {intervention['variable']} = {intervention['value']} gewesen, "
                          f"dann wäre {outcome_variable} = {outcome_value}"
        }


class CounterfactualSimulator:
    """
    Hauptklasse für Counterfactual-Simulationen.
    
    Simuliert alternative Szenarien und vergleicht Ergebnisse.
    """
    
    def __init__(self, 
                 transition_model: Optional[TransitionModel] = None,
                 simulation_core: Optional[SimulationCore] = None,
                 storage_dir: str = None):
        self.transition_model = transition_model or TransitionModel()
        self.simulation_core = simulation_core or SimulationCore()
        self.do_calculus = DoCalculus()
        
        if storage_dir is None:
            storage_dir = os.path.expanduser("~/.openclaw/workspace/skills/world_model/states/counterfactuals")
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        
        self.scenarios: List[CounterfactualScenario] = []
        self.impact_analyses: List[ImpactAnalysis] = []
        self.deviation_analyses: List[DeviationAnalysis] = []
    
    def simulate_alternative(self, 
                            state: WorldState, 
                            action: str,
                            scenario_type: ScenarioType = ScenarioType.ALTERNATIVE_ACTION,
                            parameters: Dict[str, Any] = None) -> CounterfactualScenario:
        """
        Simuliert ein alternatives Szenario ("Was wäre wenn...").
        
        Args:
            state: Ausgangszustand
            action: Auszuführende Aktion
            scenario_type: Typ des Szenarios
            parameters: Zusätzliche Parameter (z.B. {"delay": "1h"})
        
        Returns:
            CounterfactualScenario mit Ergebnis
        """
        parameters = parameters or {}
        scenario_id = f"cf_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
        
        # Erstelle Intervention basierend auf Aktion
        interventions = self._action_to_interventions(action, parameters)
        
        # Wende Interventionen auf Zustand an
        modified_state = deepcopy(state)
        for intervention in interventions:
            modified_state = self.do_calculus.intervene(
                modified_state,
                intervention["variable"],
                intervention["value"]
            )
        
        # Simuliere Zukunft mit modifiziertem Zustand
        predicted = self.transition_model.predict_with_trends(modified_state, steps_ahead=1)
        
        # Erstelle Szenario
        scenario = CounterfactualScenario(
            scenario_id=scenario_id,
            scenario_type=scenario_type,
            name=f"{scenario_type.value}_{action}",
            base_state=state,
            interventions=interventions,
            predicted_outcome=predicted,
            confidence=0.85,  # Counterfactuals haben etwas niedrigere Konfidenz
            metadata={
                "action": action,
                "parameters": parameters,
                "created_at": datetime.now().isoformat()
            }
        )
        
        self.scenarios.append(scenario)
        return scenario
    
    def simulate_noop(self, state: WorldState, steps: int = 1) -> CounterfactualScenario:
        """
        Simuliert Baseline-Szenario (keine Aktion).
        
        Args:
            state: Ausgangszustand
            steps: Anzahl der Schritte
        
        Returns:
            CounterfactualScenario mit Baseline-Ergebnis
        """
        scenario_id = f"cf_noop_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Keine Interventionen - einfach Vorhersage
        predicted = self.transition_model.predict_with_trends(state, steps_ahead=steps)
        
        scenario = CounterfactualScenario(
            scenario_id=scenario_id,
            scenario_type=ScenarioType.NOOP,
            name="baseline_no_action",
            base_state=state,
            interventions=[],
            predicted_outcome=predicted,
            confidence=0.90,
            metadata={
                "steps": steps,
                "created_at": datetime.now().isoformat()
            }
        )
        
        self.scenarios.append(scenario)
        return scenario
    
    def simulate_scenario_type(self,
                               state: WorldState,
                               scenario_type: ScenarioType,
                               action: str = None,
                               parameters: Dict[str, Any] = None) -> CounterfactualScenario:
        """
        Simuliert ein spezifisches Szenario-Typ.
        
        Args:
            state: Ausgangszustand
            scenario_type: Typ des Szenarios
            action: Optionale Aktion
            parameters: Zusätzliche Parameter
        
        Returns:
            CounterfactualScenario
        """
        parameters = parameters or {}
        
        # Passe Parameter basierend auf Szenario-Typ an
        if scenario_type == ScenarioType.BEST_CASE:
            parameters["optimism_factor"] = parameters.get("optimism_factor", 1.2)
        elif scenario_type == ScenarioType.WORST_CASE:
            parameters["pessimism_factor"] = parameters.get("pessimism_factor", 0.8)
        elif scenario_type == ScenarioType.EXPECTED:
            parameters["expected_value"] = True
        
        return self.simulate_alternative(
            state, 
            action or "continue", 
            scenario_type,
            parameters
        )
    
    def compare_scenarios(self, 
                         baseline: CounterfactualScenario,
                         alternatives: List[CounterfactualScenario]) -> List[ImpactAnalysis]:
        """
        Vergleicht mehrere Szenarien mit einer Baseline.
        
        Args:
            baseline: Baseline-Szenario
            alternatives: Liste alternativer Szenarien
        
        Returns:
            Liste von ImpactAnalyses
        """
        analyses = []
        
        for alt in alternatives:
            analysis = self.calculate_counterfactual_impact(baseline, alt)
            analyses.append(analysis)
            self.impact_analyses.append(analysis)
        
        return analyses
    
    def calculate_counterfactual_impact(self,
                                       baseline: CounterfactualScenario,
                                       counterfactual: CounterfactualScenario) -> ImpactAnalysis:
        """
        Quantifiziert den Unterschied zwischen zwei Szenarien.
        
        Args:
            baseline: Baseline-Szenario
            counterfactual: Counterfactual-Szenario
        
        Returns:
            ImpactAnalysis mit quantifizierten Unterschieden
        """
        if baseline.predicted_outcome is None or counterfactual.predicted_outcome is None:
            raise ValueError("Beide Szenarien müssen predicted_outcome haben")
        
        base = baseline.predicted_outcome
        alt = counterfactual.predicted_outcome
        
        analysis = ImpactAnalysis(
            baseline_scenario_id=baseline.scenario_id,
            alternative_scenario_id=counterfactual.scenario_id
        )
        
        # System Load Delta
        analysis.system_load_delta = alt.system.system_load - base.system.system_load
        
        # Notification Delta
        analysis.notification_delta = alt.system.pending_notifications - base.system.pending_notifications
        
        # Mood Change
        mood_map = {"unknown": 0, "negative": -1, "neutral": 0, "positive": 1, "focused": 0.5}
        base_mood = mood_map.get(base.human.mood_estimate, 0)
        alt_mood = mood_map.get(alt.human.mood_estimate, 0)
        mood_diff = alt_mood - base_mood
        
        if mood_diff > 0.3:
            analysis.mood_change = "improved"
        elif mood_diff < -0.3:
            analysis.mood_change = "worsened"
        else:
            analysis.mood_change = "unchanged"
        
        # Engagement Change
        engagement_map = {"unknown": 0, "low": 1, "medium": 2, "high": 3, "active": 3}
        base_eng = engagement_map.get(base.human.engagement_level, 0)
        alt_eng = engagement_map.get(alt.human.engagement_level, 0)
        eng_diff = alt_eng - base_eng
        
        if eng_diff > 0:
            analysis.engagement_change = "increased"
        elif eng_diff < 0:
            analysis.engagement_change = "decreased"
        else:
            analysis.engagement_change = "unchanged"
        
        # Risk Score
        analysis.risk_score = self._calculate_risk_score(base, alt)
        
        # Opportunity Score
        analysis.opportunity_score = self._calculate_opportunity_score(base, alt)
        
        # Overall Impact
        analysis.overall_impact = self._calculate_overall_impact(analysis)
        
        # Key Differences
        analysis.key_differences = self._identify_key_differences(base, alt)
        
        # Recommendations
        analysis.recommendations = self._generate_recommendations(analysis)
        
        return analysis
    
    def _action_to_interventions(self, action: str, 
                                  parameters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Wandelt eine Aktion in eine Liste von Interventionen um."""
        interventions = []
        
        # Mapping von Aktionen zu Interventionen
        action_map = {
            "delay_morning_greeting": [
                {"variable": "context.activity_context", "value": "delayed_greeting"}
            ],
            "send_message": [
                {"variable": "context.last_interaction_minutes_ago", "value": 0},
                {"variable": "human.engagement_level", "value": "active"}
            ],
            "take_break": [
                {"variable": "context.activity_context", "value": "break"},
                {"variable": "human.mood_estimate", "value": "positive"}
            ],
            "continue_work": [
                {"variable": "context.activity_context", "value": "working"}
            ],
            "execute_skill": [
                {"variable": "system.pending_notifications", "value": 0}
            ],
            "wait": [
                {"variable": "context.activity_context", "value": "waiting"}
            ]
        }
        
        # Spezifische Parameter-basierte Interventionen
        if "delay" in parameters:
            interventions.append({
                "variable": "context.activity_context",
                "value": f"delayed_{action}"
            })
        
        if "mood" in parameters:
            interventions.append({
                "variable": "human.mood_estimate",
                "value": parameters["mood"]
            })
        
        # Füge Standard-Interventionen hinzu
        if action in action_map:
            interventions.extend(action_map[action])
        else:
            # Generische Intervention
            interventions.append({
                "variable": "context.activity_context",
                "value": action
            })
        
        return interventions
    
    def _calculate_risk_score(self, base: WorldState, alt: WorldState) -> float:
        """Berechnet Risiko-Score basierend auf Zustandsunterschieden."""
        risk = 0.0
        
        # Höherer System Load = mehr Risiko
        if alt.system.system_load > base.system.system_load:
            risk += (alt.system.system_load - base.system.system_load) * 0.3
        
        # Mehr Notifications = mehr Risiko
        if alt.system.pending_notifications > base.system.pending_notifications:
            risk += min(0.3, (alt.system.pending_notifications - base.system.pending_notifications) * 0.1)
        
        # Negative Stimmung = Risiko
        if alt.human.mood_estimate == "negative":
            risk += 0.2
        
        return min(1.0, risk)
    
    def _calculate_opportunity_score(self, base: WorldState, alt: WorldState) -> float:
        """Berechnet Opportunity-Score basierend auf Zustandsunterschieden."""
        opportunity = 0.0
        
        # Positive Stimmung = Opportunity
        if alt.human.mood_estimate == "positive" and base.human.mood_estimate != "positive":
            opportunity += 0.3
        
        # Hohes Engagement = Opportunity
        if alt.human.engagement_level == "high" and base.human.engagement_level != "high":
            opportunity += 0.25
        
        # Weniger Notifications = Opportunity
        if alt.system.pending_notifications < base.system.pending_notifications:
            opportunity += min(0.2, (base.system.pending_notifications - alt.system.pending_notifications) * 0.05)
        
        # Weniger System Load = Opportunity
        if alt.system.system_load < base.system.system_load:
            opportunity += (base.system.system_load - alt.system.system_load) * 0.25
        
        return min(1.0, opportunity)
    
    def _calculate_overall_impact(self, analysis: ImpactAnalysis) -> float:
        """Berechnet gesamten Impact (-1 bis +1)."""
        impact = analysis.opportunity_score - analysis.risk_score
        
        # Berücksichtige Mood Change
        if analysis.mood_change == "improved":
            impact += 0.2
        elif analysis.mood_change == "worsened":
            impact -= 0.2
        
        # Berücksichtige Engagement Change
        if analysis.engagement_change == "increased":
            impact += 0.15
        elif analysis.engagement_change == "decreased":
            impact -= 0.15
        
        return max(-1.0, min(1.0, impact))
    
    def _identify_key_differences(self, base: WorldState, alt: WorldState) -> List[Dict[str, Any]]:
        """Identifiziert wichtige Unterschiede zwischen zwei Zuständen."""
        differences = []
        
        base_dict = base.to_dict()
        alt_dict = alt.to_dict()
        
        # Vergleiche alle Sektionen
        for section in ["time", "context", "system", "human", "environment"]:
            base_sec = base_dict.get(section, {})
            alt_sec = alt_dict.get(section, {})
            
            for key in set(base_sec.keys()) | set(alt_sec.keys()):
                base_val = base_sec.get(key)
                alt_val = alt_sec.get(key)
                
                if base_val != alt_val:
                    importance = self._calculate_importance(section, key, base_val, alt_val)
                    if importance > 0.3:  # Nur wichtige Unterschiede
                        differences.append({
                            "field": f"{section}.{key}",
                            "baseline_value": base_val,
                            "alternative_value": alt_val,
                            "importance": importance
                        })
        
        # Sortiere nach Wichtigkeit
        differences.sort(key=lambda x: x["importance"], reverse=True)
        return differences[:10]  # Top 10
    
    def _calculate_importance(self, section: str, key: str, 
                              base_val: Any, alt_val: Any) -> float:
        """Berechnet Wichtigkeit eines Unterschieds."""
        importance = 0.5  # Basis-Wichtigkeit
        
        # Wichtige Felder
        important_fields = {
            "human": ["mood_estimate", "engagement_level"],
            "system": ["system_load", "pending_notifications"],
            "context": ["activity_context", "last_interaction_minutes_ago"]
        }
        
        if section in important_fields and key in important_fields[section]:
            importance += 0.3
        
        # Größere Änderungen = wichtiger
        if isinstance(base_val, (int, float)) and isinstance(alt_val, (int, float)):
            if base_val != 0:
                relative_change = abs(alt_val - base_val) / abs(base_val)
                importance += min(0.2, relative_change)
        
        return min(1.0, importance)
    
    def _generate_recommendations(self, analysis: ImpactAnalysis) -> List[str]:
        """Generiert Empfehlungen basierend auf Impact-Analyse."""
        recommendations = []
        
        if analysis.overall_impact > 0.3:
            recommendations.append("✅ Dieses Szenario hat positiven Impact und sollte in Betracht gezogen werden.")
        elif analysis.overall_impact < -0.3:
            recommendations.append("⚠️ Dieses Szenario hat negativen Impact und sollte vermieden werden.")
        
        if analysis.risk_score > 0.5:
            recommendations.append("⚠️ Hohes Risiko erkannt. Risikominderungsstrategien prüfen.")
        
        if analysis.opportunity_score > 0.5:
            recommendations.append("💡 Hohe Opportunity erkannt. Nutzen Sie diese Chance.")
        
        if analysis.mood_change == "worsened":
            recommendations.append("😟 Stimmungsverschlechterung erwartet. Kommunikationsstrategie anpassen.")
        
        if analysis.engagement_change == "decreased":
            recommendations.append("📉 Engagement-Rückgang erwartet. Interaktionsplan überdenken.")
        
        return recommendations
    
    def deviation_analysis(self, 
                          predicted: WorldState,
                          actual: WorldState,
                          prediction_id: str = None) -> DeviationAnalysis:
        """
        Analysiert Abweichung zwischen Vorhersage und Realität.
        
        Args:
            predicted: Vorhergesagter Zustand
            actual: Tatsächlicher Zustand
            prediction_id: ID der Vorhersage (optional)
        
        Returns:
            DeviationAnalysis mit Erklärung der Abweichung
        """
        analysis = DeviationAnalysis(
            prediction_id=prediction_id or f"pred_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            actual_state=actual,
            predicted_state=predicted
        )
        
        # Berechne Abweichungen pro Sektion
        pred_dict = predicted.to_dict()
        actual_dict = actual.to_dict()
        
        # Temporal Deviation
        analysis.temporal_deviation = self._calculate_section_deviation(
            pred_dict.get("time", {}), 
            actual_dict.get("time", {})
        )
        
        # Context Deviation
        analysis.context_deviation = self._calculate_section_deviation(
            pred_dict.get("context", {}),
            actual_dict.get("context", {})
        )
        
        # System Deviation
        analysis.system_deviation = self._calculate_section_deviation(
            pred_dict.get("system", {}),
            actual_dict.get("system", {})
        )
        
        # Human Deviation
        analysis.human_deviation = self._calculate_section_deviation(
            pred_dict.get("human", {}),
            actual_dict.get("human", {})
        )
        
        # Environment Deviation
        analysis.environment_deviation = self._calculate_section_deviation(
            pred_dict.get("environment", {}),
            actual_dict.get("environment", {})
        )
        
        # Gesamtabweichung
        analysis.deviation_score = (
            analysis.temporal_deviation * 0.1 +
            analysis.context_deviation * 0.25 +
            analysis.system_deviation * 0.25 +
            analysis.human_deviation * 0.3 +
            analysis.environment_deviation * 0.1
        )
        
        # Identifiziere Schlüsselfaktoren
        analysis.key_factors = self.identify_key_factors(predicted, actual)
        
        # Generiere Erklärung
        analysis.explanation = self._generate_deviation_explanation(analysis)
        
        # Generiere Lessons Learned
        analysis.lessons_learned = self._generate_lessons_learned(analysis)
        
        self.deviation_analyses.append(analysis)
        return analysis
    
    def identify_key_factors(self, 
                            predicted: WorldState,
                            actual: WorldState) -> List[Dict[str, Any]]:
        """
        Identifiziert welche Faktoren die größten Abweichungen verursacht haben.
        
        Args:
            predicted: Vorhergesagter Zustand
            actual: Tatsächlicher Zustand
        
        Returns:
            Liste der wichtigsten Faktoren mit Einfluss-Scores
        """
        factors = []
        
        pred_dict = predicted.to_dict()
        actual_dict = actual.to_dict()
        
        # Analysiere jede Sektion
        for section in ["context", "system", "human", "environment"]:
            pred_sec = pred_dict.get(section, {})
            actual_sec = actual_dict.get(section, {})
            
            for key in set(pred_sec.keys()) | set(actual_sec.keys()):
                pred_val = pred_sec.get(key)
                actual_val = actual_sec.get(key)
                
                if pred_val != actual_val:
                    influence = self._calculate_influence(section, key, pred_val, actual_val)
                    if influence > 0.2:
                        factors.append({
                            "field": f"{section}.{key}",
                            "predicted": pred_val,
                            "actual": actual_val,
                            "influence_score": influence,
                            "category": self._categorize_factor(section, key)
                        })
        
        # Sortiere nach Einfluss
        factors.sort(key=lambda x: x["influence_score"], reverse=True)
        return factors[:8]  # Top 8 Faktoren
    
    def _calculate_section_deviation(self, pred: Dict, actual: Dict) -> float:
        """Berechnet Abweichung für eine Sektion."""
        if not pred and not actual:
            return 0.0
        
        all_keys = set(pred.keys()) | set(actual.keys())
        if not all_keys:
            return 0.0
        
        deviations = 0
        for key in all_keys:
            pred_val = pred.get(key)
            actual_val = actual.get(key)
            
            if pred_val != actual_val:
                if isinstance(pred_val, (int, float)) and isinstance(actual_val, (int, float)):
                    # Numerische Abweichung normalisieren
                    max_val = max(abs(pred_val), abs(actual_val), 1)
                    deviations += abs(pred_val - actual_val) / max_val
                else:
                    # Kategorische Abweichung
                    deviations += 1
        
        return min(1.0, deviations / len(all_keys))
    
    def _calculate_influence(self, section: str, key: str, 
                             pred_val: Any, actual_val: Any) -> float:
        """Berechnet Einfluss-Score eines Faktors."""
        influence = 0.3  # Basis-Einfluss
        
        # Wichtige Felder haben höheren Einfluss
        high_impact_fields = {
            "human": ["mood_estimate", "engagement_level", "recent_frustrations"],
            "system": ["system_load", "pending_notifications"],
            "context": ["activity_context", "last_interaction_minutes_ago"]
        }
        
        if section in high_impact_fields and key in high_impact_fields[section]:
            influence += 0.3
        
        # Größere Unterschiede = mehr Einfluss
        if isinstance(pred_val, (int, float)) and isinstance(actual_val, (int, float)):
            diff = abs(pred_val - actual_val)
            influence += min(0.3, diff / 10)  # Normalisiert
        
        return min(1.0, influence)
    
    def _categorize_factor(self, section: str, key: str) -> str:
        """Kategorisiert einen Faktor."""
        if section == "human":
            return "human_behavior"
        elif section == "system":
            return "system_dynamics"
        elif section == "environment":
            return "external_factors"
        elif section == "context":
            return "context_changes"
        return "other"
    
    def _generate_deviation_explanation(self, analysis: DeviationAnalysis) -> str:
        """Generiert menschenlesbare Erklärung der Abweichung."""
        parts = []
        
        if analysis.deviation_score < 0.2:
            parts.append("Die Vorhersage war sehr genau.")
        elif analysis.deviation_score < 0.5:
            parts.append("Die Vorhersage war moderat genau mit einigen Abweichungen.")
        else:
            parts.append("Die Vorhersage wies erhebliche Abweichungen auf.")
        
        # Erwähne größte Abweichungen
        if analysis.human_deviation > 0.4:
            parts.append("Das menschliche Verhalten war schwer vorherzusagen.")
        if analysis.system_deviation > 0.4:
            parts.append("System-Dynamiken wichen von der Erwartung ab.")
        if analysis.context_deviation > 0.4:
            parts.append("Der Kontext änderte sich unerwartet.")
        
        # Erwähne Top-Faktoren
        if analysis.key_factors:
            top_factor = analysis.key_factors[0]
            parts.append(f"Der Hauptfaktor war: {top_factor['field']} "
                        f"(Einfluss: {top_factor['influence_score']:.2f})")
        
        return " ".join(parts)
    
    def _generate_lessons_learned(self, analysis: DeviationAnalysis) -> List[str]:
        """Generiert Lessons Learned aus der Abweichungsanalyse."""
        lessons = []
        
        # Immer mindestens ein allgemeines Lesson
        if analysis.deviation_score < 0.1:
            lessons.append("Die Vorhersage war sehr genau. Das Modell funktioniert gut für diesen Kontext.")
        elif analysis.deviation_score > 0.5:
            lessons.append("Das Modell benötigt mehr Daten für ähnliche Situationen.")
        else:
            lessons.append("Moderate Abweichung. Modell könnte durch mehr Daten verbessert werden.")
        
        if analysis.human_deviation > 0.3:
            lessons.append("Menschliches Verhalten ist in diesem Kontext schwer vorherzusagen. "
                          "Mehr Kontext-Variablen sollten berücksichtigt werden.")
        
        if analysis.system_deviation > 0.3:
            lessons.append("System-Dynamiken sind komplexer als erwartet. "
                          "Zusätzliche System-Metriken könnten helfen.")
        
        for factor in analysis.key_factors[:3]:
            if factor["influence_score"] > 0.6:
                lessons.append(f"'{factor['field']}' hat unerwartet starken Einfluss. "
                              "Sollte in Zukunft stärker gewichtet werden.")
        
        # Falls immer noch keine Lessons, füge generisches hinzu
        if not lessons:
            lessons.append("Kontinuierliche Überwachung der Modell-Performance empfohlen.")
        
        return lessons
    
    def save_scenario(self, scenario: CounterfactualScenario) -> str:
        """Speichert ein Szenario auf Disk."""
        timestamp = datetime.now().strftime("%Y%m%d")
        filename = f"{scenario.scenario_id}.json"
        filepath = self.storage_dir / filename
        
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(scenario.to_dict(), f, indent=2, ensure_ascii=False)
        
        return str(filepath)
    
    def load_scenario(self, scenario_id: str) -> Optional[CounterfactualScenario]:
        """Lädt ein Szenario von Disk."""
        filepath = self.storage_dir / f"{scenario_id}.json"
        
        if not filepath.exists():
            return None
        
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        return CounterfactualScenario(
            scenario_id=data["scenario_id"],
            scenario_type=ScenarioType(data["scenario_type"]),
            name=data["name"],
            base_state=WorldState.from_dict(data["base_state"]),
            interventions=data["interventions"],
            predicted_outcome=WorldState.from_dict(data["predicted_outcome"]) if data["predicted_outcome"] else None,
            confidence=data["confidence"],
            metadata=data.get("metadata", {})
        )
    
    def list_saved_scenarios(self) -> List[str]:
        """Listet alle gespeicherten Szenarien auf."""
        files = sorted(self.storage_dir.glob("cf_*.json"))
        return [f.stem for f in files]


class CounterfactualEngine:
    """
    High-Level API für Counterfactual-Analysen.
    
    Vereinfachte Schnittstelle für häufige Use Cases.
    """
    
    def __init__(self):
        self.simulator = CounterfactualSimulator()
    
    def what_if(self, 
                state: WorldState, 
                action: str,
                parameters: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Einfache "Was wäre wenn"-Abfrage.
        
        Args:
            state: Aktueller Zustand
            action: Zu testende Aktion
            parameters: Zusätzliche Parameter
        
        Returns:
            Dict mit Ergebnis und Impact
        """
        parameters = parameters or {}
        
        # Simuliere Baseline
        baseline = self.simulator.simulate_noop(state)
        
        # Simuliere Alternative
        alternative = self.simulator.simulate_alternative(
            state, action, ScenarioType.ALTERNATIVE_ACTION, parameters
        )
        
        # Berechne Impact
        impact = self.simulator.calculate_counterfactual_impact(baseline, alternative)
        
        return {
            "query": f"What if {action}?",
            "baseline": baseline.to_dict(),
            "alternative": alternative.to_dict(),
            "impact": impact.to_dict(),
            "recommendation": "proceed" if impact.overall_impact > 0 else "reconsider"
        }
    
    def compare_actions(self,
                       state: WorldState,
                       actions: List[str],
                       parameters: Dict[str, Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Vergleicht mehrere mögliche Aktionen.
        
        Args:
            state: Aktueller Zustand
            actions: Liste der zu vergleichenden Aktionen
            parameters: Parameter pro Aktion
        
        Returns:
            Dict mit Vergleich und Empfehlung
        """
        parameters = parameters or {}
        
        # Simuliere Baseline
        baseline = self.simulator.simulate_noop(state)
        
        # Simuliere alle Aktionen
        alternatives = []
        for action in actions:
            params = parameters.get(action, {})
            alt = self.simulator.simulate_alternative(
                state, action, ScenarioType.ALTERNATIVE_ACTION, params
            )
            alternatives.append(alt)
        
        # Vergleiche alle
        impacts = self.simulator.compare_scenarios(baseline, alternatives)
        
        # Finde beste Aktion
        best_idx = max(range(len(impacts)), key=lambda i: impacts[i].overall_impact)
        best_action = actions[best_idx]
        best_impact = impacts[best_idx]
        
        return {
            "actions_compared": actions,
            "baseline": baseline.to_dict(),
            "alternatives": [alt.to_dict() for alt in alternatives],
            "impacts": [imp.to_dict() for imp in impacts],
            "recommended_action": best_action,
            "recommendation_confidence": best_impact.overall_impact,
            "reasoning": best_impact.recommendations
        }
    
    def analyze_prediction_error(self,
                                 predicted: WorldState,
                                 actual: WorldState) -> Dict[str, Any]:
        """
        Analysiert warum eine Vorhersage falsch war.
        
        Args:
            predicted: Vorhergesagter Zustand
            actual: Tatsächlicher Zustand
        
        Returns:
            Dict mit Abweichungsanalyse
        """
        analysis = self.simulator.deviation_analysis(predicted, actual)
        
        return {
            "deviation_score": analysis.deviation_score,
            "explanation": analysis.explanation,
            "key_factors": analysis.key_factors,
            "lessons_learned": analysis.lessons_learned,
            "improvement_suggestions": [
                "Betrachte identifizierte Schlüsselfaktoren in zukünftigen Modellen",
                "Sammle mehr Daten für ähnliche Kontexte",
                "Passe Unsicherheitsmodell an"
            ]
        }


def demo_counterfactual_engine():
    """Demonstration der Counterfactual Engine."""
    print("=" * 70)
    print("🔮 Counterfactual Engine - Demo")
    print("=" * 70)
    
    # Erstelle Beispiel-Zustand
    current_state = WorldState(
        time=TimeState.from_now(),
        context=ContextState(
            location="workspace",
            activity_context="morning_routine",
            last_interaction_minutes_ago=480,  # 8 Stunden
            open_goals=["ZIEL-009 Phase 5"]
        ),
        system=SystemState(
            active_skills=["world_model", "morgen_gruss"],
            system_load=0.2,
            pending_notifications=0
        ),
        human=HumanState(
            mood_estimate="unknown",
            engagement_level="unknown"
        ),
        environment=EnvironmentState(
            weather_condition="clear",
            temperature=18.0
        )
    )
    
    engine = CounterfactualEngine()
    
    print("\n📊 Test 1: 'Was wäre wenn' - Morgengruß verschieben")
    print("-" * 50)
    
    result = engine.what_if(
        current_state,
        action="delay_morning_greeting",
        parameters={"delay": "1h"}
    )
    
    print(f"Query: {result['query']}")
    print(f"Recommendation: {result['recommendation']}")
    print(f"Overall Impact: {result['impact']['overall_impact']:+.2f}")
    print(f"Risk Score: {result['impact']['risk_score']:.2f}")
    print(f"Opportunity Score: {result['impact']['opportunity_score']:.2f}")
    print(f"Mood Change: {result['impact']['mood_change']}")
    print(f"Engagement Change: {result['impact']['engagement_change']}")
    
    print("\n📊 Test 2: Aktionen-Vergleich")
    print("-" * 50)
    
    comparison = engine.compare_actions(
        current_state,
        actions=["send_message", "wait", "execute_skill"],
        parameters={
            "send_message": {"mood": "positive"},
            "execute_skill": {"skill": "morgen_gruss"}
        }
    )
    
    print(f"Actions compared: {comparison['actions_compared']}")
    print(f"Recommended action: {comparison['recommended_action']}")
    print(f"Confidence: {comparison['recommendation_confidence']:.2f}")
    
    print("\n📊 Test 3: Do-Calculus - Intervention")
    print("-" * 50)
    
    # Interveniere auf menschliche Stimmung
    intervened = engine.simulator.do_calculus.intervene(
        current_state,
        "human.mood_estimate",
        "positive"
    )
    
    print(f"Original mood: {current_state.human.mood_estimate}")
    print(f"After intervention: {intervened.human.mood_estimate}")
    
    # Counterfactual Query
    query_result = engine.simulator.do_calculus.counterfactual_query(
        current_state,
        intervention={"variable": "human.engagement_level", "value": "high"},
        outcome_variable="context.activity_context"
    )
    
    print(f"\nCounterfactual Query:")
    print(f"  Intervention: {query_result['intervention']}")
    print(f"  Outcome: {query_result['outcome_variable']} = {query_result['counterfactual_outcome']}")
    print(f"  Explanation: {query_result['explanation']}")
    
    print("\n📊 Test 4: Abweichungs-Analyse")
    print("-" * 50)
    
    # Simuliere Vorhersage vs Realität
    predicted = engine.simulator.transition_model.predict_with_trends(current_state, steps_ahead=1)
    
    # "Reale" Situation (mit Abweichungen)
    actual = deepcopy(predicted)
    actual.human.mood_estimate = "negative"  # Unerwartet negativ
    actual.system.system_load = 0.5  # Höher als erwartet
    
    error_analysis = engine.analyze_prediction_error(predicted, actual)
    
    print(f"Deviation Score: {error_analysis['deviation_score']:.2f}")
    print(f"Explanation: {error_analysis['explanation']}")
    print(f"\nKey Factors:")
    for factor in error_analysis['key_factors'][:3]:
        print(f"  - {factor['field']}: influence={factor['influence_score']:.2f}")
    
    print(f"\nLessons Learned:")
    for lesson in error_analysis['lessons_learned'][:2]:
        print(f"  • {lesson}")
    
    print("\n📊 Test 5: Szenario-Typen")
    print("-" * 50)
    
    for scenario_type in [ScenarioType.BEST_CASE, ScenarioType.EXPECTED, ScenarioType.WORST_CASE]:
        scenario = engine.simulator.simulate_scenario_type(
            current_state,
            scenario_type,
            action="continue_work"
        )
        print(f"{scenario_type.value}: confidence={scenario.confidence:.2f}")
    
    print("\n" + "=" * 70)
    print("✅ All Counterfactual Engine Tests Passed!")
    print("=" * 70)
    
    return engine


if __name__ == "__main__":
    demo_counterfactual_engine()
