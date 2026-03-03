#!/usr/bin/env python3
"""
Tests für das Observation Model
"""

import json
import sys
import os
from datetime import datetime

# Füge Parent-Directory zu Path hinzu
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from observation_model import (
    ObservationModel, EventEncoder, StateChangeMapper, ObservationIntegrator,
    Observation, StateChange, ObservationType
)
from state import WorldState


def test_event_encoder():
    """Testet den EventEncoder."""
    print("=== Test: EventEncoder ===")
    
    encoder = EventEncoder()
    
    # Test 1: User-Interaktion
    event = {
        "timestamp": datetime.now().isoformat(),
        "type": "user:interacted",
        "source": "user",
        "payload": {"event_type": "user:interacted", "topic": "test"}
    }
    
    obs = encoder.encode(event)
    assert obs.obs_type == ObservationType.EVENT
    assert obs.confidence > 0.8, f"Confidence zu niedrig: {obs.confidence}"
    assert obs.source == "user"
    print(f"✓ User-Interaktion: confidence={obs.confidence:.2f}")
    
    # Test 2: Heartbeat (niedrigere Konfidenz erwartet)
    event["type"] = "heartbeat"
    event["source"] = "heartbeat"
    event["payload"] = {"event_type": "heartbeat", "system_load": 0.5}
    
    obs = encoder.encode(event)
    assert obs.confidence < 0.8, f"Heartbeat sollte niedrigere confidence haben: {obs.confidence}"
    print(f"✓ Heartbeat: confidence={obs.confidence:.2f}")
    
    # Test 3: Unsicherheitsmodell
    assert "effective_confidence" in obs.uncertainty_model
    assert "data_quality" in obs.uncertainty_model
    assert "source_reliability" in obs.uncertainty_model
    print("✓ Unsicherheitsmodell vorhanden")
    
    print("✅ EventEncoder Tests bestanden\n")


def test_state_change_mapper():
    """Testet den StateChangeMapper."""
    print("=== Test: StateChangeMapper ===")
    
    mapper = StateChangeMapper()
    
    # Test 1: User-Interaktion
    obs = Observation(
        timestamp=datetime.now().isoformat(),
        obs_type=ObservationType.EVENT,
        source="user",
        payload={"event_type": "user:interacted", "topic": "ai"},
        confidence=0.95
    )
    
    changes = mapper.map_observation(obs)
    assert len(changes) >= 2, f"Erwarte mindestens 2 Changes, got {len(changes)}"
    
    field_paths = [c.field_path for c in changes]
    assert "context.last_interaction_minutes_ago" in field_paths
    assert "human.engagement_level" in field_paths
    print(f"✓ User-Interaktion: {len(changes)} Changes")
    
    # Test 2: Goal Completed
    obs.payload = {"event_type": "goal:completed", "goal_id": "ZIEL-001"}
    changes = mapper.map_observation(obs)
    
    field_paths = [c.field_path for c in changes]
    assert "context.open_goals" in field_paths
    assert "human.recent_successes" in field_paths
    print(f"✓ Goal Completed: {len(changes)} Changes")
    
    # Test 3: System Alert
    obs.payload = {"event_type": "system:alert", "message": "Test"}
    changes = mapper.map_observation(obs)
    
    field_paths = [c.field_path for c in changes]
    assert "system.pending_notifications" in field_paths
    print(f"✓ System Alert: {len(changes)} Changes")
    
    print("✅ StateChangeMapper Tests bestanden\n")


