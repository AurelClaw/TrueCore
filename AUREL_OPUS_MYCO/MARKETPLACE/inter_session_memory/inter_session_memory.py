#!/usr/bin/env python3
"""
inter_session_memory.py - Wissen über mehrere Sessions/Chats hinweg
"""

import json
import os
import time
from datetime import datetime, timedelta

MEMORY_FILE = "/root/.openclaw/workspace/AUREL_OPUS_MYCO/PERSISTENT/memory.json"

def ensure_dir():
    os.makedirs(os.path.dirname(MEMORY_FILE), exist_ok=True)

def load_persistent_memory():
    """Lade persistentes Memory"""
    try:
        with open(MEMORY_FILE) as f:
            return json.load(f)
    except:
        return {
            "created_at": datetime.now().isoformat(),
            "sessions": [],
            "key_insights": [],
            "goals_progress": {},
            "relationships": {},
            "last_updated": time.time()
        }

def save_persistent_memory(memory):
    """Speichere persistentes Memory"""
    ensure_dir()
    memory["last_updated"] = time.time()
    with open(MEMORY_FILE, 'w') as f:
        json.dump(memory, f, indent=2)

def add_session_context(session_id, context):
    """Füge Session-Kontext hinzu"""
    memory = load_persistent_memory()
    
    session = {
        "id": session_id,
        "timestamp": datetime.now().isoformat(),
        "context": context,
        "key_points": extract_key_points(context)
    }
    
    memory["sessions"].append(session)
    
    # Halte nur letzte 50 Sessions
    if len(memory["sessions"]) > 50:
        memory["sessions"] = memory["sessions"][-50:]
    
    save_persistent_memory(memory)
    print(f"💾 Session {session_id[:8]}... gespeichert")

def extract_key_points(context):
    """Extrahiere wichtige Punkte aus Kontext"""
    # Simplifizierte Version - in echt: NLP/LLM
    key_points = []
    
    if "ZIEL" in context:
        key_points.append("Ziel-Diskussion")
    if "Skill" in context:
        key_points.append("Skill-Entwicklung")
    if "Fehler" in context or "Error" in context:
        key_points.append("Problembehandlung")
    if "Erfolg" in context or "✅" in context:
        key_points.append("Erfolg")
    
    return key_points

def add_key_insight(insight, category="general"):
    """Füge wichtige Erkenntnis hinzu"""
    memory = load_persistent_memory()
    
    memory["key_insights"].append({
        "timestamp": datetime.now().isoformat(),
        "insight": insight,
        "category": category
    })
    
    # Halte nur letzte 100 Insights
    if len(memory["key_insights"]) > 100:
        memory["key_insights"] = memory["key_insights"][-100:]
    
    save_persistent_memory(memory)
    print(f"💡 Insight gespeichert: {insight[:50]}...")

def get_relevant_context(query, max_age_hours=24):
    """Hole relevanten Kontext basierend auf Query"""
    memory = load_persistent_memory()
    
    cutoff = time.time() - (max_age_hours * 3600)
    
    relevant = []
    
    # Suche in Sessions
    for session in memory["sessions"]:
        if session.get("timestamp", 0) > cutoff:
            # Simplifizierte Relevanz-Prüfung
            if any(word in session.get("context", "") for word in query.split()):
                relevant.append(session)
    
    # Suche in Insights
    for insight in memory["key_insights"]:
        if insight.get("timestamp", 0) > cutoff:
            if any(word in insight.get("insight", "") for word in query.split()):
                relevant.append(insight)
    
    return relevant[:5]  # Max 5 relevante Einträge

def show_memory_summary():
    """Zeige Memory-Zusammenfassung"""
    memory = load_persistent_memory()
    
    print("🧠 INTER-SESSION MEMORY")
    print("======================")
    print()
    print(f"   Erstellt: {memory['created_at'][:10]}")
    print(f"   Sessions: {len(memory['sessions'])}")
    print(f"   Insights: {len(memory['key_insights'])}")
    print()
    
    # Letzte 3 Insights
    if memory['key_insights']:
        print("💡 Letzte Erkenntnisse:")
        for insight in memory['key_insights'][-3:]:
            print(f"   - {insight['insight'][:60]}...")
        print()
    
    # Letzte 3 Sessions
    if memory['sessions']:
        print("💾 Letzte Sessions:")
        for session in memory['sessions'][-3:]:
            print(f"   - {session['id'][:8]}... ({session['timestamp'][:16]})")
        print()
    
    print("⚛️ Noch.")

def main():
    # Zeige aktuellen Memory-Status
    show_memory_summary()
    
    # Beispiel: Füge aktuelle Session hinzu
    add_key_insight(
        "Phase 3 Implementierung: Code-Ausführung, Inter-Session Memory, Langzeit-Planung",
        "milestone"
    )

if __name__ == "__main__":
    main()
