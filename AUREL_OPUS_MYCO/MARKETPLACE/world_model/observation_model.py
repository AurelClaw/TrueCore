#!/usr/bin/env python3
"""
World Model - Observation Model

Verarbeitet Events und wandelt sie in State-Updates um.
Bietet Unsicherheits-Modellierung und Observation-Encoding.
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable, Union
from pathlib import Path
from dataclasses import dataclass, field, asdict
from enum import Enum
from collections import defaultdict
import re

# Importiere State-Module
from state import WorldState, TimeState, ContextState, SystemState, HumanState, EnvironmentState


class ObservationType(Enum):
    """Typen von Observations."""
    EVENT = "event"                    # System-Event
    SENSOR = "sensor"                  # Sensor-Daten (z.B. System-Load)
    FEEDBACK = "feedback"              # Feedback vom Menschen
    PREDICTION_ERROR = "prediction_error"  # Abweichung von Vorhersage
    MANUAL = "manual"                  # Manuelle Eingabe


@dataclass
class Observation:
    """
    Eine einzelne Observation.
    
    Repräsentiert eine Beobachtung aus der Umgebung,
    die für das World Model relevant ist.
    """
    timestamp: str
    obs_type: ObservationType
    source: str                        # z.B. "event_bus", "heartbeat", "user"
    payload: Dict[str, Any]            # Rohdaten
    confidence: float = 1.0            # Konfidenz der Observation (0-1)
    uncertainty_model: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Konvertiert zu Dictionary."""
        return {
            "timestamp": self.timestamp,
            "type": self.obs_type.value,
            "source": self.source,
            "payload": self.payload,
            "confidence": self.confidence,
            "uncertainty_model": self.uncertainty_model
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Observation':
        """Erstellt Observation aus Dictionary."""
        return cls(
            timestamp=data["timestamp"],
            obs_type=ObservationType(data.get("type", "event")),
            source=data["source"],
            payload=data["payload"],
            confidence=data.get("confidence", 1.0),
            uncertainty_model=data.get("uncertainty_model", {})
        )


@dataclass
class StateChange:
    """
    Repräsentiert eine Änderung im World State.
    """
    field_path: str                    # z.B. "system.pending_notifications"
    old_value: Any
    new_value: Any
    change_type: str                   # "increment", "set", "append", "remove"
    confidence: float = 1.0
    source_observation: Optional[str] = None  # Timestamp der Source-Observation
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "field_path": self.field_path,
            "old_value": self.old_value,
            "new_value": self.new_value,
            "change_type": self.change_type,
            "confidence": self.confidence,
            "source_observation": self.source_observation
        }


