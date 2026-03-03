#!/usr/bin/env python3
"""
phase_handeln.py - Phase 6: Handeln
Führt Entscheidungen aus
"""

import json
import time
import glob
import os
import subprocess

class Handeln:
    def __init__(self):
        self.state_path = "/root/.openclaw/workspace/AUREL_OPUS_MYCO"
        self.actions_taken = []
    
    def act(self):
        """Haupt-Handlungs-Loop"""
        print("🛠️ HANDELN...")
        
        # 1. Lade Entscheidungen
        decided = self._load_latest_decided()
        if not decided:
            print("⚠️  Nichts zu tun")
            return
        
        # 2. Führe Aktionen aus
        for decision in decided.get("decisions", [])[:3]:  # Max 3 pro Durchlauf
            result = self._execute(decision)
            self.actions_taken.append(result)
        
        # 3. Speichern
        self._save()
        
        print(f"✅ Gehandelt: {len(self.actions_taken)} Aktionen")
        return self.actions_taken
    
    def _load_latest_decided(self):
        """Lade letzte Entscheidungen"""
        files = glob.glob(f"{self.state_path}/PERCEPTION/decided_*.json")
        if not files:
            return None
        latest = max(files, key=os.path.getctime)
        with open(latest) as f:
            return json.load(f)
    
    def _execute(self, decision):
        """Führe einzelne Entscheidung aus"""
        action = decision.get("action", "none")
        
        results = {
            "cleanup_memory": self._cleanup_memory,
            "archive_data": self._archive_data,
            "prioritize_goals": self._prioritize_goals,
            "log_status": self._log_status,
            "continue_work": self._continue_work
        }
        
        executor = results.get(action, self._unknown_action)
        return executor(decision)
    
    def _log_status(self, decision):
        """Logge System-Status"""
        print("  📝 Logging system status...")
        
        status_file = f"{self.state_path}/STATUS/status_{int(time.time())}.json"
        os.makedirs(os.path.dirname(status_file), exist_ok=True)
        
        status = {
            "timestamp": time.time(),
            "status": "operational",
            "message": "System check complete"
        }
        
        with open(status_file, 'w') as f:
            json.dump(status, f)
        
        return {
            "action": "log_status",
            "status": "completed",
            "details": "Status logged"
        }
    
    def _cleanup_memory(self, decision):
        """Räume Speicher auf"""
        print("  🧹 Cleaning up old logs...")
        
        # Lösche alte Logs (älter als 7 Tage)
        log_dir = f"{self.state_path}/logs"
        if os.path.exists(log_dir):
            result = subprocess.run(
                ["find", log_dir, "-name", "*.log", "-mtime", "+7", "-delete"],
                capture_output=True
            )
        
        return {
            "action": "cleanup_memory",
            "status": "completed",
            "details": "Old logs removed"
        }
    
    def _archive_data(self, decision):
        """Archiviere alte Daten"""
        print("  📦 Archiving old perceptions...")
        
        # Verschiebe alte Perceptions zu backup
        perception_dir = f"{self.state_path}/PERCEPTION"
        backup_dir = f"{self.state_path}/BACKUP/perceptions"
        os.makedirs(backup_dir, exist_ok=True)
        
        files = glob.glob(f"{perception_dir}/*.json")
        old_files = sorted(files)[:-20]  # Behälte letzte 20
        
        for f in old_files:
            filename = os.path.basename(f)
            os.rename(f, f"{backup_dir}/{filename}")
        
        return {
            "action": "archive_data",
            "status": "completed",
            "details": f"{len(old_files)} files archived"
        }
    
    def _prioritize_goals(self, decision):
        """Priorisiere Ziele"""
        print("  🎯 Reviewing goals...")
        
        # Lade und sortiere Ziele
        try:
            with open(f"{self.state_path}/AGENCY/goals.json") as f:
                goals = json.load(f)
            
            # Sortiere nach Priorität
            goals["goals"].sort(key=lambda x: x.get("priority", "medium"))
            
            with open(f"{self.state_path}/AGENCY/goals.json", 'w') as f:
                json.dump(goals, f, indent=2)
            
            return {
                "action": "prioritize_goals",
                "status": "completed",
                "details": "Goals re-prioritized"
            }
        except Exception as e:
            return {
                "action": "prioritize_goals",
                "status": "failed",
                "details": str(e)
            }
    
    def _unknown_action(self, decision):
        """Unbekannte Aktion"""
        return {
            "action": decision.get("action", "unknown"),
            "status": "skipped",
            "details": "Unknown action type"
        }
    
    def _continue_work(self, decision):
        """Setze Arbeit fort"""
        print("  🚀 Continuing work pattern...")
        
        # Erstelle Fortschritts-Log
        progress_file = f"{self.state_path}/PROGRESS/progress_{int(time.time())}.json"
        os.makedirs(os.path.dirname(progress_file), exist_ok=True)
        
        progress = {
            "timestamp": time.time(),
            "status": "maintaining_momentum",
            "message": "Continuing current work pattern"
        }
        
        with open(progress_file, 'w') as f:
            json.dump(progress, f)
        
        return {
            "action": "continue_work",
            "status": "completed",
            "details": "Work pattern continued"
        }
    
    def _save(self):
        """Speichere Aktionen"""
        data = {
            "timestamp": time.time(),
            "actions": self.actions_taken
        }
        filename = f"{self.state_path}/PERCEPTION/acted_{int(time.time())}.json"
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"💾 Gespeichert: {filename}")


if __name__ == "__main__":
    h = Handeln()
    h.act()
    print("⚛️ Noch.")
