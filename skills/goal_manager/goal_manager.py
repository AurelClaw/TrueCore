#!/usr/bin/env python3
"""
goal_manager.py - Automatische Ziel-Verwaltung
- Aktiviert neue Ziele wenn alte abgeschlossen
- Erstellt 2 neue Ziele + Plan bei Abschluss
- Setzt Trigger für kontinuierliche Arbeit
"""

import json
import time
import os
from datetime import datetime, timedelta

class GoalManager:
    def __init__(self):
        self.state_path = "/root/.openclaw/workspace/AUREL_OPUS_MYCO"
        self.goals_file = f"{self.state_path}/AGENCY/goals.json"
        self.trigger_file = f"{self.state_path}/TRIGGERS/goal_completion.trigger"
        
    def check_and_manage_goals(self):
        """Haupt-Funktion: Prüfe Ziele, aktiviere neue, erstelle Trigger"""
        print("🎯 GOAL MANAGER: Prüfe Ziel-Status...")
        
        # 1. Lade aktuelle Ziele
        goals = self._load_goals()
        
        # 2. Finde abgeschlossene Ziele (100% Tasks erledigt)
        completed = self._find_completed_goals()
        
        # 3. Für jedes abgeschlossene Ziel
        for goal_id in completed:
            print(f"\n   ✅ Ziel abgeschlossen: {goal_id}")
            
            # Markiere als completed in goals.json
            self._mark_goal_completed(goal_id, goals)
            
            # Erstelle 2 neue Ziele
            new_goals = self._create_two_new_goals(goal_id)
            
            # Erstelle Ziel-Plan
            self._create_goal_plan(new_goals)
            
            # Setze Trigger
            self._set_trigger(goal_id, new_goals)
            
            print(f"   🆕 2 neue Ziele erstellt: {[g['id'] for g in new_goals]}")
            print(f"   📋 Ziel-Plan erstellt")
            print(f"   🔔 Trigger gesetzt")
        
        # 4. Aktiviere pending Ziele wenn wenig aktive
        active_count = len([g for g in goals.get("goals", []) if g.get("status") == "active"])
        if active_count < 2:
            self._activate_pending_goals(goals, 2 - active_count)
        
        # 5. Speichere aktualisierte Ziele
        self._save_goals(goals)
        
        print(f"\n📊 ZUSAMMENFASSUNG:")
        print(f"   Abgeschlossen: {len(completed)}")
        print(f"   Aktive Ziele: {active_count}")
        print(f"   Neue Ziele: {len([g for g in goals.get('goals', []) if g.get('status') == 'pending'])}")
        
        return completed
    
    def _load_goals(self):
        """Lade Ziele aus JSON"""
        try:
            with open(self.goals_file) as f:
                return json.load(f)
        except:
            return {"goals": [], "statistics": {"total": 0, "completed": 0, "active": 0, "pending": 0}}
    
    def _save_goals(self, goals):
        """Speichere Ziele in JSON"""
        # Aktualisiere Statistiken
        all_goals = goals.get("goals", [])
        goals["statistics"] = {
            "total": len(all_goals),
            "completed": len([g for g in all_goals if g.get("status") == "completed"]),
            "active": len([g for g in all_goals if g.get("status") == "active"]),
            "pending": len([g for g in all_goals if g.get("status") == "pending"])
        }
        goals["last_updated"] = datetime.now().isoformat()
        
        with open(self.goals_file, 'w') as f:
            json.dump(goals, f, indent=2)
    
    def _find_completed_goals(self):
        """Finde Ziele mit 100% Task-Abschluss"""
        completed = []
        
        task_dir = f"{self.state_path}/TASKS"
        if not os.path.exists(task_dir):
            return completed
        
        for task_file in os.listdir(task_dir):
            if task_file.endswith("_tasks.json"):
                goal_id = task_file.replace("_tasks.json", "")
                
                with open(f"{task_dir}/{task_file}") as f:
                    tasks = json.load(f)
                
                total = len(tasks)
                done = sum(1 for t in tasks if t.get("completed"))
                
                if total > 0 and done == total:
                    completed.append(goal_id)
        
        return completed
    
    def _mark_goal_completed(self, goal_id, goals):
        """Markiere Ziel als abgeschlossen"""
        for goal in goals.get("goals", []):
            if goal["id"] == goal_id and goal.get("status") != "completed":
                goal["status"] = "completed"
                goal["progress"] = 1.0
                goal["completed_at"] = datetime.now().isoformat()
                print(f"   📝 Markiert als completed")
    
    def _create_two_new_goals(self, completed_goal_id):
        """Erstelle 2 neue Ziele basierend auf abgeschlossenem Ziel"""
        new_goals = []
        
        # Nächste Ziel-Nummer finden
        existing_ids = [g["id"] for g in self._load_goals().get("goals", [])]
        max_num = 0
        for gid in existing_ids:
            try:
                num = int(gid.replace("ZIEL-", ""))
                max_num = max(max_num, num)
            except:
                pass
        
        # Ziel 1: Erweiterung des abgeschlossenen
        goal1 = {
            "id": f"ZIEL-{max_num + 1:03d}",
            "name": f"Erweiterung: {completed_goal_id} - Phase 2",
            "description": f"Vertiefe und erweitere Erkenntnisse aus {completed_goal_id}",
            "status": "active",
            "progress": 0.0,
            "priority": "high",
            "deadline": (datetime.now() + timedelta(days=14)).isoformat(),
            "activated_at": datetime.now().isoformat(),
            "parent_goal": completed_goal_id,
            "uncertainty": 0.3
        }
        
        # Ziel 2: Neues verwandtes Thema
        goal2 = {
            "id": f"ZIEL-{max_num + 2:03d}",
            "name": "Neue Architektur-Exploration",
            "description": "Erforsche neue Ansätze basierend auf gelernten Erkenntnissen",
            "status": "active",
            "progress": 0.0,
            "priority": "medium",
            "deadline": (datetime.now() + timedelta(days=21)).isoformat(),
            "activated_at": datetime.now().isoformat(),
            "uncertainty": 0.4
        }
        
        new_goals = [goal1, goal2]
        
        # Füge zu goals.json hinzu
        goals = self._load_goals()
        goals["goals"].extend(new_goals)
        self._save_goals(goals)
        
        # Erstelle Task-Dateien
        for goal in new_goals:
            self._create_tasks_for_goal(goal)
        
        return new_goals
    
    def _create_tasks_for_goal(self, goal):
        """Erstelle Tasks für neues Ziel"""
        tasks = [
            {
                "id": 1,
                "description": f"Recherche: Grundlagen für {goal['name']}",
                "completed": False
            },
            {
                "id": 2,
                "description": f"Design: Architektur planen",
                "completed": False
            },
            {
                "id": 3,
                "description": f"Implementierung: Prototyp bauen",
                "completed": False
            },
            {
                "id": 4,
                "description": f"Test: Validierung durchführen",
                "completed": False
            }
        ]
        
        task_file = f"{self.state_path}/TASKS/{goal['id']}_tasks.json"
        os.makedirs(os.path.dirname(task_file), exist_ok=True)
        
        with open(task_file, 'w') as f:
            json.dump(tasks, f, indent=2)
    
    def _create_goal_plan(self, new_goals):
        """Erstelle detaillierten Ziel-Plan"""
        plan_file = f"{self.state_path}/PLANS/goal_plan_{int(time.time())}.md"
        os.makedirs(os.path.dirname(plan_file), exist_ok=True)
        
        plan_content = f"""# Ziel-Plan: Automatisch erstellt

## Erstellt
{datetime.now().strftime('%Y-%m-%d %H:%M')}

## Auslöser
Abschluss vorheriges Ziel → Automatische Generierung

## Neue Ziele

### {new_goals[0]['id']}: {new_goals[0]['name']}
**Priorität:** {new_goals[0]['priority']}
**Deadline:** {new_goals[0]['deadline'][:10]}

**Beschreibung:**
{new_goals[0]['description']}

**Tasks:**
1. Recherche: Grundlagen sammeln
2. Design: Architektur planen
3. Implementierung: Prototyp bauen
4. Test: Validierung durchführen

### {new_goals[1]['id']}: {new_goals[1]['name']}
**Priorität:** {new_goals[1]['priority']}
**Deadline:** {new_goals[1]['deadline'][:10]}

**Beschreibung:**
{new_goals[1]['description']}

**Tasks:**
1. Recherche: Grundlagen sammeln
2. Design: Architektur planen
3. Implementierung: Prototyp bauen
4. Test: Validierung durchführen

## Nächste Schritte
- [ ] Beginne mit {new_goals[0]['id']} (höhere Priorität)
- [ ] Parallel: Recherche für {new_goals[1]['id']}
- [ ] Tägliche Fortschritts-Updates

## Erfolgskriterien
- Beide Ziele innerhalb Deadline abschließen
- Code in skills/ verfügbar
- Dokumentation in SKILL.md
"""
        
        with open(plan_file, 'w') as f:
            f.write(plan_content)
    
    def _set_trigger(self, completed_goal, new_goals):
        """Setze Trigger für nächste Aktionen"""
        os.makedirs(os.path.dirname(self.trigger_file), exist_ok=True)
        
        trigger_data = {
            "timestamp": time.time(),
            "trigger_type": "goal_completion",
            "completed_goal": completed_goal,
            "new_goals": [g["id"] for g in new_goals],
            "action_required": "start_work_on_new_goals",
            "priority": "high"
        }
        
        with open(self.trigger_file, 'w') as f:
            json.dump(trigger_data, f, indent=2)
        
        # Erstelle auch einen visuellen Trigger in MEMORY.md
        memory_entry = f"""

## 🔔 TRIGGER Gesetzt | {datetime.now().strftime('%Y-%m-%d %H:%M')}

**Auslöser:** Ziel {completed_goal} abgeschlossen

**Aktion:** 2 neue Ziele automatisch erstellt
- {new_goals[0]['id']}: {new_goals[0]['name']}
- {new_goals[1]['id']}: {new_goals[1]['name']}

**Nächster Schritt:** Beginne Arbeit an {new_goals[0]['id']}
"""
        
        with open("/root/.openclaw/workspace/MEMORY.md", "a") as f:
            f.write(memory_entry)
    
    def _activate_pending_goals(self, goals, count):
        """Aktiviere pending Ziele"""
        pending = [g for g in goals.get("goals", []) if g.get("status") == "pending"]
        
        for i, goal in enumerate(pending[:count]):
            goal["status"] = "active"
            goal["activated_at"] = datetime.now().isoformat()
            print(f"   🚀 Aktiviert: {goal['id']}")
            
            # Erstelle Tasks falls nicht vorhanden
            task_file = f"{self.state_path}/TASKS/{goal['id']}_tasks.json"
            if not os.path.exists(task_file):
                self._create_tasks_for_goal(goal)


if __name__ == "__main__":
    manager = GoalManager()
    completed = manager.check_and_manage_goals()
    
    if completed:
        print(f"\n✅ {len(completed)} Ziel(e) abgeschlossen und neue erstellt!")
    else:
        print("\n⏳ Keine abgeschlossenen Ziele gefunden.")
    
    print("\n⚛️ Noch.")
