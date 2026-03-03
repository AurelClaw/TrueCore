#!/usr/bin/env python3
"""
World Model - Transition Model

Vorhersage zukünftiger Zustände basierend auf historischen Übergängen.
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
from dataclasses import asdict
import numpy as np
from collections import defaultdict

from state import WorldState, TimeState, ContextState, SystemState, HumanState, EnvironmentState


class TransitionModel:
    """
    Modelliert Zustandsübergänge und macht Vorhersagen.
    
    Features:
    - Baseline-Vorhersage (naive: Zustand bleibt gleich)
    - Trend-Erkennung (lineare Regression auf numerische Werte)
    - Pattern-Matching (ähnliche Zustandsübergänge finden)
    """
    
    def __init__(self, states_dir: str = None):
        if states_dir is None:
            states_dir = os.path.expanduser("~/.openclaw/workspace/skills/world_model/states")
        self.states_dir = Path(states_dir)
        self.transitions: List[Tuple[WorldState, WorldState]] = []
        self._load_historical_states()
    
    def _load_historical_states(self):
        """Lädt alle gespeicherten States und baut Transition-Pairs auf."""
        state_files = sorted(self.states_dir.glob("state_*.json"))
        states = []
        
        for filepath in state_files:
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    state = WorldState.from_json(f.read())
                    states.append((filepath.name, state))
            except Exception as e:
                print(f"Fehler beim Laden von {filepath}: {e}")
        
        # Sortiere nach Timestamp
        states.sort(key=lambda x: x[1].time.timestamp)
        
        # Baue Transition-Pairs (State A -> State B)
        for i in range(len(states) - 1):
            self.transitions.append((states[i][1], states[i + 1][1]))
        
        print(f"TransitionModel: {len(states)} States geladen, {len(self.transitions)} Transitions")
    
    def predict_baseline(self, current_state: WorldState) -> WorldState:
        """
        Naive Baseline-Vorhersage: Der Zustand bleibt gleich,
        nur Zeit wird aktualisiert.
        """
        predicted = WorldState.from_dict(current_state.to_dict())
        
        # Aktualisiere Zeit um 1 Stunde
        current_time = datetime.fromisoformat(current_state.time.timestamp)
        future_time = current_time + timedelta(hours=1)
        
        predicted.time = TimeState(
            timestamp=future_time.isoformat(),
            time_of_day=self._get_time_of_day(future_time.hour),
            day_of_week=future_time.weekday(),
            week_of_year=future_time.isocalendar()[1],
            is_weekend=future_time.weekday() >= 5,
            is_holiday=current_state.time.is_holiday
        )
        
        return predicted
    
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
    
    def predict_with_trends(self, current_state: WorldState, 
                           steps_ahead: int = 1) -> WorldState:
        """
        Vorhersage mit Trend-Erkennung.
        
        Nutzt lineare Regression auf numerische Werte über alle verfügbaren
        historischen Transitions.
        """
        if len(self.transitions) < 2:
            # Nicht genug Daten für Trend-Analyse
            return self.predict_baseline(current_state)
        
        predicted = WorldState.from_dict(current_state.to_dict())
        
        # Sammle numerische Features aus Transitions
        features = self._extract_numeric_transitions()
        
        # Berechne Trends
        trends = {}
        for feature_name, values in features.items():
            if len(values) >= 2:
                trend = self._calculate_trend(values)
                trends[feature_name] = trend
        
        # Wende Trends auf aktuellen Zustand an
        current_dict = current_state.to_dict()
        
        # System Load Trend
        if "system_load" in trends:
            current_load = current_dict["system"]["system_load"]
            predicted_load = current_load + trends["system_load"] * steps_ahead
            predicted.system.system_load = max(0.0, min(1.0, predicted_load))
        
        # Temperature Trend
        if "temperature" in trends and current_dict["environment"]["temperature"]:
            current_temp = current_dict["environment"]["temperature"]
            if trends["temperature"]:
                predicted_temp = current_temp + trends["temperature"] * steps_ahead
                predicted.environment.temperature = predicted_temp
        
        # Aktualisiere Zeit
        current_time = datetime.fromisoformat(current_state.time.timestamp)
        future_time = current_time + timedelta(hours=steps_ahead)
        
        predicted.time = TimeState(
            timestamp=future_time.isoformat(),
            time_of_day=self._get_time_of_day(future_time.hour),
            day_of_week=future_time.weekday(),
            week_of_year=future_time.isocalendar()[1],
            is_weekend=future_time.weekday() >= 5,
            is_holiday=current_state.time.is_holiday
        )
        
        # Füge Vorhersage-Metadaten hinzu
        predicted.context.open_goals.append(f"predicted_{steps_ahead}h_ahead")
        
        return predicted
    
    def _extract_numeric_transitions(self) -> Dict[str, List[Tuple[int, float]]]:
        """
        Extrahiert numerische Features aus allen Transitions.
        
        Returns:
            Dict mit Feature-Namen -> Liste von (Index, Wert) Tupeln
        """
        features = defaultdict(list)
        
        for idx, (state_a, state_b) in enumerate(self.transitions):
            dict_a = state_a.to_dict()
            dict_b = state_b.to_dict()
            
            # System Load
            features["system_load"].append((idx, dict_b["system"]["system_load"] - 
                                                   dict_a["system"]["system_load"]))
            
            # Temperature
            temp_a = dict_a["environment"]["temperature"]
            temp_b = dict_b["environment"]["temperature"]
            if temp_a is not None and temp_b is not None:
                features["temperature"].append((idx, temp_b - temp_a))
            
            # Pending Notifications
            features["pending_notifications"].append((idx, 
                dict_b["system"]["pending_notifications"] - 
                dict_a["system"]["pending_notifications"]))
        
        return features
    
    def _calculate_trend(self, values: List[Tuple[int, float]]) -> float:
        """
        Berechnet linearen Trend (Steigung) aus Werten.
        
        Einfache lineare Regression: y = mx + b
        Returns: Steigung m
        """
        if len(values) < 2:
            return 0.0
        
        x = np.array([v[0] for v in values])
        y = np.array([v[1] for v in values])
        
        # Lineare Regression
        n = len(x)
        m = (n * np.sum(x * y) - np.sum(x) * np.sum(y)) / \
            (n * np.sum(x * x) - np.sum(x) ** 2)
        
        return float(m)
    
    def find_similar_transitions(self, current_state: WorldState, 
                                  top_k: int = 3) -> List[Tuple[WorldState, WorldState, float]]:
        """
        Findet ähnliche historische Zustandsübergänge.
        
        Ähnlichkeit basiert auf:
        - Gleiche Tageszeit
        - Ähnlicher System Load
        - Ähnliche Anzahl aktiver Skills
        
        Returns:
            Liste von (State A, State B, similarity_score) Tupeln
        """
        similarities = []
        current_dict = current_state.to_dict()
        
        for state_a, state_b in self.transitions:
            dict_a = state_a.to_dict()
            
            # Berechne Ähnlichkeit
            score = 0.0
            
            # Gleiche Tageszeit
            if dict_a["time"]["time_of_day"] == current_dict["time"]["time_of_day"]:
                score += 0.3
            
            # Gleicher Wochentag
            if dict_a["time"]["day_of_week"] == current_dict["time"]["day_of_week"]:
                score += 0.2
            
            # Ähnlicher System Load (innerhalb 0.1)
            load_diff = abs(dict_a["system"]["system_load"] - 
                          current_dict["system"]["system_load"])
            if load_diff < 0.1:
                score += 0.3 * (1 - load_diff * 10)
            
            # Ähnliche Anzahl Skills (innerhalb 5)
            skills_diff = abs(len(dict_a["system"]["active_skills"]) - 
                            len(current_dict["system"]["active_skills"]))
            if skills_diff < 5:
                score += 0.2 * (1 - skills_diff / 5)
            
            similarities.append((state_a, state_b, score))
        
        # Sortiere nach Ähnlichkeit (absteigend)
        similarities.sort(key=lambda x: x[2], reverse=True)
        
        return similarities[:top_k]
    
    def predict_with_patterns(self, current_state: WorldState,
                              steps_ahead: int = 1) -> WorldState:
        """
        Vorhersage basierend auf Pattern-Matching.
        
        Findet ähnliche historische Transitions und extrapoliert.
        """
        similar = self.find_similar_transitions(current_state, top_k=3)
        
        if not similar or similar[0][2] < 0.3:
            # Keine guten Patterns gefunden
            return self.predict_with_trends(current_state, steps_ahead)
        
        predicted = WorldState.from_dict(current_state.to_dict())
        
        # Aggregiere Änderungen aus ähnlichen Transitions
        system_load_changes = []
        notification_changes = []
        
        for state_a, state_b, score in similar:
            if score > 0.3:  # Nur gute Matches
                dict_a = state_a.to_dict()
                dict_b = state_b.to_dict()
                
                system_load_changes.append(
                    dict_b["system"]["system_load"] - dict_a["system"]["system_load"]
                )
                notification_changes.append(
                    dict_b["system"]["pending_notifications"] - 
                    dict_a["system"]["pending_notifications"]
                )
        
        # Wende durchschnittliche Änderungen an
        if system_load_changes:
            avg_load_change = sum(system_load_changes) / len(system_load_changes)
            current_load = current_state.system.system_load
            predicted.system.system_load = max(0.0, min(1.0, 
                current_load + avg_load_change * steps_ahead))
        
        if notification_changes:
            avg_notif_change = sum(notification_changes) / len(notification_changes)
            current_notif = current_state.system.pending_notifications
            predicted.system.pending_notifications = max(0, 
                int(current_notif + avg_notif_change * steps_ahead))
        
        # Aktualisiere Zeit
        current_time = datetime.fromisoformat(current_state.time.timestamp)
        future_time = current_time + timedelta(hours=steps_ahead)
        
        predicted.time = TimeState(
            timestamp=future_time.isoformat(),
            time_of_day=self._get_time_of_day(future_time.hour),
            day_of_week=future_time.weekday(),
            week_of_year=future_time.isocalendar()[1],
            is_weekend=future_time.weekday() >= 5,
            is_holiday=current_state.time.is_holiday
        )
        
        predicted.context.open_goals.append(f"pattern_predicted_{steps_ahead}h_ahead")
        
        return predicted
    
    def predict(self, current_state: WorldState, 
                method: str = "pattern",
                steps_ahead: int = 1) -> WorldState:
        """
        Haupt-Vorhersage-Funktion.
        
        Args:
            current_state: Aktueller Zustand
            method: "baseline", "trend", oder "pattern"
            steps_ahead: Wie viele Stunden in die Zukunft
        
        Returns:
            Vorhergesagter Zustand
        """
        if method == "baseline":
            return self.predict_baseline(current_state)
        elif method == "trend":
            return self.predict_with_trends(current_state, steps_ahead)
        elif method == "pattern":
            return self.predict_with_patterns(current_state, steps_ahead)
        else:
            raise ValueError(f"Unbekannte Methode: {method}")
    
    def get_transition_statistics(self) -> Dict[str, Any]:
        """
        Berechnet Statistiken über alle gespeicherten Transitions.
        """
        if not self.transitions:
            return {"error": "Keine Transitions verfügbar"}
        
        stats = {
            "total_transitions": len(self.transitions),
            "avg_system_load_change": 0.0,
            "avg_pending_notifications_change": 0.0,
            "time_distribution": defaultdict(int),
            "most_common_skills": defaultdict(int)
        }
        
        load_changes = []
        notif_changes = []
        
        for state_a, state_b in self.transitions:
            dict_a = state_a.to_dict()
            dict_b = state_b.to_dict()
            
            load_changes.append(dict_b["system"]["system_load"] - 
                              dict_a["system"]["system_load"])
            notif_changes.append(dict_b["system"]["pending_notifications"] - 
                               dict_a["system"]["pending_notifications"])
            
            # Zeit-Verteilung
            stats["time_distribution"][dict_a["time"]["time_of_day"]] += 1
            
            # Skills
            for skill in dict_a["system"]["active_skills"]:
                stats["most_common_skills"][skill] += 1
        
        if load_changes:
            stats["avg_system_load_change"] = sum(load_changes) / len(load_changes)
        if notif_changes:
            stats["avg_pending_notifications_change"] = sum(notif_changes) / len(notif_changes)
        
        # Konvertiere defaultdicts zu normalen dicts
        stats["time_distribution"] = dict(stats["time_distribution"])
        stats["most_common_skills"] = dict(stats["most_common_skills"])
        
        return stats


class PredictedStateStorage:
    """Speichert vorhergesagte Zustände."""
    
    def __init__(self, storage_dir: str = None):
        if storage_dir is None:
            storage_dir = os.path.expanduser("~/.openclaw/workspace/skills/world_model/states")
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
    
    def save_prediction(self, predicted_state: WorldState, 
                       method: str,
                       base_state_timestamp: str) -> str:
        """Speichert einen vorhergesagten Zustand."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"predicted_{method}_{timestamp}.json"
        filepath = self.storage_dir / filename
        
        data = {
            "metadata": {
                "prediction_method": method,
                "base_state_timestamp": base_state_timestamp,
                "prediction_timestamp": timestamp,
                "version": "1.0"
            },
            "state": predicted_state.to_dict()
        }
        
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        return str(filepath)
    
    def list_predictions(self) -> List[str]:
        """Listet alle gespeicherten Vorhersagen auf."""
        pred_files = sorted(self.storage_dir.glob("predicted_*.json"), reverse=True)
        return [str(f.name) for f in pred_files]


