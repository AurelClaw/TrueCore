#!/usr/bin/env python3
"""
auto_skill_activator.py - Aktiviert relevante Skills basierend auf aktivem Ziel
"""

import json
import os
from datetime import datetime

RELATIONSHIPS_FILE = "/root/.openclaw/workspace/AUREL_OPUS_MYCO/PERSISTENT/skill_relationships.json"
CURRENT_GOAL_FILE = "/root/.openclaw/workspace/AUREL_OPUS_MYCO/TRIGGERS/current_goal.json"
ACTIVE_SKILLS_FILE = "/root/.openclaw/workspace/AUREL_OPUS_MYCO/TRIGGERS/active_skills.json"

def load_relationships():
    """Lade Skill-Beziehungen"""
    try:
        with open(RELATIONSHIPS_FILE) as f:
            return json.load(f)
    except:
        return {"skills": {}, "relationships": {}}

def load_current_goal():
    """Lade aktuelles Ziel"""
    try:
        with open(CURRENT_GOAL_FILE) as f:
            return json.load(f)
    except:
        return {"id": "ZIEL-017"}

def find_relevant_skills(goal_id, relationships):
    """Finde Skills, die zum aktuellen Ziel passen"""
    relevant = []
    
    # Extrahiere Keywords aus Ziel-ID
    goal_keywords = {
        "ZIEL-015": ["meta", "learning", "adaptive", "database", "task"],
        "ZIEL-016": ["architektur", "exploration", "neu", "pattern", "auto"],
        "ZIEL-017": ["world", "model", "simulation", "prediction", "state"],
        "ZIEL-018": ["architektur", "alternative", "emergent", "pattern"]
    }
    
    keywords = goal_keywords.get(goal_id, ["auto", "self", "learning"])
    
    # Suche Skills mit passenden Keywords
    for skill_name, skill_info in relationships.get("skills", {}).items():
        skill_keywords = skill_info.get("keywords", [])
        skill_funcs = ' '.join(skill_info.get("functions", []))
        
        # Prüfe Überschneidung in Keywords
        matches = set(keywords) & set(skill_keywords)
        
        # Prüfe auch Funktionsnamen
        for kw in keywords:
            if kw in skill_funcs.lower():
                matches.add(kw)
        
        # Prüche Skill-Namen
        for kw in keywords:
            if kw in skill_name.lower():
                matches.add(kw)
        
        if len(matches) >= 1:
            relevant.append({
                "name": skill_name,
                "matches": list(matches),
                "description": skill_info.get("description", "Keine Beschreibung")[:60],
                "functions": skill_info.get("functions", [])[:3]
            })
    
    # Sortiere nach Relevanz
    relevant.sort(key=lambda x: -len(x["matches"]))
    
    return relevant[:10]  # Top 10

def activate_skills(skills):
    """Aktiviere Skills (speichere in Datei)"""
    activation = {
        "timestamp": datetime.now().isoformat(),
        "active_skills": [s["name"] for s in skills],
        "details": skills
    }
    
    os.makedirs(os.path.dirname(ACTIVE_SKILLS_FILE), exist_ok=True)
    with open(ACTIVE_SKILLS_FILE, 'w') as f:
        json.dump(activation, f, indent=2)
    
    return activation

def main():
    print("🚀 AUTO SKILL ACTIVATOR")
    print("========================")
    print()
    
    # Lade Daten
    goal = load_current_goal()
    relationships = load_relationships()
    
    print(f"🎯 Aktuelles Ziel: {goal['id']}")
    print()
    
    # Finde relevante Skills
    relevant = find_relevant_skills(goal['id'], relationships)
    
    if relevant:
        print(f"✅ {len(relevant)} relevante Skills gefunden:")
        print()
        
        for skill in relevant[:5]:
            print(f"📌 {skill['name']}")
            print(f"   Matches: {', '.join(skill['matches'])}")
            print(f"   {skill['description']}...")
            print()
        
        # Aktiviere Skills
        activation = activate_skills(relevant)
        
        print(f"💾 {len(activation['active_skills'])} Skills aktiviert")
        print(f"📁 Gespeichert: {ACTIVE_SKILLS_FILE}")
    else:
        print("⚠️ Keine relevanten Skills gefunden")
    
    print()
    print("⚛️ Noch.")

if __name__ == "__main__":
    main()
