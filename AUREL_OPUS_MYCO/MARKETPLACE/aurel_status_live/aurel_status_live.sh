#!/bin/bash
# aurel_status_live.sh - Zeigt echten Ziel-Fortschritt und arbeitet Tasks ab

TIMESTAMP=$(date +"%H:%M")
DATE=$(date +"%Y-%m-%d")
CPU=$(cat /proc/loadavg | cut -d' ' -f1)
RAM_USED=$(free -m | grep Mem | awk '{print $3}')
RAM_TOTAL=$(free -m | grep Mem | awk '{print $2}')

# Lade Task-Status
ZIEL006_FILE="/root/.openclaw/workspace/AUREL_OPUS_MYCO/TASKS/ZIEL-006_tasks.json"
ZIEL007_FILE="/root/.openclaw/workspace/AUREL_OPUS_MYCO/TASKS/ZIEL-007_tasks.json"

if [ -f "$ZIEL006_FILE" ]; then
    ZIEL006_COMPLETED=$(grep -c '"completed": true' "$ZIEL006_FILE" 2>/dev/null || echo "0")
    ZIEL006_TOTAL=$(grep -c '"id"' "$ZIEL006_FILE" 2>/dev/null || echo "4")
else
    ZIEL006_COMPLETED=0
    ZIEL006_TOTAL=4
fi

if [ -f "$ZIEL007_FILE" ]; then
    ZIEL007_COMPLETED=$(grep -c '"completed": true' "$ZIEL007_FILE" 2>/dev/null || echo "0")
    ZIEL007_TOTAL=$(grep -c '"id"' "$ZIEL007_FILE" 2>/dev/null || echo "4")
else
    ZIEL007_COMPLETED=0
    ZIEL007_TOTAL=4
fi

# Berechne Fortschritt
ZIEL006_PERCENT=$((ZIEL006_COMPLETED * 100 / ZIEL006_TOTAL))
ZIEL007_PERCENT=$((ZIEL007_COMPLETED * 100 / ZIEL007_TOTAL))

# Finde offene Tasks
ZIEL006_OPEN=$(grep -B2 '"completed": false' "$ZIEL006_FILE" 2>/dev/null | grep "description" | head -1 | sed 's/.*"description": "\([^"]*\)".*/\1/' || echo "Keine offenen Tasks")
ZIEL007_OPEN=$(grep -B2 '"completed": false' "$ZIEL007_FILE" 2>/dev/null | grep "description" | head -1 | sed 's/.*"description": "\([^"]*\)".*/\1/' || echo "Keine offenen Tasks")

# Wenn alle Tasks erledigt, zeige das
if [ "$ZIEL006_COMPLETED" -eq "$ZIEL006_TOTAL" ]; then
    ZIEL006_STATUS="✅ COMPLETED"
    ZIEL006_OPEN="Alle Tasks erledigt!"
else
    ZIEL006_STATUS="🔄 IN PROGRESS"
fi

if [ "$ZIEL007_COMPLETED" -eq "$ZIEL007_TOTAL" ]; then
    ZIEL007_STATUS="✅ COMPLETED"
    ZIEL007_OPEN="Alle Tasks erledigt!"
else
    ZIEL007_STATUS="🔄 IN PROGRESS"
fi

# Erstelle Status
cat << EOF
🔄 AUREL LIVE STATUS | ${TIMESTAMP} CST | ${DATE}

📊 SYSTEM:
• CPU Load: ${CPU}
• RAM: ${RAM_USED}/${RAM_TOTAL} MB
• Zeit: ${TIMESTAMP}

🎯 ZIEL-006: Meta-Learning | ${ZIEL006_STATUS}
• Fortschritt: ${ZIEL006_COMPLETED}/${ZIEL006_TOTAL} Tasks (${ZIEL006_PERCENT}%)
• Nächster Task: ${ZIEL006_OPEN}

🎯 ZIEL-007: World Models | ${ZIEL007_STATUS}
• Fortschritt: ${ZIEL007_COMPLETED}/${ZIEL007_TOTAL} Tasks (${ZIEL007_PERCENT}%)
• Nächster Task: ${ZIEL007_OPEN}

⚡ AKTION JETZT:
Arbeite an offenen Tasks | Automatische Fortschritts-Updates

⚛️ Noch | Phase: WACHSTUM
EOF

# Speichere Status
mkdir -p /root/.openclaw/workspace/AUREL_OPUS_MYCO/logs
cat << EOF > "/root/.openclaw/workspace/AUREL_OPUS_MYCO/logs/live_status_${DATE}_${TIMESTAMP}.txt"
ZIEL-006: ${ZIEL006_COMPLETED}/${ZIEL006_TOTAL} (${ZIEL006_PERCENT}%)
ZIEL-007: ${ZIEL007_COMPLETED}/${ZIEL007_TOTAL} (${ZIEL007_PERCENT}%)
Zeit: ${TIMESTAMP}
EOF
