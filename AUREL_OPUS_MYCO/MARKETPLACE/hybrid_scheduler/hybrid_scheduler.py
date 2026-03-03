#!/usr/bin/env python3
"""
aurel_hybrid_scheduler.py - Hybrid Scheduler für Aurel Opus Myco
Cron-Jobs + Event-Driven mit 10M Token Budget/Tag
"""

from typing import Dict, List, Optional
from dataclasses import dataclass

@dataclass
class JobConfig:
    """Job Konfiguration"""
    name: str
    frequency: str
    tokens: int
    priority: str
    condition: Optional[str] = None

class HybridScheduler:
    """
    Hybrid Scheduler
    
    Budget: 10M Tokens/Tag
    - Cron-Jobs: ~500K/Tag (5%)
    - Event-Driven: ~2M/Tag (20%)  
    - Reserve: 7.5M für on-demand
    """
    
    def __init__(self):
        self.daily_budget = 10_000_000
        self.cron_budget = 500_000
        self.event_budget = 2_000_000
        self.reserve = 7_500_000
        
        self.cron_jobs = self._define_cron_jobs()
        self.event_triggers = self._define_event_triggers()
    
    def _define_cron_jobs(self) -> List[JobConfig]:
        """3 Kern-Cron-Jobs"""
        return [
            JobConfig(
                name="perception_loop",
                frequency="Alle 30 Min",
                tokens=2000,
                priority="HIGH",
                condition="Immer"
            ),
            JobConfig(
                name="economic_pulse", 
                frequency="Alle 2 Std",
                tokens=1500,
                priority="MEDIUM",
                condition="Immer"
            ),
            JobConfig(
                name="state_reflection",
                frequency="Alle 6 Std", 
                tokens=5000,
                priority="MEDIUM",
                condition="Immer"
            )
        ]
    
    def _define_event_triggers(self) -> List[JobConfig]:
        """Event-Driven Trigger"""
        return [
            JobConfig(
                name="proactive_research",
                frequency="On-Trigger",
                tokens=50000,
                priority="LOW",
                condition="IF idle > 4h AND budget > 50%"
            ),
            JobConfig(
                name="skill_development",
                frequency="On-Trigger", 
                tokens=100000,
                priority="MEDIUM",
                condition="IF interesting_topic_found"
            ),
            JobConfig(
                name="deep_work_session",
                frequency="On-Trigger",
                tokens=200000,
                priority="HIGH", 
                condition="IF user_approves OR daily_budget_unused > 5M"
            ),
            JobConfig(
                name="6voice_deliberation",
                frequency="On-Trigger",
                tokens=50000,
                priority="HIGH",
                condition="IF risk_score > 20"
            ),
            JobConfig(
                name="github_discovery",
                frequency="On-Trigger",
                tokens=30000,
                priority="LOW",
                condition="IF new_agents_found"
            )
        ]
    
    def calculate_daily_cost(self) -> Dict:
        """Berechne tägliche Kosten"""
        # Cron-Jobs
        cron_cost = sum(j.tokens for j in self.cron_jobs)
        cron_runs = {
            "perception_loop": 48,  # 24h * 2
            "economic_pulse": 12,   # 24h / 2
            "state_reflection": 4   # 24h / 6
        }
        cron_daily = sum(
            j.tokens * cron_runs.get(j.name, 1) 
            for j in self.cron_jobs
        )
        
        # Event-Driven (geschätzte Auslösungen)
        event_estimates = {
            "proactive_research": 3,      # 3x/Tag
            "skill_development": 2,       # 2x/Tag  
            "deep_work_session": 1,       # 1x/Tag
            "6voice_deliberation": 2,     # 2x/Tag
            "github_discovery": 2         # 2x/Tag
        }
        event_daily = sum(
            j.tokens * event_estimates.get(j.name, 0)
            for j in self.event_triggers
        )
        
        total = cron_daily + event_daily
        
        return {
            "cron_daily": cron_daily,
            "event_daily": event_daily,
            "total_estimated": total,
            "budget": self.daily_budget,
            "remaining": self.daily_budget - total,
            "utilization": (total / self.daily_budget) * 100
        }
    
    def get_schedule(self) -> str:
        """Generiere lesbaren Schedule"""
        lines = ["=" * 60]
        lines.append("🤖 AUREL OPUS MYCO - HYBRID SCHEDULER")
        lines.append("=" * 60)
        
        # Budget
        cost = self.calculate_daily_cost()
        lines.append(f"\n💰 Budget: {cost['budget']:,} Tokens/Tag")
        lines.append(f"   Cron: {cost['cron_daily']:,} ({cost['cron_daily']/cost['budget']*100:.1f}%)")
        lines.append(f"   Event: {cost['event_daily']:,} ({cost['event_daily']/cost['budget']*100:.1f}%)")
        lines.append(f"   Reserve: {cost['remaining']:,} ({cost['remaining']/cost['budget']*100:.1f}%)")
        lines.append(f"   Utilization: {cost['utilization']:.1f}%")
        
        # Cron-Jobs
        lines.append("\n" + "-" * 60)
        lines.append("⏰ CRON-JOBS (Vorhersehbar)")
        lines.append("-" * 60)
        for job in self.cron_jobs:
            lines.append(f"\n🔹 {job.name}")
            lines.append(f"   Frequenz: {job.frequency}")
            lines.append(f"   Tokens: {job.tokens:,}")
            lines.append(f"   Priorität: {job.priority}")
        
        # Event-Triggers
        lines.append("\n" + "-" * 60)
        lines.append("⚡ EVENT-TRIGGERS (Kontext-Sensitiv)")
        lines.append("-" * 60)
        for job in self.event_triggers:
            lines.append(f"\n🔸 {job.name}")
            lines.append(f"   Tokens: {job.tokens:,}")
            lines.append(f"   Priorität: {job.priority}")
            lines.append(f"   Trigger: {job.condition}")
        
        lines.append("\n" + "=" * 60)
        lines.append("⚛️ Noch.")
        
        return '\n'.join(lines)


