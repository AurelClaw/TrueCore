#!/usr/bin/env python3
"""
longterm_planner.py - Tages-, Wochen- und Monatsplanung
"""

import json
import os
from datetime import datetime, timedelta

PLAN_FILE = "/root/.openclaw/workspace/AUREL_OPUS_MYCO/PERSISTENT/longterm_plan.json"

def ensure_dir():
    os.makedirs(os.path.dirname(PLAN_FILE), exist_ok=True)

def load_plan():
    """Lade Langzeit-Plan"""
    try:
        with open(PLAN_FILE) as f:
            return json.load(f)
    except:
        return create_default_plan()

def save_plan(plan):
    """Speichere Langzeit-Plan"""
    ensure_dir()
    with open(PLAN_FILE, 'w') as f:
        json.dump(plan, f, indent=2)

def create_default_plan():
    """Erstelle Standard-Plan"""
    now = datetime.now()
    
    return {
        "created_at": now.isoformat(),
        "daily": {
            "morning": [
                "Status-Check und System-Health",
                "Aktives Ziel reviewen",
                "Nächsten Task starten"
            ],
            "afternoon": [
                "Skill-Entwicklung",
                "Tests ausführen",
                "Dokumentation aktualisieren"
            ],
            "evening": [
                "Tages-Review",
                "Fortschritt loggen",
                "Morgen planen"
            ]
        },
        "weekly": {
            "monday": "Wochenplanung und Ziel-Review",
            "tuesday": "Hauptentwicklung",
            "wednesday": "Hauptentwicklung",
            "thursday": "Hauptentwicklung",
            "friday": "Testing und Integration",
            "saturday": "Research und Exploration",
            "sunday": "Wochen-Review und Planung"
        },
        "monthly": {
            "week_1": "Planung und Architektur",
            "week_2": "Hauptimplementierung",
            "week_3": "Testing und Optimierung",
            "week_4": "Review und Dokumentation"
        },
        "current_focus": "Phase 3: Echte Code-Ausführung und Langzeit-Planung",
        "milestones": [
            {"name": "Phase 1 Complete", "date": "2026-03-03", "status": "completed"},
            {"name": "Phase 2 Complete", "date": "2026-03-03", "status": "completed"},
            {"name": "Phase 3 Complete", "date": "2026-03-10", "status": "in_progress"},
            {"name": "Phase 4 Start", "date": "2026-03-17", "status": "pending"}
        ]
    }

def get_today_plan():
    """Hole Tagesplan für heute"""
    plan = load_plan()
    weekday = datetime.now().strftime("%A").lower()
    
    return {
        "daily": plan["daily"],
        "weekly_focus": plan["weekly"].get(weekday, "Hauptentwicklung"),
        "current_focus": plan["current_focus"],
        "milestones": plan["milestones"]
    }

def show_plan():
    """Zeige aktuellen Plan"""
    plan = load_plan()
    today = get_today_plan()
    weekday = datetime.now().strftime("%A")
    
    print("📅 LANGZEIT-PLANUNG")
    print("===================")
    print()
    
    # Tagesplan
    print(f"📆 HEUTE ({weekday})")
    print(f"   Fokus: {today['weekly_focus']}")
    print()
    
    print("🌅 Morgen:")
    for task in today['daily']['morning']:
        print(f"   - {task}")
    print()
    
    print("☀️ Nachmittag:")
    for task in today['daily']['afternoon']:
        print(f"   - {task}")
    print()
    
    print("🌙 Abend:")
    for task in today['daily']['evening']:
        print(f"   - {task}")
    print()
    
    # Milestones
    print("🎯 Meilensteine:")
    for ms in today['milestones']:
        status = "✅" if ms['status'] == 'completed' else "🔄" if ms['status'] == 'in_progress' else "⏳"
        print(f"   {status} {ms['name']} ({ms['date']})")
    print()
    
    print("⚛️ Noch.")

def update_milestone(name, status):
    """Update Milestone-Status"""
    plan = load_plan()
    
    for ms in plan["milestones"]:
        if ms["name"] == name:
            ms["status"] = status
            print(f"🎯 Milestone '{name}' auf '{status}' gesetzt")
            break
    
    save_plan(plan)

def main():
    show_plan()
    
    # Update Phase 3
    update_milestone("Phase 3 Complete", "in_progress")

if __name__ == "__main__":
    main()
