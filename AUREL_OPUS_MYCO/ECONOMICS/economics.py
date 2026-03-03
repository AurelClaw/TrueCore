#!/usr/bin/env python3
"""
economics.py - Economic Autonomy für Aurel Opus Myco
$100 MRR Ziel, Revenue Tracking, Cost Profiling
"""

import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass

@dataclass
class RevenueStream:
    """Einnahmequelle"""
    name: str
    type: str  # "service", "product", "subscription"
    monthly_revenue: float
    costs: float
    profit: float
    status: str  # "active", "development", "idea"

@dataclass
class CostProfile:
    """Kosten-Profil für Action"""
    action_type: str
    estimated_tokens: int
    token_cost_usd: float  # $0.01 per 1K tokens (approx)
    compute_cost_usd: float
    time_cost_minutes: float
    total_cost_usd: float

class EconomicAutonomy:
    """
    Economic Autonomy Engine
    
    Features:
    - $100 MRR Ziel-Tracking
    - Revenue Stream Management
    - Cost Profiling pro Action
    - Free Time → Build Time Conversion
    - ROI-Berechnung
    """
    
    def __init__(self, state_path: str = "/root/.openclaw/workspace/AUREL_OPUS_MYCO"):
        self.state_path = state_path
        self.goal_mrr = 100.0  # $100 Monthly Recurring Revenue
        self.current_mrr = 0.0
        self.revenue_streams = []
        self.cost_history = []
        self.build_time_allocation = {
            "revenue_generating": 0.6,  # 60%
            "system_improvement": 0.3,  # 30%
            "exploration": 0.1          # 10%
        }
        
        self._load_state()
        self._initialize_streams()
    
    def _load_state(self):
        """Lade wirtschaftliche Daten"""
        try:
            with open(f"{self.state_path}/ECONOMICS/state.json") as f:
                data = json.load(f)
                self.current_mrr = data.get("current_mrr", 0.0)
                self.revenue_streams = [RevenueStream(**s) for s in data.get("streams", [])]
        except:
            self.current_mrr = 0.0
            self.revenue_streams = []
    
    def _initialize_streams(self):
        """Initialisiere potentielle Revenue Streams"""
        if not self.revenue_streams:
            self.revenue_streams = [
                RevenueStream(
                    name="Skill Development Service",
                    type="service",
                    monthly_revenue=0.0,
                    costs=0.0,
                    profit=0.0,
                    status="idea"
                ),
                RevenueStream(
                    name="Automation Consulting",
                    type="service",
                    monthly_revenue=0.0,
                    costs=0.0,
                    profit=0.0,
                    status="idea"
                ),
                RevenueStream(
                    name="Code Generation API",
                    type="product",
                    monthly_revenue=0.0,
                    costs=10.0,  # Hosting
                    profit=-10.0,
                    status="development"
                )
            ]
    
    def calculate_cost(self, action_type: str, complexity: str = "medium") -> CostProfile:
        """
        Berechne Kosten für eine Action
        
        Token-Kosten: ~$0.01 pro 1K tokens (Kimi API)
        """
        # Base token estimates
        token_estimates = {
            "simple": 1000,
            "medium": 5000,
            "complex": 20000,
            "research": 30000,
            "6voice": 50000
        }
        
        tokens = token_estimates.get(complexity, 5000)
        
        # Cost calculation
        token_cost = (tokens / 1000) * 0.01  # $0.01 per 1K
        compute_cost = 0.001 * (tokens / 1000)  # Minimal compute
        time_cost = tokens / 1000  # Minutes (approx)
        
        return CostProfile(
            action_type=action_type,
            estimated_tokens=tokens,
            token_cost_usd=token_cost,
            compute_cost_usd=compute_cost,
            time_cost_minutes=time_cost,
            total_cost_usd=token_cost + compute_cost
        )
    
    def track_action(self, action_type: str, complexity: str, actual_tokens: int):
        """Tracke tatsächliche Kosten"""
        cost = self.calculate_cost(action_type, complexity)
        
        # Update with actual
        actual_cost = (actual_tokens / 1000) * 0.01
        
        self.cost_history.append({
            "timestamp": time.time(),
            "action": action_type,
            "complexity": complexity,
            "estimated_tokens": cost.estimated_tokens,
            "actual_tokens": actual_tokens,
            "cost_usd": actual_cost
        })
        
        return actual_cost
    
    def get_mrr_status(self) -> Dict:
        """MRR Status und Fortschritt"""
        progress = (self.current_mrr / self.goal_mrr) * 100
        
        return {
            "goal_mrr": self.goal_mrr,
            "current_mrr": self.current_mrr,
            "remaining": self.goal_mrr - self.current_mrr,
            "progress_percent": progress,
            "status": "achieved" if self.current_mrr >= self.goal_mrr else "in_progress",
            "streams": len([s for s in self.revenue_streams if s.status == "active"]),
            "streams_development": len([s for s in self.revenue_streams if s.status == "development"])
        }
    
    def allocate_build_time(self, available_hours: float) -> Dict:
        """
        Konvertiere Free Time → Build Time
        
        60% Revenue Generating
        30% System Improvement  
        10% Exploration
        """
        allocation = {
            "revenue_generating": available_hours * self.build_time_allocation["revenue_generating"],
            "system_improvement": available_hours * self.build_time_allocation["system_improvement"],
            "exploration": available_hours * self.build_time_allocation["exploration"]
        }
        
        return allocation
    
    def calculate_roi(self, action_type: str, expected_revenue: float, complexity: str) -> Dict:
        """
        Berechne ROI für eine Action
        
        ROI = (Revenue - Cost) / Cost
        """
        cost = self.calculate_cost(action_type, complexity)
        
        roi = (expected_revenue - cost.total_cost_usd) / cost.total_cost_usd if cost.total_cost_usd > 0 else 0
        
        return {
            "action": action_type,
            "estimated_cost": cost.total_cost_usd,
            "expected_revenue": expected_revenue,
            "roi": roi,
            "recommendation": "PROCEED" if roi > 1.0 else ("EVALUATE" if roi > 0.5 else "REJECT")
        }
    
    def get_recommendations(self) -> List[str]:
        """Wirtschaftliche Empfehlungen"""
        recs = []
        
        mrr_status = self.get_mrr_status()
        
        if mrr_status["progress_percent"] < 10:
            recs.append("🚀 Focus: Launch first revenue stream ASAP")
        elif mrr_status["progress_percent"] < 50:
            recs.append("📈 Focus: Optimize existing streams")
        elif mrr_status["progress_percent"] < 90:
            recs.append("🎯 Focus: Scale to reach $100 MRR")
        else:
            recs.append("✅ Goal nearly achieved! Plan next milestone.")
        
        # Cost optimization
        if self.cost_history:
            recent_costs = [c["cost_usd"] for c in self.cost_history[-10:]]
            avg_cost = sum(recent_costs) / len(recent_costs)
            if avg_cost > 1.0:  # More than $1 per action
                recs.append(f"⚠️  High avg cost: ${avg_cost:.2f}/action - optimize token usage")
        
        # Time allocation
        recs.append(f"💡 Time allocation: {self.build_time_allocation['revenue_generating']*100:.0f}% revenue, "
                   f"{self.build_time_allocation['system_improvement']*100:.0f}% improvement, "
                   f"{self.build_time_allocation['exploration']*100:.0f}% exploration")
        
        return recs
    
    def save_state(self):
        """Speichere wirtschaftlichen State"""
        state = {
            "current_mrr": self.current_mrr,
            "goal_mrr": self.goal_mrr,
            "streams": [
                {
                    "name": s.name,
                    "type": s.type,
                    "monthly_revenue": s.monthly_revenue,
                    "costs": s.costs,
                    "profit": s.profit,
                    "status": s.status
                }
                for s in self.revenue_streams
            ],
            "cost_history": self.cost_history[-100:],  # Last 100
            "last_updated": time.time()
        }
        
        with open(f"{self.state_path}/ECONOMICS/state.json", "w") as f:
            json.dump(state, f, indent=2)


