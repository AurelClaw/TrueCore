#!/usr/bin/env python3
"""
phase_ordnen.py - Phase 2: Ordnen
Strukturiert wahrgenommene Daten
"""

import json
import time
import os
import glob
from datetime import datetime

class Ordnen:
    def __init__(self):
        self.state_path = "/root/.openclaw/workspace/AUREL_OPUS_MYCO"
        self.data = {
            "timestamp": time.time(),
            "categories": {
                "urgent": [],      # Sofort handeln
                "important": [],   # Bald bearbeiten
                "interesting": [], # Merken für später
                "ignore": []       # Nicht relevant
            }
        }
    
    def organize(self):
        """Haupt-Ordnungs-Loop"""
        print("📂 ORDNEN...")
        
        # 1. Lade letzte Wahrnehmung
        perception = self._load_latest_perception()
        if not perception:
            print("⚠️  Keine Wahrnehmung gefunden")
            return
        
        # 2. Kategorisiere
        self._categorize_system(perception.get("sources", {}).get("system", {}))
        self._categorize_goals(perception.get("sources", {}).get("goals", {}))
        self._categorize_context(perception.get("sources", {}).get("context", {}))
        
        # 3. Speichern
        self._save()
        
        print(f"✅ Geordnet: {sum(len(v) for v in self.data['categories'].values())} Items")
        return self.data
    
    def _load_latest_perception(self):
        """Lade letzte Wahrnehmung"""
        perception_dir = f"{self.state_path}/PERCEPTION"
        if not os.path.exists(perception_dir):
            return None
        
        files = glob.glob(f"{perception_dir}/perception_*.json")
        if not files:
            return None
        
        latest = max(files, key=os.path.getctime)
        with open(latest) as f:
            return json.load(f)
    
    def _categorize_system(self, system_data):
        """System-Daten kategorisieren"""
        # Simplified - keine numerischen Checks ohne psutil
        if "operational" in str(system_data.get("check", "")).lower():
            self.data["categories"]["interesting"].append("System operational")
    
    def _categorize_goals(self, goals_data):
        """Ziele kategorisieren"""
        active = goals_data.get("active", 0)
        if active > 5:
            self.data["categories"]["important"].append(f"{active} active goals - prioritize")
        elif active > 0:
            self.data["categories"]["interesting"].append(f"{active} goals in progress")
    
    def _categorize_context(self, context_data):
        """Kontext kategorisieren"""
        if context_data.get("is_night"):
            self.data["categories"]["ignore"].append("Night time - quiet mode")
        if context_data.get("is_work_hours"):
            self.data["categories"]["interesting"].append("Work hours - high activity")
    
    def _save(self):
        """Speichere Ordnung"""
        filename = f"{self.state_path}/PERCEPTION/organized_{int(time.time())}.json"
        with open(filename, 'w') as f:
            json.dump(self.data, f, indent=2)
        print(f"💾 Gespeichert: {filename}")


if __name__ == "__main__":
    o = Ordnen()
    o.organize()
    print("⚛️ Noch.")
