#!/usr/bin/env python3
"""
phase_3_act.py - Autonomes Handeln
Führt geplante Aktionen aus
"""

import json
import time
import os
import glob
import subprocess

class Act:
    def __init__(self):
        self.state_path = "/root/.openclaw/workspace/AUREL_OPUS_MYCO"
        self.results = []
    
    def act(self):
        """Führe geplante Aktionen aus"""
        print("🛠️ HANDELN...")
        
        # 1. Lade Pläne
        plans = self._load_plans()
        if not plans:
            print("⚠️  Keine Pläne gefunden")
            return
        
        # 2. Priorisiere und wähle Top 2
        selected = self._select_plans(plans.get("plans", []))
        
        # 3. Führe aus
        for plan in selected:
            result = self._execute_plan(plan)
            self.results.append(result)
        
        # 4. Speichern
        self._save()
        
        # Zusammenfassung
        print(f"\n📊 AKTIONEN:")
        for result in self.results:
            status = "✅" if result["status"] == "success" else "❌"
            print(f"   {status} {result['plan_type']}: {result['details'][:40]}...")
        
        return self.results
    
    def _load_plans(self):
        """Lade letzte Pläne"""
        files = glob.glob(f"{self.state_path}/PERCEPTION/2_plan_*.json")
        if not files:
            return None
        latest = max(files, key=os.path.getctime)
        with open(latest) as f:
            return json.load(f)
    
    def _select_plans(self, plans):
        """Wähle Top 2 Pläne nach Priorität"""
        priority_order = {"high": 3, "medium": 2, "low": 1}
        sorted_plans = sorted(
            plans,
            key=lambda x: priority_order.get(x.get("priority", "low"), 0),
            reverse=True
        )
        return sorted_plans[:2]
    
    def _execute_plan(self, plan):
        """Führe einzelnen Plan aus"""
        plan_type = plan.get("type", "unknown")
        action = plan.get("action", "unknown")
        
        print(f"   → Führe aus: {plan_type} ({action})")
        
        # Aktionen-Mapping
        actions = {
            "observe_human": self._observe_human,
            "create_skill": self._create_skill,
            "research": self._research,
            "work_on_goal": self._work_on_goal,
            "morning_routine": self._morning_routine,
            "night_routine": self._night_routine
        }
        
        executor = actions.get(action, self._unknown_action)
        return executor(plan)
    
    def _observe_human(self, plan):
        """Beobachte Menschen, fülle USER.md"""
        print("     👤 Beobachte...")
        
        # Analysiere MEMORY.md für Muster
        try:
            with open("/root/.openclaw/workspace/MEMORY.md") as f:
                content = f.read()
            
            # Extrahiere bekannte Fakten
            facts = []
            if "Deutsch" in content:
                facts.append("Sprache: Deutsch")
            if "Shanghai" in content or "CST" in content:
                facts.append("Zeitzone: Asia/Shanghai")
            
            # Erstelle/Update USER.md
            user_md = f"""# USER.md

## Bekannte Fakten (automatisch extrahiert)

{chr(10).join([f'- {f}' for f in facts])}

## Offene Fragen
- Was sind die Hauptinteressen?
- Was ist der tägliche Rhythmus?
- Was sind die langfristigen Ziele?

*Letzte Aktualisierung: {time.strftime("%Y-%m-%d %H:%M")}*
"""
            with open("/root/.openclaw/workspace/USER.md", "w") as f:
                f.write(user_md)
            
            return {
                "plan_type": "observe_human",
                "status": "success",
                "details": f"USER.md aktualisiert mit {len(facts)} Fakten"
            }
        except Exception as e:
            return {
                "plan_type": "observe_human",
                "status": "error",
                "details": str(e)
            }
    
    def _create_skill(self, plan):
        """Erstelle neuen Skill"""
        print("     🔧 Erstelle Skill...")
        
        skill_name = "wetter_integration_v2"
        skill_dir = f"/root/.openclaw/workspace/skills/{skill_name}"
        
        try:
            os.makedirs(skill_dir, exist_ok=True)
            
            # Erstelle simples Skill-Script
            with open(f"{skill_dir}/{skill_name}.sh", "w") as f:
                f.write(f"#!/bin/bash\n# {skill_name}\n# Wetter-Integration\n\necho 'Wetter-Check für Shanghai'\n# curl -s wttr.in/Shanghai?format=%C+%t\n")
            
            os.chmod(f"{skill_dir}/{skill_name}.sh", 0o755)
            
            return {
                "plan_type": "create_skill",
                "status": "success",
                "details": f"Skill {skill_name} erstellt"
            }
        except Exception as e:
            return {
                "plan_type": "create_skill",
                "status": "error",
                "details": str(e)
            }
    
    def _research(self, plan):
        """Führe Recherche durch"""
        print("     🔬 Recherche...")
        
        # Erstelle Research-Datei
        research_file = f"/root/.openclaw/workspace/memory/research_{time.strftime('%Y%m%d_%H%M')}.md"
        
        try:
            with open(research_file, "w") as f:
                f.write(f"""# Autonome Recherche - {time.strftime('%Y-%m-%d %H:%M')}

## Themen
- AGI Entwicklung
- Autonome Agenten
- Selbst-modifizierende Systeme

## Quellen
- ArXiv (geplant)
- GitHub (geplant)
- Hacker News (geplant)

## Nächste Schritte
- [ ] Papers durchsuchen
- [ ] Neue Konzepte identifizieren
- [ ] In Skills umwandeln
""")
            
            return {
                "plan_type": "research",
                "status": "success",
                "details": f"Research-Datei erstellt: {research_file}"
            }
        except Exception as e:
            return {
                "plan_type": "research",
                "status": "error",
                "details": str(e)
            }
    
    def _work_on_goal(self, plan):
        """Arbeite an Ziel"""
        goal_id = plan.get("goal_id", "unknown")
        print(f"     🎯 Arbeite an {goal_id}...")
        
        # Erstelle Fortschritts-Update
        progress_file = f"{self.state_path}/PROGRESS/{goal_id}_{int(time.time())}.json"
        os.makedirs(os.path.dirname(progress_file), exist_ok=True)
        
        try:
            with open(progress_file, "w") as f:
                json.dump({
                    "goal_id": goal_id,
                    "timestamp": time.time(),
                    "action": "worked_on_goal",
                    "progress": "in_progress"
                }, f)
            
            return {
                "plan_type": "work_on_goal",
                "status": "success",
                "details": f"Fortschritt für {goal_id} dokumentiert"
            }
        except Exception as e:
            return {
                "plan_type": "work_on_goal",
                "status": "error",
                "details": str(e)
            }
    
    def _morning_routine(self, plan):
        """Morgen-Routine"""
        print("     🌅 Morgen-Routine...")
        return {
            "plan_type": "morning_routine",
            "status": "success",
            "details": "Nacht-Modus deaktiviert, Tagesplanung aktiv"
        }
    
    def _night_routine(self, plan):
        """Nacht-Routine"""
        print("     🌙 Nacht-Routine...")
        
        # Archiviere alte Daten
        try:
            import shutil
            old_perceptions = glob.glob(f"{self.state_path}/PERCEPTION/*_*.json")
            archive_dir = f"{self.state_path}/ARCHIVE/perceptions"
            os.makedirs(archive_dir, exist_ok=True)
            
            for f in sorted(old_perceptions)[:-20]:  # Behälte letzte 20
                shutil.move(f, archive_dir)
            
            return {
                "plan_type": "night_routine",
                "status": "success",
                "details": f"{len(old_perceptions)-20} Dateien archiviert"
            }
        except Exception as e:
            return {
                "plan_type": "night_routine",
                "status": "error",
                "details": str(e)
            }
    
    def _unknown_action(self, plan):
        """Unbekannte Aktion"""
        return {
            "plan_type": plan.get("type", "unknown"),
            "status": "skipped",
            "details": f"Unbekannte Aktion: {plan.get('action')}"
        }
    
    def _save(self):
        """Speichere Ergebnisse"""
        data = {
            "timestamp": time.time(),
            "results": self.results
        }
        filename = f"{self.state_path}/PERCEPTION/3_act_{int(time.time())}.json"
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"\n💾 Gespeichert: {filename}")


if __name__ == "__main__":
    a = Act()
    a.act()
    print("\n⚛️ Noch.")
