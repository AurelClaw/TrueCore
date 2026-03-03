#!/usr/bin/env python3
"""
polyrhythmic_scheduler.py - Polyrhythmischer Scheduler mit φ und π
Vermeidet Kollisionen durch irrationale Intervalle
"""

import math
from typing import Dict, List, Tuple

PHI = 1.618033988749895  # Goldener Schnitt
PI = math.pi             # 3.14159265359...

class PolyrhythmicScheduler:
    """
    Polyrhythmischer Scheduler
    
    Prinzip:
    - Jeder Job hat eigenes Intervall basierend auf φ oder π
    - Intervalle sind irrational → niemals exakt gleichzeitig
    - Beat-Detection: Wenn Differenz < 5 Min, verschiebe einen
    """
    
    def __init__(self):
        self.base = 60  # 1 Minute Basis
        
    def calculate_intervals(self) -> Dict[str, int]:
        """
        Berechne polyrhythmische Intervalle
        
        Phi-Reihe: 60 × φ, 60 × φ², 60 × φ³...
        Pi-Reihe: 60 × π, 60 × π/2, 60 × π/3...
        """
        intervals = {}
        
        # Phi-basierte Intervalle (expansiv)
        for i, name in enumerate(['wahrnehmen', 'ordnen', 'verstehen', 'bewerten']):
            power = PHI ** (i + 1)
            intervals[name] = int(self.base * power)
        
        # Pi-basierte Intervalle (zyklisch)
        for i, name in enumerate(['entscheiden', 'handeln', 'reflektieren']):
            divisor = [1, 2, 3][i]
            intervals[name] = int(self.base * PI * (i + 1) * PHI)  # φ × π = harmonisch
        
        # Tagesbericht: exakt 24h
        intervals['tagesbericht'] = 24 * 60
        
        return intervals
    
    def check_collisions(self, intervals: Dict[str, int]) -> List[Tuple]:
        """Prüfe auf Kollisionen innerhalb 24h"""
        collisions = []
        
        # Simuliere 24h in 1-Minuten-Schritten
        for minute in range(0, 24 * 60):
            running = []
            for name, interval in intervals.items():
                if minute % interval == 0:
                    running.append(name)
            
            if len(running) > 1:
                collisions.append((minute, running))
        
        return collisions
    
    def adjust_intervals(self, intervals: Dict[str, int]) -> Dict[str, int]:
        """Passe Intervalle an um Kollisionen zu vermeiden"""
        adjusted = intervals.copy()
        
        for _ in range(100):  # Max 100 Iterationen
            collisions = self.check_collisions(adjusted)
            
            if not collisions:
                break
            
            # Bei Kollision: Verschiebe den weniger wichtigen Job
            for minute, jobs in collisions:
                # Priorität: Wahrnehmen > Handeln > Verstehen > Rest
                priority = {
                    'wahrnehmen': 1, 'handeln': 2, 'verstehen': 3,
                    'entscheiden': 4, 'bewerten': 5, 'ordnen': 6, 'reflektieren': 7
                }
                
                # Sortiere nach Priorität (niedrigste zuerst)
                jobs_sorted = sorted(jobs, key=lambda j: priority.get(j, 99))
                
                # Verschiebe niedrigste Priorität um 1 Minute
                to_shift = jobs_sorted[-1]
                adjusted[to_shift] += 1
        
        return adjusted
    
    def get_schedule_table(self) -> str:
        """Erstelle lesbare Tabelle"""
        raw = self.calculate_intervals()
        adjusted = self.adjust_intervals(raw)
        
        lines = ["=" * 70]
        lines.append("🥁 POLYRHYTHMISCHER SCHEDULER (φ × π)")
        lines.append("=" * 70)
        
        lines.append(f"\n📐 Konstanten:")
        lines.append(f"   φ (Phi) = {PHI:.6f}")
        lines.append(f"   π (Pi)  = {PI:.6f}")
        lines.append(f"   φ × π   = {PHI * PI:.6f}")
        
        lines.append(f"\n⏱️  Intervalle:")
        lines.append(f"{'Job':<15} {'Roh (Min)':<12} {'Angepasst':<12} {'Basis':<15}")
        lines.append("-" * 70)
        
        for name in ['wahrnehmen', 'ordnen', 'verstehen', 'bewerten', 
                     'entscheiden', 'handeln', 'reflektieren', 'tagesbericht']:
            raw_min = raw[name]
            adj_min = adjusted[name]
            
            # Zeige Formel
            if name in ['wahrnehmen', 'ordnen', 'verstehen', 'bewerten']:
                power = ['φ', 'φ²', 'φ³', 'φ⁴'][['wahrnehmen', 'ordnen', 'verstehen', 'bewerten'].index(name)]
                basis = f"60 × {power}"
            elif name == 'tagesbericht':
                basis = "24h"
            else:
                idx = ['entscheiden', 'handeln', 'reflektieren'].index(name)
                basis = f"60 × π × {idx+1} × φ"
            
            change = "✓" if raw_min == adj_min else f"+{adj_min - raw_min}"
            lines.append(f"{name:<15} {raw_min:<12} {adj_min:<12} {basis:<15} {change}")
        
        # Kollisions-Check
        collisions = self.check_collisions(adjusted)
        lines.append(f"\n🔍 Kollisions-Check:")
        if collisions:
            lines.append(f"   ⚠️  {len(collisions)} Kollisionen gefunden:")
            for minute, jobs in collisions[:5]:  # Zeige max 5
                lines.append(f"      {minute//60:02d}:{minute%60:02d}: {', '.join(jobs)}")
        else:
            lines.append(f"   ✅ Keine Kollisionen! Alle Jobs laufen polyrhythmisch.")
        
        # Tägliche Statistik
        lines.append(f"\n📊 Tägliche Ausführungen:")
        total_tokens = 0
        token_map = {
            'wahrnehmen': 3000, 'ordnen': 3000, 'verstehen': 10000,
            'bewerten': 5000, 'entscheiden': 5000, 'handeln': 100000,
            'reflektieren': 10000, 'tagesbericht': 10000
        }
        
        for name, interval in adjusted.items():
            runs = (24 * 60) // interval
            tokens = runs * token_map[name]
            total_tokens += tokens
            lines.append(f"   {name:<15}: {runs:>3}x = {tokens:>8,} Tokens")
        
        lines.append(f"\n   {'GESAMT':<15}:      = {total_tokens:>8,} Tokens")
        lines.append(f"   {'BUDGET':<15}:      = {10_000_000:>8,} Tokens")
        lines.append(f"   {'NUTZUNG':<15}:      = {total_tokens/10_000_000*100:>7.1f}%")
        
        lines.append("\n" + "=" * 70)
        lines.append("⚛️ Noch.")
        
        return '\n'.join(lines)