def main():
    """CLI-Interface für Transition Model."""
    import argparse
    
    parser = argparse.ArgumentParser(description="World Model Transition Model")
    parser.add_argument("--predict", action="store_true", help="Mache Vorhersage")
    parser.add_argument("--method", default="pattern", 
                       choices=["baseline", "trend", "pattern"],
                       help="Vorhersage-Methode")
    parser.add_argument("--steps", type=int, default=1,
                       help="Stunden in die Zukunft")
    parser.add_argument("--stats", action="store_true",
                       help="Zeige Transition-Statistiken")
    parser.add_argument("--load-latest", action="store_true",
                       help="Lade neuesten State als Basis")
    
    args = parser.parse_args()
    
    model = TransitionModel()
    storage = PredictedStateStorage()
    
    if args.stats:
        stats = model.get_transition_statistics()
        print(json.dumps(stats, indent=2, ensure_ascii=False))
    
    elif args.predict or args.load_latest:
        # Lade neuesten State
        from state import StateCollector
        collector = StateCollector()
        latest = collector.load_latest()
        
        if latest is None:
            print("Kein State gefunden!")
            return
        
        print(f"Basis-State: {latest.time.timestamp}")
        print(f"Methode: {args.method}, Steps: {args.steps}")
        
        # Mache Vorhersage
        predicted = model.predict(latest, method=args.method, steps_ahead=args.steps)
        
        print("\n--- Vorhergesagter Zustand ---")
        print(predicted.to_json())
        
        # Speichere Vorhersage
        filepath = storage.save_prediction(predicted, args.method, latest.time.timestamp)
        print(f"\nVorhersage gespeichert: {filepath}")
    
    else:
        # Default: Zeige Statistiken
        stats = model.get_transition_statistics()
        print(json.dumps(stats, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
