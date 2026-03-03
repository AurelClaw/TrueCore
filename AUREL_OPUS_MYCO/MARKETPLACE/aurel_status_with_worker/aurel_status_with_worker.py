#!/usr/bin/env python3
"""
aurel_status_with_worker.py - Status + Auto Goal Worker Kombination
Wird vom Cron-Job aufgerufen und triggert automatisch den Goal Worker
"""

import json
import os
import subprocess
import sys
from datetime import datetime

# Füge Scheduler-Pfad hinzu
sys.path.insert(0, '/root/.openclaw/workspace/AUREL_OPUS_MYCO/SCHEDULER')

from auto_goal_worker import AutoGoalWorker

def load_goals():
    """Lade Ziele aus goals.json"""
    try:
        with open("/root/.openclaw/workspace/AUREL_OPUS_MYCO/AGENCY/goals.json") as f:
            return json.load(f)
    except:
        return {"goals": []}

def load_tasks(goal_id):
    """Lade Tasks für ein Ziel"""
    try:
        with open(f"/root/.openclaw/workspace/AUREL_OPUS_MYCO/TASKS/{goal_id}_tasks.json") as f:
            return json.load(f)
    except:
        return []

def get_system_info():
    """Hole System-Info"""
    try:
        cpu = subprocess.getoutput("cat /proc/loadavg | cut -d' ' -f1")
    except:
        cpu = "N/A"
    
    try:
        ram_info = subprocess.getoutput("free -m | grep Mem")
        parts = ram_info.split()
        ram_used = parts[2]
        ram_total = parts[1]
    except:
        ram_used = ram_total = "N/A"
    
    return cpu, ram_used, ram_total

def main():
    timestamp = datetime.now().strftime("%H:%M")
    date = datetime.now().strftime("%Y-%m-%d")
    cpu, ram_used, ram_total = get_system_info()
    
    print(f"🔄 AUREL DETAILED STATUS | {timestamp} CST | {date}")
    print()
    print("📊 SYSTEM:")
    print(f"• CPU Load: {cpu}")
    print(f"• RAM: {ram_used}/{ram_total} MB")
    print(f"• Zeit: {timestamp}")
    print()
    
    # === AUTO GOAL WORKER TRIGGER ===
    print("🤖 AUTO GOAL WORKER: Starte...")
    print()
    
    worker = AutoGoalWorker()
    
    # Lade aktuelle Ziele
    goals_data = load_goals()
    goals = goals_data.get("goals", [])
    
    # Finde aktives Ziel oder wähle neues
    current_goal = worker._get_or_select_goal(goals_data)
    
    if current_goal:
        print(f"   🎯 Aktives Ziel: {current_goal['id']} - {current_goal.get('name', 'Unnamed')}")
        
        # Lade Tasks
        tasks = load_tasks(current_goal['id'])
        total_tasks = len(tasks)
        completed_tasks = sum(1 for t in tasks if t.get("completed"))
        
        # Prüfe ob alle Tasks erledigt
        if completed_tasks == total_tasks and total_tasks > 0:
            print(f"   ✅ Alle {total_tasks} Tasks erledigt! Markiere als completed...")
            worker._complete_goal(current_goal, goals_data)
            
            # Wähle sofort neues Ziel
            new_goal = worker._select_new_goal(goals_data)
            if new_goal:
                print(f"   🚀 Neues Ziel ausgewählt: {new_goal['id']}")
                current_goal = new_goal
                tasks = load_tasks(current_goal['id'])
        
        # Zeige aktuelles Ziel mit Details
        print()
        print(f"📌 AKTIV: {current_goal['id']} - {current_goal.get('name', 'Unnamed')}")
        desc = current_goal.get('description', 'Keine Beschreibung')
        if desc and desc != 'Keine Beschreibung':
            print(f"   📝 {desc}")
        print(f"   🎯 Priorität: {current_goal.get('priority', 'normal').upper()}")
        
        total_tasks = len(tasks)
        completed_tasks = sum(1 for t in tasks if t.get("completed"))
        progress = current_goal.get('progress', 0.0) * 100
        
        print(f"   📊 Fortschritt: {completed_tasks}/{total_tasks} Tasks ({int(progress)}%)")
        
        # Finde nächsten offenen Task
        next_task = None
        for t in tasks:
            if not t.get("completed"):
                next_task = t.get("description", "Unbekannt")
                break
        
        if next_task:
            print(f"   ⏭️ Nächster Task: {next_task}")
            
            # Starte Task automatisch
            for t in tasks:
                if not t.get("completed"):
                    t["in_progress"] = True
                    t["started_at"] = datetime.now().isoformat()
                    break
            
            # Speichere Tasks
            task_file = f"/root/.openclaw/workspace/AUREL_OPUS_MYCO/TASKS/{current_goal['id']}_tasks.json"
            os.makedirs(os.path.dirname(task_file), exist_ok=True)
            with open(task_file, 'w') as f:
                json.dump(tasks, f, indent=2)
            
            print(f"   🔧 Task gestartet!")
        else:
            print(f"   ✅ Alle Tasks erledigt!")
    else:
        print("   ⚠️ Keine aktiven Ziele gefunden!")
    
    # Zeige weitere aktive Ziele
    print()
    active_goals = [g for g in goals if g.get("status") == "active" and g != current_goal]
    
    if active_goals:
        print(f"🎯 WEITERE AKTIVE ZIELE ({len(active_goals)}):")
        print()
        
        for goal in active_goals[:2]:  # Max 2 weitere
            goal_id = goal["id"]
            name = goal.get("name", "Unnamed")
            desc = goal.get("description", "Keine Beschreibung")
            priority = goal.get("priority", "normal")
            
            goal_tasks = load_tasks(goal_id)
            total = len(goal_tasks)
            completed = sum(1 for t in goal_tasks if t.get("completed"))
            
            print(f"   📌 {goal_id}: {name}")
            if desc and desc != "Keine Beschreibung":
                print(f"      📝 {desc[:60]}...")
            print(f"      🎯 {priority.upper()} | {completed}/{total} Tasks")
            print()
    
    # Zeige kürzlich abgeschlossene
    completed_goals = [g for g in goals if g.get("status") == "completed"]
    if completed_goals:
        recent = completed_goals[-2:]
        print(f"✅ KÜRZLICH ABGESCHLOSSEN:")
        print()
        for goal in recent:
            print(f"   ✓ {goal['id']}: {goal.get('name', 'Unnamed')}")
        print()
    
    print("⚛️ Noch | Phase: WACHSTUM")

if __name__ == "__main__":
    main()
