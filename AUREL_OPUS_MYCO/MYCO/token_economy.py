#!/usr/bin/env python3
"""
token_economy.py - Token-Optimierung für Aurel Opus Myco
Maximiere Nutzen pro Token: score = value / token_cost
"""

import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass

@dataclass
class TokenBudget:
    """Tägliches Token-Budget"""
    daily_limit: int = 100000
    used_today: int = 0
    reserved: int = 0  # Für critical events
    
    @property
    def available(self) -> int:
        return self.daily_limit - self.used_today - self.reserved
    
    @property
    def efficiency(self) -> float:
        """Effizienz-Score: value / tokens"""
        if self.used_today == 0:
            return 1.0
        # Wird durch externen Tracker aktualisiert
        return 1.0

class TokenEconomy:
    """
    Token-Economy Engine
    
    Features:
    - Budget-Tracking pro Kategorie
    - Action-Scoring: value / cost
    - Auto-Optimization
    - Cost-Profiling
    """
    
    def __init__(self, state_path: str = "/root/.openclaw/workspace/AUREL_OPUS_MYCO"):
        self.state_path = state_path
        self.budgets = {
            "critical": TokenBudget(daily_limit=20000, reserved=5000),
            "important": TokenBudget(daily_limit=40000),
            "normal": TokenBudget(daily_limit=30000),
            "sidequest": TokenBudget(daily_limit=10000)
        }
        self.action_history = []
        self.cost_profiles = self._load_cost_profiles()
        
    def _load_cost_profiles(self) -> Dict:
        """Lade bekannte Kosten-Profile"""
        return {
            "simple_query": {"tokens": 50, "value_base": 1.0},
            "complex_analysis": {"tokens": 500, "value_base": 5.0},
            "6voice_council": {"tokens": 3000, "value_base": 8.0},
            "research_deep": {"tokens": 2000, "value_base": 6.0},
            "skill_creation": {"tokens": 1500, "value_base": 7.0},
            "code_generation": {"tokens": 800, "value_base": 4.0},
            "perception_process": {"tokens": 100, "value_base": 2.0},
            "belief_update": {"tokens": 50, "value_base": 1.5},
            "checkpoint_create": {"tokens": 10, "value_base": 0.5}
        }
    
    def score_action(self, action_type: str, context: Dict) -> Dict:
        """
        Berechne Score für Action
        
        score = estimated_value / token_cost
        
        Returns: {
            "score": float,
            "estimated_tokens": int,
            "estimated_value": float,
            "recommendation": "proceed" | "defer" | "reject"
        }
        """
        profile = self.cost_profiles.get(action_type, {"tokens": 100, "value_base": 1.0})
        
        estimated_tokens = profile["tokens"]
        base_value = profile["value_base"]
        
        # Context-Adjustments
        urgency_multiplier = context.get("urgency", 1.0)  # 0.5-2.0
        importance_multiplier = context.get("importance", 1.0)  # 0.5-3.0
        uncertainty_penalty = context.get("uncertainty", 0.0)  # 0.0-0.5
        
        estimated_value = base_value * urgency_multiplier * importance_multiplier * (1 - uncertainty_penalty)
        
        score = estimated_value / max(estimated_tokens, 1)
        
        # Recommendation
        if score >= 0.01:
            recommendation = "proceed"
        elif score >= 0.005:
            recommendation = "defer"
        else:
            recommendation = "reject"
        
        return {
            "score": score,
            "estimated_tokens": estimated_tokens,
            "estimated_value": estimated_value,
            "recommendation": recommendation,
            "breakdown": {
                "base_value": base_value,
                "urgency_mult": urgency_multiplier,
                "importance_mult": importance_multiplier,
                "uncertainty_penalty": uncertainty_penalty
            }
        }
    
    def check_budget(self, category: str, requested_tokens: int) -> bool:
        """Prüfe ob Budget verfügbar"""
        budget = self.budgets.get(category, self.budgets["normal"])
        
        if requested_tokens <= budget.available:
            return True
        
        # Try to borrow from lower priority
        if category == "important" and self.budgets["normal"].available > requested_tokens:
            return True
        if category == "critical":
            # Critical can use reserved
            return requested_tokens <= (budget.available + budget.reserved)
        
        return False
    
    def spend(self, category: str, tokens: int, action: str, value: float):
        """Buche Token-Ausgabe"""
        budget = self.budgets.get(category, self.budgets["normal"])
        
        if tokens <= budget.available:
            budget.used_today += tokens
        else:
            # Borrow from normal
            if category != "normal" and self.budgets["normal"].available > tokens:
                self.budgets["normal"].used_today += tokens
            else:
                budget.used_today += tokens  # Overspend (alert)
        
        self.action_history.append({
            "timestamp": time.time(),
            "category": category,
            "action": action,
            "tokens": tokens,
            "value": value,
            "efficiency": value / max(tokens, 1)
        })
    
    def get_recommendations(self) -> List[str]:
        """Auto-Optimierungs-Empfehlungen"""
        recs = []
        
        # Check budget usage
        for cat, budget in self.budgets.items():
            usage = budget.used_today / budget.daily_limit
            if usage > 0.8:
                recs.append(f"⚠️  {cat}: Budget 80%+ used ({budget.used_today}/{budget.daily_limit})")
            elif usage < 0.2 and cat == "sidequest":
                recs.append(f"💡 {cat}: Underutilized, consider exploration")
        
        # Check efficiency
        if self.action_history:
            recent = self.action_history[-10:]
            avg_efficiency = sum(a["efficiency"] for a in recent) / len(recent)
            if avg_efficiency < 0.01:
                recs.append(f"⚠️  Low efficiency: {avg_efficiency:.4f} value/token")
        
        return recs
    
    def get_stats(self) -> Dict:
        """Token-Economy Statistiken"""
        total_used = sum(b.used_today for b in self.budgets.values())
        total_limit = sum(b.daily_limit for b in self.budgets.values())
        
        return {
            "total_budget": total_limit,
            "total_used": total_used,
            "total_available": total_limit - total_used,
            "usage_percent": (total_used / total_limit) * 100,
            "by_category": {
                cat: {
                    "used": b.used_today,
                    "limit": b.daily_limit,
                    "available": b.available
                }
                for cat, b in self.budgets.items()
            },
            "recent_efficiency": self._calculate_recent_efficiency(),
            "recommendations": self.get_recommendations()
        }
    
    def _calculate_recent_efficiency(self) -> float:
        """Berechne letzte Effizienz"""
        if not self.action_history:
            return 1.0
        recent = self.action_history[-20:]
        total_value = sum(a["value"] for a in recent)
        total_tokens = sum(a["tokens"] for a in recent)
        return total_value / max(total_tokens, 1)