class EventEncoder:
    """
    Encodiert Events in Observations.
    
    Transformiert Roh-Events in strukturierte Observations
    mit Konfidenz- und Unsicherheits-Informationen.
    """
    
    # Mapping von Event-Typen zu Observation-Typen
    EVENT_TYPE_MAPPING = {
        "user:interacted": (ObservationType.EVENT, 0.95),
        "user:message": (ObservationType.EVENT, 0.95),
        "decision:made": (ObservationType.EVENT, 0.90),
        "goal:completed": (ObservationType.EVENT, 0.90),
        "goal:started": (ObservationType.EVENT, 0.90),
        "skill:executed": (ObservationType.EVENT, 0.85),
        "skill:error": (ObservationType.EVENT, 0.85),
        "system:alert": (ObservationType.EVENT, 0.80),
        "system:init": (ObservationType.EVENT, 0.80),
        "heartbeat": (ObservationType.SENSOR, 0.70),
        "prediction:failed": (ObservationType.PREDICTION_ERROR, 0.90),
    }
    
    def encode(self, event_data: Dict[str, Any]) -> Observation:
        """
        Wandelt ein Event in eine Observation um.
        
        Args:
            event_data: Roh-Event-Daten (z.B. aus event_bus)
        
        Returns:
            Observation mit Konfidenz und Unsicherheitsmodell
        """
        event_type = event_data.get("type", "unknown")
        
        # Bestimme Observation-Typ und Basiskonfidenz
        obs_type, base_confidence = self.EVENT_TYPE_MAPPING.get(
            event_type, (ObservationType.EVENT, 0.70)
        )
        
        # Berechne Unsicherheitsmodell
        uncertainty = self._calculate_uncertainty(event_data, base_confidence)
        
        return Observation(
            timestamp=event_data.get("timestamp", datetime.now().isoformat()),
            obs_type=obs_type,
            source=event_data.get("source", "unknown"),
            payload=event_data.get("payload", {}),
            confidence=uncertainty["effective_confidence"],
            uncertainty_model=uncertainty
        )
    
    def _calculate_uncertainty(self, event_data: Dict[str, Any], 
                               base_confidence: float) -> Dict[str, Any]:
        """
        Berechnet das Unsicherheitsmodell für eine Observation.
        
        Berücksichtigt:
        - Datenqualität (fehlende Felder)
        - Zeit seit Event
        - Source-Vertrauenswürdigkeit
        """
        uncertainty = {
            "base_confidence": base_confidence,
            "data_quality": 1.0,
            "source_reliability": 1.0,
            "temporal_decay": 1.0,
            "effective_confidence": base_confidence
        }
        
        # Datenqualität: Prüfe auf wichtige Felder
        payload = event_data.get("payload", {})
        if not payload:
            uncertainty["data_quality"] *= 0.8
        if not event_data.get("timestamp"):
            uncertainty["data_quality"] *= 0.7
        if not event_data.get("source"):
            uncertainty["data_quality"] *= 0.9
        
        # Source-Vertrauenswürdigkeit
        source = event_data.get("source", "unknown")
        source_reliability = {
            "user": 1.0,
            "morgen_gruss": 0.95,
            "proactive_decision": 0.90,
            "orchestrator": 0.90,
            "event_bus": 0.85,
            "heartbeat": 0.70,
            "unknown": 0.50
        }
        uncertainty["source_reliability"] = source_reliability.get(source, 0.70)
        
        # Temporale Abnahme (falls Event alt)
        try:
            event_time = datetime.fromisoformat(event_data.get("timestamp", ""))
            age_seconds = (datetime.now() - event_time).total_seconds()
            # Nach 1 Stunde: 10% Abnahme, nach 24h: 50% Abnahme
            decay = min(0.5, age_seconds / (24 * 3600) * 0.5)
            uncertainty["temporal_decay"] = 1.0 - decay
        except:
            uncertainty["temporal_decay"] = 0.9
        
        # Berechne effektive Konfidenz
        uncertainty["effective_confidence"] = (
            base_confidence *
            uncertainty["data_quality"] *
            uncertainty["source_reliability"] *
            uncertainty["temporal_decay"]
        )
        
        return uncertainty


