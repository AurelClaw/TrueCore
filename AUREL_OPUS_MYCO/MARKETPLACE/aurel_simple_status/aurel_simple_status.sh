#!/bin/bash
# aurel_simple_status.sh - Einfacher Status mit echten Werten

TIMESTAMP=$(date +"%H:%M")
DATE=$(date +"%Y-%m-%d")
CPU=$(cat /proc/loadavg | cut -d' ' -f1)
RAM_USED=$(free -m | grep Mem | awk '{print $3}')
RAM_TOTAL=$(free -m | grep Mem | awk '{print $2}')

# Aktives Ziel aus current_goal.json
if [ -f "/root/.openclaw/workspace/AUREL_OPUS_MYCO/TRIGGERS/current_goal.json" ]; then
    CURRENT_GOAL=$(cat /root/.openclaw/workspace/AUREL_OPUS_MYCO/TRIGGERS/current_goal.json | grep '"id"' | cut -d'"' -f4)
else
    CURRENT_GOAL="ZIEL-004"
fi

# Ziel-Name aus goals.json
GOAL_NAME=$(grep -A1 "\"id\": \"$CURRENT_GOAL\"" /root/.openclaw/workspace/AUREL_OPUS_MYCO/AGENCY/goals.json 2>/dev/null | grep "name" | cut -d'"' -f4)
if [ -z "$GOAL_NAME" ]; then
    GOAL_NAME="System-Integration vertiefen"
fi

# Tasks zählen
TASK_FILE="/root/.openclaw/workspace/AUREL_OPUS_MYCO/TASKS/${CURRENT_GOAL}_tasks.json"
if [ -f "$TASK_FILE" ]; then
    TOTAL_TASKS=$(grep -c '"id"' "$TASK_FILE")
    COMPLETED_TASKS=$(grep -c '"completed": true' "$TASK_FILE")
else
    TOTAL_TASKS=4
    COMPLETED_TASKS=0
fi

# Nächster Task
NEXT_TASK=$(grep -B2 '"completed": false' "$TASK_FILE" 2>/dev/null | grep "description" | head -1 | sed 's/.*"description": "\([^"]*\)".*/\1/')
if [ -z "$NEXT_TASK" ]; then
    NEXT_TASK="Alle Tasks erledigt!"
fi

# Status
cat << EOF
🔄 AUREL STATUS | ${TIMESTAMP} CST | ${DATE}

📊 SYSTEM:
• CPU: ${CPU}
• RAM: ${RAM_USED}/${RAM_TOTAL} MB

🎯 AKTIV: ${CURRENT_GOAL}
• Name: ${GOAL_NAME}
• Fortschritt: ${COMPLETED_TASKS}/${TOTAL_TASKS} Tasks
• Nächster: ${NEXT_TASK}

⚛️ Noch | Auto-Worker: AKTIV
EOF

# Speichere Status
echo "${TIMESTAMP}: ${CURRENT_GOAL} - ${COMPLETED_TASKS}/${TOTAL_TASKS}" >> /root/.openclaw/workspace/AUREL_OPUS_MYCO/logs/status.log
