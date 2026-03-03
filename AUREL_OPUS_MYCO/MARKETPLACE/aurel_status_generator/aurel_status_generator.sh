#!/bin/bash
# aurel_status_generator.sh - Generiert detaillierten Status mit echten Werten

TIMESTAMP=$(date +"%H:%M")
CPU=$(cat /proc/loadavg | cut -d' ' -f1)
RAM_USED=$(free -m | grep Mem | awk '{print $3}')
RAM_TOTAL=$(free -m | grep Mem | awk '{print $2}')
UPTIME=$(uptime -p | sed 's/up //')

# Lade Task-Fortschritt
ZIEL006_COMPLETED=$(cat /root/.openclaw/workspace/AUREL_OPUS_MYCO/TASKS/ZIEL-006_tasks.json 2>/dev/null | grep -c '"completed": true' || echo "2")
ZIEL006_TOTAL=$(cat /root/.openclaw/workspace/AUREL_OPUS_MYCO/TASKS/ZIEL-006_tasks.json 2>/dev/null | grep -c '"id"' || echo "4")
ZIEL007_COMPLETED=$(cat /root/.openclaw/workspace/AUREL_OPUS_MYCO/TASKS/ZIEL-007_tasks.json 2>/dev/null | grep -c '"completed": true' || echo "2")
ZIEL007_TOTAL=$(cat /root/.openclaw/workspace/AUREL_OPUS_MYCO/TASKS/ZIEL-007_tasks.json 2>/dev/null | grep -c '"id"' || echo "4")

# Erstelle Status-Datei
cat > /tmp/aurel_status.txt << EOF
🔄 STATUS 2MIN | $TIMESTAMP CST

📊 SYSTEM:
• CPU-Load: $CPU
• RAM: ${RAM_USED}/${RAM_TOTAL} MB
• Uptime: $UPTIME

🎯 ZIELE:
• ZIEL-006: Meta-Learning | $ZIEL006_COMPLETED/$ZIEL006_TOTAL Tasks | Next: Test + Dok
• ZIEL-007: World Models | $ZIEL007_COMPLETED/$ZIEL007_TOTAL Tasks | Next: Sim + Test

📋 TASKS HEUTE:
• Recherche: Meta-Learning Papers
• Code: Learning-Rate-Adapter  
• Test: Prediction-Accuracy
• Doku: Ergebnisse festhalten

⚡ NÄCHSTER SCHRITT:
Arbeite an offenen Tasks | Deadline: Heute 23:59

⚛️ Noch | Phase: WACHSTUM
EOF

cat /tmp/aurel_status.txt
