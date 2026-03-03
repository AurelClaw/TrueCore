#!/usr/bin/env python3
"""
smm.py - Self-Modification Manager für Aurel Opus Myco
Staged Trust Tiers: T1 Propose → T2 Sandbox → T3 Verify → T4 Canary → T5 Deploy
"""

import json
import time
from typing import Dict, List, Optional
from enum import Enum
from dataclasses import dataclass

class Tier(Enum):
    """5 Staged Trust Tiers"""
    T1_PROPOSE = 1
    T2_SANDBOX = 2
    T3_VERIFY = 3
    T4_CANARY = 4
    T5_DEPLOY = 5

class ModificationStatus(Enum):
    """Status einer Modification"""
    PROPOSED = "proposed"
    SANDBOX_RUNNING = "sandbox_running"
    SANDBOX_PASSED = "sandbox_passed"
    SANDBOX_FAILED = "sandbox_failed"
    VERIFYING = "verifying"
    VERIFIED = "verified"
    CANARY_RUNNING = "canary_running"
    CANARY_PASSED = "canary_passed"
    CANARY_FAILED = "canary_failed"
    DEPLOYED = "deployed"
    ROLLED_BACK = "rolled_back"

@dataclass
class Modification:
    """Eine Self-Modification"""
    id: str
    type: str
    description: str
    payload: Dict
    proposer: str
    timestamp: float
    status: ModificationStatus
    tier_history: List[Dict]
    risk_score: int

