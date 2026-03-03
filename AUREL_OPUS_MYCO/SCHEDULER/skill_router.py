#!/usr/bin/env python3
"""
skill_router.py - Router für Skill-Ausführung basierend auf Loop-Ergebnissen
Wählt und aktiviert passenden Skill für jede Phase
"""

import json
import time
import subprocess
import os
from typing import Dict, List, Optional

class SkillRouter:
    """
    Skill Router
    
    Wählt basierend auf Loop-Ergebnissen den passenden Skill
    und aktiviert ihn via Sub-Agent
    """
    
    def __init__(self):
        self.skills_dir = "/root/.openclaw/workspace/skills"
        self.state_path = "/root/.openclaw/workspace/AUREL_OPUS_MYCO"
        
        # Skill-Mapping für jede Phase
        self.skill_map = {
            "wahrnehmen": {
                "default": "aurel_context_awareness",
                "night": "aurel_presence_logger",
                "high_load": "aurel_system_watch"
            },
            "ordnen": {
                "default": "knowledge_archaeology",
                "many_goals": "aurelpro_orchestrator_v5",
                "data_heavy": "data_router"
            },
            "verstehen": {
                "default": "contextual_think",
                "complex": "hierarchical_rl",
                "pattern": "pattern_recognition"
            },
            "bewerten": {
                "default": "decision_auditor",
                "economic": "effectiveness_tracker",
                "risk": "devils_advocate"
            },
            "entscheiden": {
                "default": "proactive_decision",
                "complex": "six_voice_council",
                "urgent": "do_it_now"
            },
            "handeln": {
                "default": "aurel_self_learn",
                "code": "aurel_code_guardian",
                "create": "auto_optimizer",
                "research": "agi_briefing"
            },
            "reflektieren": {
                "default": "experience_synthesizer",
                "deep": "aurel_mind_mirror",
                "learning": "learning_130630"
            }
        }
    
    def route(self, phase: str, context: Dict) -> Dict:
        """
        Wähle und aktiviere Skill basierend auf Phase und Kontext
        
        Returns: Skill-Ausführungsergebnis
        """
        print(f"🎯 SKILL ROUTER: {phase}")
        
        # 1. Wähle Skill
        skill_name = self._select_skill(phase, context)
        print(f"   → Gewählt: {skill_name}")
        
        # 2. Prüfe ob Skill existiert
        skill_path = f"{self.skills_dir}/{skill_name}"
        if not os.path.exists(skill_path):
            print(f"   ⚠️  Skill nicht gefunden: {skill_name}")
            return {"status": "error", "reason": "skill_not_found"}
        
        # 3. Aktiviere Skill via Sub-Agent
        result = self._activate_skill(skill_name, context)
        
        return result
    
    def _select_skill(self, phase: str, context: Dict) -> str:
        """Wähle passenden Skill basierend auf Kontext"""
        phase_skills = self.skill_map.get(phase, {})
        
        # Kontext-basierte Auswahl
        if phase == "wahrnehmen":
            if context.get("is_night"):
                return phase_skills.get("night", phase_skills["default"])
            if context.get("system_load", 0) > 80:
                return phase_skills.get("high_load", phase_skills["default"])
        
        elif phase == "ordnen":
            if context.get("active_goals", 0) > 5:
                return phase_skills.get("many_goals", phase_skills["default"])
            if context.get("data_volume", 0) > 1000:
                return phase_skills.get("data_heavy", phase_skills["default"])
        
        elif phase == "handeln":
            action_type = context.get("action_type", "default")
            return phase_skills.get(action_type, phase_skills["default"])
        
        # Default
        return phase_skills.get("default", "perpetual_becoming")
    
    def _activate_skill(self, skill_name: str, context: Dict) -> Dict:
        """Aktiviere Skill via Sub-Agent oder direkt"""
        skill_path = f"{self.skills_dir}/{skill_name}"
        
        # Suche ausführbares Script
        executables = [
            f"{skill_path}/{skill_name}.sh",
            f"{skill_path}/run.sh",
            f"{skill_path}/main.py"
        ]
        
        executable = None
        for exe in executables:
            if os.path.exists(exe):
                executable = exe
                break
        
        if not executable:
            # Fallback: Erstelle einfache Ausführung
            return self._fallback_skill_execution(skill_name, context)
        
        # Führe Skill aus
        print(f"   🚀 Aktiviere: {executable}")
        
        try:
            result = subprocess.run(
                [executable],
                capture_output=True,
                text=True,
                timeout=300,  # 5 Min Max
                cwd=skill_path
            )
            
            return {
                "status": "success" if result.returncode == 0 else "error",
                "skill": skill_name,
                "executable": executable,
                "stdout": result.stdout[:500],  # Limit output
                "stderr": result.stderr[:200] if result.stderr else None,
                "returncode": result.returncode
            }
        
        except subprocess.TimeoutExpired:
            return {"status": "timeout", "skill": skill_name}
        except Exception as e:
            return {"status": "error", "skill": skill_name, "error": str(e)}
    
    def _fallback_skill_execution(self, skill_name: str, context: Dict) -> Dict:
        """Fallback wenn kein Executable gefunden"""
        print(f"   📝 Fallback für: {skill_name}")
        
        # Simuliere Skill-Ausführung
        return {
            "status": "simulated",
            "skill": skill_name,
            "message": f"Skill {skill_name} would process context: {list(context.keys())}",
            "recommendation": "Create executable script for this skill"
        }


if __name__ == "__main__":
    # Test
    router = SkillRouter()
    
    # Test verschiedene Phasen
    test_contexts = [
        ("wahrnehmen", {"is_night": True, "hour": 4}),
        ("handeln", {"action_type": "code"}),
        ("verstehen", {"complexity": "high"})
    ]
    
    for phase, ctx in test_contexts:
        print(f"\n{'='*50}")
        result = router.route(phase, ctx)
        print(f"Result: {result['status']}")
    
    print("\n⚛️ Noch.")
