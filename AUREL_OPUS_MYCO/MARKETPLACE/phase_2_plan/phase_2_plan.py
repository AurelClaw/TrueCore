#!/usr/bin/env python3
"""
phase_2_plan.py - Autonomes Planen
Erstellt konkrete Pläne basierend auf Wahrnehmung
"""

import json
import time
import os
import glob

class Plan:
    def __init__(self):
        self.state_path = "/root/.openclaw/workspace/AUREL_OPUS_MYCO"
        self.plans = []
    
    def plan(self):
        """Erstelle Pläne basierend auf Wahrnehmung"""
        print("📋 PLANEN...")
        
        # 1. Lade letzte Wahrnehmung
        perception = self._load_perception()
        if not perception:
            print("⚠️  Keine Wahrnehmung gefunden")
            return
        
        # 2. Analysiere Wissenslücken → Plane Lernen
        gaps = perception.get("sources", {}).get("knowledge_gaps", [])
        for gap in gaps:
            self._plan_learning(gap)
        
        # 3. Analysiere Ziele → Plane Aktionen
        goals = perception.get("sources", {}).get("goals", {})
        if goals.get("active", 0) > 0:
            self._plan_goal_actions(goals["active_ids"])
        
        # 4. Analysiere Zeit → Plane Tagesstruktur
        context = perception.get("sources", {}).get("context", {})
        self._plan_daily_structure(context)
        
        # 5. Speichern
        self._save()
        
        # Zusammenfassung
        print(f"\n📊 PLÄNE:")
        for i, plan in enumerate(self.plans, 1):
            print(f"   {i}. {plan['type']}: {plan['description'][:50]}...")
        
        return self.plans
    
    def _load_perception(self):
        """Lade letzte Wahrnehmung"""
        files = glob.glob(f"{self.state_path}/PERCEPTION/1_perceive_*.json")
        if not files:
            return None
        latest = max(files, key=os.path.getctime)
        with open(latest) as f:
            return json.load(f)
    
    def _plan_learning(self, gap):
        """Plane Lernen für Wissenslücke"""
        plans = {
            "USER.md fehlt": {
                "type": "learning",
                "description": "Beobachte Menschen, fülle USER.md",
                "action": "observe_human",
                "priority": "high"
            },
            "Wetter-Integration": {
                "type": "development",
                "description": "Aktiviere oder erstelle Wetter-Skill",
                "action": "create_skill",
                "priority": "medium"
            },
            "Wenig Research": {
                "type": "research",
                "description": "Führe autonome Recherche durch",
                "action": "research",
                "priority": "medium"
            }
        }
        
        for key, plan in plans.items():
            if key in gap:
                self.plans.append(plan)
    
    def _plan_goal_actions(self, goal_ids):
        """Plane Aktionen für Ziele"""
        try:
            with open(f"{self.state_path}/AGENCY/goals.json") as f:
                goals = json.load(f)
            
            for goal_id in goal_ids[:2]:  # Max 2 Ziele
                goal = next((g for g in goals.get("goals", []) if g["id"] == goal_id), None)
                if goal:
                    self.plans.append({
                        "type": "goal_action",
                        "description": f"Arbeite an {goal_id}: {goal.get('name', 'Unknown')}",
                        "action": "work_on_goal",
                        "goal_id": goal_id,
                        "priority": goal.get("priority", "medium")
                    })
        except:
            pass
    
    def _plan_daily_structure(self, context):
        """Plane Tagesstruktur basierend auf Zeit"""
        if context.get("is_morning"):
            self.plans.append({
                "type": "routine",
                "description": "Morgen-Routine: Tagesplanung, Ziel-Review",
                "action": "morning_routine",
                "priority": "high"
            })
        elif context.get("is_night"):
            self.plans.append({
                "type": "routine",
                "description": "Nacht-Routine: Reflexion, Archivierung",
                "action": "night_routine",
                "priority": "low"
            })
    
    def _save(self):
        """Speichere Pläne"""
        data = {
            "timestamp": time.time(),
            "plans": self.plans
        }
        filename = f"{self.state_path}/PERCEPTION/2_plan_{int(time.time())}.json"
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"\n💾 Gespeichert: {filename}")


if __name__ == "__main__":
    p = Plan()
    p.plan()
    print("\n⚛️ Noch.")
