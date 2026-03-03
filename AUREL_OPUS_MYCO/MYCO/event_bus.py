#!/usr/bin/env python3
"""
event_bus.py - Zentrales Event-System für Aurel Opus Myco
Ersetzt alle Cron-Jobs durch Event-Driven Architektur
"""

import json
import time
import queue
import threading
from datetime import datetime
from typing import Dict, List, Callable, Any
from dataclasses import dataclass, asdict
from enum import Enum

class EventType(Enum):
    """Event-Typen im System"""
    USER_INPUT = "user_input"
    TIME_TRIGGER = "time_trigger"
    GOAL_COMPLETED = "goal_completed"
    BELIEF_UPDATED = "belief_updated"
    HYPHESIS_VALIDATED = "hypothesis_validated"
    SYSTEM_ALERT = "system_alert"
    PERCEPTION_READY = "perception_ready"
    EXECUTION_COMPLETE = "execution_complete"
    CHECKPOINT_CREATED = "checkpoint_created"

class Priority(Enum):
    """Event-Prioritäten"""
    CRITICAL = 0
    HIGH = 1
    NORMAL = 2
    LOW = 3
    BACKGROUND = 4

@dataclass
class Event:
    """Ein Event im System"""
    id: str
    type: EventType
    source: str
    payload: Dict[str, Any]
    priority: Priority
    timestamp: float
    correlation_id: str = None
    
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "type": self.type.value,
            "source": self.source,
            "payload": self.payload,
            "priority": self.priority.value,
            "timestamp": self.timestamp,
            "correlation_id": self.correlation_id
        }

class EventBus:
    """
    Zentrale Event-Bus für Aurel Opus Myco
    
    Features:
    - Prioritäts-Queue (nicht FIFO)
    - Async-Verarbeitung
    - Event-Routing
    - Provenance-Tracking
    """
    
    def __init__(self, state_path: str = "/root/.openclaw/workspace/AUREL_OPUS_MYCO"):
        self.state_path = state_path
        self.event_queue = queue.PriorityQueue()
        self.subscribers: Dict[EventType, List[Callable]] = {}
        self.running = False
        self.processed_count = 0
        self.event_log = []
        
        # Load state for context
        self._load_state()
        
    def _load_state(self):
        """Lade aktuellen State für Kontext"""
        try:
            with open(f"{self.state_path}/STATE/meta.json") as f:
                self.meta_state = json.load(f)
            with open(f"{self.state_path}/AGENCY/goals.json") as f:
                self.goals = json.load(f)
            print(f"✅ State loaded: {self.meta_state['meta']['name']} v{self.meta_state['meta']['version']}")
        except Exception as e:
            print(f"⚠️  Could not load state: {e}")
            self.meta_state = {}
            self.goals = {}
    
    def subscribe(self, event_type: EventType, handler: Callable):
        """Registriere Handler für Event-Typ"""
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []
        self.subscribers[event_type].append(handler)
        print(f"📎 Subscribed {handler.__name__} to {event_type.value}")
    
    def publish(self, event: Event) -> str:
        """
        Publiziere Event mit Token-Economy-Check
        
        Returns: event_id oder None (wenn rejected)
        """
        # Token-Economy: Prüfe ob Event Wert hat
        estimated_tokens = self._estimate_token_cost(event)
        estimated_value = self._estimate_value(event)
        
        score = estimated_value / max(estimated_tokens, 1)
        
        # Reject low-value events
        if score < 0.01 and event.priority != Priority.CRITICAL:
            print(f"⛔ Event rejected (score={score:.4f}): {event.type.value}")
            return None
        
        # Add to queue (priority, timestamp, event)
        self.event_queue.put((event.priority.value, event.timestamp, event))
        self.event_log.append(event.to_dict())
        
        print(f"📤 Published: {event.type.value} (priority={event.priority.name}, score={score:.2f})")
        return event.id
    
    def _estimate_token_cost(self, event: Event) -> int:
        """Schätze Token-Kosten für Event-Verarbeitung"""
        base_costs = {
            EventType.USER_INPUT: 100,
            EventType.TIME_TRIGGER: 50,
            EventType.GOAL_COMPLETED: 30,
            EventType.BELIEF_UPDATED: 20,
            EventType.HYPHESIS_VALIDATED: 200,
            EventType.SYSTEM_ALERT: 80,
            EventType.PERCEPTION_READY: 150,
            EventType.EXECUTION_COMPLETE: 40,
            EventType.CHECKPOINT_CREATED: 10
        }
        return base_costs.get(event.type, 100)
    
    def _estimate_value(self, event: Event) -> float:
        """Schätze Wert des Events"""
        # User Input hat immer hohen Wert
        if event.type == EventType.USER_INPUT:
            return 10.0
        
        # Critical Alerts haben hohen Wert
        if event.priority == Priority.CRITICAL:
            return 5.0
        
        # Goal completion hat Wert
        if event.type == EventType.GOAL_COMPLETED:
            return 3.0
        
        # Default basierend auf Payload
        payload_value = len(str(event.payload)) / 100
        return max(0.5, payload_value)
    
    def process_next(self) -> bool:
        """Verarbeite nächstes Event"""
        try:
            priority, timestamp, event = self.event_queue.get(timeout=1)
            
            print(f"\n🔔 Processing: {event.type.value} (from {event.source})")
            
            # Route zu Subscribers
            handlers = self.subscribers.get(event.type, [])
            for handler in handlers:
                try:
                    handler(event)
                except Exception as e:
                    print(f"❌ Handler error: {e}")
            
            self.processed_count += 1
            self.event_queue.task_done()
            return True
            
        except queue.Empty:
            return False
    
    def start(self):
        """Starte Event-Loop"""
        self.running = True
        print("\n🚀 Event Bus started")
        print("⏳ Waiting for events...")
        
        while self.running:
            self.process_next()
            time.sleep(0.1)  # 100ms polling (event-driven, not busy-wait)
    
    def stop(self):
        """Stoppe Event-Loop"""
        self.running = False
        print(f"\n🛑 Event Bus stopped")
        print(f"📊 Processed: {self.processed_count} events")
    
    def get_stats(self) -> dict:
        """System-Statistiken"""
        return {
            "queue_size": self.event_queue.qsize(),
            "processed": self.processed_count,
            "subscribers": {k.value: len(v) for k, v in self.subscribers.items()},
            "meta_mode": self.meta_state.get("meta", {}).get("mode", "UNKNOWN")
        }


