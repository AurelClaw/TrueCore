#!/usr/bin/env python3
"""
self_modify.py - Korrekte Self-Modification mit Sandbox
Beispiel: Wie eine Self-Modification korrekt durchläuft
"""

import sys
sys.path.insert(0, "/root/.openclaw/workspace/AUREL_OPUS_MYCO")

from SMM.smm import SelfModificationManager, ModificationStatus

def demonstrate_correct_self_modify():
    """
    Demonstriert korrekten Self-Modify Flow:
    1. Propose mit Sandbox-Flag
    2. Shield validation (L5: Sandbox required)
    3. SMM Tier 1-5
    4. Deploy
    """
    
    print("=" * 60)
    print("🔧 SELF-MODIFY IMPLEMENTATION DEMO")
    print("=" * 60)
    print("\n📋 Scenario: Create new optimization skill")
    print("-" * 60)
    
    # Step 1: Shield Pre-Check
    print("\n🛡️  Step 1: Shield Pre-Validation")
    from SHIELD.shield import Shield
    
    shield = Shield()
    
    # Correct payload WITH sandbox flag
    payload = {
        "name": "optimization_v2",
        "code": "def optimize():\n    return 'optimized'\n",
        "sandbox": True,  # REQUIRED for self_modify
        "tests": ["test_optimize"]
    }
    
    # Quick risk assessment
    risk = shield.get_risk_assessment("self_modify", payload)
    print(f"  Risk Score: {risk['risk_score']}/40 ({risk['level']})")
    print(f"  Requires 6Voice: {risk['requires_6voice']}")
    print(f"  Requires User: {risk['requires_user_approval']}")
    
    # Full validation
    approved, results = shield.validate("self_modify", payload, {"estimated_tokens": 500})
    
    print(f"\n  Shield Results:")
    for r in results:
        status = "✅" if r.passed else "❌"
        print(f"    {status} L{r.level.value}: {r.level.name}")
        if r.warnings:
            for w in r.warnings:
                print(f"       WARN: {w}")
    
    if not approved:
        print(f"\n  ❌ REJECTED by Shield")
        return False
    
    print(f"\n  ✅ APPROVED by Shield")
    
    # Step 2: SMM Pipeline
    print("\n" + "=" * 60)
    print("🔧 Step 2: SMM Pipeline")
    print("-" * 60)
    
    smm = SelfModificationManager()
    
    # Propose with proper sandbox configuration
    mod_id = smm.propose(
        mod_type="skill_create",
        description="Create optimization_v2 skill with sandbox",
        payload=payload,
        proposer="system",
        risk_score=risk['risk_score']
    )
    
    # Check final status
    print("\n" + "=" * 60)
    print("📊 Final Status:")
    status = smm.get_status(mod_id)
    print(f"  Modification: {mod_id}")
    print(f"  Status: {status['status']}")
    print(f"  Tier History:")
    for h in status['tier_history']:
        print(f"    - {h['tier']}: {h['result']}")
    
    # Summary
    print("\n" + "=" * 60)
    if status['status'] == 'deployed':
        print("✅ SELF-MODIFY SUCCESS")
        print("  → Change deployed to production")
        print("  → Immutable checkpoint created")
        print("  → Rollback available if needed")
    elif status['status'] == 'sandbox_failed':
        print("❌ SELF-MODIFY FAILED at T2")
        print("  → Fix issues and retry")
        print("  → Sandbox destroyed, no harm done")
    else:
        print(f"⏳ SELF-MODIFY STATUS: {status['status']}")
    
    return status['status'] == 'deployed'


if __name__ == "__main__":
    success = demonstrate_correct_self_modify()
    
    print("\n" + "=" * 60)
    print("💡 KEY INSIGHTS")
    print("=" * 60)
    print("""
1. Sandbox Flag REQUIRED in payload
   → Without: L5 Constitutional REJECTS

2. Shield validates BEFORE SMM
   → Catches violations early

3. SMM 5-Tier Pipeline:
   T1: Propose (anyone)
   T2: Sandbox (auto-test)
   T3: Verify (6Voice/manual)
   T4: Canary (10% traffic)
   T5: Deploy (100% rollout)

4. Failure at any tier = Safe rollback
   → No production impact

5. Success = Immutable checkpoint
   → Full traceability
""")
    
    print("⚛️ Noch.")
