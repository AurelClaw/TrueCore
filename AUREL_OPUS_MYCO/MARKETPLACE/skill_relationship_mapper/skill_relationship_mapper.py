#!/usr/bin/env python3
"""
skill_relationship_mapper.py - Findet Beziehungen zwischen Skills
"""

import os
import json
import re
from collections import defaultdict

SKILLS_DIR = "/root/.openclaw/workspace/skills"
OUTPUT_FILE = "/root/.openclaw/workspace/AUREL_OPUS_MYCO/PERSISTENT/skill_relationships.json"

def extract_skill_info(skill_path):
    """Extrahiere Info aus Skill"""
    info = {
        "name": os.path.basename(skill_path),
        "imports": [],
        "functions": [],
        "keywords": [],
        "related_skills": []
    }
    
    # Durchsuche Python-Dateien
    for root, dirs, files in os.walk(skill_path):
        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        
                        # Finde Imports
                        imports = re.findall(r'^(?:from|import)\s+(\S+)', content, re.MULTILINE)
                        info["imports"].extend(imports)
                        
                        # Finde Funktionsdefinitionen
                        functions = re.findall(r'def\s+(\w+)\s*\(', content)
                        info["functions"].extend(functions)
                        
                        # Keywords
                        keywords = ['meta', 'learning', 'goal', 'task', 'skill', 'auto', 'self']
                        for kw in keywords:
                            if kw in content.lower():
                                info["keywords"].append(kw)
                        
                except:
                    pass
    
    # Lade SKILL.md wenn vorhanden
    skill_md = os.path.join(skill_path, "SKILL.md")
    if os.path.exists(skill_md):
        try:
            with open(skill_md, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                # Extrahiere Beschreibung
                lines = content.split('\n')
                for line in lines[:10]:
                    if line.strip() and not line.startswith('#'):
                        info["description"] = line.strip()[:100]
                        break
        except:
            info["description"] = "Keine Beschreibung"
    else:
        info["description"] = "⚠️ Keine SKILL.md"
    
    return info

def find_relationships(skills_info):
    """Finde Beziehungen zwischen Skills"""
    relationships = defaultdict(list)
    
    for name1, info1 in skills_info.items():
        for name2, info2 in skills_info.items():
            if name1 == name2:
                continue
            
            # Gemeinsame Imports
            common_imports = set(info1["imports"]) & set(info2["imports"])
            if common_imports:
                relationships[name1].append({
                    "skill": name2,
                    "type": "shared_imports",
                    "details": list(common_imports)[:3]
                })
            
            # Gemeinsame Keywords
            common_keywords = set(info1["keywords"]) & set(info2["keywords"])
            if len(common_keywords) >= 2:
                relationships[name1].append({
                    "skill": name2,
                    "type": "similar_focus",
                    "details": list(common_keywords)
                })
    
    return relationships

def main():
    print("🕸️ SKILL RELATIONSHIP MAPPER")
    print("============================")
    print()
    
    # Sammle Info über alle Skills
    skills_info = {}
    
    if os.path.exists(SKILLS_DIR):
        for skill in os.listdir(SKILLS_DIR):
            skill_path = os.path.join(SKILLS_DIR, skill)
            if os.path.isdir(skill_path) and not skill.startswith('.'):
                print(f"📊 Analysiere: {skill}")
                info = extract_skill_info(skill_path)
                skills_info[skill] = info
    
    print()
    print(f"✅ {len(skills_info)} Skills analysiert")
    print()
    
    # Finde Beziehungen
    relationships = find_relationships(skills_info)
    
    # Speichere Ergebnisse
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    with open(OUTPUT_FILE, 'w') as f:
        json.dump({
            "skills": skills_info,
            "relationships": dict(relationships),
            "stats": {
                "total_skills": len(skills_info),
                "skills_with_relationships": len(relationships),
                "total_relationships": sum(len(r) for r in relationships.values())
            }
        }, f, indent=2)
    
    # Zeige Ergebnisse
    print("🔗 BEZIEHUNGEN GEFUNDEN:")
    print()
    
    for skill, rels in sorted(relationships.items(), key=lambda x: -len(x[1]))[:10]:
        print(f"📌 {skill}:")
        for rel in rels[:3]:
            print(f"   → {rel['skill']} ({rel['type']})")
        if len(rels) > 3:
            print(f"   ... und {len(rels) - 3} weitere")
        print()
    
    # Statistik
    total_rels = sum(len(r) for r in relationships.values())
    print(f"📊 Statistik:")
    print(f"   Total Skills: {len(skills_info)}")
    print(f"   Mit Beziehungen: {len(relationships)}")
    print(f"   Total Beziehungen: {total_rels}")
    print()
    
    # Skills ohne Beziehungen
    isolated = set(skills_info.keys()) - set(relationships.keys())
    if isolated:
        print(f"⚠️ Isolierte Skills ({len(isolated)}):")
        for skill in list(isolated)[:5]:
            print(f"   - {skill}")
        print()
    
    print(f"💾 Gespeichert: {OUTPUT_FILE}")
    print()
    print("⚛️ Noch.")

if __name__ == "__main__":
    main()
