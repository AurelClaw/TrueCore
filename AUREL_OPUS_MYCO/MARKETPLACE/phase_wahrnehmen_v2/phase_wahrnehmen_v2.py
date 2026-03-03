#!/usr/bin/env python3
"""
phase_wahrnehmen_v2.py - Phase 1: Wahrnehmen mit Skill-Aktivierung
"""

import json
import time
import os
import sys
from datetime import datetime

# Füge Scheduler-Pfad hinzu
sys.path.insert(0, "/root/.openclaw/workspace/AUREL_OPUS_MYCO/SCHEDULER")
from skill_router import SkillRouter

class WahrnehmenV2:
    def __init__(self):
        self.state_path = "/root/.openclaw/workspace/AUREL_OPUS_MYCO"
        self.data = {
            "timestamp": time.time(),
            "datetime": datetime.now().isoformat(),
            "sources": {},
            "skill_result": None
        }
    
    def perceive(self):
        """Haupt-Wahrnehmungs-Loop mit Skill"""
        print("👁️ WAHRNEHMEN V2...")
        
        # 1. Sammle Daten
        self._perceive_system()
        self._perceive_context()
        self._perceive_goals()
        
        # 2. Wähle und aktiviere Skill
        print("\n🎯 Aktiviere Skill...")
        router = SkillRouter()
        
        context = {
            "is_night": self.data["sources"]["context"]["is_night"],
            "hour": self.data["sources"]["context"]["hour"],
            "active_goals": self.data["sources"]["goals"]["active"]
        }
        
        skill_result = router.route("wahrnehmen", context)
        self.data["skill_result"] = skill_result
        
        # 3. Integriere Skill-Ergebnis
        if skill_result["status"] == "success":
            print(f"   ✅ Skill erfolgreich: {skill_result['skill']}")
            self.data["sources"]["skill_insight"] = skill_result.get("stdout", "")[:200]
        else:
            print(f"   ⚠️  Skill-Status: {skill_result['status']}")
        
        # 4. Speichern
        self._save()
        
        # 5. Zusammenfassung
        print(f"\n📊 ZUSAMMENFASSUNG WAHRNEHMEN:")
        print(f"   Zeit: {self.data['sources']['context']['hour']:02d}:{datetime.now().minute:02d}")
        print(f"   Ziele: {self.data['sources']['goals']['active']} aktiv")
        print(f"   Skill: {skill_result['skill']} ({skill_result['status']})")
        
        return self.data
    
    def _perceive_system(self):
        """System-Status"""
        self.data["sources"]["system"] = {
            "check": "system operational",
            "timestamp": time.time()
        }
    
    def _perceive_context(self):
        """Zeitlicher Kontext"""
        now = datetime.now()
        self.data["sources"]["context"] = {
            "hour": now.hour,
            "minute": now.minute,
            "is_night": now.hour < 6 or now.hour > 22,
            "is_work_hours": 9 <= now.hour <= 18
        }
    
    def _perceive_goals(self):
        """Offene Ziele"""
        try:
            with open(f"{self.state_path}/AGENCY/goals.json") as f:
                goals = json.load(f)
                active = [g for g in goals.get("goals", []) if g.get("status") == "active"]
                self.data["sources"]["goals"] = {
                    "total": len(goals.get("goals", [])),
                    "active": len(active),
                    "active_ids": [g["id"] for g in active[:3]]
                }
        except:
            self.data["sources"]["goals"] = {"total": 0, "active": 0, "active_ids": []}
    
    def _save(self):
        """Speichere Wahrnehmung"""
        filename = f"{self.state_path}/PERCEPTION/perception_v2_{int(time.time())}.json"
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, 'w') as f:
            json.dump(self.data, f, indent=2)
        print(f"\n💾 Gespeichert: {filename}")


if __name__ == "__main__":
    w = WahrnehmenV2()
    w.perceive()
    print("\n⚛️ Noch.")
