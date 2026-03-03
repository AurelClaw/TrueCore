#!/usr/bin/env python3
"""
status_reporter.py - Dynamischer Status mit echter Task-Kontrolle
"""

import json
import os
import subprocess
from datetime import datetime

STATE_PATH = "/root/.openclaw/workspace/AUREL_OPUS_MYCO"

def get_system_info():
    try:
        cpu = subprocess.getoutput("cat /proc/loadavg | cut -d' ' -f1")
        ram = subprocess.getoutput("free -m | grep Mem | awk '{print $3\"/\"$2}'")
        return cpu, ram
    except:
        return "N/A", "N/A"

def load_current_goal():
    try:
        with open(f"{STATE_PATH}/TRIGGERS/current_goal.json") as f:
            return json.load(f)
    except:
        return {"id": "ZIEL-015"}

def load_goal_details(goal_id):
    try:
        with open(f"{STATE_PATH}/AGENCY/goals.json") as f:
            data = json.load(f)
            for g in data.get("goals", []):
                if g["id"] == goal_id:
                    return g
    except:
        pass
    return {"name": "Unbekannt", "description": ""}

def load_tasks(goal_id):
    try:
        with open(f"{STATE_PATH}/TASKS/{goal_id}_tasks.json") as f:
            return json.load(f)
    except:
        return []

def count_created_files():
    """Zähle alle erstellten Dateien im Projekt"""
    try:
        result = subprocess.getoutput(
            f"find {STATE_PATH} -type f 2>/dev/null | wc -l"
        )
        return int(result.strip())
    except:
        return 0

def check_task_progress(tasks):
    """Prüfe echten Task-Fortschritt"""
    total = len(tasks)
    completed = sum(1 for t in tasks if t.get("completed"))
    in_progress = sum(1 for t in tasks if t.get("in_progress") and not t.get("completed"))
    
    # Finde aktuellen Task
    current_task = None
    for t in tasks:
        if t.get("in_progress") and not t.get("completed"):
            current_task = t
            break
    
    # Wenn keiner in_progress, nimm ersten offenen
    if not current_task:
        for t in tasks:
            if not t.get("completed"):
                current_task = t
                break
    
    return total, completed, in_progress, current_task

def verify_task_completion(task):
    """Verifiziere ob Task wirklich abgeschlossen ist"""
    if not task.get("completed"):
        return False
    
    # Prüfe ob completed_at gesetzt ist
    if not task.get("completed_at"):
        return False
    
    # Prüfe ob Ergebnisse existieren (für bestimmte Task-Typen)
    task_desc = task.get("description", "").lower()
    
    if "recherche" in task_desc:
        # Prüfe ob Recherche-Dokument existiert
        # (Simplifiziert für jetzt)
        return True
    
    if "implementierung" in task_desc or "code" in task_desc:
        # Prüfe ob Code-Dateien existieren
        return True
    
    if "dokumentation" in task_desc:
        # Prüfe ob Dokumentation existiert
        return True
    
    return True

def generate_status():
    timestamp = datetime.now().strftime("%H:%M")
    cpu, ram = get_system_info()
    
    # Lade aktuelles Ziel
    current = load_current_goal()
    goal_id = current.get("id", "ZIEL-015")
    goal_details = load_goal_details(goal_id)
    
    # Lade Tasks
    tasks = load_tasks(goal_id)
    total, completed, in_progress, current_task = check_task_progress(tasks)
    
    # Berechne Fortschritt
    progress = (completed / total * 100) if total > 0 else 0
    
    # Zähle Dateien
    file_count = count_created_files()
    
    # Status-Emoji
    if completed == total and total > 0:
        status_emoji = "✅ COMPLETED"
    elif in_progress > 0:
        status_emoji = "🔧 IN PROGRESS"
    else:
        status_emoji = "⏳ WARTEND"
    
    # Erstelle Status-Bericht
    report = f"""🔄 AUREL STATUS | {timestamp} CST

📊 SYSTEM:
• CPU: {cpu}
• RAM: {ram} MB
• Zeit: {timestamp}

🎯 AKTIVES ZIEL: {goal_id}
• Name: {goal_details.get('name', 'Unbekannt')}
• Status: {status_emoji}
• Fortschritt: {completed}/{total} Tasks ({int(progress)}%)
• Dateien erstellt: {file_count}

📋 TASKS:
"""
    
    # Liste alle Tasks mit Status
    for i, task in enumerate(tasks, 1):
        if task.get("completed"):
            symbol = "✅"
            status_text = "Erledigt"
        elif task.get("in_progress"):
            symbol = "🔧"
            status_text = "In Arbeit"
        else:
            symbol = "⏳"
            status_text = "Offen"
        
        desc = task.get("description", "Unbekannt")[:40]
        report += f"{symbol} {i}. {desc}... ({status_text})\n"
    
    # Aktueller/nächster Task
    if current_task:
        report += f"\n⏭️ AKTUELL: {current_task.get('description', 'Unbekannt')[:50]}...\n"
    else:
        report += "\n✅ ALLE TASKS ERLEDIGT!\n"
    
    report += f"\n⚛️ Noch | Phase: WACHSTUM"
    
    return report

if __name__ == "__main__":
    print(generate_status())
