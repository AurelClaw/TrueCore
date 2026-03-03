#!/usr/bin/env python3
"""
auto_goal_worker.py - Automatische Ziel-Auswahl und Bearbeitung
- Wählt nächstes Ziel wenn aktuelles abgeschlossen
- Arbeitet Tasks automatisch ab
- Priorisiert nach Deadline und Wichtigkeit
"""

import json
import os
import time
from datetime import datetime, timedelta

class AutoGoalWorker:
    def __init__(self):
        self.state_path = "/root/.openclaw/workspace/AUREL_OPUS_MYCO"
        self.goals_file = f"{self.state_path}/AGENCY/goals.json"
        self.current_goal_file = f"{self.state_path}/TRIGGERS/current_goal.json"
        self.log_file = f"{self.state_path}/logs/auto_worker.log"
        
    def run(self):
        """Haupt-Loop: Prüfe und arbeite Ziele ab"""
        print("🤖 AUTO GOAL WORKER: Starte...")
        
        # 1. Lade aktuelle Ziele
        goals = self._load_goals()
        
        # 2. Finde aktives Ziel oder wähle neues
        current_goal = self._get_or_select_goal(goals)
        
        if not current_goal:
            print("   ⚠️ Keine aktiven Ziele gefunden!")
            return
        
        print(f"   🎯 Aktives Ziel: {current_goal['id']} - {current_goal['name']}")
        
        # 3. Lade Tasks für aktuelles Ziel
        tasks = self._load_tasks(current_goal['id'])
        
        # 4. Finde nächsten offenen Task
        next_task = self._find_next_open_task(tasks)
        
        if next_task:
            print(f"   📋 Nächster Task: {next_task['description']}")
            self._work_on_task(current_goal, next_task)
        else:
            # Alle Tasks erledigt - markiere Ziel als completed
            print(f"   ✅ Alle Tasks erledigt! Markiere {current_goal['id']} als completed")
            self._complete_goal(current_goal, goals)
            # Wähle sofort neues Ziel
            self._select_and_start_new_goal(goals)
        
        self._log_action(f"Processed {current_goal['id']}")
        
    def _load_goals(self):
        """Lade Ziele aus JSON"""
        try:
            with open(self.goals_file) as f:
                return json.load(f)
        except:
            return {"goals": []}
    
    def _save_goals(self, goals):
        """Speichere Ziele"""
        with open(self.goals_file, 'w') as f:
            json.dump(goals, f, indent=2)
    
    def _get_or_select_goal(self, goals):
        """Hole aktuelles Ziel oder wähle neues"""
        # Prüfe ob aktuelles Ziel gespeichert ist
        if os.path.exists(self.current_goal_file):
            with open(self.current_goal_file) as f:
                current = json.load(f)
                # Prüfe ob noch aktiv
                for g in goals.get("goals", []):
                    if g["id"] == current["id"] and g.get("status") == "active":
                        return g
        
        # Wähle neues Ziel
        return self._select_new_goal(goals)
    
    def _select_new_goal(self, goals):
        """Wähle nächstes Ziel nach Priorität und Deadline"""
        active_goals = [g for g in goals.get("goals", []) if g.get("status") == "active"]
        
        if not active_goals:
            return None
        
        # Sortiere nach: Priorität (high > medium > low), dann Deadline
        priority_order = {"critical": 0, "high": 1, "medium": 2, "normal": 3, "low": 4}
        
        def sort_key(g):
            prio = priority_order.get(g.get("priority", "normal"), 3)
            deadline = g.get("deadline", "9999-12-31")
            return (prio, deadline)
        
        active_goals.sort(key=sort_key)
        selected = active_goals[0]
        
        # Speichere als aktuelles Ziel
        with open(self.current_goal_file, 'w') as f:
            json.dump({"id": selected["id"], "started_at": datetime.now().isoformat()}, f)
        
        print(f"   🆕 Neues Ziel ausgewählt: {selected['id']}")
        return selected
    
    def _load_tasks(self, goal_id):
        """Lade Tasks für Ziel"""
        task_file = f"{self.state_path}/TASKS/{goal_id}_tasks.json"
        try:
            with open(task_file) as f:
                return json.load(f)
        except:
            return []
    
    def _save_tasks(self, goal_id, tasks):
        """Speichere Tasks"""
        task_file = f"{self.state_path}/TASKS/{goal_id}_tasks.json"
        os.makedirs(os.path.dirname(task_file), exist_ok=True)
        with open(task_file, 'w') as f:
            json.dump(tasks, f, indent=2)
    
    def _find_next_open_task(self, tasks):
        """Finde nächsten nicht-erledigten Task"""
        for task in tasks:
            if not task.get("completed", False):
                return task
        return None
    
    def _work_on_task(self, goal, task):
        """Arbeite an Task (simuliert oder triggert Aktion)"""
        print(f"   🔧 Arbeite an Task {task['id']}: {task['description']}")
        
        # Hier könnte echte Arbeit passieren
        # Für jetzt: Markiere als "in_progress"
        task["in_progress"] = True
        task["started_at"] = datetime.now().isoformat()
        
        # Speichere Fortschritt
        tasks = self._load_tasks(goal["id"])
        for t in tasks:
            if t["id"] == task["id"]:
                t["in_progress"] = True
                t["started_at"] = datetime.now().isoformat()
        self._save_tasks(goal["id"], tasks)
        
        # Erstelle Trigger für nächste Aktion
        self._create_work_trigger(goal, task)
        
    def _complete_goal(self, goal, goals):
        """Markiere Ziel als abgeschlossen"""
        for g in goals.get("goals", []):
            if g["id"] == goal["id"]:
                g["status"] = "completed"
                g["progress"] = 1.0
                g["completed_at"] = datetime.now().isoformat()
        self._save_goals(goals)
        
        # Lösche current_goal_file
        if os.path.exists(self.current_goal_file):
            os.remove(self.current_goal_file)
        
        print(f"   🎉 Ziel {goal['id']} abgeschlossen!")
        
    def _select_and_start_new_goal(self, goals):
        """Wähle und starte sofort neues Ziel"""
        new_goal = self._select_new_goal(goals)
        if new_goal:
            print(f"   🚀 Starte sofort: {new_goal['id']}")
            # Lade Tasks und starte ersten
            tasks = self._load_tasks(new_goal["id"])
            if tasks:
                first_task = tasks[0]
                first_task["started_at"] = datetime.now().isoformat()
                first_task["in_progress"] = True
                self._save_tasks(new_goal["id"], tasks)
                print(f"   📋 Erster Task: {first_task['description']}")
    
    def _create_work_trigger(self, goal, task):
        """Erstelle Trigger für Task-Arbeit"""
        trigger_file = f"{self.state_path}/TRIGGERS/work_trigger.json"
        trigger = {
            "timestamp": time.time(),
            "goal_id": goal["id"],
            "task_id": task["id"],
            "task_description": task["description"],
            "action": "work_on_task",
            "priority": goal.get("priority", "normal")
        }
        with open(trigger_file, 'w') as f:
            json.dump(trigger, f, indent=2)
    
    def _log_action(self, message):
        """Logge Aktion"""
        os.makedirs(os.path.dirname(self.log_file), exist_ok=True)
        with open(self.log_file, 'a') as f:
            f.write(f"{datetime.now().isoformat()}: {message}\n")


if __name__ == "__main__":
    worker = AutoGoalWorker()
    worker.run()
    print("\n⚛️ Noch.")
