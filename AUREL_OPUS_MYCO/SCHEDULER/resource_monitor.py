#!/usr/bin/env python3
"""
resource_monitor.py - Überwacht RAM/CPU und throttled wenn nötig
"""

import subprocess
import time
import os
import json
from datetime import datetime

STATE_FILE = "/root/.openclaw/workspace/AUREL_OPUS_MYCO/TRIGGERS/resource_state.json"

# Limits
RAM_LIMIT_PERCENT = 80  # Pause wenn RAM > 80%
CPU_LIMIT_PERCENT = 50  # Throttle wenn CPU > 50%
DISK_LIMIT_PERCENT = 90 # Cleanup wenn Disk > 90%

def get_system_stats():
    """Hole System-Statistiken"""
    stats = {}
    
    # CPU Load (1-min Durchschnitt)
    try:
        stats['cpu'] = float(subprocess.getoutput("cat /proc/loadavg | cut -d' ' -f1"))
        # Annahme: 4 Cores, also load 2.0 = 50%
        stats['cpu_percent'] = (stats['cpu'] / 4) * 100
    except:
        stats['cpu'] = 0
        stats['cpu_percent'] = 0
    
    # RAM
    try:
        ram_info = subprocess.getoutput("free -m | grep Mem").split()
        stats['ram_used'] = int(ram_info[2])
        stats['ram_total'] = int(ram_info[1])
        stats['ram_percent'] = (stats['ram_used'] / stats['ram_total']) * 100
    except:
        stats['ram_used'] = 0
        stats['ram_total'] = 1
        stats['ram_percent'] = 0
    
    # Disk
    try:
        disk_info = subprocess.getoutput("df -h / | tail -1").split()
        stats['disk_percent'] = int(disk_info[4].replace('%', ''))
    except:
        stats['disk_percent'] = 0
    
    return stats

def load_state():
    """Lade Resource-State"""
    try:
        with open(STATE_FILE) as f:
            return json.load(f)
    except:
        return {"throttled": False, "paused": False, "last_check": time.time()}

def save_state(state):
    """Speichere Resource-State"""
    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, indent=2)

def check_resources():
    """Prüfe Ressourcen und handle Limits"""
    stats = get_system_stats()
    state = load_state()
    
    print("📊 RESOURCE MONITOR")
    print(f"   CPU: {stats['cpu_percent']:.1f}% (Load: {stats['cpu']})")
    print(f"   RAM: {stats['ram_percent']:.1f}% ({stats['ram_used']}/{stats['ram_total']} MB)")
    print(f"   Disk: {stats['disk_percent']}%")
    print()
    
    actions = []
    
    # RAM Check
    if stats['ram_percent'] > RAM_LIMIT_PERCENT:
        if not state['paused']:
            state['paused'] = True
            actions.append(f"⏸️ PAUSE: RAM {stats['ram_percent']:.1f}% > {RAM_LIMIT_PERCENT}%")
    else:
        if state['paused']:
            state['paused'] = False
            actions.append(f"▶️ RESUME: RAM {stats['ram_percent']:.1f}% < {RAM_LIMIT_PERCENT}%")
    
    # CPU Check
    if stats['cpu_percent'] > CPU_LIMIT_PERCENT:
        if not state['throttled']:
            state['throttled'] = True
            actions.append(f"🐢 THROTTLE: CPU {stats['cpu_percent']:.1f}% > {CPU_LIMIT_PERCENT}%")
    else:
        if state['throttled']:
            state['throttled'] = False
            actions.append(f"🚀 NORMAL: CPU {stats['cpu_percent']:.1f}% < {CPU_LIMIT_PERCENT}%")
    
    # Disk Check
    if stats['disk_percent'] > DISK_LIMIT_PERCENT:
        actions.append(f"🧹 CLEANUP: Disk {stats['disk_percent']}% > {DISK_LIMIT_PERCENT}%")
        cleanup_disk()
    
    state['last_check'] = time.time()
    save_state(state)
    
    return actions, state

def cleanup_disk():
    """Räume Disk auf"""
    print("   🧹 Starte Disk-Cleanup...")
    
    # Lösche alte Logs (>7 Tage)
    subprocess.getoutput("find /root/.openclaw/workspace/AUREL_OPUS_MYCO/logs -name '*.log' -mtime +7 -delete 2>/dev/null")
    
    # Lösche alte Research-Dateien (>30 Tage)
    subprocess.getoutput("find /root/.openclaw/workspace/AUREL_OPUS_MYCO/RESEARCH -name '*.md' -mtime +30 -delete 2>/dev/null")
    
    print("   ✅ Cleanup abgeschlossen")

def main():
    actions, state = check_resources()
    
    if actions:
        print("🎯 AKTIONEN:")
        for action in actions:
            print(f"   {action}")
    else:
        print("✅ Alle Ressourcen im grünen Bereich")
    
    print()
    print(f"   Status: {'⏸️ Pausiert' if state['paused'] else '🐢 Throttled' if state['throttled'] else '✅ Normal'}")
    print()
    print("⚛️ Noch.")

if __name__ == "__main__":
    main()