if __name__ == "__main__":
    # Demo
    economy = TokenEconomy()
    
    print("=" * 50)
    print("🪙 TOKEN ECONOMY DEMO")
    print("=" * 50)
    
    # Test verschiedene Actions
    test_actions = [
        ("simple_query", {"urgency": 1.0, "importance": 1.0, "uncertainty": 0.0}),
        ("complex_analysis", {"urgency": 1.5, "importance": 2.0, "uncertainty": 0.1}),
        ("6voice_council", {"urgency": 1.0, "importance": 1.5, "uncertainty": 0.2}),
        ("research_deep", {"urgency": 0.8, "importance": 1.0, "uncertainty": 0.3}),
        ("perception_process", {"urgency": 1.2, "importance": 1.0, "uncertainty": 0.0}),
    ]
    
    print("\n📊 Action Scoring:")
    print("-" * 50)
    for action_type, context in test_actions:
        result = economy.score_action(action_type, context)
        print(f"\n{action_type}:")
        print(f"  Score: {result['score']:.4f} value/token")
        print(f"  Tokens: {result['estimated_tokens']}")
        print(f"  Value: {result['estimated_value']:.2f}")
        print(f"  → {result['recommendation'].upper()}")
    
    # Simulate spending
    print("\n" + "=" * 50)
    print("💰 Simulating token spending...")
    economy.spend("important", 500, "complex_analysis", 5.0)
    economy.spend("normal", 50, "simple_query", 1.0)
    economy.spend("critical", 3000, "6voice_council", 8.0)
    
    # Stats
    print("\n" + "=" * 50)
    print("📊 Stats:")
    stats = economy.get_stats()
    print(f"  Usage: {stats['total_used']}/{stats['total_budget']} ({stats['usage_percent']:.1f}%)")
    print(f"  Efficiency: {stats['recent_efficiency']:.4f} value/token")
    
    print("\n💡 Recommendations:")
    for rec in stats['recommendations']:
        print(f"  {rec}")
    
    print("\n✅ Token Economy demo complete")
    print("⚛️ Noch.")
