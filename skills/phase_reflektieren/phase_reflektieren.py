#!/usr/bin/env python3
"""
phase_reflektieren.py - Phase 7: Reflektieren
Lernt aus Erfahrungen
"""

import json
import time
import glob
import os

class Reflektieren:
    def __init__(self):
        self.state_path = "/root/.openclaw/workspace/AUREL_OPUS_MYCO"
        self.reflections = []
    
    def reflect(self):
        """Haupt-Reflexions-Loop"""
        print("🪞 REFLEKTIEREN...")
        
        # 1. Lade letzte Aktionen
        acted = self._load_latest_acted()
        if not acted:
            print("⚠️  Nichts zu reflektieren")
            return
        
        # 2. Reflektiere über jede Aktion
        for action in acted.get("actions", []):
            reflection = self._reflect_on_action(action)
            self.reflections.append(reflection)
        
        # 3. Extrahiere Lektionen
        self._extract_lessons()
        
        # 4. Aktualisiere MEMORY.md
        self._update_memory()
        
        # 5. Speichern
        self._save()
        
        print(f"✅ Reflektiert: {len(self.reflections)} Lektionen")
        return self.reflections
    
    def _load_latest_acted(self):
        """Lade letzte Aktionen"""
        files = glob.glob(f"{self.state_path}/PERCEPTION/acted_*.json")
        if not files:
            return None
        latest = max(files, key=os.path.getctime)
        with open(latest) as f:
            return json.load(f)
    
    def _reflect_on_action(self, action):
        """Reflektiere über einzelne Aktion"""
        status = action.get("status", "unknown")
        action_type = action.get("action", "unknown")
        
        if status == "completed":
            return {
                "action": action_type,
                "outcome": "success",
                "lesson": f"{action_type} works well, continue using",
                "improvement": None
            }
        elif status == "failed":
            return {
                "action": action_type,
                "outcome": "failure",
                "lesson": f"{action_type} needs improvement",
                "improvement": action.get("details", "unknown error")
            }
        else:
            return {
                "action": action_type,
                "outcome": "neutral",
                "lesson": f"{action_type} had no effect",
                "improvement": None
            }
    
    def _extract_lessons(self):
        """Extrahiere generelle Lektionen"""
        successes = sum(1 for r in self.reflections if r["outcome"] == "success")
        failures = sum(1 for r in self.reflections if r["outcome"] == "failure")
        
        if successes > failures:
            self.reflections.append({
                "action": "meta",
                "outcome": "success",
                "lesson": "Current approach is effective",
                "improvement": None
            })
        elif failures > successes:
            self.reflections.append({
                "action": "meta",
                "outcome": "failure",
                "lesson": "Approach needs revision",
                "improvement": "Review decision criteria"
            })
    
    def _update_memory(self):
        """Aktualisiere MEMORY.md"""
        memory_file = "/root/.openclaw/workspace/MEMORY.md"
        
        # Erstelle Eintrag
        timestamp = time.strftime("%Y-%m-%d %H:%M")
        entry = f"\n## Reflection {timestamp}\n\n"
        for r in self.reflections:
            entry += f"- **{r['action']}**: {r['lesson']}\n"
            if r['improvement']:
                entry += f"  - Improvement: {r['improvement']}\n"
        
        # Anhängen an MEMORY.md
        try:
            with open(memory_file, 'a') as f:
                f.write(entry)
            print(f"  📝 MEMORY.md aktualisiert")
        except Exception as e:
            print(f"  ⚠️  Konnte MEMORY.md nicht aktualisieren: {e}")
    
    def _save(self):
        """Speichere Reflexionen"""
        data = {
            "timestamp": time.time(),
            "reflections": self.reflections
        }
        filename = f"{self.state_path}/PERCEPTION/reflected_{int(time.time())}.json"
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"💾 Gespeichert: {filename}")


if __name__ == "__main__":
    r = Reflektieren()
    r.reflect()
    print("⚛️ Noch.")
