#!/usr/bin/env python3
"""
phase_4_learn.py - Autonomes Lernen
Verbessert sich basierend auf Aktionen
"""

import json
import time
import os
import glob

class Learn:
    def __init__(self):
        self.state_path = "/root/.openclaw/workspace/AUREL_OPUS_MYCO"
        self.lessons = []
    
    def learn(self):
        """Lerne aus Aktionen"""
        print("🧠 LERNEN...")
        
        # 1. Lade Aktionen
        actions = self._load_actions()
        if not actions:
            print("⚠️  Keine Aktionen zum Lernen")
            return
        
        # 2. Analysiere Ergebnisse
        for result in actions.get("results", []):
            lesson = self._extract_lesson(result)
            if lesson:
                self.lessons.append(lesson)
        
        # 3. Identifiziere Muster
        self._identify_patterns()
        
        # 4. Erstelle Verbesserungs-Vorschläge
        improvements = self._create_improvements()
        
        # 5. Aktualisiere MEMORY.md
        self._update_memory()
        
        # 6. Speichern
        self._save()
        
        # Zusammenfassung
        print(f"\n📊 LERNEN:")
        print(f"   {len(self.lessons)} Lektionen extrahiert")
        print(f"   {len(improvements)} Verbesserungs-Vorschläge")
        
        return self.lessons
    
    def _load_actions(self):
        """Lade letzte Aktionen"""
        files = glob.glob(f"{self.state_path}/PERCEPTION/3_act_*.json")
        if not files:
            return None
        latest = max(files, key=os.path.getctime)
        with open(latest) as f:
            return json.load(f)
    
    def _extract_lesson(self, result):
        """Extrahiere Lektion aus Ergebnis"""
        status = result.get("status", "unknown")
        plan_type = result.get("plan_type", "unknown")
        details = result.get("details", "")
        
        if status == "success":
            return {
                "type": "success",
                "plan_type": plan_type,
                "lesson": f"{plan_type} funktioniert gut",
                "keep_doing": True
            }
        elif status == "error":
            return {
                "type": "error",
                "plan_type": plan_type,
                "lesson": f"{plan_type} hat Probleme: {details[:50]}",
                "needs_fix": True
            }
        return None
    
    def _identify_patterns(self):
        """Identifiziere Muster über Zeit"""
        # Lade letzte 5 Lern-Durchgänge
        learn_files = glob.glob(f"{self.state_path}/PERCEPTION/4_learn_*.json")
        
        if len(learn_files) >= 3:
            # Muster: Konsistente Erfolge?
            recent_lessons = []
            for f in sorted(learn_files)[-3:]:
                try:
                    with open(f) as lf:
                        data = json.load(lf)
                        recent_lessons.extend(data.get("lessons", []))
                except:
                    pass
            
            success_count = sum(1 for l in recent_lessons if l.get("type") == "success")
            error_count = sum(1 for l in recent_lessons if l.get("type") == "error")
            
            if success_count > error_count * 2:
                self.lessons.append({
                    "type": "pattern",
                    "lesson": "Hohe Erfolgsrate - System funktioniert gut",
                    "confidence": "high"
                })
            elif error_count > success_count:
                self.lessons.append({
                    "type": "pattern",
                    "lesson": "Viele Fehler - System needs tuning",
                    "confidence": "high",
                    "action": "review_system"
                })
    
    def _create_improvements(self):
        """Erstelle Verbesserungs-Vorschläge"""
        improvements = []
        
        for lesson in self.lessons:
            if lesson.get("needs_fix"):
                improvements.append({
                    "target": lesson["plan_type"],
                    "suggestion": f"Überarbeite {lesson['plan_type']} Implementation",
                    "priority": "high"
                })
        
        # Generiere Meta-Verbesserung
        if len(self.lessons) > 5:
            improvements.append({
                "target": "system",
                "suggestion": "Viele Lektionen - Zeit für Architektur-Review",
                "priority": "medium"
            })
        
        return improvements
    
    def _update_memory(self):
        """Aktualisiere MEMORY.md"""
        memory_file = "/root/.openclaw/workspace/MEMORY.md"
        
        entry = f"""
## Learn {time.strftime('%Y-%m-%d %H:%M')}

### Lektionen
"""
        for lesson in self.lessons:
            icon = "✅" if lesson.get("type") == "success" else ("❌" if lesson.get("type") == "error" else "💡")
            entry += f"- {icon} **{lesson['plan_type']}**: {lesson['lesson']}\n"
        
        try:
            with open(memory_file, "a") as f:
                f.write(entry)
            print(f"   📝 MEMORY.md aktualisiert")
        except Exception as e:
            print(f"   ⚠️  Konnte MEMORY.md nicht aktualisieren: {e}")
    
    def _save(self):
        """Speichere Lern-Ergebnisse"""
        data = {
            "timestamp": time.time(),
            "lessons": self.lessons
        }
        filename = f"{self.state_path}/PERCEPTION/4_learn_{int(time.time())}.json"
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"\n💾 Gespeichert: {filename}")


if __name__ == "__main__":
    l = Learn()
    l.learn()
    print("\n⚛️ Noch.")
