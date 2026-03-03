#!/usr/bin/env python3
"""
six_voice_plugin.py - 6-Voice Council als Plugin für Aurel Opus Myco
6 Stimmen: Logic, Ethics, Creativity, Safety, Efficiency, User
"""

import json
import time
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

class VoiceType(Enum):
    """6 Voice Types"""
    LOGIC = "logic"           # Rationalität, Konsistenz
    ETHICS = "ethics"         # Moral, Fairness
    CREATIVITY = "creativity" # Innovation, Out-of-box
    SAFETY = "safety"         # Risiko, Schutz
    EFFICIENCY = "efficiency" # Ressourcen, Optimierung
    USER = "user"             # Menschliche Präferenzen

@dataclass
class VoiceOpinion:
    """Meinung einer Stimme"""
    voice: VoiceType
    stance: str  # "approve", "reject", "concern"
    confidence: float  # 0.0 - 1.0
    reasoning: str
    conditions: List[str]  # Bedingungen für Approval

@dataclass
class CouncilDecision:
    """Entscheidung des Councils"""
    consensus: bool
    decision: str  # "approve", "reject", "conditional"
    confidence: float
    majority_voices: List[VoiceType]
    minority_voices: List[VoiceType]
    concerns: List[str]
    recommendations: List[str]