# Beispiel-Handler
def handle_user_input(event: Event):
    """Handler für User Input"""
    print(f"  👤 User: {event.payload.get('message', 'N/A')}")
    # Route to Perception Layer
    print("  → Routing to Perception Layer")

def handle_goal_completed(event: Event):
    """Handler für Goal Completion"""
    goal_id = event.payload.get('goal_id')
    print(f"  🎯 Goal {goal_id} completed!")
    # Update State A
    print("  → Updating AGENCY/goals.json")

def handle_time_trigger(event: Event):
    """Handler für Zeit-Trigger"""
    trigger_type = event.payload.get('type')
    print(f"  ⏰ Time trigger: {trigger_type}")
    # Check for scheduled tasks
    print("  → Checking scheduled tasks")


if __name__ == "__main__":
    # Demo
    bus = EventBus()
    
    # Subscribe handlers
    bus.subscribe(EventType.USER_INPUT, handle_user_input)
    bus.subscribe(EventType.GOAL_COMPLETED, handle_goal_completed)
    bus.subscribe(EventType.TIME_TRIGGER, handle_time_trigger)
    
    # Publish some events
    print("\n📤 Publishing test events...")
    
    # High-value user input
    bus.publish(Event(
        id="evt-001",
        type=EventType.USER_INPUT,
        source="telegram",
        payload={"message": "Status ZIEL-007", "user": "witness"},
        priority=Priority.HIGH,
        timestamp=time.time()
    ))
    
    # Low-value background (might be rejected)
    bus.publish(Event(
        id="evt-002",
        type=EventType.TIME_TRIGGER,
        source="scheduler",
        payload={"type": "heartbeat"},
        priority=Priority.BACKGROUND,
        timestamp=time.time()
    ))
    
    # Critical alert
    bus.publish(Event(
        id="evt-003",
        type=EventType.SYSTEM_ALERT,
        source="monitor",
        payload={"alert": "token_budget_80_percent"},
        priority=Priority.CRITICAL,
        timestamp=time.time()
    ))
    
    # Process events
    print("\n" + "="*50)
    for _ in range(5):
        bus.process_next()
        time.sleep(0.5)
    
    # Stats
    print("\n" + "="*50)
    print("📊 Stats:", json.dumps(bus.get_stats(), indent=2))
    
    print("\n✅ Event Bus demo complete")
    print("⚛️ Noch.")
