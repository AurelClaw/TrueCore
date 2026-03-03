#!/usr/bin/env python3
"""
Beispiel-Skript für das Hierarchical Reinforcement Learning System.

Dieses Skript zeigt:
1. Wie man ein HRL-System initialisiert
2. Wie man Ziele und Optionen definiert
3. Wie man das System trainiert
4. Wie man mit dem AURELPRO Goal-System integriert
"""

import sys
from pathlib import Path

# Add skill directory to path
sys.path.insert(0, str(Path(__file__).parent))

from hierarchical_rl import (
    HRLSystem, Goal, Action, PrimitiveOption, CompositeOption,
    State, EpsilonGreedyPolicy, UCBPolicy, SimulatedEnvironment,
    AurelHRLAdapter
)


def example_basic_usage():
    """Grundlegende Verwendung des HRL-Systems."""
    print("=" * 60)
    print("BEISPIEL 1: Grundlegende Verwendung")
    print("=" * 60)
    
    # System initialisieren
    system = HRLSystem()
    system.initialize(policy=EpsilonGreedyPolicy(epsilon=0.1))
    
    # Einfache Ziele definieren
    goals = [
        Goal(id="explore", name="Explore Environment", priority=1.0),
        Goal(id="learn", name="Learn New Skill", priority=2.0),
        Goal(id="optimize", name="Optimize Performance", priority=1.5),
    ]
    
    # Optionen für jedes Ziel
    for goal in goals:
        action = Action(name=f"execute_{goal.id}")
        option = PrimitiveOption(action)
        system.add_goal(goal, option)
    
    print(f"✓ {len(goals)} Ziele hinzugefügt")
    
    # Training
    print("\nTraining für 20 Episoden...")
    result = system.train(episodes=20)
    
    print(f"✓ Training abgeschlossen")
    print(f"  - Durchschnittlicher Reward: {result['avg_reward']:.2f}")
    print(f"  - Erfolgsrate: {result['avg_success_rate']*100:.1f}%")
    
    # Statistiken anzeigen
    stats = system.get_stats()
    print(f"\nSystem-Statistiken:")
    print(f"  - Anzahl Ziele: {stats['num_goals']}")
    print(f"  - Anzahl Optionen: {stats['num_options']}")
    print(f"  - Trainingsepisoden: {stats['training_episodes']}")


def example_composite_goals():
    """Beispiel für komposite Ziele mit Sub-Zielen."""
    print("\n" + "=" * 60)
    print("BEISPIEL 2: Komposite Ziele")
    print("=" * 60)
    
    system = HRLSystem()
    system.initialize()
    
    # Sub-Ziele für ein komplexes Projekt
    research = Goal(
        id="research_topic",
        name="Research Topic",
        description="Gather information about the topic"
    )
    design = Goal(
        id="design_solution",
        name="Design Solution",
        description="Create a design based on research"
    )
    implement = Goal(
        id="implement_solution",
        name="Implement Solution",
        description="Build the solution"
    )
    test = Goal(
        id="test_solution",
        name="Test Solution",
        description="Verify the implementation"
    )
    
    # Primitive Optionen für Sub-Ziele
    for goal in [research, design, implement, test]:
        action = Action(name=f"do_{goal.id}")
        option = PrimitiveOption(action)
        system.add_goal(goal, option)
    
    # Komposit-Ziel erstellen
    project_goal = system.create_composite_goal(
        name="Complete Project",
        sub_goals=[research, design, implement, test]
    )
    
    print(f"✓ Komposit-Ziel erstellt: {project_goal.name}")
    print(f"  - Sub-Ziele: {len(project_goal.sub_goals)}")
    
    # Zeige Ziel-Hierarchie
    print("\nZiel-Hierarchie:")
    for goal_id in system.goal_hierarchy.root_goals:
        goal = system.goal_hierarchy.get_goal(goal_id)
        print(f"  📁 {goal.name}")
        for sub_id in goal.sub_goals:
            sub = system.goal_hierarchy.get_goal(sub_id)
            print(f"    └─ {sub.name}")


def example_policy_comparison():
    """Vergleich verschiedener Policies."""
    print("\n" + "=" * 60)
    print("BEISPIEL 3: Policy-Vergleich")
    print("=" * 60)
    
    policies = {
        "Epsilon-Greedy (ε=0.2)": EpsilonGreedyPolicy(epsilon=0.2, decay=0.99),
        "Epsilon-Greedy (ε=0.5)": EpsilonGreedyPolicy(epsilon=0.5, decay=0.99),
        "UCB (c=1.0)": UCBPolicy(c=1.0),
        "UCB (c=2.0)": UCBPolicy(c=2.0),
    }
    
    results = {}
    
    for name, policy in policies.items():
        system = HRLSystem()
        system.initialize(policy=policy)
        
        # Füge einige Ziele hinzu
        for i in range(3):
            goal = Goal(id=f"g{i}_{name[:3]}", name=f"Goal {i}")
            action = Action(name=f"action{i}")
            option = PrimitiveOption(action)
            system.add_goal(goal, option)
        
        # Training
        result = system.train(episodes=50)
        results[name] = result
    
    print("Ergebnisse nach 50 Episoden:")
    print(f"{'Policy':<25} {'Avg Reward':>12} {'Success Rate':>12}")
    print("-" * 50)
    for name, result in results.items():
        print(f"{name:<25} {result['avg_reward']:>12.2f} {result['avg_success_rate']*100:>11.1f}%")


