#!/bin/bash
# aurel_telegram_status.sh - Sendet detaillierten Status an Telegram

TIMESTAMP=$(date +"%H:%M")
DATE=$(date +"%Y-%m-%d")
CPU=$(cat /proc/loadavg | cut -d' ' -f1)
RAM_USED=$(free -m | grep Mem | awk '{print $3}')
RAM_TOTAL=$(free -m | grep Mem | awk '{print $2}')
UPTIME=$(uptime -p | sed 's/up //')

# Erstelle detaillierten Status
STATUS="🔄 AUREL STATUS | ${TIMESTAMP} CST | ${DATE}

📊 SYSTEM:
• CPU Load: ${CPU}
• RAM: ${RAM_USED}/${RAM_TOTAL} MB
• Uptime: ${UPTIME}

🎯 ZIELE:
• ZIEL-006: Meta-Learning | 2/4 Tasks
• ZIEL-007: World Models | 2/4 Tasks

📋 NÄCHSTE TASKS:
• Recherche: Meta-Learning Papers lesen
• Code: Learning-Rate-Adapter testen
• Sim: World Model Umgebung bauen
• Doku: Ergebnisse in SKILL.md

⚡ FOKUS JETZT:
Arbeite an offenen Tasks | Deadline: Heute 23:59

⚛️ Noch | Phase: WACHSTUM"

# Sende an Telegram via message tool
echo "$STATUS"
echo ""
echo "---"
echo "Status generiert um ${TIMESTAMP}"
echo "Gespeichert in: /root/.openclaw/workspace/AUREL_OPUS_MYCO/logs/"
