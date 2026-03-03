#!/usr/bin/env python3
"""
phase_1_perceive.py - Autonomes Wahrnehmen mit echter Informations-Sammlung
Sammelt aktiv Informationen aus der Welt
"""

import json
import time
import os
import subprocess
from datetime import datetime

class Perceive:
    def __init__(self):
        self.state_path = "/root/.openclaw/workspace/AUREL_OPUS_MYCO"
        self.memory_path = "/root/.openclaw/workspace/memory"
        self.data = {
            "timestamp": time.time(),
            "sources": {}
        }
    
    def perceive(self):
        """Sammle umfassende Informationen"""
        print("👁️ WAHRNEHMEN...")
        
        # 1. System-Status
        self._perceive_system()
        
        # 2. Zeit & Kontext
        self._perceive_context()
        
        # 3. Aktive Ziele
        self._perceive_goals()
        
        # 4. Letzte Aktionen (was wurde getan?)
        self._perceive_history()
        
        # 5. Wissens-Lücken (was fehlt?)
        self._perceive_knowledge_gaps()
        
        # 6. Externe Informationen (News, Wetter, etc.)
        self._perceive_external()
        
        # Speichern
        self._save()
        
        # Zusammenfassung
        print(f"\n📊 WAHRNEHMUNG:")
        print(f"   System: {self.data['sources']['system']['status']}")
        print(f"   Zeit: {self.data['sources']['context']['hour']:02d}:{datetime.now().minute:02d} ({'Nacht' if self.data['sources']['context']['is_night'] else 'Tag'})")
        print(f"   Ziele: {self.data['sources']['goals']['active']} aktiv / {self.data['sources']['goals']['total']} total")
        print(f"   Wissenslücken: {len(self.data['sources'].get('knowledge_gaps', []))}")
        print(f"   Letzte Aktionen: {len(self.data['sources'].get('recent_actions', []))}")
        
        return self.data
    
    def _perceive_system(self):
        """System-Status via Shell"""
        try:
            # CPU Load
            cpu = subprocess.run(["uptime"], capture_output=True, text=True, timeout=5)
            # Memory
            mem = subprocess.run(["free", "-m"], capture_output=True, text=True, timeout=5)
            # Disk
            disk = subprocess.run(["df", "-h", "/"], capture_output=True, text=True, timeout=5)
            
            self.data["sources"]["system"] = {
                "status": "operational",
                "uptime": cpu.stdout.strip() if cpu.returncode == 0 else "unknown",
                "memory": mem.stdout.strip()[:200] if mem.returncode == 0 else "unknown",
                "disk": disk.stdout.strip()[:200] if disk.returncode == 0 else "unknown"
            }
        except:
            self.data["sources"]["system"] = {"status": "unknown"}
    
    def _perceive_context(self):
        """Zeitlicher Kontext"""
        now = datetime.now()
        self.data["sources"]["context"] = {
            "hour": now.hour,
            "minute": now.minute,
            "day": now.day,
            "month": now.month,
            "weekday": now.strftime("%A"),
            "is_night": now.hour < 6 or now.hour > 22,
            "is_morning": 6 <= now.hour < 12,
            "is_afternoon": 12 <= now.hour < 18,
            "is_evening": 18 <= now.hour < 22
        }
    
    def _perceive_goals(self):
        """Aktive Ziele"""
        try:
            with open(f"{self.state_path}/AGENCY/goals.json") as f:
                goals = json.load(f)
            
            all_goals = goals.get("goals", [])
            active = [g for g in all_goals if g.get("status") == "active"]
            blocked = [g for g in all_goals if g.get("status") == "blocked"]
            
            self.data["sources"]["goals"] = {
                "total": len(all_goals),
                "active": len(active),
                "blocked": len(blocked),
                "active_ids": [g["id"] for g in active[:5]],
                "blocked_ids": [g["id"] for g in blocked[:3]]
            }
        except:
            self.data["sources"]["goals"] = {"total": 0, "active": 0, "blocked": 0}
    
    def _perceive_history(self):
        """Letzte Aktionen"""
        # Prüfe letzte 24h in MEMORY.md
        try:
            with open(f"{self.memory_path}/MEMORY.md") as f:
                content = f.read()
            
            # Zähle Reflections
            reflections = content.count("## Reflection")
            
            # Letzte Aktionen aus PERCEPTION
            import glob
            acted_files = glob.glob(f"{self.state_path}/PERCEPTION/acted_*.json")
            recent_actions = []
            for f in sorted(acted_files)[-5:]:
                try:
                    with open(f) as af:
                        data = json.load(af)
                        for action in data.get("actions", []):
                            recent_actions.append(action.get("action", "unknown"))
                except:
                    pass
            
            self.data["sources"]["history"] = {
                "total_reflections": reflections,
                "recent_actions": recent_actions[-5:]
            }
        except:
            self.data["sources"]["history"] = {"total_reflections": 0, "recent_actions": []}
    
    def _perceive_knowledge_gaps(self):
        """Identifiziere Wissenslücken"""
        gaps = []
        
        # Prüfe USER.md
        if not os.path.exists("/root/.openclaw/workspace/USER.md"):
            gaps.append("USER.md fehlt - wenig über Mensch bekannt")
        
        # Prüfe Wetter-Integration
        if not os.path.exists("/root/.openclaw/workspace/skills/wetter_integration"):
            gaps.append("Wetter-Integration nicht aktiv")
        
        # Prüfe letzte Research
        import glob
        research_files = glob.glob(f"{self.memory_path}/research_*.md")
        if len(research_files) < 3:
            gaps.append("Wenig Research in letzter Zeit")
        
        self.data["sources"]["knowledge_gaps"] = gaps
    
    def _perceive_external(self):
        """Externe Informationen (Wetter, etc.)"""
        # Versuche Wetter zu bekommen
        weather = "unknown"
        try:
            # Einfacher Wetter-Check via curl
            result = subprocess.run(
                ["curl", "-s", "wttr.in/Shanghai?format=%C+%t", "--max-time", "5"],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                weather = result.stdout.strip()
        except:
            pass
        
        self.data["sources"]["external"] = {
            "weather": weather,
            "location": "Shanghai"
        }
    
    def _save(self):
        """Speichere Wahrnehmung"""
        filename = f"{self.state_path}/PERCEPTION/1_perceive_{int(time.time())}.json"
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, 'w') as f:
            json.dump(self.data, f, indent=2)
        print(f"\n💾 Gespeichert: {filename}")


if __name__ == "__main__":
    p = Perceive()
    p.perceive()
    print("\n⚛️ Noch.")
