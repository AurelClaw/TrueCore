#!/usr/bin/env python3
"""
World Model - State Representation Module

Einfache Zustandsrepräsentation für das World Model System.
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from pathlib import Path


@dataclass
class TimeState:
    """Zeitliche Dimension des Zustands."""
    timestamp: str
    time_of_day: str  # morning, afternoon, evening, night
    day_of_week: int  # 0-6
    week_of_year: int  # 1-52
    is_weekend: bool
    is_holiday: bool = False
    
    @classmethod
    def from_now(cls) -> 'TimeState':
        """Erstellt TimeState aus aktuellem Zeitpunkt."""
        now = datetime.now()
        hour = now.hour
        
        if 5 <= hour < 12:
            time_of_day = "morning"
        elif 12 <= hour < 17:
            time_of_day = "afternoon"
        elif 17 <= hour < 22:
            time_of_day = "evening"
        else:
            time_of_day = "night"
        
        return cls(
            timestamp=now.isoformat(),
            time_of_day=time_of_day,
            day_of_week=now.weekday(),
            week_of_year=now.isocalendar()[1],
            is_weekend=now.weekday() >= 5
        )


@dataclass
class ContextState:
    """Kontextuelle Dimension des Zustands."""
    location: str = "unknown"
    activity_context: str = "unknown"
    last_interaction_minutes_ago: Optional[int] = None
    recent_topics: List[str] = None
    open_goals: List[str] = None
    
    def __post_init__(self):
        if self.recent_topics is None:
            self.recent_topics = []
        if self.open_goals is None:
            self.open_goals = []


@dataclass
class SystemState:
    """System-Dimension des Zustands."""
    active_skills: List[str] = None
    running_processes: List[str] = None
    pending_notifications: int = 0
    system_load: float = 0.0
    recent_events: List[str] = None
    
    def __post_init__(self):
        if self.active_skills is None:
            self.active_skills = []
        if self.running_processes is None:
            self.running_processes = []
        if self.recent_events is None:
            self.recent_events = []


@dataclass
class HumanState:
    """Geschätzter Zustand des Menschen."""
    mood_estimate: str = "unknown"
    engagement_level: str = "unknown"
    preferred_communication: str = "unknown"
    recent_successes: List[str] = None
    recent_frustrations: List[str] = None
    
    def __post_init__(self):
        if self.recent_successes is None:
            self.recent_successes = []
        if self.recent_frustrations is None:
            self.recent_frustrations = []


@dataclass
class EnvironmentState:
    """Environment-Dimension des Zustands."""
    weather_condition: str = "unknown"
    temperature: Optional[float] = None
    humidity: Optional[float] = None
    calendar_load: str = "unknown"
    upcoming_events: List[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.upcoming_events is None:
            self.upcoming_events = []


@dataclass
class WorldState:
    """Vollständiger Weltzustand."""
    version: str = "1.0"
    time: TimeState = None
    context: ContextState = None
    system: SystemState = None
    human: HumanState = None
    environment: EnvironmentState = None
    
    def __post_init__(self):
        if self.time is None:
            self.time = TimeState.from_now()
        if self.context is None:
            self.context = ContextState()
        if self.system is None:
            self.system = SystemState()
        if self.human is None:
            self.human = HumanState()
        if self.environment is None:
            self.environment = EnvironmentState()
    
    def to_dict(self) -> Dict[str, Any]:
        """Konvertiert zu Dictionary."""
        return {
            "version": self.version,
            "time": asdict(self.time),
            "context": asdict(self.context),
            "system": asdict(self.system),
            "human": asdict(self.human),
            "environment": asdict(self.environment)
        }
    
    def to_json(self, indent: int = 2) -> str:
        """Konvertiert zu JSON-String."""
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'WorldState':
        """Erstellt WorldState aus Dictionary."""
        return cls(
            version=data.get("version", "1.0"),
            time=TimeState(**data.get("time", {})),
            context=ContextState(**data.get("context", {})),
            system=SystemState(**data.get("system", {})),
            human=HumanState(**data.get("human", {})),
            environment=EnvironmentState(**data.get("environment", {}))
        )
    
    @classmethod
    def from_json(cls, json_str: str) -> 'WorldState':
        """Erstellt WorldState aus JSON-String."""
        return cls.from_dict(json.loads(json_str))


class StateCollector:
    """Sammelt und speichert WorldState-Instanzen."""
    
    def __init__(self, storage_dir: str = None):
        if storage_dir is None:
            storage_dir = os.path.expanduser("~/.openclaw/workspace/skills/world_model/states")
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
    
    def collect(self) -> WorldState:
        """Sammelt aktuellen Zustand."""
        state = WorldState()
        
        # System-Daten sammeln
        state.system = self._collect_system_state()
        
        # Environment-Daten sammeln (falls verfügbar)
        state.environment = self._collect_environment_state()
        
        return state
    
    def _collect_system_state(self) -> SystemState:
        """Sammelt System-Informationen."""
        system = SystemState()
        
        # Aktive Skills ermitteln
        skills_dir = Path("~/.openclaw/workspace/skills").expanduser()
        if skills_dir.exists():
            system.active_skills = [
                d.name for d in skills_dir.iterdir() 
                if d.is_dir() and not d.name.startswith(".")
            ][:20]  # Limit auf 20
        
        # System Load (Linux)
        try:
            with open("/proc/loadavg", "r") as f:
                load = f.read().split()[0]
                system.system_load = float(load) / os.cpu_count()
        except:
            system.system_load = 0.0
        
        return system
    
    def _collect_environment_state(self) -> EnvironmentState:
        """Sammelt Environment-Informationen."""
        env = EnvironmentState()
        
        # Wetter-Daten (falls Wetter-Integration verfügbar)
        weather_file = Path("~/.openclaw/workspace/skills/wetter_integration/cache.json").expanduser()
        if weather_file.exists():
            try:
                with open(weather_file, "r") as f:
                    weather_data = json.load(f)
                    env.weather_condition = weather_data.get("condition", "unknown")
                    env.temperature = weather_data.get("temperature")
                    env.humidity = weather_data.get("humidity")
            except:
                pass
        
        return env
    
    def save(self, state: WorldState) -> str:
        """Speichert Zustand und gibt Pfad zurück."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"state_{timestamp}.json"
        filepath = self.storage_dir / filename
        
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(state.to_json())
        
        return str(filepath)
    
    def load_latest(self) -> Optional[WorldState]:
        """Lädt den neuesten gespeicherten Zustand."""
        state_files = sorted(self.storage_dir.glob("state_*.json"))
        if not state_files:
            return None
        
        with open(state_files[-1], "r", encoding="utf-8") as f:
            return WorldState.from_json(f.read())
    
    def list_states(self, limit: int = 10) -> List[str]:
        """Listet gespeicherte Zustände auf."""
        state_files = sorted(self.storage_dir.glob("state_*.json"), reverse=True)
        return [str(f.name) for f in state_files[:limit]]


def main():
    """CLI-Interface für State-Collection."""
    import argparse
    
    parser = argparse.ArgumentParser(description="World Model State Collector")
    parser.add_argument("--collect", action="store_true", help="Sammelt aktuellen Zustand")
    parser.add_argument("--show", action="store_true", help="Zeigt aktuellen Zustand")
    parser.add_argument("--list", action="store_true", help="Listet gespeicherte Zustände")
    
    args = parser.parse_args()
    
    collector = StateCollector()
    
    if args.collect:
        state = collector.collect()
        filepath = collector.save(state)
        print(f"Zustand gespeichert: {filepath}")
    
    elif args.show:
        state = collector.collect()
        print(state.to_json())
    
    elif args.list:
        states = collector.list_states()
        print("Gespeicherte Zustände:")
        for s in states:
            print(f"  - {s}")
    
    else:
        # Default: collect + show
        state = collector.collect()
        filepath = collector.save(state)
        print(f"Zustand gespeichert: {filepath}")
        print("\nZustand:")
        print(state.to_json())


if __name__ == "__main__":
    main()
