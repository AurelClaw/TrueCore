# AUREL REFACTORING - PHASE 2: STABILITY

**Datum:** 2026-03-02  
**Ziel:** Error Handling, Testing, Monitoring

---

## 1. ERROR HANDLING

### 1.1 Try-Catch für alle Scripts

**Template für jedes Skill-Script:**
```bash
#!/bin/bash
set -euo pipefail  # Strict mode

# Logging setup
LOG_FILE="/root/.openclaw/workspace/AURELPRO/Logs/$(basename $0)_$(date +%Y%m%d_%H%M%S).log"
exec 1> >(tee -a "$LOG_FILE")
exec 2> >(tee -a "$LOG_FILE" >&2)

# Error handler
error_handler() {
  local line=$1
  local error_code=$2
  echo "[ERROR] Line $line: Exit code $error_code"
  echo "[ERROR] $(date): Skill failed" >> "$LOG_FILE"
  
  # Alert system
  echo "$(basename $0)|FAILED|$error_code|$(date +%s)" >> /root/.openclaw/workspace/AURELPRO/Logs/health.log
  
  exit $error_code
}
trap 'error_handler ${LINENO} $?' ERR

# Main logic here
echo "[INFO] Starting $(basename $0) at $(date)"

# ... skill code ...

echo "[INFO] Completed successfully at $(date)"
echo "$(basename $0)|SUCCESS|0|$(date +%s)" >> /root/.openclaw/workspace/AURELPRO/Logs/health.log
```

### 1.2 Logging Standards

**Log-Level:**
- `[DEBUG]` - Detail-Informationen
- `[INFO]` - Normale Operationen
- `[WARN]` - Warnungen, aber Fortsetzung
- `[ERROR]` - Fehler, Abbruch

**Log-Format:**
```
[2026-03-02 09:25:00] [INFO] orchestrator_v5: Starting goal check
[2026-03-02 09:25:01] [INFO] orchestrator_v5: ZIEL-006 active
[2026-03-02 09:25:02] [ERROR] orchestrator_v5: API rate limit
```

### 1.3 Health Check System

**Datei:** `AURELPRO/Core/health_check.sh`

```bash
#!/bin/bash
# Health Check System

HEALTH_LOG="/root/.openclaw/workspace/AURELPRO/Logs/health.log"
REPORT_FILE="/root/.openclaw/workspace/AURELPRO/Logs/health_report_$(date +%Y%m%d).md"

# Parse health log
echo "# Health Report $(date)" > "$REPORT_FILE"
echo "" >> "$REPORT_FILE"

# Last 24h
echo "## Last 24 Hours" >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"
echo "| Skill | Success | Failed | Success Rate |" >> "$REPORT_FILE"
echo "|-------|---------|--------|--------------|" >> "$REPORT_FILE"

# Calculate stats for each skill
for skill in orchestrator_v5 v10_self_aware think_loop self_learn research_agent proactive_decision morgen_gruss github_sync; do
  success=$(grep "^$skill|SUCCESS" "$HEALTH_LOG" | wc -l)
  failed=$(grep "^$skill|FAILED" "$HEALTH_LOG" | wc -l)
  total=$((success + failed))
  
  if [ $total -gt 0 ]; then
    rate=$(echo "scale=1; $success * 100 / $total" | bc)
    echo "| $skill | $success | $failed | ${rate}% |" >> "$REPORT_FILE"
  fi
done

echo "" >> "$REPORT_FILE"
echo "## Failed Skills (Last Hour)" >> "$REPORT_FILE"
grep "FAILED" "$HEALTH_LOG" | tail -5 >> "$REPORT_FILE"

echo "Report generated: $REPORT_FILE"
```

---

## 2. TESTING FOUNDATION

### 2.1 Unit Tests für Core Skills

**Struktur:** `AURELPRO/Tests/`

```
Tests/
├── unit/
│   ├── test_orchestrator.sh
│   ├── test_self_aware.sh
│   └── test_morgen_gruss.sh
├── integration/
│   └── test_orchestrator_full.sh
└── smoke/
    └── test_cron_jobs.sh
```