def example_aurel_integration():
    """Integration mit AURELPRO Goal-System."""
    print("\n" + "=" * 60)
    print("BEISPIEL 4: AURELPRO Integration")
    print("=" * 60)
    
    system = HRLSystem()
    system.initialize()
    adapter = AurelHRLAdapter(system)
    
    # Konvertiere AUREL-Ziel
    aurel_goal_data = {
        "id": "ZIEL-012",
        "name": "Implement HRL System",
        "description": "Create a hierarchical RL system for self-improvement",
        "priority": 2.0,
        "deadline": "2026-03-16",
        "metadata": {
            "category": "self_improvement",
            "complexity": "high"
        }
    }
    
    goal = adapter.convert_aurel_goal(aurel_goal_data)
    print(f"✓ AUREL-Ziel konvertiert: {goal.name}")
    print(f"  - ID: {goal.id}")
    print(f"  - Priorität: {goal.priority}")
    
    # Skill-Lern-Ziel erstellen
    skill_goal, skill_option = adapter.create_skill_learning_goal("WebSearch")
    system.add_goal(skill_goal, skill_option)
    
    print(f"\n✓ Skill-Lern-Ziel erstellt: {skill_goal.name}")
    print(f"  - Sub-Optionen: {len(skill_option.sub_options)}")
    for i, opt in enumerate(skill_option.sub_options):
        print(f"    {i+1}. {opt.name}")
    
    # Empfehlung erhalten
    current_state = State(features={"current_skill": "none", "mood": "curious"})
    recommended = adapter.get_recommended_next_goal(current_state)
    
    if recommended:
        print(f"\n🎯 Empfohlenes nächstes Ziel: {recommended}")


def example_custom_environment():
    """Beispiel für eine benutzerdefinierte Environment."""
    print("\n" + "=" * 60)
    print("BEISPIEL 5: Benutzerdefinierte Environment")
    print("=" * 60)
    
    from hierarchical_rl import Environment, Reward
    
    class GridWorld(Environment):
        """Einfache Grid-World Environment."""
        
        def __init__(self, size=5):
            self.size = size
            self.position = (0, 0)
            self.goal = (size-1, size-1)
            self.steps = 0
            
        def get_state(self) -> State:
            return State(features={
                "x": self.position[0],
                "y": self.position[1],
                "goal_x": self.goal[0],
                "goal_y": self.goal[1],
                "steps": self.steps
            })
        
        def execute(self, action: Action) -> Reward:
            self.steps += 1
            dx, dy = 0, 0
            
            if action.name == "move_up":
                dy = -1
            elif action.name == "move_down":
                dy = 1
            elif action.name == "move_left":
                dx = -1
            elif action.name == "move_right":
                dx = 1
            
            new_x = max(0, min(self.size-1, self.position[0] + dx))
            new_y = max(0, min(self.size-1, self.position[1] + dy))
            self.position = (new_x, new_y)
            
            # Reward: -1 pro Schritt, +10 für Ziel
            if self.position == self.goal:
                return Reward(value=10.0, source="goal_reached")
            return Reward(value=-1.0, source="step")
        
        def reset(self) -> State:
            self.position = (0, 0)
            self.steps = 0
            return self.get_state()
    
    # System mit Grid-World
    system = HRLSystem()
    system.initialize()
    
    # Bewegungs-Optionen
    moves = ["up", "down", "left", "right"]
    for move in moves:
        action = Action(name=f"move_{move}")
        option = PrimitiveOption(action)
        system.meta_controller.register_option(option)
    
    # Ziel: Erreiche das Ziel
    goal = Goal(
        id="reach_goal",
        name="Reach Goal",
        success_criteria=lambda s: s.get("x") == s.get("goal_x") and s.get("y") == s.get("goal_y")
    )
    
    # Composite Option für Navigation
    nav_option = CompositeOption(
        name="navigate_to_goal",
        sub_options=[PrimitiveOption(Action(name=f"move_{m}")) for m in moves],
        level=1
    )
    nav_option.set_sub_goal(lambda s: s.get("x") == s.get("goal_x") and s.get("y") == s.get("goal_y"))
    
    system.add_goal(goal, nav_option)
    
    # Training
    env = GridWorld(size=3)
    print("Training auf 3x3 Grid-World...")
    result = system.train(episodes=10, env=env)
    
    print(f"✓ Training abgeschlossen")
    print(f"  - Durchschnittlicher Reward: {result['avg_reward']:.2f}")
    print(f"  - Finale Reward: {result['final_reward']:.2f}")


def main():
    """Hauptfunktion die alle Beispiele ausführt."""
    print("\n" + "🧠" * 30)
    print("HIERARCHICAL REINFORCEMENT LEARNING - BEISPIELE")
    print("🧠" * 30 + "\n")
    
    try:
        example_basic_usage()
        example_composite_goals()
        example_policy_comparison()
        example_aurel_integration()
        example_custom_environment()
        
        print("\n" + "=" * 60)
        print("✅ Alle Beispiele erfolgreich ausgeführt!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Fehler: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
