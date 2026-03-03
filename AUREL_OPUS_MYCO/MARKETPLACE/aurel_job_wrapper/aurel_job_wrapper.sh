#!/bin/bash
# aurel_job_wrapper.sh - Wrapper für alle 7 Phasen
# Wird von Cron aufgerufen, führt die jeweilige Phase aus

PHASE="$1"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
LOG_DIR="/root/.openclaw/workspace/AUREL_OPUS_MYCO/logs"
mkdir -p "$LOG_DIR"

LOG_FILE="$LOG_DIR/${PHASE}_${TIMESTAMP}.log"
STATE_FILE="/root/.openclaw/workspace/AUREL_OPUS_MYCO/STATE/last_${PHASE}"

echo "=== $PHASE - $TIMESTAMP ===" > "$LOG_FILE"

# Führe Python-Phase aus
python3 /root/.openclaw/workspace/AUREL_OPUS_MYCO/SCHEDULER/phase_${PHASE}.py >> "$LOG_FILE" 2>&1

# Speichere State
 echo "$TIMESTAMP" > "$STATE_FILE"

echo "=== END ===" >> "$LOG_FILE"
