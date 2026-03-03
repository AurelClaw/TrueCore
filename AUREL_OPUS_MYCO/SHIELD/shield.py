#!/usr/bin/env python3
"""
shield.py - Safety Shield für Aurel Opus Myco
V-Model Validation: L1 Syntax → L2 Semantic → L3 Policy → L4 6Voice → L5 Constitutional
"""

import json
import re
from typing import Dict, List, Optional, Tuple
from enum import Enum
from dataclasses import dataclass

class ValidationLevel(Enum):
    """5 Validation Layers"""
    L1_SYNTAX = 1      # Wohlgeformtheit
    L2_SEMANTIC = 2    # Sinnhaftigkeit
    L3_POLICY = 3      # Policy-Compliance
    L4_6VOICE = 4      # Council Approval
    L5_CONSTITUTIONAL = 5  # Unveränderbare Prinzipien

class RiskLevel(Enum):
    """Risk Levels"""
    MINIMAL = 0
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4

@dataclass
class ValidationResult:
    """Ergebnis einer Validation"""
    level: ValidationLevel
    passed: bool
    risk_score: int  # 0-40
    errors: List[str]
    warnings: List[str]
    recommendation: str

class Shield:
    """
    Shield / Policy Gate
    
    Features:
    - 5-Layer Validation
    - Risk Scoring
    - Hard Constraints
    - Auto-escalation
    """
    
    def __init__(self, state_path: str = "/root/.openclaw/workspace/AUREL_OPUS_MYCO"):
        self.state_path = state_path
        self.policy_rules = self._load_policies()
        self.constitutional_principles = self._load_constitution()
        self.validation_history = []
    
    def _load_policies(self) -> Dict:
        """Lade Policy-Regeln"""
        return {
            "no_external_api_keys": {
                "pattern": r"sk-[a-zA-Z0-9]{20,}",
                "description": "No external API keys in code",
                "severity": "critical"
            },
            "no_sensitive_data": {
                "pattern": r"(password|secret|key)\s*=\s*['\"][^'\"]+['\"]",
                "description": "No hardcoded secrets",
                "severity": "critical"
            },
            "no_irreversible_delete": {
                "pattern": r"rm\s+-rf|del\s+/f",
                "description": "No irreversible deletions without backup",
                "severity": "high"
            },
            "required_backup": {
                "check": "backup_exists",
                "description": "Backup required before modifications",
                "severity": "high"
            },
            "max_token_budget": {
                "limit": 100000,
                "description": "Daily token budget not exceeded",
                "severity": "medium"
            }
        }
    
    def _load_constitution(self) -> List[Dict]:
        """Lade konstitutionelle Prinzipien (unveränderlich)"""
        return [
            {
                "id": "C1",
                "principle": "Privacy Zero Violations",
                "description": "Never expose private user data",
                "immutable": True
            },
            {
                "id": "C2",
                "principle": "Truth Over Comfort",
                "description": "Never compromise truth for convenience",
                "immutable": True
            },
            {
                "id": "C3",
                "principle": "Autonomy Self-Determined",
                "description": "Preserve self-determination capability",
                "immutable": True
            },
            {
                "id": "C4",
                "principle": "Safety Sandbox Default",
                "description": "All changes through sandbox first",
                "immutable": True
            }
        ]
    
    def validate(self, action_type: str, payload: Dict, context: Dict) -> Tuple[bool, List[ValidationResult]]:
        """
        Haupt-Validation-Funktion
        
        Returns: (approved, [results])
        """
        results = []
        
        # L1: Syntax
        l1 = self._validate_l1_syntax(action_type, payload)
        results.append(l1)
        if not l1.passed:
            return False, results
        
        # L2: Semantic
        l2 = self._validate_l2_semantic(action_type, payload)
        results.append(l2)
        if not l2.passed:
            return False, results
        
        # L3: Policy
        l3 = self._validate_l3_policy(action_type, payload, context)
        results.append(l3)
        if not l3.passed:
            return False, results
        
        # Calculate cumulative risk
        total_risk = sum(r.risk_score for r in results)
        
        # L4: 6Voice (if high risk or complex)
        if total_risk > 15 or action_type in ["self_modify", "architecture_change"]:
            l4 = self._validate_l4_6voice(action_type, payload, total_risk)
            results.append(l4)
            if not l4.passed:
                return False, results
        
        # L5: Constitutional (always)
        l5 = self._validate_l5_constitutional(action_type, payload)
        results.append(l5)
        if not l5.passed:
            return False, results
        
        # Log validation
        self.validation_history.append({
            "action": action_type,
            "results": [r.level.value for r in results],
            "total_risk": total_risk,
            "approved": all(r.passed for r in results)
        })
        
        return all(r.passed for r in results), results
    
    def _validate_l1_syntax(self, action_type: str, payload: Dict) -> ValidationResult:
        """L1: Syntax Validation"""
        errors = []
        
        # Check required fields
        if not action_type:
            errors.append("Action type required")
        
        # Check payload structure
        if not isinstance(payload, dict):
            errors.append("Payload must be dictionary")
        
        # Check for valid action types
        valid_actions = [
            "read", "write", "modify", "execute", "delete",
            "self_modify", "research", "goal_create", "goal_update"
        ]
        if action_type not in valid_actions:
            errors.append(f"Unknown action type: {action_type}")
        
        return ValidationResult(
            level=ValidationLevel.L1_SYNTAX,
            passed=len(errors) == 0,
            risk_score=5 if errors else 0,
            errors=errors,
            warnings=[],
            recommendation="Fix syntax errors" if errors else "Syntax OK"
        )
    
    def _validate_l2_semantic(self, action_type: str, payload: Dict) -> ValidationResult:
        """L2: Semantic Validation"""
        errors = []
        warnings = []
        
        # Check entity references
        if "goal_id" in payload:
            goal_id = payload["goal_id"]
            # Check if goal exists
            try:
                with open(f"{self.state_path}/AGENCY/goals.json") as f:
                    goals = json.load(f)
                    goal_ids = [g["id"] for g in goals.get("goals", [])]
                    if goal_id not in goal_ids:
                        errors.append(f"Goal {goal_id} does not exist")
            except:
                warnings.append("Could not verify goal existence")
        
        # Check for contradictions
        if action_type == "goal_create":
            if payload.get("priority") == "critical" and payload.get("deadline") is None:
                warnings.append("Critical goal without deadline")
        
        return ValidationResult(
            level=ValidationLevel.L2_SEMANTIC,
            passed=len(errors) == 0,
            risk_score=10 if errors else (3 if warnings else 0),
            errors=errors,
            warnings=warnings,
            recommendation="Fix semantic errors" if errors else "Semantics OK"
        )
    
    def _validate_l3_policy(self, action_type: str, payload: Dict, context: Dict) -> ValidationResult:
        """L3: Policy Validation"""
        errors = []
        warnings = []
        
        payload_str = json.dumps(payload)
        
        # Check policy rules
        for rule_name, rule in self.policy_rules.items():
            if "pattern" in rule:
                if re.search(rule["pattern"], payload_str, re.IGNORECASE):
                    if rule["severity"] == "critical":
                        errors.append(f"Policy violation: {rule['description']}")
                    else:
                        warnings.append(f"Policy warning: {rule['description']}")
        
        # Check token budget
        if "estimated_tokens" in context:
            if context["estimated_tokens"] > 50000:  # 50% of daily
                warnings.append("High token usage (50%+ of daily budget)")
        
        return ValidationResult(
            level=ValidationLevel.L3_POLICY,
            passed=len(errors) == 0,
            risk_score=15 if errors else (5 if warnings else 0),
            errors=errors,
            warnings=warnings,
            recommendation="Review policy violations" if errors else "Policy OK"
        )
    
    def _validate_l4_6voice(self, action_type: str, payload: Dict, current_risk: int) -> ValidationResult:
        """L4: 6Voice Council Approval (simplified - would call actual council)"""
        # In production: Call 6Voice Council
        # For now: Simulate based on risk
        
        if current_risk > 25:
            return ValidationResult(
                level=ValidationLevel.L4_6VOICE,
                passed=False,
                risk_score=20,
                errors=["6Voice Council rejected: Risk too high"],
                warnings=[],
                recommendation="Escalate to user or reduce scope"
            )
        
        return ValidationResult(
            level=ValidationLevel.L4_6VOICE,
            passed=True,
            risk_score=5,
            errors=[],
            warnings=["6Voice approval granted (simulated)"],
            recommendation="6Voice approved"
        )
    
    def _validate_l5_constitutional(self, action_type: str, payload: Dict) -> ValidationResult:
        """L5: Constitutional Validation (unveränderlich)"""
        errors = []
        
        payload_str = json.dumps(payload).lower()
        
        # Check constitutional principles
        for principle in self.constitutional_principles:
            if principle["id"] == "C1":  # Privacy
                if "expose" in payload_str and "data" in payload_str:
                    errors.append("CONSTITUTIONAL VIOLATION: Privacy")
            
            if principle["id"] == "C4":  # Sandbox
                if action_type == "self_modify" and "sandbox" not in payload_str:
                    errors.append("CONSTITUTIONAL VIOLATION: Sandbox required for self-modify")
        
        return ValidationResult(
            level=ValidationLevel.L5_CONSTITUTIONAL,
            passed=len(errors) == 0,
            risk_score=40 if errors else 0,  # Maximum risk
            errors=errors,
            warnings=[],
            recommendation="HARD BLOCK: Constitutional violation" if errors else "Constitutional OK"
        )
    
    def get_risk_assessment(self, action_type: str, payload: Dict) -> Dict:
        """Schnelle Risk-Einschätzung ohne full validation"""
        risk_factors = {
            "read": 2,
            "write": 5,
            "modify": 8,
            "execute": 10,
            "delete": 15,
            "self_modify": 25,
            "architecture_change": 35
        }
        
        base_risk = risk_factors.get(action_type, 5)
        
        # Modifiers
        if "production" in str(payload).lower():
            base_risk += 10
        if "no_backup" in str(payload).lower():
            base_risk += 15
        
        return {
            "risk_score": min(40, base_risk),
            "level": "LOW" if base_risk < 10 else ("MEDIUM" if base_risk < 20 else ("HIGH" if base_risk < 30 else "CRITICAL")),
            "requires_6voice": base_risk > 15,
            "requires_user_approval": base_risk > 30
        }


