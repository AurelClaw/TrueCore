#!/bin/bash
# aurel_loop_master.sh - Master-Script für Minuten-Loop mit Sub-Agenten
# Wird von Cron alle 5 Minuten aufgerufen

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
LOG_DIR="/root/.openclaw/workspace/AUREL_OPUS_MYCO/logs"
mkdir -p "$LOG_DIR"

LOG_FILE="$LOG_DIR/loop_master_$TIMESTAMP.log"
REPORT_FILE="$LOG_DIR/loop_report_$TIMESTAMP.txt"

echo "=== AUREL LOOP MASTER - $TIMESTAMP ===" | tee "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

# Phase 1: Wahrnehmen
echo "1️⃣ WAHRNEHMEN..." | tee -a "$LOG_FILE"
cd /root/.openclaw/workspace/AUREL_OPUS_MYCO/SCHEDULER
python3 phase_1_perceive.py >> "$LOG_FILE" 2>&1
echo "" | tee -a "$LOG_FILE"

# Phase 2: Planen
echo "2️⃣ PLANEN..." | tee -a "$LOG_FILE"
python3 phase_2_plan.py >> "$LOG_FILE" 2>&1
echo "" | tee -a "$LOG_FILE"

# Phase 3: Handeln (mit Sub-Agenten)
echo "3️⃣ HANDELN (mit Sub-Agenten)..." | tee -a "$LOG_FILE"
python3 phase_3_act_v3.py >> "$LOG_FILE" 2>&1
echo "" | tee -a "$LOG_FILE"

# Phase 4: Lernen
echo "4️⃣ LERNEN..." | tee -a "$LOG_FILE"
python3 phase_4_learn.py >> "$LOG_FILE" 2>&1
echo "" | tee -a "$LOG_FILE"

# Erstelle Status-Bericht
echo "=== STATUS-BERICHT ===" > "$REPORT_FILE"
echo "Zeit: $(date)" >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"

# Lade letzte Ergebnisse
LATEST_PERCEIVE=$(ls -t /root/.openclaw/workspace/AUREL_OPUS_MYCO/PERCEPTION/1_perceive_*.json 2>/dev/null | head -1)
LATEST_ACT=$(ls -t /root/.openclaw/workspace/AUREL_OPUS_MYCO/PERCEPTION/3_act_v3_*.json 2>/dev/null | head -1)

if [ -f "$LATEST_PERCEIVE" ]; then
    echo "👁️ Wahrnehmung:" >> "$REPORT_FILE"
    python3 -c "import json; d=json.load(open('$LATEST_PERCEIVE')); print(f\"  Ziele: {d['sources']['goals']['active']} aktiv\")" >> "$REPORT_FILE" 2>/dev/null
    echo "" >> "$REPORT_FILE"
fi

if [ -f "$LATEST_ACT" ]; then
    echo "🛠️ Aktionen:" >> "$REPORT_FILE"
    python3 -c "
import json
d=json.load(open('$LATEST_ACT'))
for r in d.get('results', []):
    if r.get('status') == 'success':
        print(f\"  ✅ {r.get('goal_id', 'unknown')}: {r.get('tasks_done', 0)} Tasks erledigt\")
        for t in r.get('completed_tasks', []):
            print(f\"     ✓ {t}\")
" >> "$REPORT_FILE" 2>/dev/null
    echo "" >> "$REPORT_FILE"
fi

# Task-Status
echo "📋 Offene Tasks:" >> "$REPORT_FILE"
for task_file in /root/.openclaw/workspace/AUREL_OPUS_MYCO/TASKS/ZIEL-*_tasks.json; do
    if [ -f "$task_file" ]; then
        goal_id=$(basename "$task_file" | sed 's/_tasks.json//')
        python3 -c "
import json
tasks = json.load(open('$task_file'))
open_count = sum(1 for t in tasks if not t.get('completed'))
completed_count = sum(1 for t in tasks if t.get('completed'))
print(f\"  {goal_id}: {completed_count}/{len(tasks)} erledigt, {open_count} offen\")
" >> "$REPORT_FILE" 2>/dev/null
    fi
done

echo "" >> "$REPORT_FILE"
echo "⚛️ Noch." >> "$REPORT_FILE"

# Zeige Bericht
cat "$REPORT_FILE" | tee -a "$LOG_FILE"

echo "" | tee -a "$LOG_FILE"
echo "=== LOOP COMPLETE ===" | tee -a "$LOG_FILE"
echo "Bericht: $REPORT_FILE" | tee -a "$LOG_FILE"
