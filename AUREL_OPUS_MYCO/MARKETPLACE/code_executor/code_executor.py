#!/usr/bin/env python3
"""
code_executor.py - Führt Code wirklich aus und testet Ergebnisse
"""

import subprocess
import os
import sys
import tempfile
import json
from datetime import datetime

EXECUTION_LOG = "/root/.openclaw/workspace/AUREL_OPUS_MYCO/logs/code_execution.log"

def log_execution(code_file, result, success):
    """Logge Code-Ausführung"""
    os.makedirs(os.path.dirname(EXECUTION_LOG), exist_ok=True)
    with open(EXECUTION_LOG, 'a') as f:
        status = "✅ SUCCESS" if success else "❌ FAILED"
        f.write(f"{datetime.now().isoformat()}: {status} {code_file}\n")
        if not success:
            f.write(f"  Error: {result}\n")

def execute_python(code, timeout=30):
    """Führe Python-Code sicher aus"""
    # Erstelle temporäre Datei
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(code)
        temp_file = f.name
    
    try:
        # Führe Code aus
        result = subprocess.run(
            [sys.executable, temp_file],
            capture_output=True,
            text=True,
            timeout=timeout
        )
        
        success = result.returncode == 0
        output = result.stdout if success else result.stderr
        
        log_execution(temp_file, output, success)
        
        return {
            "success": success,
            "output": output,
            "returncode": result.returncode
        }
        
    except subprocess.TimeoutExpired:
        log_execution(temp_file, "Timeout", False)
        return {"success": False, "output": "Execution timeout", "returncode": -1}
    except Exception as e:
        log_execution(temp_file, str(e), False)
        return {"success": False, "output": str(e), "returncode": -1}
    finally:
        # Cleanup
        try:
            os.unlink(temp_file)
        except:
            pass

def test_skill(skill_path):
    """Teste einen Skill"""
    print(f"🧪 Teste Skill: {skill_path}")
    
    # Prüfe ob SKILL.md existiert
    skill_md = os.path.join(skill_path, "SKILL.md")
    if not os.path.exists(skill_md):
        return {"success": False, "error": "Keine SKILL.md gefunden"}
    
    # Prüfe ob ausführbare Scripts existieren
    scripts = []
    for root, dirs, files in os.walk(skill_path):
        for file in files:
            if file.endswith('.py') or file.endswith('.sh'):
                scripts.append(os.path.join(root, file))
    
    if not scripts:
        return {"success": False, "error": "Keine ausführbaren Scripts gefunden"}
    
    # Teste erstes Python-Script
    for script in scripts:
        if script.endswith('.py'):
            with open(script) as f:
                code = f.read()
            
            result = execute_python(code)
            return {
                "success": result["success"],
                "script": script,
                "output": result["output"]
            }
    
    return {"success": True, "message": f"{len(scripts)} Scripts gefunden"}

def run_tests():
    """Führe alle Tests aus"""
    print("🧪 RUNNING TESTS")
    print("=================")
    print()
    
    skills_dir = "/root/.openclaw/workspace/skills"
    results = []
    
    if os.path.exists(skills_dir):
        for skill in os.listdir(skills_dir):
            skill_path = os.path.join(skills_dir, skill)
            if os.path.isdir(skill_path):
                result = test_skill(skill_path)
                results.append({"skill": skill, **result})
                
                status = "✅" if result.get("success") else "❌"
                print(f"{status} {skill}: {result.get('message', result.get('error', 'OK'))}")
    
    print()
    print(f"✅ {sum(1 for r in results if r.get('success'))}/{len(results)} Skills OK")
    
    return results

def main():
    results = run_tests()
    
    # Speichere Test-Report
    report_file = f"/root/.openclaw/workspace/AUREL_OPUS_MYCO/logs/test_report_{int(time.time())}.json"
    with open(report_file, 'w') as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "results": results
        }, f, indent=2)
    
    print(f"📄 Report gespeichert: {report_file}")
    print()
    print("⚛️ Noch.")

if __name__ == "__main__":
    import time
    main()