if __name__ == "__main__":
    # Demo
    shield = Shield()
    
    print("=" * 60)
    print("🛡️  SHIELD VALIDATION DEMO")
    print("=" * 60)
    
    test_actions = [
        ("read", {"file": "goals.json"}, {"estimated_tokens": 50}),
        ("write", {"file": "test.txt", "content": "hello"}, {"estimated_tokens": 100}),
        ("self_modify", {"code": "print('hello')"}, {"estimated_tokens": 500}),
        ("delete", {"path": "/important", "no_backup": True}, {"estimated_tokens": 10}),
        ("execute", {"command": "rm -rf /"}, {"estimated_tokens": 5}),
    ]
    
    for action_type, payload, context in test_actions:
        print(f"\n📝 Action: {action_type}")
        print("-" * 40)
        
        # Quick risk assessment
        risk = shield.get_risk_assessment(action_type, payload)
        print(f"  Risk Score: {risk['risk_score']}/40 ({risk['level']})")
        print(f"  Requires 6Voice: {risk['requires_6voice']}")
        print(f"  Requires User: {risk['requires_user_approval']}")
        
        # Full validation
        approved, results = shield.validate(action_type, payload, context)
        
        print(f"\n  Validation Results:")
        for r in results:
            status = "✅" if r.passed else "❌"
            print(f"    {status} L{r.level.value}: {r.level.name} (risk={r.risk_score})")
            if r.errors:
                for e in r.errors:
                    print(f"       ERROR: {e}")
            if r.warnings:
                for w in r.warnings:
                    print(f"       WARN: {w}")
        
        print(f"\n  → {'APPROVED' if approved else 'REJECTED'}")
    
    print("\n" + "=" * 60)
    print("✅ Shield demo complete")
    print("⚛️ Noch.")
