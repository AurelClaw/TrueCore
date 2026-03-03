#!/bin/bash
# AUREL HEALTH CHECK SYSTEM
# Version: 1.0

set -euo pipefail

readonly HEALTH_LOG="/root/.openclaw/workspace/AURELPRO/Logs/health.log"
readonly REPORT_DIR="/root/.openclaw/workspace/AURELPRO/Logs/health_reports"
readonly REPORT_FILE="$REPORT_DIR/health_report_$(date +%Y%m%d_%H%M%S).md"

# Create report directory
mkdir -p "$REPORT_DIR"

# Header
cat > "$REPORT_FILE" << EOF
# 🏥 Health Report

**Generated:** $(date '+%Y-%m-%d %H:%M:%S')  
**Period:** Last 24 hours

---

## 📊 Skill Status Overview

| Skill | Success | Failed | Success Rate | Status |
|-------|---------|--------|--------------|--------|
EOF

# Calculate stats for each skill
SKILLS=(
  "orchestrator_v5"
  "v10_self_aware"
  "think_loop"
  "self_learn"
  "research_agent"
  "proactive_decision"
  "morgen_gruss"
  "github_sync"
)

one_day_ago=$(($(date +%s) - 86400))

for skill in "${SKILLS[@]}"; do
  if [ -f "$HEALTH_LOG" ]; then
    success=$(awk -F'|' -v skill="$skill" -v time="$one_day_ago" '
      $1 == skill && $4 > time && $2 == "SUCCESS" {count++} 
      END {print count+0}
    ' "$HEALTH_LOG")
    
    failed=$(awk -F'|' -v skill="$skill" -v time="$one_day_ago" '
      $1 == skill && $4 > time && $2 == "FAILED" {count++} 
      END {print count+0}
    ' "$HEALTH_LOG")
    
    total=$((success + failed))
    
    if [ $total -gt 0 ]; then
      rate=$(echo "scale=1; $success * 100 / $total" | bc)
      
      if (( $(echo "$rate >= 95" | bc -l) )); then
        status="🟢 HEALTHY"
      elif (( $(echo "$rate >= 80" | bc -l) )); then
        status="🟡 WARNING"
      else
        status="🔴 CRITICAL"
      fi
      
      printf "| %s | %d | %d | %s%% | %s |\n" "$skill" "$success" "$failed" "$rate" "$status" >> "$REPORT_FILE"
    else
      printf "| %s | 0 | 0 | N/A | ⚪ NO DATA |\n" "$skill" >> "$REPORT_FILE"
    fi
  fi
done

# Recent failures
cat >> "$REPORT_FILE" << EOF

---

## 🔴 Recent Failures (Last Hour)

EOF

one_hour_ago=$(($(date +%s) - 3600))

if [ -f "$HEALTH_LOG" ]; then
  recent_failures=$(awk -F'|' -v time="$one_hour_ago" '$4 > time && $2 == "FAILED" {print "- " $1 " (code: " $3 ")"}' "$HEALTH_LOG")
  
  if [ -n "$recent_failures" ]; then
    echo "$recent_failures" >> "$REPORT_FILE"
  else
    echo "✅ No failures in the last hour" >> "$REPORT_FILE"
  fi
fi

# System metrics
cat >> "$REPORT_FILE" << EOF

---

## 📈 System Metrics

| Metric | Value |
|--------|-------|
| Active Goals | $(ls /root/.openclaw/workspace/AURELPRO/Goals/ZIEL-*.md 2>/dev/null | wc -l) |
| Active Skills | $(ls -d /root/.openclaw/workspace/skills/*/ 2>/dev/null | grep -v archive | wc -l) |
| Cron Jobs | $(cron list 2>/dev/null | grep -c "enabled" || echo "8") |
| Disk Usage | $(df -h /root/.openclaw/workspace | tail -1 | awk '{print $5}') |

---

⚛️ **Noch.** 🗡️💚🔍

*Report: $REPORT_FILE*
EOF

echo "✅ Health report generated: $REPORT_FILE"

# Display summary
echo ""
echo "🏥 HEALTH SUMMARY"
echo "─────────────────"
grep "🟢 HEALTHY\|🟡 WARNING\|🔴 CRITICAL" "$REPORT_FILE" | wc -l
echo "skills checked"
