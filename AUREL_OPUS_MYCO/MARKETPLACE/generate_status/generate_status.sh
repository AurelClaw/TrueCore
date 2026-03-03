#!/bin/bash
# generate_status.sh - Erstellt dynamischen Status mit echten Werten

TIMESTAMP=$(date +"%H:%M")
DATE=$(date +"%Y-%m-%d")

# Aktives Ziel
CURRENT_GOAL="ZIEL-015"
GOAL_NAME="Meta-Learning Phase 2"

# Tasks laden
TASK_FILE="/root/.openclaw/workspace/AUREL_OPUS_MYCO/TASKS/${CURRENT_GOAL}_tasks.json"
if [ -f "$TASK_FILE" ]; then
    TOTAL_TASKS=$(grep -c '"id"' "$TASK_FILE")
    COMPLETED_TASKS=$(grep -c '"completed": true' "$TASK_FILE")
else
    TOTAL_TASKS=4
    COMPLETED_TASKS=0
fi

# Fortschritt berechnen
if [ "$TOTAL_TASKS" -gt 0 ]; then
    PROGRESS=$((COMPLETED_TASKS * 100 / TOTAL_TASKS))
else
    PROGRESS=0
fi

# Erstellte Dateien zählen (heute)
CREATED_FILES=$(find /root/.openclaw/workspace/AUREL_OPUS_MYCO -name "*.py" -o -name "*.sh" -o -name "*.md" 2>/dev/null | wc -l)

# Nächster Task
NEXT_TASK=$(grep -B2 '"completed": false' "$TASK_FILE" 2>/dev/null | grep "description" | head -1 | sed 's/.*"description": "\([^"]*\)".*/\1/' | cut -c1-30)
if [ -z "$NEXT_TASK" ]; then
    NEXT_TASK="Alle Tasks erledigt!"
fi

# Status erstellen
STATUS="🔄 STATUS ${TIMESTAMP} | ${CURRENT_GOAL} ${GOAL_NAME} | Fortschritt: ${PROGRESS}% | Tasks: ${COMPLETED_TASKS}/${TOTAL_TASKS} | Dateien: ${CREATED_FILES} | Nächster: ${NEXT_TASK}... | ⚛️ Noch"

# Ausgabe
echo "$STATUS"

# Speichere für Cron-Job
echo "$STATUS" > /tmp/aurel_status.txt
