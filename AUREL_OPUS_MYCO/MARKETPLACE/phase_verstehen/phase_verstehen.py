#!/usr/bin/env python3
"""
phase_verstehen.py - Phase 3: Verstehen
Analysiert und erkennt Muster
"""

import json
import time
import glob
import os

class Verstehen:
    def __init__(self):
        self.state_path = "/root/.openclaw/workspace/AUREL_OPUS_MYCO"
        self.insights = []
    
    def understand(self):
        """Haupt-Verstehungs-Loop"""
        print("🧠 VERSTEHEN...")
        
        # 1. Lade geordnete Daten
        organized = self._load_latest_organized()
        if not organized:
            print("⚠️  Nichts zu verstehen")
            return
        
        # 2. Analysiere Kategorien
        self._analyze_urgent(organized.get("categories", {}).get("urgent", []))
        self._analyze_important(organized.get("categories", {}).get("important", []))
        self._analyze_patterns()
        
        # 3. Formuliere Erkenntnisse
        self._formulate_insights()
        
        # 4. Speichern
        self._save()
        
        print(f"✅ Verstanden: {len(self.insights)} Erkenntnisse")
        return self.insights
    
    def _load_latest_organized(self):
        """Lade letzte Ordnung"""
        files = glob.glob(f"{self.state_path}/PERCEPTION/organized_*.json")
        if not files:
            return None
        latest = max(files, key=os.path.getctime)
        with open(latest) as f:
            return json.load(f)
    
    def _analyze_urgent(self, urgent_items):
        """Analysiere dringende Items"""
        for item in urgent_items:
            if "memory" in item.lower():
                self.insights.append({
                    "type": "system",
                    "insight": "Memory pressure detected - consider cleanup",
                    "action": "cleanup_memory"
                })
            if "disk" in item.lower():
                self.insights.append({
                    "type": "system",
                    "insight": "Storage critical - archive old data",
                    "action": "archive_data"
                })
    
    def _analyze_important(self, important_items):
        """Analysiere wichtige Items"""
        for item in important_items:
            if "goals" in item.lower():
                self.insights.append({
                    "type": "goals",
                    "insight": "Many active goals - need prioritization",
                    "action": "prioritize_goals"
                })
    
    def _analyze_patterns(self):
        """Erkenne Muster über Zeit"""
        # Prüfe letzte 24h
        perception_files = glob.glob(f"{self.state_path}/PERCEPTION/perception_*.json")
        recent = sorted(perception_files)[-10:]  # Letzte 10
        
        if len(recent) >= 5:
            self.insights.append({
                "type": "pattern",
                "insight": f"High activity: {len(recent)} perceptions in recent period",
                "action": "maintain_momentum"
            })
    
    def _formulate_insights(self):
        """Formuliere finale Erkenntnisse"""
        if not self.insights:
            self.insights.append({
                "type": "status",
                "insight": "System stable, no immediate action required",
                "action": "continue_monitoring"
            })
    
    def _save(self):
        """Speichere Erkenntnisse"""
        data = {
            "timestamp": time.time(),
            "insights": self.insights
        }
        filename = f"{self.state_path}/PERCEPTION/understood_{int(time.time())}.json"
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"💾 Gespeichert: {filename}")


if __name__ == "__main__":
    v = Verstehen()
    v.understand()
    print("⚛️ Noch.")