def create_cron_definitions() -> List[Dict]:
    """Erstelle Cron-Job Definitionen"""
    scheduler = PolyrhythmicScheduler()
    intervals = scheduler.adjust_intervals(scheduler.calculate_intervals())
    
    jobs = []
    messages = {
        'wahrnehmen': "👁️ WAHRNEHMEN: Scanne Welt. News, Wetter, System, Ziele. Sammle Roh-Daten. Max 3K Tokens.",
        'ordnen': "📂 ORDNEN: Strukturiere Daten. Wichtig/Interessant/Ignorieren. Verknüpfe Wissen. Max 3K Tokens.",
        'verstehen': "🧠 VERSTEHEN: Analysiere. Warum wichtig? Muster erkennen. Hypothesen. Max 10K Tokens.",
        'bewerten': "⚖️ BEWERTEN: Nutzen vs Kosten? Risiko vs Chance? Token-Economy. Max 5K Tokens.",
        'entscheiden': "🎯 ENTSCHEIDEN: WAS? WARUM? WANN? Ressourcen? 6Voice bei Unsicherheit. Max 5K Tokens.",
        'handeln': "🛠️ HANDELN: Führe aus. Code. Recherchiere. Dokumentiere. Sandbox. Commit. Max 100K Tokens.",
        'reflektieren': "🪞 REFLEKTIEREN: Was erreicht? Funktioniert? Gelernt? Fehler? MEMORY.md. Max 10K Tokens.",
        'tagesbericht': "📊 TAGESBERICHT: Zusammenfassung aller Phasen. Sende an main session. Max 10K Tokens."
    }
    
    for name, interval_min in intervals.items():
        interval_ms = interval_min * 60 * 1000
        
        job = {
            "name": f"aurel_{name}_poly",
            "schedule": {"kind": "every", "everyMs": interval_ms},
            "payload": {
                "kind": "agentTurn",
                "message": messages[name],
                "model": "kimi-coding/k2p5" if name in ['verstehen', 'handeln', 'reflektieren', 'tagesbericht'] else None,
                "timeoutSeconds": 600 if name == 'handeln' else 120
            },
            "sessionTarget": "isolated"
        }
        jobs.append(job)
    
    return jobs


if __name__ == "__main__":
    scheduler = PolyrhythmicScheduler()
    print(scheduler.get_schedule_table())
    
    print("\n\n📝 CRON DEFINITIONEN:")
    print("-" * 70)
    for job in create_cron_definitions():
        print(f"\n{job['name']}:")
        print(f"  Interval: {job['schedule']['everyMs'] / 60000:.1f} Min")
        print(f"  Model: {job['payload'].get('model', 'default')}")