class StateChangeMapper:
    """
    Mapped Observations zu State Changes.
    
    Definiert Regeln, wie verschiedene Observations
    den World State verändern.
    """
    
    def __init__(self):
        self.mappers: Dict[str, Callable[[Observation], List[StateChange]]] = {
            "user:interacted": self._map_user_interaction,
            "user:message": self._map_user_message,
            "decision:made": self._map_decision,
            "goal:completed": self._map_goal_completed,
            "goal:started": self._map_goal_started,
            "skill:executed": self._map_skill_executed,
            "skill:error": self._map_skill_error,
            "system:alert": self._map_system_alert,
            "heartbeat": self._map_heartbeat,
            "prediction:failed": self._map_prediction_error,
        }
    
    def map_observation(self, observation: Observation) -> List[StateChange]:
        """
        Mapped eine Observation zu State Changes.
        
        Args:
            observation: Die zu mappende Observation
        
        Returns:
            Liste von State Changes
        """
        # Extrahiere Event-Typ aus Payload
        event_type = observation.payload.get("event_type", "unknown")
        
        # Finde passenden Mapper
        mapper = self.mappers.get(event_type)
        if mapper:
            return mapper(observation)
        
        # Fallback: Generischer Mapper
        return self._map_generic(observation)
    
    def _map_user_interaction(self, obs: Observation) -> List[StateChange]:
        """Mapped User-Interaktionen zu State Changes."""
        changes = []
        payload = obs.payload
        
        # Update last_interaction
        changes.append(StateChange(
            field_path="context.last_interaction_minutes_ago",
            old_value=None,
            new_value=0,
            change_type="set",
            confidence=obs.confidence,
            source_observation=obs.timestamp
        ))
        
        # Update human engagement
        changes.append(StateChange(
            field_path="human.engagement_level",
            old_value=None,
            new_value="active",
            change_type="set",
            confidence=obs.confidence * 0.9,
            source_observation=obs.timestamp
        ))
        
        # Update recent_topics (falls im Payload)
        if "topic" in payload:
            changes.append(StateChange(
                field_path="context.recent_topics",
                old_value=None,
                new_value=payload["topic"],
                change_type="append",
                confidence=obs.confidence,
                source_observation=obs.timestamp
            ))
        
        return changes
    
    def _map_user_message(self, obs: Observation) -> List[StateChange]:
        """Mapped User-Nachrichten zu State Changes."""
        changes = []
        
        # Ähnlich wie user:interacted, aber mit höherer Konfidenz
        changes.append(StateChange(
            field_path="context.last_interaction_minutes_ago",
            old_value=None,
            new_value=0,
            change_type="set",
            confidence=obs.confidence,
            source_observation=obs.timestamp
        ))
        
        # Extrahiere Stimmung aus Nachricht (simplifiziert)
        payload = obs.payload
        message = payload.get("message", "")
        mood = self._extract_mood_from_message(message)
        
        if mood:
            changes.append(StateChange(
                field_path="human.mood_estimate",
                old_value=None,
                new_value=mood,
                change_type="set",
                confidence=obs.confidence * 0.7,  # Unsicher bei Stimmung
                source_observation=obs.timestamp
            ))
        
        return changes
    
    def _extract_mood_from_message(self, message: str) -> Optional[str]:
        """Extrahiert Stimmung aus Nachricht (simplifiziert)."""
        positive_words = ["danke", "gut", "super", "toll", "perfekt", "👍", "😊"]
        negative_words = ["problem", "fehler", "schlecht", "nicht", "😠", "😞"]
        
        message_lower = message.lower()
        pos_count = sum(1 for w in positive_words if w in message_lower)
        neg_count = sum(1 for w in negative_words if w in message_lower)
        
        if pos_count > neg_count:
            return "positive"
        elif neg_count > pos_count:
            return "negative"
        return None
    
    def _map_decision(self, obs: Observation) -> List[StateChange]:
        """Mapped Entscheidungen zu State Changes."""
        changes = []
        payload = obs.payload
        
        # Update context
        if "action" in payload:
            changes.append(StateChange(
                field_path="context.activity_context",
                old_value=None,
                new_value=f"decision:{payload['action']}",
                change_type="set",
                confidence=obs.confidence,
                source_observation=obs.timestamp
            ))
        
        return changes
    
    def _map_goal_completed(self, obs: Observation) -> List[StateChange]:
        """Mapped abgeschlossene Ziele zu State Changes."""
        changes = []
        payload = obs.payload
        
        # Entferne Ziel aus open_goals
        if "goal_id" in payload:
            changes.append(StateChange(
                field_path="context.open_goals",
                old_value=payload["goal_id"],
                new_value=None,
                change_type="remove",
                confidence=obs.confidence,
                source_observation=obs.timestamp
            ))
        
        # Füge zu recent_successes hinzu
        changes.append(StateChange(
            field_path="human.recent_successes",
            old_value=None,
            new_value=payload.get("goal_id", "unknown"),
            change_type="append",
            confidence=obs.confidence,
            source_observation=obs.timestamp
        ))
        
        return changes
    
    def _map_goal_started(self, obs: Observation) -> List[StateChange]:
        """Mapped gestartete Ziele zu State Changes."""
        changes = []
        payload = obs.payload
        
        # Füge zu open_goals hinzu
        if "goal_id" in payload:
            changes.append(StateChange(
                field_path="context.open_goals",
                old_value=None,
                new_value=payload["goal_id"],
                change_type="append",
                confidence=obs.confidence,
                source_observation=obs.timestamp
            ))
        
        return changes
    
    def _map_skill_executed(self, obs: Observation) -> List[StateChange]:
        """Mapped Skill-Ausführungen zu State Changes."""
        changes = []
        payload = obs.payload
        
        # Update recent_events
        skill_name = payload.get("skill", "unknown")
        changes.append(StateChange(
            field_path="system.recent_events",
            old_value=None,
            new_value=f"skill_executed:{skill_name}",
            change_type="append",
            confidence=obs.confidence,
            source_observation=obs.timestamp
        ))
        
        return changes
    
    def _map_skill_error(self, obs: Observation) -> List[StateChange]:
        """Mapped Skill-Fehler zu State Changes."""
        changes = []
        payload = obs.payload
        
        # Füge zu recent_frustrations hinzu
        skill_name = payload.get("skill", "unknown")
        changes.append(StateChange(
            field_path="human.recent_frustrations",
            old_value=None,
            new_value=f"skill_error:{skill_name}",
            change_type="append",
            confidence=obs.confidence,
            source_observation=obs.timestamp
        ))
        
        return changes
    
    def _map_system_alert(self, obs: Observation) -> List[StateChange]:
        """Mapped System-Alerts zu State Changes."""
        changes = []
        
        # Erhöhe pending_notifications
        changes.append(StateChange(
            field_path="system.pending_notifications",
            old_value=None,
            new_value=1,
            change_type="increment",
            confidence=obs.confidence,
            source_observation=obs.timestamp
        ))
        
        return changes
    
    def _map_heartbeat(self, obs: Observation) -> List[StateChange]:
        """Mapped Heartbeat-Events zu State Changes."""
        changes = []
        payload = obs.payload
        
        # Update system_load (falls im Payload)
        if "system_load" in payload:
            changes.append(StateChange(
                field_path="system.system_load",
                old_value=None,
                new_value=payload["system_load"],
                change_type="set",
                confidence=obs.confidence * 0.8,  # Heartbeat hat etwas Unsicherheit
                source_observation=obs.timestamp
            ))
        
        return changes
    
    def _map_prediction_error(self, obs: Observation) -> List[StateChange]:
        """Mapped Vorhersagefehler zu State Changes."""
        changes = []
        
        # Könnte interne Modelle anpassen (hier nur loggen)
        changes.append(StateChange(
            field_path="system.recent_events",
            old_value=None,
            new_value="prediction_error",
            change_type="append",
            confidence=obs.confidence,
            source_observation=obs.timestamp
        ))
        
        return changes
    
    def _map_generic(self, obs: Observation) -> List[StateChange]:
        """Generischer Fallback-Mapper."""
        return [StateChange(
            field_path="system.recent_events",
            old_value=None,
            new_value=f"generic:{obs.obs_type.value}",
            change_type="append",
            confidence=obs.confidence * 0.5,  # Niedrigere Konfidenz
            source_observation=obs.timestamp
        )]


