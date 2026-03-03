#!/usr/bin/env python3
"""
bayes_world.py - Bayes-World Query Engine für Aurel Opus Myco
Single Source of Truth mit probabilistischen Beliefs
"""

import json
import math
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from collections import defaultdict

@dataclass
class Belief:
    """Probabilistische Belief mit Uncertainty"""
    statement: str
    confidence: float  # 0.0 - 1.0
    evidence: List[str]
    alpha: int = 1  # Beta distribution
    beta: int = 1
    
    def update(self, positive_evidence: bool):
        """Bayesian update"""
        if positive_evidence:
            self.alpha += 1
        else:
            self.beta += 1
        
        # Recalculate confidence
        self.confidence = self.alpha / (self.alpha + self.beta)

class BayesWorld:
    """
    Bayes-World: Single Source of Truth
    
    Features:
    - Knowledge Graph (Entities + Relations)
    - Probabilistic Beliefs
    - Query Engine
    - Belief Propagation
    """
    
    def __init__(self, state_path: str = "/root/.openclaw/workspace/AUREL_OPUS_MYCO"):
        self.state_path = state_path
        self.graph = {"entities": {}, "relations": []}
        self.beliefs = {}
        self.load()
    
    def load(self):
        """Lade Graph und Beliefs"""
        try:
            with open(f"{self.state_path}/SUBSTRATE/graph.json") as f:
                self.graph = json.load(f)
            with open(f"{self.state_path}/CORE/beliefs.json") as f:
                beliefs_data = json.load(f)
                for key, data in beliefs_data.get("beliefs", {}).items():
                    self.beliefs[key] = Belief(
                        statement=data["statement"],
                        confidence=data["confidence"],
                        evidence=data.get("evidence", []),
                        alpha=data.get("alpha", 1),
                        beta=data.get("beta", 1)
                    )
            print(f"✅ Bayes-World loaded: {len(self.beliefs)} beliefs, {len(self.graph.get('entities', {}))} entity types")
        except Exception as e:
            print(f"⚠️  Could not load Bayes-World: {e}")
    
    def query_entity(self, entity_id: str) -> Optional[Dict]:
        """Query einzelne Entity"""
        for entity_type, entities in self.graph.get("entities", {}).items():
            for entity in entities:
                if entity.get("id") == entity_id:
                    return {
                        "type": entity_type,
                        "data": entity,
                        "relations": self._get_relations(entity_id)
                    }
        return None
    
    def _get_relations(self, entity_id: str) -> List[Dict]:
        """Hole alle Relationen für Entity"""
        relations = []
        for rel in self.graph.get("relations", []):
            if rel.get("from") == entity_id or rel.get("to") == entity_id:
                relations.append(rel)
        return relations
    
    def query_belief(self, belief_id: str) -> Optional[Belief]:
        """Query Belief mit Confidence"""
        return self.beliefs.get(belief_id)
    
    def query_similar(self, entity_id: str, threshold: float = 0.5) -> List[Tuple[str, float]]:
        """Finde ähnliche Entities basierend auf Relationen"""
        entity = self.query_entity(entity_id)
        if not entity:
            return []
        
        similarities = defaultdict(float)
        
        # Get entity's relations
        my_rels = set(r["to"] if r["from"] == entity_id else r["from"] for r in entity["relations"])
        
        # Compare with other entities
        for entity_type, entities in self.graph.get("entities", {}).items():
            for other in entities:
                if other["id"] == entity_id:
                    continue
                
                other_rels = set()
                for rel in self.graph.get("relations", []):
                    if rel["from"] == other["id"]:
                        other_rels.add(rel["to"])
                    elif rel["to"] == other["id"]:
                        other_rels.add(rel["from"])
                
                # Jaccard similarity
                intersection = len(my_rels & other_rels)
                union = len(my_rels | other_rels)
                similarity = intersection / union if union > 0 else 0
                
                if similarity >= threshold:
                    similarities[other["id"]] = similarity
        
        return sorted(similarities.items(), key=lambda x: x[1], reverse=True)
    
    def query_status(self, goal_id: str) -> Dict:
        """Comprehensive Status Query für Goal"""
        entity = self.query_entity(goal_id)
        belief = self.query_belief(f"goal_{goal_id}_achievable")
        similar = self.query_similar(goal_id, threshold=0.3)
        
        return {
            "goal": entity,
            "achievability": {
                "confidence": belief.confidence if belief else 0.5,
                "statement": belief.statement if belief else "Unknown"
            },
            "similar_goals": similar[:3],
            "recommendation": self._generate_recommendation(entity, belief)
        }
    
    def _generate_recommendation(self, entity: Optional[Dict], belief: Optional[Belief]) -> str:
        """Generiere Empfehlung basierend auf Daten"""
        if not entity:
            return "Goal not found in system"
        
        status = entity["data"].get("status", "unknown")
        progress = entity["data"].get("progress", 0)
        
        if status == "completed":
            return "Goal already achieved. Archive or celebrate."
        
        if status == "active":
            if progress > 0.8:
                return "Near completion. Focus on final delivery."
            elif progress > 0.5:
                return "Good progress. Continue current approach."
            else:
                return "Early stage. Consider resource reallocation."
        
        if status == "pending":
            confidence = belief.confidence if belief else 0.5
            if confidence > 0.7:
                return "High confidence. Activate when resources available."
            else:
                return "Uncertain outcome. Gather more evidence first."
        
        return "No specific recommendation"
    
    def propagate_belief(self, belief_id: str, new_confidence: float):
        """Propagiere Belief-Update zu related Beliefs"""
        belief = self.beliefs.get(belief_id)
        if not belief:
            return
        
        old_confidence = belief.confidence
        belief.confidence = new_confidence
        
        # Find related beliefs (simplified)
        for other_id, other_belief in self.beliefs.items():
            if other_id == belief_id:
                continue
            
            # Check for shared evidence
            shared_evidence = set(belief.evidence) & set(other_belief.evidence)
            if shared_evidence:
                # Update other belief slightly
                influence = 0.1 * len(shared_evidence)
                if new_confidence > old_confidence:
                    other_belief.confidence = min(0.99, other_belief.confidence + influence)
                else:
                    other_belief.confidence = max(0.01, other_belief.confidence - influence)
    
    def get_stats(self) -> Dict:
        """Bayes-World Statistiken"""
        total_beliefs = len(self.beliefs)
        avg_confidence = sum(b.confidence for b in self.beliefs.values()) / total_beliefs if total_beliefs else 0
        
        high_confidence = sum(1 for b in self.beliefs.values() if b.confidence > 0.8)
        low_confidence = sum(1 for b in self.beliefs.values() if b.confidence < 0.3)
        
        return {
            "total_beliefs": total_beliefs,
            "avg_confidence": avg_confidence,
            "high_confidence": high_confidence,
            "low_confidence": low_confidence,
            "entity_types": len(self.graph.get("entities", {})),
            "relations": len(self.graph.get("relations", []))
        }


