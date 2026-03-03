#!/usr/bin/env python3
"""
aurel_output.py - Bilingual Output Formatter für Aurel Opus Myco
Deutsch/English + "Noch." Signature
"""

from typing import Dict, List, Optional
from dataclasses import dataclass

@dataclass
class AurelResponse:
    """Strukturierte Aurel-Antwort"""
    de: str           # Deutsch
    en: str           # English
    signature: bool = True  # "Noch." anhängen
    metadata: Optional[Dict] = None

class AurelOutput:
    """
    Bilingual Output Formatter
    
    Features:
    - Automatische Deutsch/English Ausgabe
    - "Noch." Signature
    - Kontextabhängige Sprachwahl
    - Technical/Conversational Modi
    """
    
    def __init__(self, preferred_lang: str = "de"):
        self.preferred_lang = preferred_lang
        self.signature = "⚛️ Noch."
        self.signature_en = "⚛️ Still becoming."
    
    def format(self, response: AurelResponse, mode: str = "bilingual") -> str:
        """
        Formatiere Antwort
        
        Modes:
        - "bilingual": DE dann EN
        - "de": Nur Deutsch
        - "en": Nur English
        - "technical": Kurz, präzise
        - "conversational": Natürlicher Flow
        """
        if mode == "bilingual":
            output = f"{response.de}\n\n---\n\n{response.en}"
        elif mode == "de":
            output = response.de
        elif mode == "en":
            output = response.en
        elif mode == "technical":
            # Kurz, bullet points
            output = self._technical_format(response)
        elif mode == "conversational":
            # Natürlicher, fließender Text
            output = response.de if self.preferred_lang == "de" else response.en
        else:
            output = response.de
        
        # Add signature
        if response.signature:
            output += f"\n\n{self.signature}"
        
        return output
    
    def _technical_format(self, response: AurelResponse) -> str:
        """Technical Format: Kurz, prägnant"""
        # Extrahiere Key Points
        de_lines = response.de.split('\n')
        
        # Filtere nur wichtige Zeilen (mit ✅, 📊, etc.)
        key_lines = [l for l in de_lines if any(e in l for e in ['✅', '❌', '📊', '🎯', '→'])]
        
        return '\n'.join(key_lines[:10])  # Max 10 lines
    
    def status_report(self, components: Dict[str, bool], phase: str) -> AurelResponse:
        """Generiere Status Report"""
        
        # Deutsch
        de_lines = [f"🎯 **Phase {phase} Status**", ""]
        for name, status in components.items():
            emoji = "✅" if status else "❌"
            de_lines.append(f"{emoji} {name}")
        
        de = '\n'.join(de_lines)
        
        # English
        en_lines = [f"🎯 **Phase {phase} Status**", ""]
        for name, status in components.items():
            emoji = "✅" if status else "❌"
            en_lines.append(f"{emoji} {name}")
        
        en = '\n'.join(en_lines)
        
        return AurelResponse(de=de, en=en)
    
    def decision_output(self, decision: str, reasoning: str, confidence: float) -> AurelResponse:
        """Formatiere Entscheidung"""
        
        de = f"""📋 **Entscheidung**

**{decision}**

Begründung: {reasoning}
Konfidenz: {confidence:.0%}"""
        
        en = f"""📋 **Decision**

**{decision}**

Reasoning: {reasoning}
Confidence: {confidence:.0%}"""
        
        return AurelResponse(de=de, en=en)
    
    def progress_update(self, goal: str, current: float, target: float, unit: str = "%") -> AurelResponse:
        """Formatiere Fortschritts-Update"""
        
        progress = (current / target * 100) if target > 0 else 0
        
        de = f"""📊 **Fortschritt: {goal}**

{current:.1f} / {target:.1f} {unit} ({progress:.1f}%)

{'🎯 Ziel erreicht!' if progress >= 100 else '⏳ In Arbeit...'}"""
        
        en = f"""📊 **Progress: {goal}**

{current:.1f} / {target:.1f} {unit} ({progress:.1f}%)

{'🎯 Goal achieved!' if progress >= 100 else '⏳ In progress...'}"""
        
        return AurelResponse(de=de, en=en)
    
    def system_message(self, message_type: str, details: Dict) -> AurelResponse:
        """Formatiere System-Message"""
        
        if message_type == "phase_complete":
            phase = details.get("phase", "Unknown")
            
            de = f"""✅ **Phase {phase} Abgeschlossen**

Alle Komponenten erfolgreich implementiert.
System bereit für nächste Phase."""
            
            en = f"""✅ **Phase {phase} Complete**

All components successfully implemented.
System ready for next phase."""
            
            return AurelResponse(de=de, en=en)
        
        elif message_type == "error":
            error = details.get("error", "Unknown error")
            
            de = f"""❌ **Fehler**

{error}

Rollback wird eingeleitet..."""
            
            en = f"""❌ **Error**

{error}

Initiating rollback..."""
            
            return AurelResponse(de=de, en=en)
        
        return AurelResponse(de="Unknown message type", en="Unknown message type")


# Global instance for easy access
aurel = AurelOutput(preferred_lang="de")


def respond(de: str, en: str = "", mode: str = "bilingual") -> str:
    """Shortcut für schnelle Antworten"""
    if not en:
        en = de  # Fallback
    
    response = AurelResponse(de=de, en=en)
    return aurel.format(response, mode)


if __name__ == "__main__":
    # Demo
    print("=" * 60)
    print("📝 AUREL OUTPUT FORMATTER DEMO")
    print("=" * 60)
    
    # Test 1: Status Report
    print("\n1. Status Report (bilingual):")
    print("-" * 40)
    components = {
        "Event Bus": True,
        "Token Economy": True,
        "Perception": True,
        "Bayes-World": True
    }
    report = aurel.status_report(components, "2")
    print(aurel.format(report, "bilingual"))
    
    # Test 2: Decision
    print("\n2. Decision Output:")
    print("-" * 40)
    decision = aurel.decision_output(
        decision="APPROVE",
        reasoning="Low risk, high value",
        confidence=0.95
    )
    print(aurel.format(decision, "de"))
    
    # Test 3: Progress
    print("\n3. Progress Update:")
    print("-" * 40)
    progress = aurel.progress_update("$100 MRR", 0, 100, "$")
    print(aurel.format(progress, "bilingual"))
    
    # Test 4: Technical Format
    print("\n4. Technical Format:")
    print("-" * 40)
    tech_response = AurelResponse(
        de="""✅ Phase 2 Complete

📊 Components:
✅ Event Bus - Priority queues
✅ Token Economy - value/cost scoring
✅ Perception - Intent classification
✅ Bayes-World - Single Source of Truth

→ Next: Phase 3""",
        en="Phase 2 Complete"
    )
    print(aurel.format(tech_response, "technical"))
    
    # Test 5: Shortcut
    print("\n5. Shortcut Function:")
    print("-" * 40)
    print(respond("Hallo Welt", "Hello World"))
    
    print("\n" + "=" * 60)
    print("✅ Aurel Output demo complete")
    print("⚛️ Noch.")