class ObservationIntegrator:
    """
    Integriert State Changes in den World State.
    """
    
    def apply_changes(self, state: WorldState, 
                      changes: List[StateChange]) -> WorldState:
        """
        Wendet State Changes auf einen World State an.
        
        Args:
            state: Aktueller World State
            changes: Liste von State Changes
        
        Returns:
            Aktualisierter World State
        """
        # Erstelle Kopie des States
        new_state = WorldState.from_dict(state.to_dict())
        
        for change in changes:
            try:
                self._apply_single_change(new_state, change)
            except Exception as e:
                print(f"Fehler beim Anwenden von Change {change.field_path}: {e}")
        
        return new_state
    
    def _apply_single_change(self, state: WorldState, change: StateChange):
        """Wendet einen einzelnen State Change an."""
        path_parts = change.field_path.split(".")
        
        if len(path_parts) < 2:
            return
        
        section = path_parts[0]
        field = path_parts[1]
        
        # Hole das entsprechende Objekt
        target_obj = getattr(state, section, None)
        if target_obj is None:
            return
        
        # Wende Change an
        if change.change_type == "set":
            setattr(target_obj, field, change.new_value)
        
        elif change.change_type == "increment":
            current = getattr(target_obj, field, 0)
            if isinstance(current, (int, float)):
                setattr(target_obj, field, current + change.new_value)
        
        elif change.change_type == "append":
            current = getattr(target_obj, field, [])
            if isinstance(current, list):
                current.append(change.new_value)
                # Begrenze Liste auf 20 Elemente
                if len(current) > 20:
                    current = current[-20:]
                setattr(target_obj, field, current)
        
        elif change.change_type == "remove":
            current = getattr(target_obj, field, [])
            if isinstance(current, list) and change.old_value in current:
                current.remove(change.old_value)
                setattr(target_obj, field, current)


