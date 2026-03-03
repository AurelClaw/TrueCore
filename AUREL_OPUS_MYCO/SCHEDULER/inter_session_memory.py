#!/usr/bin/env python3
"""
Inter-Session Memory Sync - Persistiert Memory-Vektoren
"""
import json
import time
import os
from pathlib import Path

class MemorySync:
    def __init__(self):
        self.workspace = Path("/root/.openclaw/workspace")
        self.memory_dir = self.workspace / "memory"
        self.state_file = self.workspace / "AUREL_OPUS_MYCO" / "STATE" / "memory_index.json"
        
    def sync(self):
        """Synchronisiert Memory-Dateien"""
        print("[AUREL Memory Synchronization]")
        print(f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Sammle alle Memory-Dateien
        memory_files = list(self.memory_dir.glob("*.md"))
        print(f"\nGefunden: {len(memory_files)} Memory-Dateien")
        
        # Erstelle Index
        index = {
            "last_sync": time.time(),
            "files": [],
            "total_size": 0
        }
        
        for f in memory_files:
            stats = f.stat()
            index["files"].append({
                "name": f.name,
                "size": stats.st_size,
                "modified": stats.st_mtime
            })
            index["total_size"] += stats.st_size
        
        # Speichere Index
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.state_file, 'w') as f:
            json.dump(index, f, indent=2)
        
        print(f"Index aktualisiert: {len(index['files'])} Dateien")
        print(f"Gesamtgröße: {index['total_size'] / 1024:.1f} KB")
        print("Status: SUCCESS")
        
        return True

if __name__ == "__main__":
    sync = MemorySync()
    sync.sync()
