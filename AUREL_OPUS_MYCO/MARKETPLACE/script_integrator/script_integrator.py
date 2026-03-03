#!/usr/bin/env python3
"""
script_integrator.py - Integriert erstellte Scripts automatisch ins System
- Indexiert neue Scripts
- Fügt sie zum Skill-System hinzu
- Aktiviert sie für automatische Ausführung
"""

import json
import os
import shutil
from datetime import datetime

class ScriptIntegrator:
    def __init__(self):
        self.base_path = "/root/.openclaw/workspace/AUREL_OPUS_MYCO"
        self.skills_path = "/root/.openclaw/workspace/skills"
        self.index_file = f"{self.base_path}/SYSTEM/script_index.json"
        
    def integrate_scripts(self):
        """Haupt-Funktion: Integriere alle neuen Scripts"""
        print("🔧 SCRIPT INTEGRATOR: Starte...")
        
        # 1. Lade aktuellen Index
        index = self._load_index()
        
        # 2. Finde neue Scripts in SCHEDULER/
        new_scripts = self._find_new_scripts(index)
        
        # 3. Integriere jedes Script
        for script in new_scripts:
            print(f"\n   📄 Gefunden: {script['name']}")
            
            # Kopiere zu skills/
            skill_path = self._create_skill(script)
            
            # Füge zu Index hinzu
            index["scripts"].append({
                "name": script["name"],
                "source": script["path"],
                "skill_path": skill_path,
                "integrated_at": datetime.now().isoformat(),
                "status": "active"
            })
            
            print(f"   ✅ Integriert als Skill: {skill_path}")
        
        # 4. Speichere Index
        self._save_index(index)
        
        # 5. Aktualisiere SYSTEM-Registry
        self._update_system_registry()
        
        print(f"\n📊 ZUSAMMENFASSUNG:")
        print(f"   Neue Scripts: {len(new_scripts)}")
        print(f"   Total im Index: {len(index['scripts'])}")
        print(f"   System-Registry: Aktualisiert")
        
        return len(new_scripts)
    
    def _load_index(self):
        """Lade Script-Index"""
        try:
            with open(self.index_file) as f:
                return json.load(f)
        except:
            return {"scripts": [], "last_updated": datetime.now().isoformat()}
    
    def _save_index(self, index):
        """Speichere Script-Index"""
        os.makedirs(os.path.dirname(self.index_file), exist_ok=True)
        index["last_updated"] = datetime.now().isoformat()
        with open(self.index_file, 'w') as f:
            json.dump(index, f, indent=2)
    
    def _find_new_scripts(self, index):
        """Finde neue Scripts die noch nicht indexiert sind"""
        scheduler_path = f"{self.base_path}/SCHEDULER"
        indexed_names = {s["name"] for s in index["scripts"]}
        
        new_scripts = []
        
        if not os.path.exists(scheduler_path):
            return new_scripts
        
        for filename in os.listdir(scheduler_path):
            if filename.endswith('.py') or filename.endswith('.sh'):
                if filename not in indexed_names:
                    new_scripts.append({
                        "name": filename,
                        "path": f"{scheduler_path}/{filename}",
                        "type": "python" if filename.endswith('.py') else "shell"
                    })
        
        return new_scripts
    
    def _create_skill(self, script):
        """Erstelle Skill aus Script"""
        skill_name = script["name"].replace('.py', '').replace('.sh', '')
        skill_dir = f"{self.skills_path}/{skill_name}"
        
        os.makedirs(skill_dir, exist_ok=True)
        
        # Kopiere Script
        dest_path = f"{skill_dir}/{script['name']}"
        shutil.copy2(script["path"], dest_path)
        
        # Erstelle SKILL.md
        skill_md = f"""# {skill_name}

## Beschreibung
Automatisch generierter Skill aus Ziel-Management-System.

## Quelle
Original: {script["path"]}
Integriert: {datetime.now().strftime('%Y-%m-%d %H:%M')}

## Verwendung
```bash
python3 {script['name']}
```

## Status
🔄 Aktiv
"""
        
        with open(f"{skill_dir}/SKILL.md", 'w') as f:
            f.write(skill_md)
        
        return skill_dir
    
    def _update_system_registry(self):
        """Aktualisiere System-Registry"""
        registry_file = f"{self.base_path}/SYSTEM/registry.json"
        
        try:
            with open(registry_file) as f:
                registry = json.load(f)
        except:
            registry = {"components": [], "version": "1.0.0"}
        
        # Füge Script-Integrator hinzu falls nicht vorhanden
        if "script_integrator" not in {c["name"] for c in registry["components"]}:
            registry["components"].append({
                "name": "script_integrator",
                "type": "automation",
                "status": "active",
                "last_run": datetime.now().isoformat()
            })
        
        os.makedirs(os.path.dirname(registry_file), exist_ok=True)
        with open(registry_file, 'w') as f:
            json.dump(registry, f, indent=2)


if __name__ == "__main__":
    integrator = ScriptIntegrator()
    count = integrator.integrate_scripts()
    
    if count > 0:
        print(f"\n✅ {count} neue Script(s) integriert!")
    else:
        print("\n⏳ Keine neuen Scripts gefunden.")
    
    print("\n⚛️ Noch.")