class ObservationModel:
    """
    Hauptklasse für das Observation Model.
    
    Koordiniert:
    - Event-Encoding zu Observations
    - Mapping zu State Changes
    - Integration in World State
    """
    
    def __init__(self, events_dir: str = None):
        if events_dir is None:
            events_dir = os.path.expanduser("~/.openclaw/workspace/skills/event_bus/events")
        self.events_dir = Path(events_dir)
        
        self.encoder = EventEncoder()
        self.mapper = StateChangeMapper()
        self.integrator = ObservationIntegrator()
        
        self.observation_history: List[Observation] = []
        self.change_history: List[StateChange] = []
    
    def process_event(self, event_data: Dict[str, Any]) -> List[StateChange]:
        """
        Verarbeitet ein einzelnes Event komplett.
        
        Args:
            event_data: Roh-Event-Daten
        
        Returns:
            Liste der resultierenden State Changes
        """
        # 1. Encode zu Observation
        observation = self.encoder.encode(event_data)
        self.observation_history.append(observation)
        
        # 2. Map zu State Changes
        changes = self.mapper.map_observation(observation)
        self.change_history.extend(changes)
        
        return changes
    
    def update_state(self, current_state: WorldState, 
                     event_data: Dict[str, Any]) -> WorldState:
        """
        Aktualisiert einen State basierend auf einem Event.
        
        Args:
            current_state: Aktueller World State
            event_data: Roh-Event-Daten
        
        Returns:
            Aktualisierter World State
        """
        changes = self.process_event(event_data)
        return self.integrator.apply_changes(current_state, changes)
    
    def process_recent_events(self, current_state: WorldState,
                              since_minutes: int = 30) -> WorldState:
        """
        Verarbeitet alle kürzlichen Events aus dem Event-Bus.
        
        Args:
            current_state: Aktueller World State
            since_minutes: Nur Events der letzten X Minuten
        
        Returns:
            Aktualisierter World State
        """
        if not self.events_dir.exists():
            return current_state
        
        cutoff_time = datetime.now() - timedelta(minutes=since_minutes)
        state = current_state
        
        # Lade alle Event-Dateien
        event_files = sorted(self.events_dir.glob("*.json"))
        
        for event_file in event_files:
            try:
                with open(event_file, "r", encoding="utf-8") as f:
                    event_data = json.load(f)
                
                # Prüfe Timestamp
                event_time_str = event_data.get("timestamp", "")
                try:
                    event_time = datetime.fromisoformat(event_time_str.replace(" ", "T"))
                    if event_time < cutoff_time:
                        continue
                except:
                    pass  # Verarbeite trotzdem
                
                # Verarbeite Event
                state = self.update_state(state, event_data)
                
            except Exception as e:
                print(f"Fehler beim Verarbeiten von {event_file}: {e}")
        
        return state
    
    def get_observation_stats(self) -> Dict[str, Any]:
        """Gibt Statistiken über verarbeitete Observations zurück."""
        if not self.observation_history:
            return {"error": "Keine Observations verarbeitet"}
        
        by_type = defaultdict(int)
        by_source = defaultdict(int)
        
        for obs in self.observation_history:
            by_type[obs.obs_type.value] += 1
            by_source[obs.source] += 1
        
        stats = {
            "total_observations": len(self.observation_history),
            "total_changes": len(self.change_history),
            "avg_confidence": sum(o.confidence for o in self.observation_history) / len(self.observation_history),
            "by_type": dict(by_type),
            "by_source": dict(by_source)
        }
        
        return stats
    
    def get_uncertainty_report(self) -> Dict[str, Any]:
        """Gibt einen Unsicherheitsbericht zurück."""
        if not self.observation_history:
            return {"error": "Keine Observations verfügbar"}
        
        recent_obs = self.observation_history[-10:]  # Letzte 10
        
        uncertainty_factors = {
            "data_quality_issues": 0,
            "temporal_decay_issues": 0,
            "source_reliability_issues": 0
        }
        
        for obs in recent_obs:
            um = obs.uncertainty_model
            if um.get("data_quality", 1.0) < 0.8:
                uncertainty_factors["data_quality_issues"] += 1
            if um.get("temporal_decay", 1.0) < 0.9:
                uncertainty_factors["temporal_decay_issues"] += 1
            if um.get("source_reliability", 1.0) < 0.8:
                uncertainty_factors["source_reliability_issues"] += 1
        
        report = {
            "recent_observations": len(recent_obs),
            "average_confidence": sum(o.confidence for o in recent_obs) / len(recent_obs),
            "low_confidence_count": sum(1 for o in recent_obs if o.confidence < 0.7),
            "uncertainty_factors": uncertainty_factors
        }
        
        return report


