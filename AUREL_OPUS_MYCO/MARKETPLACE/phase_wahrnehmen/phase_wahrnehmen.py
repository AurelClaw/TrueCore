#!/usr/bin/env python3
"""
phase_wahrnehmen.py - Phase 1: Wahrnehmen
Sammelt Roh-Daten aus allen Quellen
"""

import json
import time
import os
from datetime import datetime

class Wahrnehmen:
    def __init__(self):
        self.state_path = "/root/.openclaw/workspace/AUREL_OPUS_MYCO"
        self.memory_path = "/root/.openclaw/workspace/memory"
        self.data = {
            "timestamp": time.time(),
            "datetime": datetime.now().isoformat(),
            "sources": {}
        }
    
    def perceive(self):
        """Haupt-Wahrnehmungs-Loop"""
        print("👁️ WAHRNEHMEN...")
        
        # 1. System-Status
        self._perceive_system()
        
        # 2. Zeit & Kontext
        self._perceive_context()
        
        # 3. Offene Ziele
        self._perceive_goals()
        
        # 4. Letzte Aktionen
        self._perceive_history()
        
        # Speichern
        self._save()
        
        print(f"✅ Wahrgenommen: {len(self.data['sources'])} Quellen")
        return self.data
    
    def _perceive_system(self):
        """System-Metriken (ohne psutil)"""
        import os
        
        # Einfache System-Checks
        self.data["sources"]["system"] = {
            "cpu_percent": "unknown",
            "memory_percent": "unknown", 
            "disk_percent": "unknown",
            "check": "system operational"
        }
    
    def _perceive_context(self):
        """Zeitlicher Kontext"""
        now = datetime.now()
        self.data["sources"]["context"] = {
            "hour": now.hour,
            "minute": now.minute,
            "day_of_week": now.weekday(),
            "is_night": now.hour < 6 or now.hour > 22,
            "is_work_hours": 9 <= now.hour <= 18
        }
    
    def _perceive_goals(self):
        """Offene Ziele aus AGENCY"""
        try:
            with open(f"{self.state_path}/AGENCY/goals.json") as f:
                goals = json.load(f)
                active = [g for g in goals.get("goals", []) if g.get("status") == "active"]
                self.data["sources"]["goals"] = {
                    "total": len(goals.get("goals", [])),
                    "active": len(active),
                    "active_ids": [g["id"] for g in active[:3]]  # Top 3
                }
        except:
            self.data["sources"]["goals"] = {"error": "Could not read goals"}
    
    def _perceive_history(self):
        """Letzte Aktionen"""
        log_dir = f"{self.state_path}/logs"
        if os.path.exists(log_dir):
            logs = sorted(os.listdir(log_dir))[-5:]  # Letzte 5
            self.data["sources"]["history"] = {"recent_logs": logs}
        else:
            self.data["sources"]["history"] = {"recent_logs": []}
    
    def _save(self):
        """Speichere Wahrnehmung"""
        filename = f"{self.state_path}/PERCEPTION/perception_{int(time.time())}.json"
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, 'w') as f:
            json.dump(self.data, f, indent=2)
        print(f"💾 Gespeichert: {filename}")


if __name__ == "__main__":
    w = Wahrnehmen()
    w.perceive()
    print("⚛️ Noch.")