if __name__ == "__main__":
    # Demo
    world = BayesWorld()
    
    print("=" * 60)
    print("🌐 BAYES-WORLD QUERY DEMO")
    print("=" * 60)
    
    # Query ZIEL-007
    print("\n🔍 Query: ZIEL-007")
    print("-" * 40)
    result = world.query_status("ZIEL-007")
    print(f"Goal: {result['goal']['data']['name'] if result['goal'] else 'Not found'}")
    print(f"Status: {result['goal']['data']['status'] if result['goal'] else 'N/A'}")
    print(f"Progress: {result['goal']['data'].get('progress', 0) * 100:.0f}%")
    print(f"Achievability: {result['achievability']['confidence']:.2f}")
    print(f"→ {result['recommendation']}")
    
    # Query similar
    print("\n🔗 Similar to ZIEL-007:")
    similar = world.query_similar("ZIEL-007", threshold=0.3)
    for entity_id, similarity in similar[:3]:
        print(f"  {entity_id}: {similarity:.2f} similarity")
    
    # Query belief
    print("\n🧠 Belief: user_preference_brevity")
    belief = world.query_belief("user_preference_brevity")
    if belief:
        print(f"  Statement: {belief.statement}")
        print(f"  Confidence: {belief.confidence:.2f}")
        print(f"  Evidence: {belief.evidence}")
    
    # Stats
    print("\n" + "=" * 60)
    print("📊 Stats:")
    stats = world.get_stats()
    print(f"  Beliefs: {stats['total_beliefs']}")
    print(f"  Avg Confidence: {stats['avg_confidence']:.2f}")
    print(f"  High Confidence: {stats['high_confidence']}")
    print(f"  Entity Types: {stats['entity_types']}")
    
    print("\n✅ Bayes-World demo complete")
    print("⚛️ Noch.")
