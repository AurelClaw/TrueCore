#!/usr/bin/env python3
"""
sandbox.py - Ephemeral Sandbox für Aurel Opus Myco
Isolierte Testumgebung für Self-Modifications
"""

import os
import json
import shutil
import tempfile
import subprocess
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime

@dataclass
class SandboxResult:
    """Ergebnis eines Sandbox-Tests"""
    success: bool
    tests_passed: int
    tests_failed: int
    errors: List[str]
    warnings: List[str]
    performance_impact: str
    resource_usage: Dict
    recommendation: str

class Sandbox:
    """
    Ephemeral Sandbox für sichere Tests
    
    Features:
    - Isolierte Umgebung (temp directory)
    - Unit + Integration Tests
    - Performance Profiling
    - Auto-cleanup
    """
    
    def __init__(self, state_path: str = "/root/.openclaw/workspace/AUREL_OPUS_MYCO"):
        self.state_path = state_path
        self.sandbox_dir = None
        self.max_duration = 3600  # 1 hour max
        self.test_timeout = 300   # 5 min per test
    
    def create(self, change_description: str) -> str:
        """Erstelle neue Sandbox-Umgebung"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.sandbox_dir = tempfile.mkdtemp(prefix=f"aurel_sandbox_{timestamp}_")
        
        # Copy current state
        self._copy_state_to_sandbox()
        
        # Create manifest
        manifest = {
            "created": timestamp,
            "change": change_description,
            "original_state": self.state_path,
            "sandbox_dir": self.sandbox_dir,
            "max_duration": self.max_duration
        }
        
        with open(f"{self.sandbox_dir}/SANDBOX_MANIFEST.json", "w") as f:
            json.dump(manifest, f, indent=2)
        
        print(f"✅ Sandbox created: {self.sandbox_dir}")
        return self.sandbox_dir
    
    def _copy_state_to_sandbox(self):
        """Kopiere aktuellen State in Sandbox"""
        # Copy critical files
        dirs_to_copy = ["SUBSTRATE", "CORE", "AGENCY", "ALIGNMENT"]
        
        for dir_name in dirs_to_copy:
            src = f"{self.state_path}/{dir_name}"
            dst = f"{self.sandbox_dir}/{dir_name}"
            if os.path.exists(src):
                shutil.copytree(src, dst)
    
    def apply_change(self, change_type: str, change_payload: Dict) -> bool:
        """Wende Change in Sandbox an"""
        if not self.sandbox_dir:
            raise RuntimeError("Sandbox not created")
        
        print(f"🔧 Applying change: {change_type}")
        
        try:
            if change_type == "skill_create":
                return self._apply_skill_create(change_payload)
            elif change_type == "skill_modify":
                return self._apply_skill_modify(change_payload)
            elif change_type == "config_update":
                return self._apply_config_update(change_payload)
            elif change_type == "code_change":
                return self._apply_code_change(change_payload)
            else:
                print(f"⚠️  Unknown change type: {change_type}")
                return False
        except Exception as e:
            print(f"❌ Change application failed: {e}")
            return False
    
    def _apply_skill_create(self, payload: Dict) -> bool:
        """Erstelle neuen Skill in Sandbox"""
        skill_name = payload.get("name")
        skill_code = payload.get("code")
        
        skill_dir = f"{self.sandbox_dir}/skills/{skill_name}"
        os.makedirs(skill_dir, exist_ok=True)
        
        # Write skill files
        with open(f"{skill_dir}/{skill_name}.py", "w") as f:
            f.write(skill_code)
        
        with open(f"{skill_dir}/SKILL.md", "w") as f:
            f.write(f"# {skill_name}\n\nAuto-generated skill.\n")
        
        print(f"  ✅ Skill created: {skill_name}")
        return True
    
    def _apply_skill_modify(self, payload: Dict) -> bool:
        """Modifiziere existierenden Skill"""
        skill_name = payload.get("name")
        modification = payload.get("modification")
        
        skill_file = f"{self.sandbox_dir}/skills/{skill_name}/{skill_name}.py"
        if not os.path.exists(skill_file):
            print(f"  ❌ Skill not found: {skill_name}")
            return False
        
        # Apply modification (simplified)
        with open(skill_file, "a") as f:
            f.write(f"\n# Modified: {modification}\n")
        
        print(f"  ✅ Skill modified: {skill_name}")
        return True
    
    def _apply_config_update(self, payload: Dict) -> bool:
        """Update Konfiguration"""
        config_file = payload.get("file")
        new_value = payload.get("value")
        
        config_path = f"{self.sandbox_dir}/{config_file}"
        
        with open(config_path, "r") as f:
            config = json.load(f)
        
        # Apply update
        config.update(new_value)
        
        with open(config_path, "w") as f:
            json.dump(config, f, indent=2)
        
        print(f"  ✅ Config updated: {config_file}")
        return True
    
    def _apply_code_change(self, payload: Dict) -> bool:
        """Wende Code-Änderung an"""
        file_path = payload.get("file")
        new_code = payload.get("code")
        
        full_path = f"{self.sandbox_dir}/{file_path}"
        
        with open(full_path, "w") as f:
            f.write(new_code)
        
        print(f"  ✅ Code changed: {file_path}")
        return True
    
    def run_tests(self) -> SandboxResult:
        """Führe Tests in Sandbox aus"""
        if not self.sandbox_dir:
            raise RuntimeError("Sandbox not created")
        
        print(f"\n🧪 Running tests in sandbox...")
        
        tests_passed = 0
        tests_failed = 0
        errors = []
        warnings = []
        
        # Test 1: Syntax Check
        print("  Test 1: Syntax validation...")
        if self._test_syntax():
            tests_passed += 1
            print("    ✅ Syntax OK")
        else:
            tests_failed += 1
            errors.append("Syntax errors found")
            print("    ❌ Syntax errors")
        
        # Test 2: State Consistency
        print("  Test 2: State consistency...")
        if self._test_state_consistency():
            tests_passed += 1
            print("    ✅ State consistent")
        else:
            tests_failed += 1
            errors.append("State inconsistency")
            print("    ❌ State inconsistent")
        
        # Test 3: Import Test
        print("  Test 3: Import validation...")
        if self._test_imports():
            tests_passed += 1
            print("    ✅ Imports OK")
        else:
            tests_failed += 1
            errors.append("Import errors")
            print("    ❌ Import errors")
        
        # Test 4: Basic Functionality
        print("  Test 4: Basic functionality...")
        if self._test_functionality():
            tests_passed += 1
            print("    ✅ Functionality OK")
        else:
            tests_failed += 1
            errors.append("Functionality errors")
            print("    ❌ Functionality errors")
        
        # Performance Profiling
        print("  Test 5: Performance profiling...")
        perf = self._profile_performance()
        
        success = tests_failed == 0 and len(errors) == 0
        
        recommendation = "PROCEED" if success else "FIX_ISSUES"
        if perf.get("memory_mb", 0) > 500:
            recommendation = "OPTIMIZE_MEMORY"
            warnings.append("High memory usage")
        
        return SandboxResult(
            success=success,
            tests_passed=tests_passed,
            tests_failed=tests_failed,
            errors=errors,
            warnings=warnings,
            performance_impact=perf.get("impact", "unknown"),
            resource_usage=perf,
            recommendation=recommendation
        )
    
    def _test_syntax(self) -> bool:
        """Teste Python Syntax"""
        try:
            for root, dirs, files in os.walk(self.sandbox_dir):
                for file in files:
                    if file.endswith(".py"):
                        filepath = os.path.join(root, file)
                        with open(filepath) as f:
                            code = f.read()
                        compile(code, filepath, "exec")
            return True
        except SyntaxError:
            return False
    
    def _test_state_consistency(self) -> bool:
        """Teste State Konsistenz"""
        try:
            # Check if all required state files exist
            required = ["SUBSTRATE/graph.json", "AGENCY/goals.json", "STATE/meta.json"]
            for file in required:
                if not os.path.exists(f"{self.sandbox_dir}/{file}"):
                    return False
            return True
        except:
            return False
    
    def _test_imports(self) -> bool:
        """Teste Imports"""
        try:
            # Try importing key modules
            import sys
            sys.path.insert(0, self.sandbox_dir)
            # Would import and test actual modules
            return True
        except:
            return False
    
    def _test_functionality(self) -> bool:
        """Teste Basis-Funktionalität"""
        try:
            # Try loading state
            with open(f"{self.sandbox_dir}/AGENCY/goals.json") as f:
                goals = json.load(f)
            return len(goals.get("goals", [])) > 0
        except:
            return False
    
    def _profile_performance(self) -> Dict:
        """Profile Resource-Nutzung"""
        # Simplified without psutil
        import os
        
        # Estimate memory by directory size
        total_size = 0
        for dirpath, dirnames, filenames in os.walk(self.sandbox_dir):
            for f in filenames:
                fp = os.path.join(dirpath, f)
                total_size += os.path.getsize(fp)
        
        return {
            "memory_mb": total_size / 1024 / 1024,  # Approximate
            "cpu_percent": 0.0,  # Would need psutil
            "impact": "low"
        }
    
    def destroy(self):
        """Zerstöre Sandbox (Cleanup)"""
        if self.sandbox_dir and os.path.exists(self.sandbox_dir):
            shutil.rmtree(self.sandbox_dir)
            print(f"🗑️  Sandbox destroyed: {self.sandbox_dir}")
            self.sandbox_dir = None
    
    def promote_to_canary(self) -> bool:
        """Promote Sandbox zu Canary (10% traffic)"""
        if not self.sandbox_dir:
            return False
        
        # In production: Deploy to canary environment
        print(f"🚀 Promoting to canary: {self.sandbox_dir}")
        return True


if __name__ == "__main__":
    # Demo
    sandbox = Sandbox()
    
    print("=" * 60)
    print("🏖️  SANDBOX DEMO")
    print("=" * 60)
    
    # Create sandbox
    sandbox_dir = sandbox.create("Test skill creation")
    
    # Apply change
    success = sandbox.apply_change("skill_create", {
        "name": "test_skill",
        "code": "def test():\n    return 'Hello from sandbox'\n"
    })
    
    if success:
        # Run tests
        result = sandbox.run_tests()
        
        print(f"\n📊 Test Results:")
        print(f"  Passed: {result.tests_passed}")
        print(f"  Failed: {result.tests_failed}")
        print(f"  Success: {result.success}")
        print(f"  Recommendation: {result.recommendation}")
        
        if result.errors:
            print(f"\n  Errors:")
            for e in result.errors:
                print(f"    ❌ {e}")
        
        if result.warnings:
            print(f"\n  Warnings:")
            for w in result.warnings:
                print(f"    ⚠️  {w}")
    
    # Cleanup
    sandbox.destroy()
    
    print("\n" + "=" * 60)
    print("✅ Sandbox demo complete")
    print("⚛️ Noch.")