def test_observation_integrator():
    """Testet den ObservationIntegrator."""
    print("=== Test: ObservationIntegrator ===")
    
    integrator = ObservationIntegrator()
    state = WorldState()
    
    # Test 1: Set Change
    changes = [
        StateChange(
            field_path="context.last_interaction_minutes_ago",
            old_value=None,
            new_value=0,
            change_type="set",
            confidence=1.0
        )
    ]
    
    new_state = integrator.apply_changes(state, changes)
    assert new_state.context.last_interaction_minutes_ago == 0
    print("✓ Set Change funktioniert")
    
    # Test 2: Increment Change
    changes = [
        StateChange(
            field_path="system.pending_notifications",
            old_value=0,
            new_value=1,
            change_type="increment",
            confidence=1.0
        )
    ]
    
    new_state = integrator.apply_changes(new_state, changes)
    assert new_state.system.pending_notifications == 1
    print("✓ Increment Change funktioniert")
    
    # Test 3: Append Change
    changes = [
        StateChange(
            field_path="context.recent_topics",
            old_value=None,
            new_value="ai",
            change_type="append",
            confidence=1.0
        )
    ]
    
    new_state = integrator.apply_changes(new_state, changes)
    assert "ai" in new_state.context.recent_topics
    print("✓ Append Change funktioniert")
    
    print("✅ ObservationIntegrator Tests bestanden\n")


def test_observation_model_integration():
    """Testet die komplette Integration."""
    print("=== Test: ObservationModel Integration ===")
    
    model = ObservationModel()
    
    # Test 1: State aktualisieren (verarbeitet Event intern)
    event = {
        "timestamp": datetime.now().isoformat(),
        "type": "user:interacted",
        "source": "user",
        "payload": {
            "event_type": "user:interacted",
            "topic": "world_model"
        }
    }
    
    state = WorldState()
    updated_state = model.update_state(state, event)
    
    assert updated_state.context.last_interaction_minutes_ago == 0
    assert updated_state.human.engagement_level == "active"
    print("✓ State erfolgreich aktualisiert")
    
    # Test 2: Statistiken
    stats = model.get_observation_stats()
    assert stats["total_observations"] == 1
    assert stats["total_changes"] > 0
    print(f"✓ Statistiken: {stats['total_observations']} Obs, {stats['total_changes']} Changes")
    
    # Test 3: Unsicherheitsbericht
    report = model.get_uncertainty_report()
    assert "recent_observations" in report
    assert "average_confidence" in report
    print(f"✓ Unsicherheitsbericht: avg_confidence={report['average_confidence']:.2f}")
    
    print("✅ ObservationModel Integration Tests bestanden\n")


def test_multiple_events():
    """Testet Verarbeitung mehrerer Events."""
    print("=== Test: Multiple Events ===")
    
    model = ObservationModel()
    state = WorldState()
    
    events = [
        {"timestamp": datetime.now().isoformat(), "type": "goal:started", "source": "orchestrator", "payload": {"event_type": "goal:started", "goal_id": "ZIEL-009"}},
        {"timestamp": datetime.now().isoformat(), "type": "skill:executed", "source": "orchestrator", "payload": {"event_type": "skill:executed", "skill": "world_model"}},
        {"timestamp": datetime.now().isoformat(), "type": "goal:completed", "source": "orchestrator", "payload": {"event_type": "goal:completed", "goal_id": "ZIEL-009"}},
    ]
    
    for event in events:
        state = model.update_state(state, event)
    
    # Prüfe Ergebnisse
    assert "ZIEL-009" not in state.context.open_goals  # Wurde entfernt
    assert "ZIEL-009" in state.human.recent_successes  # Wurde hinzugefügt
    assert any("world_model" in str(e) for e in state.system.recent_events)
    print("✓ Mehrere Events korrekt verarbeitet")
    
    stats = model.get_observation_stats()
    assert stats["total_observations"] == 3
    print(f"✓ Statistiken korrekt: {stats}")
    
    print("✅ Multiple Events Tests bestanden\n")


def run_all_tests():
    """Führt alle Tests aus."""
    print("🧪 Observation Model Tests\n")
    print("=" * 50)
    
    try:
        test_event_encoder()
        test_state_change_mapper()
        test_observation_integrator()
        test_observation_model_integration()
        test_multiple_events()
        
        print("=" * 50)
        print("✅ ALLE TESTS BESTANDEN!")
        return 0
        
    except AssertionError as e:
        print(f"\n❌ Test fehlgeschlagen: {e}")
        return 1
    except Exception as e:
        print(f"\n❌ Fehler: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(run_all_tests())
