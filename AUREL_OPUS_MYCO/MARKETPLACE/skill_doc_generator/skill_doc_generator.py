#!/usr/bin/env python3
"""
skill_doc_generator.py - Generiert fehlende SKILL.md automatisch
"""

import os
import json
from datetime import datetime

SKILLS_DIR = "/root/.openclaw/workspace/skills"

def analyze_skill(skill_path):
    """Analysiere Skill-Inhalt"""
    info = {
        "scripts": [],
        "functions": [],
        "purpose": "",
        "has_readme": False
    }
    
    # Suche Scripts
    for root, dirs, files in os.walk(skill_path):
        for file in files:
            if file.endswith('.py'):
                info["scripts"].append(file)
                # Extrahiere Funktionsnamen
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, 'r') as f:
                        content = f.read()
                        if 'def ' in content:
                            import re
                            funcs = re.findall(r'def\s+(\w+)\s*\(', content)
                            info["functions"].extend(funcs[:5])  # Max 5
                except:
                    pass
            elif file == "README.md":
                info["has_readme"] = True
    
    return info

def generate_skill_md(skill_name, info):
    """Generiere SKILL.md Inhalt"""
    
    # Versuche Zweck zu erraten
    purpose_hints = {
        "status": "Status-Überwachung und Reporting",
        "goal": "Ziel-Management und Tracking",
        "task": "Task-Verwaltung und Ausführung",
        "learn": "Lernen und Selbstverbesserung",
        "phase": "Phasen-basierte Ausführung",
        "pattern": "Mustererkennung und Analyse",
        "auto": "Automatisierung",
        "self": "Selbst-referenzielle Systeme",
        "meta": "Meta-Learning und Optimierung"
    }
    
    purpose = "Skill für autonome Agenten-Funktionalität"
    for key, hint in purpose_hints.items():
        if key in skill_name.lower():
            purpose = hint
            break
    
    md_content = f"""# {skill_name}

## Beschreibung
{purpose}

## Funktionen
"""
    
    if info["functions"]:
        for func in info["functions"][:5]:
            md_content += f"- `{func}()`\n"
    else:
        md_content += "- Hauptfunktionalität\n"
    
    md_content += f"""
## Scripts
"""
    
    for script in info["scripts"][:5]:
        md_content += f"- `{script}`\n"
    
    md_content += f"""
## Verwendung
```python
# Importiere Skill
from {skill_name} import main

# Führe aus
main()
```

## Abhängigkeiten
- Python 3.8+
- Siehe requirements.txt (falls vorhanden)

## Erstellt
Automatisch generiert am {datetime.now().strftime('%Y-%m-%d %H:%M')}

---
⚛️ Noch
"""
    
    return md_content

def main():
    print("📝 SKILL DOC GENERATOR")
    print("=======================")
    print()
    
    generated = 0
    existing = 0
    
    if os.path.exists(SKILLS_DIR):
        for skill in os.listdir(SKILLS_DIR):
            skill_path = os.path.join(SKILLS_DIR, skill)
            
            if not os.path.isdir(skill_path) or skill.startswith('.'):
                continue
            
            skill_md = os.path.join(skill_path, "SKILL.md")
            
            if os.path.exists(skill_md):
                existing += 1
                continue
            
            # Generiere SKILL.md
            print(f"🆕 Generiere: {skill}/SKILL.md")
            
            info = analyze_skill(skill_path)
            content = generate_skill_md(skill, info)
            
            with open(skill_md, 'w') as f:
                f.write(content)
            
            generated += 1
    
    print()
    print(f"✅ {generated} SKILL.md generiert")
    print(f"📄 {existing} bereits vorhanden")
    print(f"📊 Total: {generated + existing} Skills")
    print()
    print("⚛️ Noch.")

if __name__ == "__main__":
    main()