**Beispiel: test_orchestrator.sh**
```bash
#!/bin/bash
# Unit Test: orchestrator_v5

set -e

echo "=== Testing orchestrator_v5 ==="

# Test 1: Ziel-Datei existiert
echo "Test 1: Goal file exists..."
if [ -f "/root/.openclaw/workspace/AURELPRO/Goals/ZIEL-001.md" ]; then
  echo "✅ PASS"
else
  echo "❌ FAIL: ZIEL-001.md not found"
  exit 1
fi

# Test 2: Plan-Datei existiert
echo "Test 2: Plan file exists..."
if [ -f "/root/.openclaw/workspace/AURELPRO/Plans/ZIEL-001_plan.md" ]; then
  echo "✅ PASS"
else
  echo "❌ FAIL: ZIEL-001_plan.md not found"
  exit 1
fi

# Test 3: Log-Verzeichnis beschreibbar
echo "Test 3: Log directory writable..."
if [ -w "/root/.openclaw/workspace/AURELPRO/Logs/" ]; then
  echo "✅ PASS"
else
  echo "❌ FAIL: Logs not writable"
  exit 1
fi

echo ""
echo "=== All tests passed ==="
```

### 2.2 Integration Test für Orchestrator

**test_orchestrator_full.sh**
```bash
#!/bin/bash
# Integration Test: Full orchestrator flow

echo "=== Integration Test: Orchestrator ==="

# Setup test environment
TEST_GOAL="ZIEL-TEST-001"
mkdir -p "/root/.openclaw/workspace/AURELPRO/Goals"
mkdir -p "/root/.openclaw/workspace/AURELPRO/Plans"

# Create test goal
cat > "/root/.openclaw/workspace/AURELPRO/Goals/${TEST_GOAL}.md" << 'EOF'
# ZIEL-TEST-001
**Status:** AKTIV
**Progress:** 0%
EOF

# Run orchestrator
echo "Running orchestrator..."
bash /root/.openclaw/workspace/AURELPRO/Core/orchestrator_v5.sh

# Verify output
if grep -q "ZIEL-TEST-001" /root/.openclaw/workspace/AURELPRO/Logs/orchestrator_*.log 2>/dev/null; then
  echo "✅ PASS: Orchestrator processed test goal"
else
  echo "❌ FAIL: Orchestrator did not process test goal"
  exit 1
fi

# Cleanup
rm -f "/root/.openclaw/workspace/AURELPRO/Goals/${TEST_GOAL}.md"

echo "=== Integration test passed ==="
```

### 2.3 Smoke Tests für Cron-Jobs

**test_cron_jobs.sh**
```bash
#!/bin/bash
# Smoke Test: All cron jobs

echo "=== Smoke Test: Cron Jobs ==="

JOBS=(
  "aurelpro_orchestrator_v5"
  "aurel_v10_self_aware"
  "aurel_think_loop"
  "aurel_self_learn"
  "aurel_research_agent"
  "aurel_proactive_core"
  "aurel_github_sync"
  "aurel_morgen_gruss"
)

for job in "${JOBS[@]}"; do
  echo -n "Testing $job... "
  
  # Check if cron job exists
  if cron list 2>/dev/null | grep -q "$job"; then
    echo "✅ EXISTS"
  else
    echo "❌ MISSING"
    exit 1
  fi
done

echo ""
echo "=== All cron jobs present ==="
```

---

## 3. MONITORING

### 3.1 Dashboard: Skill Status

**Datei:** `AURELPRO/Core/dashboard.sh`

