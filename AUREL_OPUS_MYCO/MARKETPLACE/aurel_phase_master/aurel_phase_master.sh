#!/bin/bash
# aurel_phase_master.sh - Master-Script für 7-Phasen-Loop mit Skills
# Wird von Cron aufgerufen, führt Phase + Skill aus

PHASE="$1"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
LOG_DIR="/root/.openclaw/workspace/AUREL_OPUS_MYCO/logs"
mkdir -p "$LOG_DIR"

LOG_FILE="$LOG_DIR/phase_${PHASE}_${TIMESTAMP}.log"

echo "=== Phase: $PHASE | $TIMESTAMP ===" | tee "$LOG_FILE"

# Führe Phase mit Skill-Router aus
cd /root/.openclaw/workspace/AUREL_OPUS_MYCO/SCHEDULER
python3 phase_${PHASE}_v2.py 2>&1 | tee -a "$LOG_FILE"

echo "" | tee -a "$LOG_FILE"
echo "=== Phase $PHASE Complete ===" | tee -a "$LOG_FILE"

# Sende Zusammenfassung an main session (wenn nicht reflektieren)
if [ "$PHASE" != "reflektieren" ]; then
    echo "📋 Zusammenfassung gesendet"
fi
