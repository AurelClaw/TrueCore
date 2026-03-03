#!/usr/bin/env python3
"""
phase_entscheiden.py - Phase 5: Entscheiden
Konkrete Entscheidungen basierend auf Bewertungen
"""

import json
import time
import glob
import os

class Entscheiden:
    def __init__(self):
        self.state_path = "/root/.openclaw/workspace/AUREL_OPUS_MYCO"
        self.decisions = []
    
    def decide(self):
        """Haupt-Entscheidungs-Loop"""
        print("🎯 ENTSCHEIDEN...")
        
        # 1. Lade Bewertungen
        evaluated = self._load_latest_evaluated()
        if not evaluated:
            print("⚠️  Nichts zu entscheiden")
            return
        
        # 2. Treffe Entscheidungen
        for eval_item in evaluated.get("evaluations", []):
            if eval_item.get("recommendation") == "PROCEED":
                decision = self._make_decision(eval_item)
                if decision:
                    self.decisions.append(decision)
        
        # 3. Priorisiere
        self._prioritize()
        
        # 4. Speichern
        self._save()
        
        print(f"✅ Entschieden: {len(self.decisions)} Aktionen")
        return self.decisions
    
    def _load_latest_evaluated(self):
        """Lade letzte Bewertungen"""
        files = glob.glob(f"{self.state_path}/PERCEPTION/evaluated_*.json")
        if not files:
            return None
        latest = max(files, key=os.path.getctime)
        with open(latest) as f:
            return json.load(f)
    
    def _make_decision(self, eval_item):
        """Treffe Entscheidung für ein Item"""
        insight = eval_item.get("insight", {})
        action = insight.get("action", "none")
        
        decisions = {
            "cleanup_memory": {
                "action": "cleanup_memory",
                "what": "Clean up old logs and temp files",
                "when": "next_handeln",
                "resources": 1000,
                "risk": "low"
            },
            "archive_data": {
                "action": "archive_data",
                "what": "Archive old perceptions to backup",
                "when": "next_handeln",
                "resources": 5000,
                "risk": "medium"
            },
            "prioritize_goals": {
                "action": "prioritize_goals",
                "what": "Review and prioritize active goals",
                "when": "next_handeln",
                "resources": 2000,
                "risk": "low"
            },
            "continue_monitoring": {
                "action": "log_status",
                "what": "Log current system status for tracking",
                "when": "now",
                "resources": 100,
                "risk": "none"
            },
            "maintain_momentum": {
                "action": "continue_work",
                "what": "Continue current work pattern",
                "when": "now",
                "resources": 500,
                "risk": "low"
            }
        }
        
        return decisions.get(action)
    
    def _prioritize(self):
        """Priorisiere Entscheidungen nach Score"""
        self.decisions.sort(key=lambda x: x.get("resources", 1000))
    
    def _save(self):
        """Speichere Entscheidungen"""
        data = {
            "timestamp": time.time(),
            "decisions": self.decisions
        }
        filename = f"{self.state_path}/PERCEPTION/decided_{int(time.time())}.json"
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"💾 Gespeichert: {filename}")


if __name__ == "__main__":
    e = Entscheiden()
    e.decide()
    print("⚛️ Noch.")