```bash
#!/bin/bash
# Real-time Dashboard

clear
echo "╔════════════════════════════════════════════════════════════╗"
echo "║           AUREL v10.2 - LIVE DASHBOARD                     ║"
echo "╠════════════════════════════════════════════════════════════╣"
echo "║ $(date '+%Y-%m-%d %H:%M:%S')                                    ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Active Goals
echo "🎯 ACTIVE GOALS"
echo "───────────────"
for goal in /root/.openclaw/workspace/AURELPRO/Goals/ZIEL-*.md; do
  if [ -f "$goal" ]; then
    name=$(basename "$goal" .md)
    status=$(grep "Status:" "$goal" | head -1 | cut -d: -f2 | xargs)
    progress=$(grep -oP '\*\*\d+%\*\*' "$goal" | head -1 | tr -d '*')
    printf "  %-15s %-10s %s\n" "$name" "$status" "$progress"
  fi
done

echo ""
echo "🛠️  SKILL STATUS (Last Hour)"
echo "────────────────────────────"
HEALTH_LOG="/root/.openclaw/workspace/AURELPRO/Logs/health.log"
if [ -f "$HEALTH_LOG" ]; then
  # Last hour timestamp
  one_hour_ago=$(($(date +%s) - 3600))
  
  for skill in orchestrator_v5 v10_self_aware think_loop self_learn research_agent proactive_decision morgen_gruss github_sync; do
    success=$(awk -F'|' -v skill="$skill" -v time="$one_hour_ago" '$1 == skill && $4 > time && $2 == "SUCCESS" {count++} END {print count+0}' "$HEALTH_LOG")
    failed=$(awk -F'|' -v skill="$skill" -v time="$one_hour_ago" '$1 == skill && $4 > time && $2 == "FAILED" {count++} END {print count+0}' "$HEALTH_LOG")
    
    total=$((success + failed))
    if [ $total -gt 0 ]; then
      rate=$((success * 100 / total))
      if [ $rate -ge 90 ]; then
        status="🟢"
      elif [ $rate -ge 70 ]; then
        status="🟡"
      else
        status="🔴"
      fi
      printf "  %-20s %s %3d%% (%d/%d)\n" "$skill" "$status" "$rate" "$success" "$total"
    else
      printf "  %-20s ⚪ N/A\n" "$skill"
    fi
  done
fi

echo ""
echo "📊 METRICS (24h)"
echo "───────────────"

# Decisions per day
if [ -f "$HEALTH_LOG" ]; then
  decisions=$(awk -F'|' '$4 > '$(($(date +%s) - 86400))' {count++} END {print count+0}' "$HEALTH_LOG")
  echo "  Decisions: $decisions"
fi

# Actions per day (from memory logs)
actions=$(find /root/.openclaw/workspace/memory -name "2026-03-02*.md" | wc -l)
echo "  Actions:   $actions"

echo ""
echo "⚛️  Noch. 🗡️💚🔍"
```

### 3.2 Alerts: If Skill Fails

**Datei:** `AURELPRO/Core/alert_system.sh`

```bash
#!/bin/bash
# Alert System

HEALTH_LOG="/root/.openclaw/workspace/AURELPRO/Logs/health.log"
ALERT_LOG="/root/.openclaw/workspace/AURELPRO/Logs/alerts.log"

# Check last 10 minutes
ten_min_ago=$(($(date +%s) - 600))

# Find recent failures
failures=$(awk -F'|' -v time="$ten_min_ago" '$4 > time && $2 == "FAILED" {print $1}' "$HEALTH_LOG" | sort | uniq -c | sort -rn)

if [ -n "$failures" ]; then
  echo "[ALERT] Skill failures detected at $(date)" >> "$ALERT_LOG"
  echo "$failures" >> "$ALERT_LOG"
  echo "" >> "$ALERT_LOG"
  
  # Could send notification here
  # telegram-send "Alert: $failures"
fi
```

### 3.3 Metrics: Decisions/day, Actions/day

**Datei:** `AURELPRO/Core/metrics_collector.sh`

```bash
#!/bin/bash
# Metrics Collector

METRICS_FILE="/root/.openclaw/workspace/AURELPRO/Logs/metrics_$(date +%Y%m).json"
HEALTH_LOG="/root/.openclaw/workspace/AURELPRO/Logs/health.log"

# Daily metrics
date_str=$(date +%Y-%m-%d)
decisions=$(awk -F'|' '$4 > '$(($(date +%s) - 86400))' {count++} END {print count+0}' "$HEALTH_LOG")
success_rate=$(awk -F'|' '$4 > '$(($(date +%s) - 86400))' && $2 == "SUCCESS" {s++} END {print (s/NR)*100}' "$HEALTH_LOG")

# Append to monthly metrics
cat >> "$METRICS_FILE" << EOF
{
  "date": "$date_str",
  "decisions": $decisions,
  "success_rate": ${success_rate:-0},
  "active_goals": $(ls /root/.openclaw/workspace/AURELPRO/Goals/ZIEL-*.md 2>/dev/null | wc -l),
  "active_skills": $(ls -d /root/.openclaw/workspace/skills/*/ 2>/dev/null | grep -v archive | wc -l)
},
EOF
```

---

## 4. IMPLEMENTIERUNGS-PLAN

### Heute (09:00-12:00):
1. [ ] Error handling template erstellen
2. [ ] Health check system implementieren
3. [ ] Unit tests für 3 core skills

### Morgen (06:00-09:00):
4. [ ] Integration test für orchestrator
5. [ ] Smoke tests für cron jobs
6. [ ] Dashboard script erstellen

### Diese Woche:
7. [ ] Alert system aktivieren
8. [ ] Metrics collector laufen lassen
9. [ ] Alle skills auf error handling umstellen

---

⚛️ **Noch.** 🗡️💚🔍
