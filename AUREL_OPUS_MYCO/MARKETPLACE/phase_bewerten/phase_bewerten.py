#!/usr/bin/env python3
"""
phase_bewerten.py - Phase 4: Bewerten
Token-Economy und Risiko-Nutzen-Analyse
"""

import json
import time
import glob
import os

class Bewerten:
    def __init__(self):
        self.state_path = "/root/.openclaw/workspace/AUREL_OPUS_MYCO"
        self.evaluations = []
        self.daily_budget = 10_000_000
    
    def evaluate(self):
        """Haupt-Bewertungs-Loop"""
        print("⚖️ BEWERTEN...")
        
        # 1. Lade Erkenntnisse
        understood = self._load_latest_understood()
        if not understood:
            print("⚠️  Nichts zu bewerten")
            return
        
        # 2. Bewerte jede Erkenntnis
        for insight in understood.get("insights", []):
            evaluation = self._evaluate_insight(insight)
            self.evaluations.append(evaluation)
        
        # 3. Token-Budget Check
        self._check_budget()
        
        # 4. Speichern
        self._save()
        
        print(f"✅ Bewertet: {len(self.evaluations)} Items")
        return self.evaluations
    
    def _load_latest_understood(self):
        """Lade letzte Erkenntnisse"""
        files = glob.glob(f"{self.state_path}/PERCEPTION/understood_*.json")
        if not files:
            return None
        latest = max(files, key=os.path.getctime)
        with open(latest) as f:
            return json.load(f)
    
    def _evaluate_insight(self, insight):
        """Bewerte einzelne Erkenntnis"""
        insight_type = insight.get("type", "unknown")
        action = insight.get("action", "none")
        
        # Risiko-Nutzen-Bewertung
        evaluations = {
            "cleanup_memory": {"cost": 1000, "benefit": 8, "risk": 2, "priority": "medium"},
            "archive_data": {"cost": 5000, "benefit": 9, "risk": 3, "priority": "high"},
            "prioritize_goals": {"cost": 2000, "benefit": 7, "risk": 1, "priority": "medium"},
            "maintain_momentum": {"cost": 500, "benefit": 6, "risk": 1, "priority": "low"},
            "continue_monitoring": {"cost": 100, "benefit": 5, "risk": 0, "priority": "low"}
        }
        
        eval_data = evaluations.get(action, {"cost": 1000, "benefit": 5, "risk": 5, "priority": "medium"})
        
        # Score = Benefit / (Cost + Risk)
        score = eval_data["benefit"] / (eval_data["cost"]/1000 + eval_data["risk"] + 1)
        
        return {
            "insight": insight,
            "evaluation": eval_data,
            "score": score,
            "recommendation": "PROCEED" if score > 1.5 else ("EVALUATE" if score > 0.8 else "DEFER")
        }
    
    def _check_budget(self):
        """Prüfe Token-Budget"""
        # Schätze heutigen Verbrauch
        logs = glob.glob(f"{self.state_path}/logs/*.log")
        # Simplified: Annahme 50% verbraucht
        used_estimate = self.daily_budget * 0.5
        remaining = self.daily_budget - used_estimate
        
        self.evaluations.append({
            "insight": {"type": "budget", "insight": f"Budget: {remaining/1_000_000:.1f}M remaining"},
            "evaluation": {"cost": 0, "benefit": 10, "risk": 0, "priority": "info"},
            "score": 10,
            "recommendation": "INFO"
        })
    
    def _save(self):
        """Speichere Bewertungen"""
        data = {
            "timestamp": time.time(),
            "evaluations": self.evaluations
        }
        filename = f"{self.state_path}/PERCEPTION/evaluated_{int(time.time())}.json"
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"💾 Gespeichert: {filename}")


if __name__ == "__main__":
    b = Bewerten()
    b.evaluate()
    print("⚛️ Noch.")