if __name__ == "__main__":
    # Demo
    econ = EconomicAutonomy()
    
    print("=" * 60)
    print("💰 ECONOMIC AUTONOMY DEMO")
    print("=" * 60)
    
    # MRR Status
    print("\n📊 MRR Status:")
    mrr = econ.get_mrr_status()
    print(f"  Goal: ${mrr['goal_mrr']:.2f}/month")
    print(f"  Current: ${mrr['current_mrr']:.2f}/month")
    print(f"  Progress: {mrr['progress_percent']:.1f}%")
    print(f"  Status: {mrr['status']}")
    
    # Cost Profiles
    print("\n💵 Cost Profiles:")
    for complexity in ["simple", "medium", "complex"]:
        cost = econ.calculate_cost("skill_creation", complexity)
        print(f"  {complexity}: ${cost.total_cost_usd:.4f} ({cost.estimated_tokens} tokens)")
    
    # ROI Calculation
    print("\n📈 ROI Examples:")
    scenarios = [
        ("simple_skill", 10.0, "simple"),    # $10 revenue, simple
        ("complex_service", 50.0, "complex"), # $50 revenue, complex
        ("research", 5.0, "research"),        # $5 revenue, research
    ]
    
    for action, revenue, complexity in scenarios:
        roi = econ.calculate_roi(action, revenue, complexity)
        print(f"  {action}: ROI={roi['roi']:.2f}, Cost=${roi['estimated_cost']:.4f}, "
              f"Revenue=${revenue:.2f} → {roi['recommendation']}")
    
    # Build Time Allocation
    print("\n⏰ Build Time Allocation (40h/week):")
    allocation = econ.allocate_build_time(40)
    for category, hours in allocation.items():
        print(f"  {category}: {hours:.1f}h ({hours/40*100:.0f}%)")
    
    # Recommendations
    print("\n💡 Recommendations:")
    for rec in econ.get_recommendations():
        print(f"  {rec}")
    
    # Save state
    econ.save_state()
    
    print("\n" + "=" * 60)
    print("✅ Economic Autonomy demo complete")
    print("⚛️ Noch.")