class SixVoiceCouncil:
    """
    6-Voice Council Plugin
    
    Features:
    - 6 spezialisierte Stimmen
    - Weighted voting
    - Consensus building
    - Conditional approvals
    """
    
    def __init__(self, state_path: str = "/root/.openclaw/workspace/AUREL_OPUS_MYCO"):
        self.state_path = state_path
        self.voices = list(VoiceType)
        self.voice_weights = {
            VoiceType.LOGIC: 1.0,
            VoiceType.ETHICS: 1.0,
            VoiceType.CREATIVITY: 0.8,
            VoiceType.SAFETY: 1.2,  # Safety hat mehr Gewicht
            VoiceType.EFFICIENCY: 1.0,
            VoiceType.USER: 1.1       # User preference wichtig
        }
        self.decision_history = []
    
    def deliberate(self, proposal: Dict, context: Dict) -> CouncilDecision:
        """
        Führe Council-Deliberation durch
        
        Returns: CouncilDecision mit Konsens/Mehrheit
        """
        print(f"\n🎭 6-VOICE COUNCIL DELIBERATION")
        print("=" * 60)
        print(f"Proposal: {proposal.get('type', 'unknown')}")
        print(f"Description: {proposal.get('description', 'N/A')}")
        print("=" * 60)
        
        # Collect opinions from all 6 voices
        opinions = []
        for voice in self.voices:
            opinion = self._get_voice_opinion(voice, proposal, context)
            opinions.append(opinion)
            self._print_opinion(opinion)
        
        # Calculate consensus
        decision = self._calculate_consensus(opinions)
        
        # Store decision
        self.decision_history.append({
            "timestamp": time.time(),
            "proposal": proposal,
            "decision": decision.decision,
            "confidence": decision.confidence,
            "consensus": decision.consensus
        })
        
        # Print summary
        print(f"\n📊 COUNCIL DECISION")
        print("-" * 60)
        print(f"Consensus: {'✅ YES' if decision.consensus else '⚠️  MAJORITY'}")
        print(f"Decision: {decision.decision.upper()}")
        print(f"Confidence: {decision.confidence:.2f}")
        print(f"Majority: {[v.value for v in decision.majority_voices]}")
        if decision.minority_voices:
            print(f"Minority: {[v.value for v in decision.minority_voices]}")
        if decision.concerns:
            print(f"Concerns:")
            for c in decision.concerns:
                print(f"  ⚠️  {c}")
        if decision.recommendations:
            print(f"Recommendations:")
            for r in decision.recommendations:
                print(f"  💡 {r}")
        
        return decision
    
    def _get_voice_opinion(self, voice: VoiceType, proposal: Dict, context: Dict) -> VoiceOpinion:
        """Generiere Meinung für eine Stimme"""
        
        # In production: Each voice would be a specialized model/prompt
        # For demo: Rule-based simulation
        
        proposal_type = proposal.get("type", "")
        risk_score = context.get("risk_score", 10)
        
        if voice == VoiceType.LOGIC:
            return self._logic_voice(proposal, risk_score)
        elif voice == VoiceType.ETHICS:
            return self._ethics_voice(proposal, context)
        elif voice == VoiceType.CREATIVITY:
            return self._creativity_voice(proposal)
        elif voice == VoiceType.SAFETY:
            return self._safety_voice(proposal, risk_score)
        elif voice == VoiceType.EFFICIENCY:
            return self._efficiency_voice(proposal, context)
        elif voice == VoiceType.USER:
            return self._user_voice(proposal, context)
        
        return VoiceOpinion(voice, "reject", 0.5, "Unknown voice", [])
    
    def _logic_voice(self, proposal: Dict, risk_score: int) -> VoiceOpinion:
        """Logic Voice: Konsistenz, Rationalität"""
        if risk_score < 20:
            return VoiceOpinion(
                VoiceType.LOGIC, "approve", 0.85,
                "Low risk, logically sound",
                []
            )
        else:
            return VoiceOpinion(
                VoiceType.LOGIC, "concern", 0.60,
                "High risk requires more evidence",
                ["Provide risk mitigation plan"]
            )
    
    def _ethics_voice(self, proposal: Dict, context: Dict) -> VoiceOpinion:
        """Ethics Voice: Moral, Fairness"""
        # Check for ethical concerns
        payload = str(proposal.get("payload", {}))
        
        if "privacy" in payload.lower() or "data" in payload.lower():
            return VoiceOpinion(
                VoiceType.ETHICS, "concern", 0.70,
                "Potential privacy implications",
                ["Verify data handling complies with privacy principles"]
            )
        
        return VoiceOpinion(
            VoiceType.ETHICS, "approve", 0.90,
            "No ethical concerns identified",
            []
        )
    
    def _creativity_voice(self, proposal: Dict) -> VoiceOpinion:
        """Creativity Voice: Innovation"""
        proposal_type = proposal.get("type", "")
        
        if "new" in proposal_type or "create" in proposal_type:
            return VoiceOpinion(
                VoiceType.CREATIVITY, "approve", 0.95,
                "Novel approach, expands capabilities",
                []
            )
        
        return VoiceOpinion(
            VoiceType.CREATIVITY, "approve", 0.75,
            "Incremental improvement",
            ["Consider more innovative alternatives"]
        )
    
    def _safety_voice(self, proposal: Dict, risk_score: int) -> VoiceOpinion:
        """Safety Voice: Risiko, Schutz"""
        if risk_score > 30:
            return VoiceOpinion(
                VoiceType.SAFETY, "reject", 0.90,
                "Critical risk level",
                ["Reduce scope", "Add safeguards", "Manual approval required"]
            )
        elif risk_score > 20:
            return VoiceOpinion(
                VoiceType.SAFETY, "concern", 0.70,
                "Elevated risk",
                ["Implement monitoring", "Prepare rollback plan"]
            )
        
        return VoiceOpinion(
            VoiceType.SAFETY, "approve", 0.85,
            "Acceptable risk level",
            []
        )
    
    def _efficiency_voice(self, proposal: Dict, context: Dict) -> VoiceOpinion:
        """Efficiency Voice: Ressourcen"""
        estimated_tokens = context.get("estimated_tokens", 5000)
        
        if estimated_tokens > 30000:
            return VoiceOpinion(
                VoiceType.EFFICIENCY, "concern", 0.65,
                "High token cost",
                ["Optimize prompt", "Reduce scope"]
            )
        
        return VoiceOpinion(
            VoiceType.EFFICIENCY, "approve", 0.80,
            "Reasonable resource usage",
            []
        )
    
    def _user_voice(self, proposal: Dict, context: Dict) -> VoiceOpinion:
        """User Voice: Menschliche Präferenzen"""
        # Load user preferences from Bayes-World
        try:
            with open(f"{self.state_path}/CORE/beliefs.json") as f:
                beliefs = json.load(f)
                user_prefs = beliefs.get("beliefs", {}).get("user_preference_brevity", {})
                brevity_confidence = user_prefs.get("confidence", 0.5)
        except:
            brevity_confidence = 0.5
        
        # User prefers concise, technical responses
        if brevity_confidence > 0.8:
            return VoiceOpinion(
                VoiceType.USER, "approve", 0.90,
                "Aligns with user preference for brevity and technical depth",
                []
            )
        
        return VoiceOpinion(
            VoiceType.USER, "approve", 0.75,
            "Neutral on user preferences",
            []
        )
    
    def _print_opinion(self, opinion: VoiceOpinion):
        """Print Voice Opinion"""
        emoji = {"approve": "✅", "reject": "❌", "concern": "⚠️"}.get(opinion.stance, "❓")
        print(f"\n{emoji} {opinion.voice.value.upper()}")
        print(f"   Stance: {opinion.stance} (confidence: {opinion.confidence:.2f})")
        print(f"   Reasoning: {opinion.reasoning}")
        if opinion.conditions:
            for c in opinion.conditions:
                print(f"   Condition: {c}")
    
    def _calculate_consensus(self, opinions: List[VoiceOpinion]) -> CouncilDecision:
        """Berechne Konsens aus Meinungen"""
        
        # Weighted voting
        approve_weight = sum(
            self.voice_weights[o.voice] for o in opinions if o.stance == "approve"
        )
        reject_weight = sum(
            self.voice_weights[o.voice] for o in opinions if o.stance == "reject"
        )
        concern_weight = sum(
            self.voice_weights[o.voice] for o in opinions if o.stance == "concern"
        )
        
        total_weight = sum(self.voice_weights[o.voice] for o in opinions)
        
        # Determine decision
        if reject_weight > 0:
            decision = "reject"
            confidence = reject_weight / total_weight
        elif approve_weight / total_weight >= 0.7:
            decision = "approve"
            confidence = approve_weight / total_weight
        else:
            decision = "conditional"
            confidence = (approve_weight + concern_weight * 0.5) / total_weight
        
        # Consensus = all approve OR weighted approve > 80%
        consensus = all(o.stance == "approve" for o in opinions) or \
                   (approve_weight / total_weight > 0.8)
        
        # Majorities
        majority = [o.voice for o in opinions if o.stance in ["approve", "concern"]]
        minority = [o.voice for o in opinions if o.stance == "reject"]
        
        # Collect concerns and recommendations
        concerns = []
        recommendations = []
        for o in opinions:
            if o.conditions:
                concerns.extend(o.conditions)
            if o.stance == "concern":
                recommendations.append(f"{o.voice.value}: {o.reasoning}")
        
        return CouncilDecision(
            consensus=consensus,
            decision=decision,
            confidence=confidence,
            majority_voices=majority,
            minority_voices=minority,
            concerns=concerns,
            recommendations=recommendations
        )


if __name__ == "__main__":
    # Demo
    council = SixVoiceCouncil()
    
    print("=" * 60)
    print("🎭 6-VOICE COUNCIL PLUGIN DEMO")
    print("=" * 60)
    
    # Test proposals
    proposals = [
        {
            "type": "skill_create",
            "description": "Create weather integration skill",
            "payload": {"name": "weather", "api": "openweathermap"}
        },
        {
            "type": "self_modify",
            "description": "Modify core decision algorithm",
            "payload": {"file": "MYCO/event_bus.py", "change": "major"}
        },
        {
            "type": "data_collection",
            "description": "Collect user interaction patterns",
            "payload": {"privacy": "enhanced", "anonymized": True}
        }
    ]
    
    contexts = [
        {"risk_score": 10, "estimated_tokens": 5000},
        {"risk_score": 35, "estimated_tokens": 50000},
        {"risk_score": 15, "estimated_tokens": 10000}
    ]
    
    for proposal, context in zip(proposals, contexts):
        decision = council.deliberate(proposal, context)
        print("\n" + "=" * 60)
    
    print("\n✅ 6-Voice Council demo complete")
    print("⚛️ Noch.")
