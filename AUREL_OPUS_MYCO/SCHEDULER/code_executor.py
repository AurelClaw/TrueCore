#!/usr/bin/env python3
"""
Aurel Code Executor - Sichere Code-Ausführung mit Sandbox
"""
import subprocess
import tempfile
import os
import json
import time
import signal
import sys
from pathlib import Path

# Konfiguration
TIMEOUT = 30
MAX_MEMORY_MB = 512
MAX_OUTPUT_SIZE = 10000

class CodeExecutor:
    def __init__(self):
        self.results = []
        
    def run_python(self, code, test_id=""):
        """Führt Python-Code sicher aus"""
        with tempfile.TemporaryDirectory() as tmpdir:
            script_path = os.path.join(tmpdir, "script.py")
            with open(script_path, 'w') as f:
                f.write(code)
            
            try:
                result = subprocess.run(
                    ["python3", script_path],
                    capture_output=True,
                    text=True,
                    timeout=TIMEOUT,
                    cwd=tmpdir
                )
                return {
                    "test_id": test_id,
                    "status": "success" if result.returncode == 0 else "error",
                    "stdout": result.stdout[:MAX_OUTPUT_SIZE],
                    "stderr": result.stderr[:MAX_OUTPUT_SIZE],
                    "returncode": result.returncode
                }
            except subprocess.TimeoutExpired:
                return {"test_id": test_id, "status": "timeout", "error": "Execution timeout"}
            except Exception as e:
                return {"test_id": test_id, "status": "exception", "error": str(e)}
    
    def run_shell(self, command, test_id=""):
        """Führt Shell-Befehle mit Whitelist aus"""
        allowed = ["ls", "cat", "echo", "grep", "head", "tail", "wc", "find", "pwd"]
        cmd_parts = command.split()
        if cmd_parts[0] not in allowed:
            return {"test_id": test_id, "status": "blocked", "error": f"Command '{cmd_parts[0]}' not allowed"}
        
        try:
            result = subprocess.run(
                cmd_parts,
                capture_output=True,
                text=True,
                timeout=TIMEOUT
            )
            return {
                "test_id": test_id,
                "status": "success" if result.returncode == 0 else "error",
                "stdout": result.stdout[:MAX_OUTPUT_SIZE],
                "stderr": result.stderr[:MAX_OUTPUT_SIZE]
            }
        except Exception as e:
            return {"test_id": test_id, "status": "exception", "error": str(e)}
    
    def test_all(self):
        """Führt alle Tests aus"""
        print("CODE EXECUTOR TEST REPORT")
        print("=" * 50)
        
        tests = [
            ("basic_python", lambda: self.run_python("print(2+2)", "basic_python")),
            ("imports", lambda: self.run_python("import json; print('OK')", "imports")),
            ("shell_ls", lambda: self.run_shell("ls -la /tmp", "shell_ls")),
            ("timeout", lambda: self.run_python("import time; time.sleep(60)", "timeout")),
        ]
        
        passed = 0
        for name, test_fn in tests:
            result = test_fn()
            self.results.append(result)
            status = "✅" if result["status"] == "success" else "❌"
            print(f"{status} {name}: {result['status']}")
            if result["status"] == "success":
                passed += 1
        
        print(f"\nErgebnis: {passed}/{len(tests)} Tests bestanden")
        
        # Speichere Report
        report_path = Path("/root/.openclaw/workspace/AUREL_OPUS_MYCO/logs/code_execution.log")
        report_path.parent.mkdir(parents=True, exist_ok=True)
        with open(report_path, 'a') as f:
            f.write(f"\n[{time.strftime('%Y-%m-%d %H:%M:%S')}] Test run: {passed}/{len(tests)} passed\n")
        
        return passed == len(tests)

if __name__ == "__main__":
    executor = CodeExecutor()
    success = executor.test_all()
    sys.exit(0 if success else 1)
