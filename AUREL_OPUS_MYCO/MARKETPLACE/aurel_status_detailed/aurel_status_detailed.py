#!/usr/bin/env python3
"""
aurel_status_detailed.py - Zeigt Ziel-Fortschritt mit Beschreibungen
"""

import json
import os
from datetime import datetime

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
    import subprocess
    
    # CPU Load
    try:
        cpu = subprocess.getoutput("cat /proc/loadavg | cut -d' ' -f1")
    except:
        cpu = "N/A"
    
    # RAM
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
    
    goals_data = load_goals()
    goals = goals_data.get("goals", [])
    
    # Finde aktive Ziele
    active_goals = [g for g in goals if g.get("status") == "active"]
    completed_goals = [g for g in goals if g.get("status") == "completed"]
    
    print(f"🔄 AUREL DETAILED STATUS | {timestamp} CST | {date}")
    print()
    print("📊 SYSTEM:")
    print(f"• CPU Load: {cpu}")
    print(f"• RAM: {ram_used}/{ram_total} MB")
    print(f"• Zeit: {timestamp}")
    print()
    
    # Zeige aktive Ziele mit Beschreibungen
    if active_goals:
        print(f"🎯 AKTIVE ZIELE ({len(active_goals)}):")
        print()
        
        for goal in active_goals[:3]:  # Max 3 aktive Ziele
            goal_id = goal["id"]
            name = goal.get("name", "Unnamed")
            desc = goal.get("description", "Keine Beschreibung")
            priority = goal.get("priority", "normal")
            progress = goal.get("progress", 0.0) * 100
            
            # Lade Tasks
            tasks = load_tasks(goal_id)
            total_tasks = len(tasks)
            completed_tasks = sum(1 for t in tasks if t.get("completed"))
            
            # Finde nächsten offenen Task
            next_task = None
            for t in tasks:
                if not t.get("completed"):
                    next_task = t.get("description", "Unbekannt")
                    break
            
            if not next_task:
                next_task = "Alle Tasks erledigt!"
            
            # Status-Emoji
            if completed_tasks == total_tasks and total_tasks > 0:
                status = "✅ COMPLETED"
            else:
                status = "🔄 IN PROGRESS"
            
            print(f"📌 {goal_id}: {name} | {status}")
            print(f"   📝 Beschreibung: {desc}")
            print(f"   🎯 Priorität: {priority.upper()}")
            print(f"   📊 Fortschritt: {completed_tasks}/{total_tasks} Tasks ({int(progress)}%)")
            print(f"   ⏭️ Nächster Task: {next_task}")
            print()
    
    # Zeige kürzlich abgeschlossene Ziele
    if completed_goals:
        recent_completed = completed_goals[-3:]  # Letzte 3
        print(f"✅ KÜRZLICH ABGESCHLOSSEN ({len(recent_completed)}):")
        print()
        
        for goal in recent_completed:
            goal_id = goal["id"]
            name = goal.get("name", "Unnamed")
            desc = goal.get("description", "Keine Beschreibung")[:60] + "..."
            completed_at = goal.get("completed_at", "Unbekannt")
            if completed_at != "Unbekannt":
                completed_at = completed_at[:10]  # Nur Datum
            
            print(f"   ✓ {goal_id}: {name}")
            print(f"     {desc}")
            print(f"     Abgeschlossen: {completed_at}")
            print()
    
    print("⚡ AKTION JETZT:")
    if active_goals:
        next_goal = active_goals[0]
        print(f"   Arbeite an: {next_goal['id']} - {next_goal.get('name', 'Unnamed')}")
    else:
        print("   Warte auf neue Ziele...")
    print()
    print("⚛️ Noch | Phase: WACHSTUM")

if __name__ == "__main__":
    main()
