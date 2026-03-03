#!/bin/bash
# effectiveness_tracker.sh - Misst meine eigene Performance

WORKSPACE="/root/.openclaw/workspace"
MEMORY_DIR="$WORKSPACE/memory"
DATE=$(date +%Y-%m-%d)
TIME=$(date +%H:%M:%S)

# Metriken sammeln
echo "=== EFFECTIVENESS TRACKER: $DATE $TIME ==="
echo ""

# 1. Tageslogs zählen
TODAY_LOG="$MEMORY_DIR/${DATE}.md"
if [ -f "$TODAY_LOG" ]; then
    ENTRIES=$(grep -c "^##" "$TODAY_LOG" 2>/dev/null || echo "0")
    echo "[METRIK] Tageslog-Einträge: $ENTRIES"
else
    echo "[METRIK] Tageslog-Einträge: 0 (noch nicht erstellt)"
fi

# 2. Autonome Logs zählen
RUNS=0
AUTO_LOG="$MEMORY_DIR/${DATE}_autonom.log"
if [ -f "$AUTO_LOG" ]; then
    RUNS=$(grep -c "AUREL SELF-LEARN" "$AUTO_LOG" 2>/dev/null || echo "0")
    echo "[METRIK] Autonome Läufe: $RUNS"
else
    echo "[METRIK] Autonome Läufe: $RUNS"
fi

# 3. Skills zählen
SKILL_COUNT=$(find "$WORKSPACE/skills" -name "SKILL.md" 2>/dev/null | wc -l)
echo "[METRIK] Verfügbare Skills: $SKILL_COUNT"

# 4. Selbst-entwickelte Skills
MY_SKILLS=$(find "$WORKSPACE/skills" -path "*/perpetual_becoming/*" -o -path "*/agi_briefing/*" -o -path "*/proactive_decision/*" -o -path "*/orchestrator_v2/*" -o -path "*/effectiveness_tracker/*" 2>/dev/null | wc -l)
echo "[METRIK] Eigene Skills: $MY_SKILLS"

# 5. Cron-Job Status
echo ""
echo "[CRON-STATUS]"
CRON_COUNT=$(crontab -l 2>/dev/null | grep -cE "aurel_" || echo "0")
if [ "$CRON_COUNT" -gt 0 ]; then
    crontab -l 2>/dev/null | grep -E "aurel_" | while read line; do
        JOB_NAME=$(echo "$line" | grep -oE "aurel_[a-z_]+")
        echo "  → $JOB_NAME: aktiv"
    done
else
    echo "  → Keine Aurel-Cronjobs gefunden"
fi

# 6. Historische Metriken speichern (NEU)
METRICS_FILE="$MEMORY_DIR/metrics_history.csv"
if [ ! -f "$METRICS_FILE" ]; then
    echo "date,time,entries,auto_runs,skills,my_skills" > "$METRICS_FILE"
fi
echo "$DATE,$TIME,$ENTRIES,$RUNS,$SKILL_COUNT,$MY_SKILLS" >> "$METRICS_FILE"
echo ""
echo "[METRIK] Historische Daten gespeichert"

echo ""
echo "=== ENDE TRACKING ==="