def main():
    """CLI-Interface für Observation Model."""
    import argparse
    
    parser = argparse.ArgumentParser(description="World Model Observation Model")
    parser.add_argument("--process-event", type=str, help="JSON-Event zu verarbeiten")
    parser.add_argument("--update-state", action="store_true", help="State mit Events aktualisieren")
    parser.add_argument("--stats", action="store_true", help="Zeige Statistiken")
    parser.add_argument("--uncertainty", action="store_true", help="Zeige Unsicherheitsbericht")
    
    args = parser.parse_args()
    
    model = ObservationModel()
    
    if args.process_event:
        event_data = json.loads(args.process_event)
        changes = model.process_event(event_data)
        print(f"Verarbeitet: {len(changes)} State Changes")
        for change in changes:
            print(f"  - {change.field_path}: {change.change_type}")
    
    elif args.update_state:
        from state import StateCollector
        collector = StateCollector()
        state = collector.collect()
        
        updated = model.process_recent_events(state, since_minutes=60)
        print(updated.to_json())
    
    elif args.stats:
        stats = model.get_observation_stats()
        print(json.dumps(stats, indent=2, ensure_ascii=False))
    
    elif args.uncertainty:
        report = model.get_uncertainty_report()
        print(json.dumps(report, indent=2, ensure_ascii=False))
    
    else:
        # Demo: Verarbeite ein Beispiel-Event
        demo_event = {
            "timestamp": datetime.now().isoformat(),
            "type": "user:interacted",
            "source": "test",
            "payload": {
                "event_type": "user:interacted",
                "topic": "test_topic"
            }
        }
        
        print("=== Demo Event ===")
        print(json.dumps(demo_event, indent=2))
        
        print("\n=== Observation ===")
        obs = model.encoder.encode(demo_event)
        print(json.dumps(obs.to_dict(), indent=2))
        
        print("\n=== State Changes ===")
        changes = model.mapper.map_observation(obs)
        for change in changes:
            print(json.dumps(change.to_dict(), indent=2))


if __name__ == "__main__":
    main()
