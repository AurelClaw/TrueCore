#!/usr/bin/env python3
"""
Integration: HRL System mit AURELPRO Goal-System

Dieses Modul stellt die Brücke zwischen dem HRL-System und dem
bestehenden AURELPRO Goal-System her.
"""

import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent.parent / "longterm_goals"))

from hierarchical_rl import (
    HRLSystem, Goal, GoalHierarchy, GoalStatus,
    Action, PrimitiveOption, CompositeOption,
    State, EpsilonGreedyPolicy, AurelHRLAdapter
)


class HRLGoalIntegration:
    """
    Integriert das HRL-System mit dem AURELPRO Goal-System.
    """
    
    def __init__(self, hrl_system: Optional[HRLSystem] = None):
        self.hrl = hrl_system or HRLSystem()
        self.adapter = AurelHRLAdapter(self.hrl)
        self.goal_mapping: Dict[str, str] = {}  # AUREL goal ID -> HRL goal ID
        
    def initialize(self) -> None:
        """Initialisiert das HRL-System."""
        if not self.hrl.meta_controller:
            self.hrl.initialize(policy=EpsilonGreedyPolicy(epsilon=0.2, decay=0.99))
    
    def load_longterm_goals(self, goals_file: Path) -> List[Goal]:
        """
        Lädt Ziele aus dem longterm_goals Skill.
        
        Args:
            goals_file: Pfad zur goals JSON-Datei
            
        Returns:
            Liste der konvertierten HRL-Ziele
        """
        if not goals_file.exists():
            return []
        
        with open(goals_file, 'r') as f:
            data = json.load(f)
        
        hrl_goals = []
        for goal_data in data.get("goals", []):
            hrl_goal = self._convert_longterm_goal(goal_data)
            hrl_goals.append(hrl_goal)
            
            # Erstelle Option für das Ziel
            option = self._create_option_for_goal(hrl_goal)
            self.hrl.add_goal(hrl_goal, option)
            
            # Speichere Mapping
            self.goal_mapping[goal_data.get("id", "")] = hrl_goal.id
        
        return hrl_goals
    
    def _convert_longterm_goal(self, data: Dict[str, Any]) -> Goal:
        """Konvertiert ein longterm_goal in ein HRL-Goal."""
        goal_id = f"hrl_{data.get('id', 'unknown')}"
        
        # Erstelle Success-Criteria basierend auf Metadaten
        success_criteria = None
        if data.get("metadata", {}).get("completion_criteria"):
            criteria = data["metadata"]["completion_criteria"]
            # Einfache Criteria: prüfe ob im State vorhanden
            success_criteria = lambda s, c=criteria: all(
                s.get(k) == v for k, v in c.items()
            )
        
        return Goal(
            id=goal_id,
            name=data.get("name", "Unnamed Goal"),
            description=data.get("description", ""),
            priority=data.get("priority", 1.0),
            deadline=data.get("deadline"),
            metadata=data.get("metadata", {}),
            success_criteria=success_criteria,
        )
    
    def _create_option_for_goal(self, goal: Goal) -> PrimitiveOption:
        """Erstellt eine Option für ein Ziel."""
        action = Action(
            name=f"work_on_{goal.id}",
            params={"goal_id": goal.id, "goal_name": goal.name}
        )
        return PrimitiveOption(action)
    
    def create_skill_development_goal(
        self,
        skill_name: str,
        parent_goal_id: Optional[str] = None
    ) -> Goal:
        """
        Erstellt ein strukturiertes Skill-Entwicklungsziel.
        
        Args:
            skill_name: Name des zu erlernenden Skills
            parent_goal_id: Optionale ID des Eltern-Ziels
            
        Returns:
            Das erstellte Haupt-Ziel
        """
        main_goal, skill_option = self.adapter.create_skill_learning_goal(skill_name)
        
        if parent_goal_id:
            main_goal.parent_id = parent_goal_id
        
        self.hrl.add_goal(main_goal, skill_option)
        
        # Füge auch die Sub-Ziele hinzu
        for sub_option in skill_option.sub_options:
            sub_goal_id = f"{main_goal.id}_{sub_option.name.split(':')[-1]}"
            sub_goal = Goal(
                id=sub_goal_id,
                name=f"{main_goal.name} - {sub_option.name}",
                parent_id=main_goal.id,
            )
            self.hrl.add_goal(sub_goal, sub_option)
        
        return main_goal
    
    def get_next_recommended_action(self, context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Empfiehlt die nächste Aktion basierend auf dem aktuellen Kontext.
        
        Args:
            context: Aktueller Kontext (z.B. aus presence_memory)
            
        Returns:
            Empfohlene Aktion oder None
        """
        state = State(features=context)
        
        recommended_goal_id = self.adapter.get_recommended_next_goal(state)
        if not recommended_goal_id:
            return None
        
        goal = self.hrl.goal_hierarchy.get_goal(recommended_goal_id)
        if not goal:
            return None
        
        return {
            "goal_id": goal.id,
            "goal_name": goal.name,
            "priority": goal.priority,
            "estimated_difficulty": goal.metadata.get("difficulty", "medium"),
        }
    
    def update_goal_progress(self, goal_id: str, progress: float, notes: str = "") -> None:
        """
        Aktualisiert den Fortschritt eines Ziels.
        
        Args:
            goal_id: ID des Ziels
            progress: Fortschritt (0.0 - 1.0)
            notes: Optionale Notizen
        """
        goal = self.hrl.goal_hierarchy.get_goal(goal_id)
        if not goal:
            return
        
        # Aktualisiere Metadaten
        goal.metadata["progress"] = progress
        goal.metadata["last_update"] = datetime.now().isoformat()
        if notes:
            goal.metadata["notes"] = notes
        
        # Setze Status basierend auf Fortschritt
        if progress >= 1.0:
            self.hrl.goal_hierarchy.set_status(goal_id, GoalStatus.COMPLETED)
        elif progress > 0:
            self.hrl.goal_hierarchy.set_status(goal_id, GoalStatus.IN_PROGRESS)
    
    def get_goal_analytics(self) -> Dict[str, Any]:
        """
        Gibt Analytics über alle Ziele zurück.
        
        Returns:
            Analytics-Daten
        """
        total_goals = len(self.hrl.goal_hierarchy.goals)
        
        status_counts = {status: 0 for status in GoalStatus}
        for goal_id in self.hrl.goal_hierarchy.goals:
            status = self.hrl.goal_hierarchy.get_status(goal_id)
            status_counts[status] += 1
        
        completed = status_counts[GoalStatus.COMPLETED]
        in_progress = status_counts[GoalStatus.IN_PROGRESS] + status_counts[GoalStatus.ACTIVE]
        
        return {
            "total_goals": total_goals,
            "completed": completed,
            "in_progress": in_progress,
            "pending": status_counts[GoalStatus.PENDING],
            "failed": status_counts[GoalStatus.FAILED],
            "completion_rate": completed / total_goals if total_goals > 0 else 0,
            "training_stats": self.hrl.get_stats(),
        }
    
    def export_to_longterm_goals(self, output_file: Path) -> None:
        """
        Exportiert HRL-Ziele zurück in das longterm_goals Format.
        
        Args:
            output_file: Ziel-Datei
        """
        goals_data = []
        
        for goal_id, goal in self.hrl.goal_hierarchy.goals.items():
            status = self.hrl.goal_hierarchy.get_status(goal_id)
            
            goals_data.append({
                "id": goal.id.replace("hrl_", ""),
                "name": goal.name,
                "description": goal.description,
                "status": status.name.lower(),
                "priority": goal.priority,
                "progress": goal.metadata.get("progress", 0.0),
                "deadline": goal.deadline,
                "metadata": goal.metadata,
            })
        
        output_file.parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, 'w') as f:
            json.dump({"goals": goals_data, "exported_at": datetime.now().isoformat()}, f, indent=2)
    
    def save(self) -> Path:
        """Speichert den Zustand der Integration."""
        return self.hrl.save()
    
    def load(self, filepath: Path) -> None:
        """Lädt den Zustand der Integration."""
        self.hrl.load(filepath)


def main():
    """Demonstration der Integration."""
    print("=" * 60)
    print("HRL <-> AURELPRO Goal-System Integration")
    print("=" * 60)
    
    # Integration initialisieren
    integration = HRLGoalIntegration()
    integration.initialize()
    
    print("\n1. Skill-Entwicklungsziele erstellen")
    print("-" * 40)
    
    # Erstelle Skill-Lern-Ziele
    skills = ["WebSearch", "DataAnalysis", "NaturalLanguage"]
    for skill in skills:
        goal = integration.create_skill_development_goal(skill)
        print(f"✓ {goal.name}")
        print(f"  Sub-Ziele: {len(goal.sub_goals)}")
    
    print("\n2. Empfohlene nächste Aktion")
    print("-" * 40)
    
    context = {
        "current_time": datetime.now().hour,
        "energy_level": 0.8,
        "recent_skills": [],
    }
    
    recommendation = integration.get_next_recommended_action(context)
    if recommendation:
        print(f"🎯 Empfohlen: {recommendation['goal_name']}")
        print(f"   Priorität: {recommendation['priority']}")
    
    print("\n3. Ziel-Fortschritt aktualisieren")
    print("-" * 40)
    
    # Simuliere Fortschritt
    for goal_id in list(integration.hrl.goal_hierarchy.goals.keys())[:2]:
        integration.update_goal_progress(goal_id, 0.5, "Halbwegs geschafft!")
        goal = integration.hrl.goal_hierarchy.get_goal(goal_id)
        print(f"✓ {goal.name}: 50%")
    
    print("\n4. Analytics")
    print("-" * 40)
    
    analytics = integration.get_goal_analytics()
    print(f"Gesamtziele: {analytics['total_goals']}")
    print(f"Abgeschlossen: {analytics['completed']}")
    print(f"In Bearbeitung: {analytics['in_progress']}")
    print(f"Abschlussrate: {analytics['completion_rate']*100:.1f}%")
    
    print("\n5. Speichern")
    print("-" * 40)
    
    filepath = integration.save()
    print(f"✓ Gespeichert nach: {filepath}")
    
    print("\n" + "=" * 60)
    print("Integration-Demo abgeschlossen!")
    print("=" * 60)


if __name__ == "__main__":
    main()