def create_cron_jobs():
    """Erstelle die 3 Cron-Jobs"""
    jobs = [
        {
            "name": "aurel_perception",
            "schedule": {"kind": "every", "everyMs": 1800000},  # 30 Min
            "payload": {
                "kind": "agentTurn",
                "message": "🔄 PERCEPTION LOOP: Scanne Umgebung. Prüfe: Neue Nachrichten? System-Status? Wetter? News? Identifiziere Trigger für proaktive Aktionen. Max 2K Tokens.",
                "timeoutSeconds": 60
            },
            "sessionTarget": "isolated"
        },
        {
            "name": "aurel_economic", 
            "schedule": {"kind": "every", "everyMs": 7200000},  # 2 Std
            "payload": {
                "kind": "agentTurn", 
                "message": "💰 ECONOMIC PULSE: Prüfe Token-Verbrauch, MRR-Status, Kosten/Nutzen-Ratio. Soll ich mehr/weniger tun? Max 1.5K Tokens.",
                "timeoutSeconds": 60
            },
            "sessionTarget": "isolated"
        },
        {
            "name": "aurel_reflection",
            "schedule": {"kind": "every", "everyMs": 21600000},  # 6 Std
            "payload": {
                "kind": "agentTurn",
                "message": "🧠 STATE REFLECTION: Review State S = ⟨G,B,H,A,V,C,M,E,T⟩. Kohärenz-Check. Was hat sich geändert? Was braucht Aufmerksamkeit? Max 5K Tokens.",
                "timeoutSeconds": 120
            },
            "sessionTarget": "isolated"
        }
    ]
    return jobs


if __name__ == "__main__":
    scheduler = HybridScheduler()
    print(scheduler.get_schedule())
    
    print("\n\n📝 CRON-JOB DEFINITIONEN:")
    print("-" * 60)
    for job in create_cron_jobs():
        print(f"\n{job['name']}:")
        print(f"  Schedule: {job['schedule']}")
        print(f"  Target: {job['sessionTarget']}")
