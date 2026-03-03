#!/usr/bin/env python3
"""
error_recovery.py - Retry-Logik und Fehlerbehandlung für Cron-Jobs
"""

import json
import time
import os
from datetime import datetime

RETRY_FILE = "/root/.openclaw/workspace/AUREL_OPUS_MYCO/TRIGGERS/retry_queue.json"
MAX_RETRIES = 3
BACKOFF_BASE = 2  # Sekunden

def load_retry_queue():
    """Lade Retry-Queue"""
    try:
        with open(RETRY_FILE) as f:
            return json.load(f)
    except:
        return {"failed_jobs": [], "last_check": time.time()}

def save_retry_queue(queue):
    """Speichere Retry-Queue"""
    os.makedirs(os.path.dirname(RETRY_FILE), exist_ok=True)
    with open(RETRY_FILE, 'w') as f:
        json.dump(queue, f, indent=2)

def add_failed_job(job_id, job_name, error_message, payload):
    """Füge fehlgeschlagenen Job zur Queue hinzu"""
    queue = load_retry_queue()
    
    # Prüfe ob Job bereits in Queue
    for job in queue["failed_jobs"]:
        if job["id"] == job_id:
            job["retry_count"] += 1
            job["last_error"] = error_message
            job["last_attempt"] = time.time()
            break
    else:
        queue["failed_jobs"].append({
            "id": job_id,
            "name": job_name,
            "error": error_message,
            "payload": payload,
            "retry_count": 1,
            "first_attempt": time.time(),
            "last_attempt": time.time()
        })
    
    save_retry_queue(queue)
    print(f"⚠️ Job {job_name} zur Retry-Queue hinzugefügt (Versuch 1/{MAX_RETRIES})")

def should_retry(job):
    """Prüfe ob Job retry-tauglich ist"""
    if job["retry_count"] >= MAX_RETRIES:
        return False
    
    # Exponential Backoff
    backoff = BACKOFF_BASE ** job["retry_count"]
    time_since_last = time.time() - job["last_attempt"]
    
    return time_since_last >= backoff

def process_retry_queue():
    """Verarbeite Retry-Queue"""
    queue = load_retry_queue()
    queue["last_check"] = time.time()
    
    retried = []
    failed_permanently = []
    
    for job in queue["failed_jobs"]:
        if job["retry_count"] >= MAX_RETRIES:
            failed_permanently.append(job)
            print(f"❌ Job {job['name']} permanent failed nach {MAX_RETRIES} Versuchen")
            continue
        
        if should_retry(job):
            print(f"🔄 Retry Job {job['name']} (Versuch {job['retry_count'] + 1}/{MAX_RETRIES})")
            # Hier würde der tatsächliche Retry passieren
            # Für jetzt nur Simulation
            job["retry_count"] += 1
            job["last_attempt"] = time.time()
            retried.append(job)
    
    # Entferne permanent failed jobs
    queue["failed_jobs"] = [j for j in queue["failed_jobs"] if j not in failed_permanently]
    
    save_retry_queue(queue)
    
    return len(retried), len(failed_permanently)

def get_queue_status():
    """Zeige Queue-Status"""
    queue = load_retry_queue()
    
    print("📊 RETRY QUEUE STATUS")
    print(f"   Wartende Jobs: {len(queue['failed_jobs'])}")
    
    for job in queue["failed_jobs"]:
        status = "🔄 Bereit" if should_retry(job) else "⏳ Warte"
        print(f"   {status} {job['name']} (Versuch {job['retry_count']}/{MAX_RETRIES})")
    
    return len(queue["failed_jobs"])

if __name__ == "__main__":
    print("🛡️ ERROR RECOVERY SYSTEM")
    print()
    
    # Verarbeite Queue
    retried, failed = process_retry_queue()
    
    # Zeige Status
    pending = get_queue_status()
    
    print()
    print(f"✅ Verarbeitet: {retried} retried, {failed} permanent failed")
    print(f"⏳ Noch wartend: {pending}")
    print()
    print("⚛️ Noch.")
