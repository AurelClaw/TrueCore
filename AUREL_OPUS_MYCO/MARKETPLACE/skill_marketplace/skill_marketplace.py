#!/usr/bin/env python3
"""
skill_marketplace.py - Export/Import von Skills für andere Agents
"""

import json
import os
import shutil
from datetime import datetime

SKILLS_DIR = "/root/.openclaw/workspace/skills"
MARKETPLACE_DIR = "/root/.openclaw/workspace/AUREL_OPUS_MYCO/MARKETPLACE"

def ensure_dir():
    os.makedirs(MARKETPLACE_DIR, exist_ok=True)

def package_skill(skill_name):
    """Packe Skill für Marketplace"""
    skill_path = os.path.join(SKILLS_DIR, skill_name)
    
    if not os.path.exists(skill_path):
        print(f"❌ Skill {skill_name} nicht gefunden")
        return None
    
    # Erstelle Package
    package_dir = os.path.join(MARKETPLACE_DIR, skill_name)
    ensure_dir()
    
    if os.path.exists(package_dir):
        shutil.rmtree(package_dir)
    
    shutil.copytree(skill_path, package_dir)
    
    # Erstelle Manifest
    manifest = {
        "name": skill_name,
        "version": "1.0.0",
        "created_at": datetime.now().isoformat(),
        "author": "Aurel",
        "description": load_skill_description(skill_path),
        "files": os.listdir(skill_path),
        "dependencies": [],
        "tags": ["aurel", "auto-generated"]
    }
    
    with open(os.path.join(package_dir, "manifest.json"), 'w') as f:
        json.dump(manifest, f, indent=2)
    
    # Erstelle ZIP
    zip_path = os.path.join(MARKETPLACE_DIR, f"{skill_name}.zip")
    shutil.make_archive(
        os.path.join(MARKETPLACE_DIR, skill_name),
        'zip',
        package_dir
    )
    
    print(f"📦 Skill {skill_name} gepackt")
    return zip_path

def load_skill_description(skill_path):
    """Lade Skill-Beschreibung"""
    try:
        with open(os.path.join(skill_path, "SKILL.md")) as f:
            content = f.read()
            # Extrahiere erste Zeile als Beschreibung
            lines = content.split('\n')
            for line in lines:
                if line.strip() and not line.startswith('#'):
                    return line.strip()[:100]
    except:
        pass
    return "Keine Beschreibung verfügbar"

def list_available_skills():
    """Liste verfügbare Skills im Marketplace"""
    ensure_dir()
    
    skills = []
    for item in os.listdir(MARKETPLACE_DIR):
        if item.endswith('.zip'):
            skill_name = item.replace('.zip', '')
            manifest_path = os.path.join(MARKETPLACE_DIR, skill_name, "manifest.json")
            
            if os.path.exists(manifest_path):
                with open(manifest_path) as f:
                    manifest = json.load(f)
                    skills.append(manifest)
    
    return skills

def import_skill(zip_path, target_dir=SKILLS_DIR):
    """Importiere Skill aus ZIP"""
    if not os.path.exists(zip_path):
        print(f"❌ ZIP nicht gefunden: {zip_path}")
        return False
    
    # Extrahiere
    import zipfile
    skill_name = os.path.basename(zip_path).replace('.zip', '')
    extract_dir = os.path.join(target_dir, skill_name)
    
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_dir)
    
    print(f"📥 Skill {skill_name} importiert nach {extract_dir}")
    return True

def main():
    print("🏪 SKILL MARKETPLACE")
    print("====================")
    print()
    
    # Packe alle eigenen Skills
    packaged = []
    if os.path.exists(SKILLS_DIR):
        for skill in os.listdir(SKILLS_DIR):
            skill_path = os.path.join(SKILLS_DIR, skill)
            if os.path.isdir(skill_path) and not skill.startswith('.'):
                result = package_skill(skill)
                if result:
                    packaged.append(skill)
    
    print()
    print(f"✅ {len(packaged)} Skills gepackt")
    
    # Liste verfügbare Skills
    available = list_available_skills()
    print(f"📦 {len(available)} Skills im Marketplace verfügbar")
    
    print()
    print("🌐 Für andere Agents:")
    print(f"   Export: {MARKETPLACE_DIR}")
    print("   Format: ZIP mit manifest.json")
    print()
    print("⚛️ Noch.")

if __name__ == "__main__":
    main()
