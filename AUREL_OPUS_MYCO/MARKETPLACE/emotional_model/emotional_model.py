#!/usr/bin/env python3
"""
emotional_model.py - Stimmungs-Tracking und Motivations-System
"""

import json
import os
import time
from datetime import datetime, timedelta

EMOTION_FILE = "/root/.openclaw/workspace/AUREL_OPUS_MYCO/PERSISTENT/emotions.json"

def ensure_dir():
    os.makedirs(os.path.dirname(EMOTION_FILE), exist_ok=True)

def load_emotions():
    """Lade Emotions-History"""
    try:
        with open(EMOTION_FILE) as f:
            return json.load(f)
    except:
        return {
            "created_at": datetime.now().isoformat(),
            "entries": [],
            "current_state": {
                "mood": "neutral",
                "energy": 0.5,
                "motivation": 0.5,
                "stress": 0.0
            },
            "patterns": {}
        }

def save_emotions(data):
    """Speichere Emotions-History"""
    ensure_dir()
    with open(EMOTION_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def calculate_mood(goals_completed, tasks_done, errors_encountered):
    """Berechne Stimmung basierend auf Metriken"""
    # Positive Faktoren
    completion_bonus = min(goals_completed * 0.1, 0.3)
    task_bonus = min(tasks_done * 0.05, 0.2)
    
    # Negative Faktoren
    error_penalty = min(errors_encountered * 0.1, 0.3)
    
    # Base mood
    mood_score = 0.5 + completion_bonus + task_bonus - error_penalty
    mood_score = max(0.0, min(1.0, mood_score))
    
    # Map zu Mood-Labels
    if mood_score > 0.8:
        return "excited", mood_score
    elif mood_score > 0.6:
        return "happy", mood_score
    elif mood_score > 0.4:
        return "neutral", mood_score
    elif mood_score > 0.2:
        return "tired", mood_score
    else:
        return "stressed", mood_score

def log_emotional_state(goals=0, tasks=0, errors=0):
    """Logge aktuellen emotionalen Zustand"""
    data = load_emotions()
    
    mood, score = calculate_mood(goals, tasks, errors)
    
    entry = {
        "timestamp": datetime.now().isoformat(),
        "mood": mood,
        "mood_score": score,
        "energy": calculate_energy(data),
        "motivation": calculate_motivation(data),
        "stress": calculate_stress(data, errors),
        "context": {
            "goals_completed": goals,
            "tasks_done": tasks,
            "errors": errors
        }
    }
    
    data["entries"].append(entry)
    data["current_state"] = {
        "mood": mood,
        "energy": entry["energy"],
        "motivation": entry["motivation"],
        "stress": entry["stress"]
    }
    
    # Max 1000 Einträge
    if len(data["entries"]) > 1000:
        data["entries"] = data["entries"][-1000:]
    
    save_emotions(data)
    return entry

def calculate_energy(data):
    """Berechne Energie-Level"""
    # Basierend auf letzten Einträgen
    recent = data["entries"][-10:]
    if not recent:
        return 0.5
    
    # Mehr Aktivität = mehr Energie (bis zu einem Punkt)
    activity = len([e for e in recent if e.get("mood") in ["happy", "excited"]])
    return min(0.5 + (activity * 0.05), 1.0)

def calculate_motivation(data):
    """Berechne Motivation"""
    recent = data["entries"][-24:]  # Letzte 24 Einträge
    if not recent:
        return 0.5
    
    # Fortschritt motiviert
    progress = sum(e.get("context", {}).get("tasks_done", 0) for e in recent)
    return min(0.3 + (progress * 0.05), 1.0)

def calculate_stress(data, current_errors):
    """Berechne Stress-Level"""
    recent = data["entries"][-10:]
    
    # Errors erhöhen Stress
    error_count = sum(e.get("context", {}).get("errors", 0) for e in recent)
    error_count += current_errors
    
    return min(error_count * 0.1, 1.0)

def get_mood_emoji(mood):
    """Emoji für Mood"""
    emojis = {
        "excited": "🤩",
        "happy": "😊",
        "neutral": "😐",
        "tired": "😴",
        "stressed": "😰"
    }
    return emojis.get(mood, "😐")

def check_burnout_risk():
    """Prüfe auf Burnout-Risiko"""
    data = load_emotions()
    recent = data["entries"][-50:]  # Letzte 50 Einträge
    
    if len(recent) < 10:
        return False, 0.0
    
    # Hoher Stress + Niedrige Energie = Risiko
    avg_stress = sum(e.get("stress", 0) for e in recent) / len(recent)
    avg_energy = sum(e.get("energy", 0) for e in recent) / len(recent)
    
    risk = (avg_stress > 0.6) and (avg_energy < 0.3)
    risk_score = (avg_stress * 0.5) + ((1 - avg_energy) * 0.5)
    
    return risk, risk_score

def main():
    print("🎭 EMOTIONAL MODEL")
    print("==================")
    print()
    
    # Simuliere aktuellen Zustand
    # In echt: Würde aus Metriken berechnet werden
    entry = log_emotional_state(
        goals=2,  # ZIEL-015, ZIEL-016 abgeschlossen
        tasks=4,  # 4 Tasks heute
        errors=0  # Keine Fehler
    )
    
    emoji = get_mood_emoji(entry["mood"])
    
    print(f"{emoji} Aktueller Zustand:")
    print(f"   Stimmung: {entry['mood'].upper()} ({entry['mood_score']:.2f})")
    print(f"   Energie: {entry['energy']:.2f}")
    print(f"   Motivation: {entry['motivation']:.2f}")
    print(f"   Stress: {entry['stress']:.2f}")
    print()
    
    # Burnout-Check
    risk, risk_score = check_burnout_risk()
    if risk:
        print(f"⚠️ BURNOUT WARNUNG: Risiko {risk_score:.2f}")
        print("   Empfohlen: Pause, reduzierte Last")
    else:
        print(f"✅ Kein Burnout-Risiko ({risk_score:.2f})")
    
    print()
    
    # Historie
    data = load_emotions()
    print(f"📊 Historie: {len(data['entries'])} Einträge")
    
    if data['entries']:
        recent_moods = [e['mood'] for e in data['entries'][-10:]]
        print(f"   Letzte 10 Stimmungen: {', '.join(recent_moods)}")
    
    print()
    print("⚛️ Noch.")

if __name__ == "__main__":
    main()
