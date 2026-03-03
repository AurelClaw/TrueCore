#!/usr/bin/env python3
"""
aurel_database.py - SQLite Datenbank für Ziele, Tasks und Metriken
"""

import sqlite3
import json
from datetime import datetime
import os

DB_PATH = "/root/.openclaw/workspace/AUREL_OPUS_MYCO/aurel.db"

def init_db():
    """Initialisiere Datenbank mit Tabellen"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Ziele Tabelle
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS goals (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT,
            status TEXT DEFAULT 'pending',
            priority TEXT DEFAULT 'normal',
            progress REAL DEFAULT 0.0,
            created_at TEXT,
            activated_at TEXT,
            completed_at TEXT,
            deadline TEXT,
            uncertainty REAL DEFAULT 0.5
        )
    ''')
    
    # Tasks Tabelle
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER,
            goal_id TEXT,
            description TEXT NOT NULL,
            completed BOOLEAN DEFAULT 0,
            in_progress BOOLEAN DEFAULT 0,
            created_at TEXT,
            started_at TEXT,
            completed_at TEXT,
            FOREIGN KEY (goal_id) REFERENCES goals(id),
            PRIMARY KEY (id, goal_id)
        )
    ''')
    
    # Metriken Tabelle
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS metrics (
            timestamp TEXT PRIMARY KEY,
            cpu_load REAL,
            ram_used INTEGER,
            ram_total INTEGER,
            active_goals INTEGER,
            completed_tasks INTEGER,
            total_tasks INTEGER,
            files_created INTEGER
        )
    ''')
    
    # Logs Tabelle
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            level TEXT,
            message TEXT,
            source TEXT
        )
    ''')
    
    conn.commit()
    conn.close()
    print("✅ Datenbank initialisiert:", DB_PATH)

def migrate_from_json():
    """Migriere bestehende JSON-Daten zu SQLite"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Lade goals.json
    try:
        with open("/root/.openclaw/workspace/AUREL_OPUS_MYCO/AGENCY/goals.json") as f:
            data = json.load(f)
        
        for goal in data.get("goals", []):
            cursor.execute('''
                INSERT OR REPLACE INTO goals 
                (id, name, description, status, priority, progress, created_at, activated_at, completed_at, deadline, uncertainty)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                goal.get("id"),
                goal.get("name", ""),
                goal.get("description", ""),
                goal.get("status", "pending"),
                goal.get("priority", "normal"),
                goal.get("progress", 0.0),
                goal.get("created_at"),
                goal.get("activated_at"),
                goal.get("completed_at"),
                goal.get("deadline"),
                goal.get("uncertainty", 0.5)
            ))
        
        print(f"✅ {len(data.get('goals', []))} Ziele migriert")
        
    except Exception as e:
        print(f"⚠️ Migration goals.json: {e}")
    
    # Lade Tasks für jedes Ziel
    tasks_dir = "/root/.openclaw/workspace/AUREL_OPUS_MYCO/TASKS"
    if os.path.exists(tasks_dir):
        for task_file in os.listdir(tasks_dir):
            if task_file.endswith("_tasks.json"):
                goal_id = task_file.replace("_tasks.json", "")
                try:
                    with open(f"{tasks_dir}/{task_file}") as f:
                        tasks = json.load(f)
                    
                    for task in tasks:
                        cursor.execute('''
                            INSERT OR REPLACE INTO tasks
                            (id, goal_id, description, completed, in_progress, started_at, completed_at)
                            VALUES (?, ?, ?, ?, ?, ?, ?)
                        ''', (
                            task.get("id"),
                            goal_id,
                            task.get("description", ""),
                            task.get("completed", False),
                            task.get("in_progress", False),
                            task.get("started_at"),
                            task.get("completed_at")
                        ))
                    
                    print(f"✅ {len(tasks)} Tasks für {goal_id} migriert")
                    
                except Exception as e:
                    print(f"⚠️ Migration {task_file}: {e}")
    
    conn.commit()
    conn.close()

def log_event(level, message, source="system"):
    """Logge ein Ereignis"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO logs (timestamp, level, message, source)
        VALUES (?, ?, ?, ?)
    ''', (datetime.now().isoformat(), level, message, source))
    
    conn.commit()
    conn.close()

def get_active_goal():
    """Hole aktives Ziel"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT * FROM goals WHERE status = 'active' ORDER BY priority, deadline LIMIT 1
    ''')
    
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return {
            "id": row[0],
            "name": row[1],
            "description": row[2],
            "status": row[3],
            "priority": row[4],
            "progress": row[5]
        }
    return None

def update_task_status(goal_id, task_id, completed=False, in_progress=False):
    """Update Task-Status"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    now = datetime.now().isoformat()
    
    if completed:
        cursor.execute('''
            UPDATE tasks SET completed = 1, in_progress = 0, completed_at = ?
            WHERE goal_id = ? AND id = ?
        ''', (now, goal_id, task_id))
    elif in_progress:
        cursor.execute('''
            UPDATE tasks SET in_progress = 1, started_at = ?
            WHERE goal_id = ? AND id = ?
        ''', (now, goal_id, task_id))
    
    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
    migrate_from_json()
    log_event("INFO", "Datenbank initialisiert und migriert", "setup")
    print("\n⚛️ Noch.")
