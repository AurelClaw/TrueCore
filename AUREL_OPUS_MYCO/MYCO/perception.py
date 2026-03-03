#!/usr/bin/env python3
"""
perception.py - Perception Layer für Aurel Opus Myco
Ingest, Klassifizierung und Routing
"""

import json
import re
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

class IntentType(Enum):
    """Klassifizierte Intents"""
    STATUS_QUERY = "status_query"
    GOAL_COMMAND = "goal_command"
    RESEARCH_REQUEST = "research_request"
    META_QUESTION = "meta_question"
    CREATIVE_TASK = "creative_task"
    SYSTEM_COMMAND = "system_command"
    CONVERSATION = "conversation"
    UNKNOWN = "unknown"

@dataclass
class PerceivedInput:
    """Strukturierte Wahrnehmung"""
    raw_input: str
    intent: IntentType
    entities: Dict[str, any]
    urgency: float  # 0.0-2.0
    importance: float  # 0.5-3.0
    sentiment: str  # positive, neutral, negative
    temporal_markers: List[str]
    confidence: float

class PerceptionLayer:
    """
    Perception Layer
    
    Features:
    - Intent-Klassifizierung
    - Entity-Extraktion
    - Sentiment-Analyse (basic)
    - Temporal-Marker Erkennung
    - Routing-Empfehlung
    """
    
    def __init__(self, state_path: str = "/root/.openclaw/workspace/AUREL_OPUS_MYCO"):
        self.state_path = state_path
        self._load_entities()
    
    def _load_entities(self):
        """Lade bekannte Entities für Matching"""
        try:
            with open(f"{self.state_path}/SUBSTRATE/graph.json") as f:
                graph = json.load(f)
                self.known_goals = [g["id"] for g in graph["entities"]["goals"]]
                self.known_skills = [s["id"] for s in graph["entities"]["skills"]]
        except:
            self.known_goals = []
            self.known_skills = []
    
    def perceive(self, raw_input: str, source: str = "user") -> PerceivedInput:
        """
        Haupt-Eingabe-Verarbeitung
        """
        # Intent-Klassifizierung
        intent = self._classify_intent(raw_input)
        
        # Entity-Extraktion
        entities = self._extract_entities(raw_input)
        
        # Urgency/Importance Schätzung
        urgency, importance = self._estimate_priority(raw_input, intent)
        
        # Sentiment
        sentiment = self._analyze_sentiment(raw_input)
        
        # Temporal markers
        temporal = self._extract_temporal(raw_input)
        
        # Confidence
        confidence = self._calculate_confidence(intent, entities)
        
        return PerceivedInput(
            raw_input=raw_input,
            intent=intent,
            entities=entities,
            urgency=urgency,
            importance=importance,
            sentiment=sentiment,
            temporal_markers=temporal,
            confidence=confidence
        )
    
    def _classify_intent(self, text: str) -> IntentType:
        """Klassifiziere Intent basierend auf Keywords"""
        text_lower = text.lower()
        
        # Status Query
        if any(kw in text_lower for kw in ["status", "ziel", "goal", "fortschritt", "progress"]):
            return IntentType.STATUS_QUERY
        
        # Goal Command
        if any(kw in text_lower for kw in ["aktiviere", "starte", "beginne", "create goal", "new goal"]):
            return IntentType.GOAL_COMMAND
        
        # Research Request
        if any(kw in text_lower for kw in ["recherchiere", "suche", "finde", "research", "suche nach"]):
            return IntentType.RESEARCH_REQUEST
        
        # Meta Question
        if any(kw in text_lower for kw in ["wie funktionierst du", "was bist du", "wie geht", "meta", "architektur"]):
            return IntentType.META_QUESTION
        
        # Creative Task
        if any(kw in text_lower for kw in ["schreibe", "erstelle", "kreativ", "creative", "poem", "story"]):
            return IntentType.CREATIVE_TASK
        
        # System Command
        if any(kw in text_lower for kw in ["stop", "start", "restart", "deploy", "rollback", "checkpoint"]):
            return IntentType.SYSTEM_COMMAND
        
        # Conversation (default)
        if len(text.split()) < 10:
            return IntentType.CONVERSATION
        
        return IntentType.UNKNOWN
    
    def _extract_entities(self, text: str) -> Dict:
        """Extrahiere Entities (Goals, Skills, etc.)"""
        entities = {
            "goals": [],
            "skills": [],
            "numbers": [],
            "dates": []
        }
        
        # Goal IDs
        for goal_id in self.known_goals:
            if goal_id.lower() in text.lower():
                entities["goals"].append(goal_id)
        
        # Numbers
        numbers = re.findall(r'\d+', text)
        entities["numbers"] = [int(n) for n in numbers]
        
        # Simple date patterns
        dates = re.findall(r'\d{4}-\d{2}-\d{2}', text)
        entities["dates"] = dates
        
        return entities
    
    def _estimate_priority(self, text: str, intent: IntentType) -> Tuple[float, float]:
        """Schätze Urgency und Importance"""
        text_lower = text.lower()
        
        # Urgency markers
        urgency = 1.0
        if any(kw in text_lower for kw in ["jetzt", "sofort", "dringend", "now", "urgent", "critical"]):
            urgency = 2.0
        elif any(kw in text_lower for kw in ["bald", "soon", "demnächst"]):
            urgency = 1.5
        elif any(kw in text_lower for kw in ["später", "later", "irgendwann"]):
            urgency = 0.5
        
        # Importance based on intent
        importance_map = {
            IntentType.SYSTEM_COMMAND: 3.0,
            IntentType.GOAL_COMMAND: 2.5,
            IntentType.STATUS_QUERY: 1.5,
            IntentType.RESEARCH_REQUEST: 2.0,
            IntentType.META_QUESTION: 1.0,
            IntentType.CREATIVE_TASK: 1.5,
            IntentType.CONVERSATION: 0.8,
            IntentType.UNKNOWN: 1.0
        }
        importance = importance_map.get(intent, 1.0)
        
        # Modifiers
        if "wichtig" in text_lower or "important" in text_lower:
            importance *= 1.5
        
        return urgency, importance
    
    def _analyze_sentiment(self, text: str) -> str:
        """Basic Sentiment-Analyse"""
        text_lower = text.lower()
        
        positive = ["gut", "super", "great", "awesome", "danke", "thanks", "👍", "❤️"]
        negative = ["schlecht", "bad", "problem", "error", "fehler", "mist", "💔"]
        
        pos_count = sum(1 for p in positive if p in text_lower)
        neg_count = sum(1 for n in negative if n in text_lower)
        
        if pos_count > neg_count:
            return "positive"
        elif neg_count > pos_count:
            return "negative"
        return "neutral"
    
    def _extract_temporal(self, text: str) -> List[str]:
        """Extrahiere Zeit-Marker"""
        markers = []
        text_lower = text.lower()
        
        if any(kw in text_lower for kw in ["heute", "today"]):
            markers.append("today")
        if any(kw in text_lower for kw in ["morgen", "tomorrow"]):
            markers.append("tomorrow")
        if any(kw in text_lower for kw in ["gestern", "yesterday"]):
            markers.append("yesterday")
        if any(kw in text_lower for kw in ["jetzt", "now"]):
            markers.append("now")
        if any(kw in text_lower for kw in ["später", "later"]):
            markers.append("later")
        
        return markers
    
    def _calculate_confidence(self, intent: IntentType, entities: Dict) -> float:
        """Berechne Confidence der Wahrnehmung"""
        base_confidence = 0.8
        
        # Higher confidence if we found entities
        if entities["goals"]:
            base_confidence += 0.1
        
        # Lower confidence for unknown intents
        if intent == IntentType.UNKNOWN:
            base_confidence -= 0.2
        
        return min(0.99, max(0.1, base_confidence))
    
    def get_routing_recommendation(self, perceived: PerceivedInput) -> str:
        """Empfehle Routing basierend auf Wahrnehmung"""
        
        # High confidence + specific intent → direct processing
        if perceived.confidence > 0.8 and perceived.intent != IntentType.UNKNOWN:
            return "direct_to_executor"
        
        # Complex or low confidence → 6-Voice Council
        if perceived.importance > 2.0 or perceived.confidence < 0.6:
            return "6voice_council"
        
        # Research needed
        if perceived.intent == IntentType.RESEARCH_REQUEST:
            return "research_engine"
        
        # Default
        return "direct_to_executor"


if __name__ == "__main__":
    # Demo
    perception = PerceptionLayer()
    
    print("=" * 60)
    print("👁️  PERCEPTION LAYER DEMO")
    print("=" * 60)
    
    test_inputs = [
        "Status ZIEL-007",
        "Aktiviere ZIEL-008 jetzt",
        "Recherchiere AGI-Architekturen",
        "Wie funktionierst du?",
        "Schreibe ein Gedicht",
        "Deploy neue Version",
        "Hallo",
        "Was ist mit dem System?"
    ]
    
    for inp in test_inputs:
        print(f"\n📝 Input: '{inp}'")
        print("-" * 40)
        
        p = perception.perceive(inp)
        
        print(f"  Intent: {p.intent.value}")
        print(f"  Entities: {p.entities}")
        print(f"  Urgency: {p.urgency}")
        print(f"  Importance: {p.importance}")
        print(f"  Sentiment: {p.sentiment}")
        print(f"  Temporal: {p.temporal_markers}")
        print(f"  Confidence: {p.confidence:.2f}")
        
        route = perception.get_routing_recommendation(p)
        print(f"  → Route: {route}")
    
    print("\n" + "=" * 60)
    print("✅ Perception Layer demo complete")
    print("⚛️ Noch.")