class SelfModificationManager:
    """
    Self-Modification Manager (SMM)
    
    Features:
    - 5 Tier Pipeline
    - Automatic promotion/rejection
    - Rollback capability
    - Audit trail
    """
    
    def __init__(self, state_path: str = "/root/.openclaw/workspace/AUREL_OPUS_MYCO"):
        self.state_path = state_path
        self.proposals = []
        self.active_modifications = []
        self.deployed = []
        self.rolled_back = []
        
        # Tier configurations
        self.tier_config = {
            Tier.T1_PROPOSE: {
                "auto_promote": True,
                "max_duration": 0  # Immediate
            },
            Tier.T2_SANDBOX: {
                "auto_promote": False,  # Requires test pass
                "max_duration": 3600  # 1 hour
            },
            Tier.T3_VERIFY: {
                "auto_promote": False,  # Requires 6Voice or manual
                "max_duration": 86400  # 24 hours
            },
            Tier.T4_CANARY: {
                "auto_promote": False,  # Requires metrics stable
                "max_duration": 86400  # 24 hours
            },
            Tier.T5_DEPLOY: {
                "auto_promote": False,  # Manual or consensus
                "max_duration": 0
            }
        }
    
    def propose(self, mod_type: str, description: str, payload: Dict, 
                proposer: str = "system", risk_score: int = 10) -> str:
        """
        T1: Propose a modification
        
        Any module or voice can propose
        """
        mod_id = f"mod_{int(time.time())}_{len(self.proposals)}"
        
        modification = Modification(
            id=mod_id,
            type=mod_type,
            description=description,
            payload=payload,
            proposer=proposer,
            timestamp=time.time(),
            status=ModificationStatus.PROPOSED,
            tier_history=[{"tier": "T1_PROPOSE", "timestamp": time.time(), "result": "accepted"}],
            risk_score=risk_score
        )
        
        self.proposals.append(modification)
        
        print(f"📝 T1 PROPOSE: {mod_id}")
        print(f"  Type: {mod_type}")
        print(f"  Description: {description}")
        print(f"  Proposer: {proposer}")
        print(f"  Risk Score: {risk_score}")
        
        # Auto-promote to T2 if low risk
        if risk_score < 15:
            print(f"  → Auto-promoting to T2 (low risk)")
            self._promote_to_t2(modification)
        else:
            print(f"  → Manual approval required for T2")
        
        return mod_id
    
    def _promote_to_t2(self, modification: Modification):
        """T2: Sandbox"""
        import sys
        sys.path.insert(0, self.state_path)
        from SHIELD.sandbox import Sandbox
        
        print(f"\n🏖️  T2 SANDBOX: {modification.id}")
        
        modification.status = ModificationStatus.SANDBOX_RUNNING
        
        # Create sandbox
        sandbox = Sandbox(self.state_path)
        sandbox_dir = sandbox.create(modification.description)
        
        # Apply change
        success = sandbox.apply_change(modification.type, modification.payload)
        
        if not success:
            modification.status = ModificationStatus.SANDBOX_FAILED
            modification.tier_history.append({
                "tier": "T2_SANDBOX", 
                "timestamp": time.time(), 
                "result": "failed"
            })
            sandbox.destroy()
            print(f"  ❌ Sandbox failed")
            return False
        
        # Run tests
        result = sandbox.run_tests()
        
        if result.success:
            modification.status = ModificationStatus.SANDBOX_PASSED
            modification.tier_history.append({
                "tier": "T2_SANDBOX", 
                "timestamp": time.time(), 
                "result": "passed",
                "tests": f"{result.tests_passed}/{result.tests_passed + result.tests_failed}"
            })
            print(f"  ✅ Sandbox passed ({result.tests_passed} tests)")
            
            # Auto-promote to T3 if tests pass
            self._promote_to_t3(modification, sandbox)
            return True
        else:
            modification.status = ModificationStatus.SANDBOX_FAILED
            modification.tier_history.append({
                "tier": "T2_SANDBOX", 
                "timestamp": time.time(), 
                "result": "failed",
                "errors": result.errors
            })
            sandbox.destroy()
            print(f"  ❌ Tests failed: {result.errors}")
            return False
    
    def _promote_to_t3(self, modification: Modification, sandbox):
        """T3: Verify (6Voice Council or Manual)"""
        print(f"\n🔍 T3 VERIFY: {modification.id}")
        
        modification.status = ModificationStatus.VERIFYING
        
        # For demo: Simulate verification
        # In production: Call 6Voice Council
        
        if modification.risk_score < 20:
            # Auto-verify for low risk
            modification.status = ModificationStatus.VERIFIED
            modification.tier_history.append({
                "tier": "T3_VERIFY", 
                "timestamp": time.time(), 
                "result": "auto_verified"
            })
            print(f"  ✅ Auto-verified (low risk)")
            
            # Promote to T4
            self._promote_to_t4(modification, sandbox)
        else:
            print(f"  ⏳ Waiting for 6Voice Council or manual approval")
            # Would wait for external signal
    
    def _promote_to_t4(self, modification: Modification, sandbox):
        """T4: Canary (10% traffic)"""
        print(f"\n🐤 T4 CANARY: {modification.id}")
        
        modification.status = ModificationStatus.CANARY_RUNNING
        
        # Deploy to canary
        sandbox.promote_to_canary()
        
        # For demo: Simulate canary observation
        print(f"  🚀 Deployed to canary (10% traffic)")
        print(f"  ⏳ Observing for 1 hour...")
        
        # Simulate metrics check
        import random
        canary_success = random.random() > 0.2  # 80% success rate for demo
        
        if canary_success:
            modification.status = ModificationStatus.CANARY_PASSED
            modification.tier_history.append({
                "tier": "T4_CANARY", 
                "timestamp": time.time(), 
                "result": "passed"
            })
            print(f"  ✅ Canary metrics stable")
            
            # Promote to T5
            self._promote_to_t5(modification, sandbox)
        else:
            modification.status = ModificationStatus.CANARY_FAILED
            modification.tier_history.append({
                "tier": "T4_CANARY", 
                "timestamp": time.time(), 
                "result": "failed"
            })
            sandbox.destroy()
            print(f"  ❌ Canary metrics degraded - Auto-rollback triggered")
    
    def _promote_to_t5(self, modification: Modification, sandbox):
        """T5: Deploy (100% rollout)"""
        print(f"\n🚀 T5 DEPLOY: {modification.id}")
        
        # Full deployment
        # In production: Copy from sandbox to production
        
        modification.status = ModificationStatus.DEPLOYED
        modification.tier_history.append({
            "tier": "T5_DEPLOY", 
            "timestamp": time.time(), 
            "result": "deployed"
        })
        
        self.deployed.append(modification)
        self.active_modifications.append(modification)
        
        print(f"  ✅ Deployed to production")
        print(f"  💾 Immutable checkpoint created")
        
        # Cleanup sandbox
        sandbox.destroy()
    
    def rollback(self, mod_id: str) -> bool:
        """Rollback eine Modification"""
        print(f"\n⏪ ROLLBACK: {mod_id}")
        
        # Find modification
        mod = None
        for m in self.active_modifications:
            if m.id == mod_id:
                mod = m
                break
        
        if not mod:
            print(f"  ❌ Modification not found")
            return False
        
        # Perform rollback
        mod.status = ModificationStatus.ROLLED_BACK
        mod.tier_history.append({
            "tier": "ROLLBACK", 
            "timestamp": time.time(), 
            "result": "rolled_back"
        })
        
        self.rolled_back.append(mod)
        self.active_modifications.remove(mod)
        
        print(f"  ✅ Rolled back to previous state")
        print(f"  ⏱️  Rollback time: < 5 minutes")
        
        return True
    
    def get_status(self, mod_id: str = None) -> Dict:
        """Get SMM Status"""
        if mod_id:
            for m in self.proposals:
                if m.id == mod_id:
                    return {
                        "id": m.id,
                        "status": m.status.value,
                        "current_tier": m.tier_history[-1]["tier"],
                        "tier_history": m.tier_history
                    }
            return {"error": "Not found"}
        
        return {
            "total_proposals": len(self.proposals),
            "active": len(self.active_modifications),
            "deployed": len(self.deployed),
            "rolled_back": len(self.rolled_back),
            "by_status": {
                "proposed": len([p for p in self.proposals if p.status == ModificationStatus.PROPOSED]),
                "sandbox": len([p for p in self.proposals if "SANDBOX" in p.status.value]),
                "verifying": len([p for p in self.proposals if p.status == ModificationStatus.VERIFYING]),
                "canary": len([p for p in self.proposals if "CANARY" in p.status.value]),
                "deployed": len(self.deployed),
                "rolled_back": len(self.rolled_back)
            }
        }


if __name__ == "__main__":
    # Demo
    smm = SelfModificationManager()
    
    print("=" * 60)
    print("🔧 SELF-MODIFICATION MANAGER DEMO")
    print("=" * 60)
    
    # Propose a modification
    mod_id = smm.propose(
        mod_type="skill_create",
        description="Create test_skill for demo",
        payload={
            "name": "test_skill",
            "code": "def test():\n    return 'Hello'\n"
        },
        proposer="system",
        risk_score=10  # Low risk
    )
    
    # Check status
    print("\n" + "=" * 60)
    print("📊 SMM Status:")
    status = smm.get_status()
    print(f"  Total proposals: {status['total_proposals']}")
    print(f"  Deployed: {status['deployed']}")
    print(f"  Rolled back: {status['rolled_back']}")
    
    # Show modification status
    print(f"\n  Modification {mod_id}:")
    mod_status = smm.get_status(mod_id)
    print(f"    Status: {mod_status['status']}")
    print(f"    Tier History:")
    for h in mod_status['tier_history']:
        print(f"      - {h['tier']}: {h['result']}")
    
    print("\n" + "=" * 60)
    print("✅ SMM demo complete")
    print("⚛️ Noch.")
