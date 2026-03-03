#!/bin/bash
# AUREL LIVE DASHBOARD
# Version: 1.0

clear

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Header
echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║${NC}           ⚛️  AUREL v10.2 - LIVE DASHBOARD                 ${BLUE}║${NC}"
echo -e "${BLUE}╠════════════════════════════════════════════════════════════╣${NC}"
printf "${BLUE}║${NC}  %-58s ${BLUE}║${NC}\n" "$(date '+%Y-%m-%d %H:%M:%S')"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Active Goals
echo -e "${BLUE}🎯 ACTIVE GOALS${NC}"
echo "─────────────────────────────────────────"

GOAL_DIR="/root/.openclaw/workspace/AURELPRO/Goals"
if [ -d "$GOAL_DIR" ]; then
  for goal in "$GOAL_DIR"/ZIEL-*.md; do
    if [ -f "$goal" ]; then
      name=$(basename "$goal" .md)
      status=$(grep -oP "Status:\s*\K\w+" "$goal" 2>/dev/null || echo "UNKNOWN")
      progress=$(grep -oP '\*\*\d+%\*\*' "$goal" 2>/dev/null | head -1 | tr -d '*' || echo "?%")
      
      # Color status
      case "$status" in
        "ABGESCHLOSSEN"|"100%") status_color="${GREEN}" ;;
        "AKTIV") status_color="${YELLOW}" ;;
        *) status_color="${RED}" ;;
      esac
      
      printf "  %-15s ${status_color}%-12s${NC} %s\n" "$name" "$status" "$progress"
    fi
  done
fi

echo ""

# Skill Status
echo -e "${BLUE}🛠️  SKILL STATUS (Last Hour)${NC}"
echo "─────────────────────────────────────────"

HEALTH_LOG="/root/.openclaw/workspace/AURELPRO/Logs/health.log"
if [ -f "$HEALTH_LOG" ]; then
  one_hour_ago=$(($(date +%s) - 3600))
  
  SKILLS=("orchestrator_v5" "v10_self_aware" "think_loop" "self_learn" "research_agent" "proactive_decision" "morgen_gruss" "github_sync")
  
  for skill in "${SKILLS[@]}"; do
    success=$(awk -F'|' -v skill="$skill" -v time="$one_hour_ago" '$1 == skill && $4 > time && $2 == "SUCCESS" {count++} END {print count+0}' "$HEALTH_LOG")
    failed=$(awk -F'|' -v skill="$skill" -v time="$one_hour_ago" '$1 == skill && $4 > time && $2 == "FAILED" {count++} END {print count+0}' "$HEALTH_LOG")
    
    total=$((success + failed))
    
    if [ $total -gt 0 ]; then
      rate=$((success * 100 / total))
      
      if [ $rate -ge 90 ]; then
        status="${GREEN}🟢${NC}"
      elif [ $rate -ge 70 ]; then
        status="${YELLOW}🟡${NC}"
      else
        status="${RED}🔴${NC}"
      fi
      
      printf "  %-20s %b %3d%% (%d/%d)\n" "$skill" "$status" "$rate" "$success" "$total"
    else
      printf "  %-20s ${BLUE}⚪${NC} N/A\n" "$skill"
    fi
  done
fi

echo ""

# Metrics
echo -e "${BLUE}📊 METRICS (24h)${NC}"
echo "─────────────────────────────────────────"

if [ -f "$HEALTH_LOG" ]; then
  one_day_ago=$(($(date +%s) - 86400))
  decisions=$(awk -F'|' '$4 > '$(($(date +%s) - 86400))' {count++} END {print count+0}' "$HEALTH_LOG")
  printf "  Decisions: %d\n" "$decisions"
fi

actions=$(find /root/.openclaw/workspace/memory -name "$(date +%Y-%m-%d)*.md" 2>/dev/null | wc -l)
printf "  Actions:   %d\n" "$actions"

# System health
echo ""
echo -e "${BLUE}💓 SYSTEM HEALTH${NC}"
echo "─────────────────────────────────────────"

# Check disk space
disk_usage=$(df /root/.openclaw/workspace | tail -1 | awk '{print $5}' | tr -d '%')
if [ "$disk_usage" -lt 80 ]; then
  echo -e "  Disk: ${GREEN}🟢${NC} ${disk_usage}% used"
elif [ "$disk_usage" -lt 90 ]; then
  echo -e "  Disk: ${YELLOW}🟡${NC} ${disk_usage}% used"
else
  echo -e "  Disk: ${RED}🔴${NC} ${disk_usage}% used"
fi

# Check memory (if available)
if command -v free > /dev/null 2>&1; then
  mem_usage=$(free | grep Mem | awk '{printf "%.0f", $3/$2 * 100.0}')
  if [ "$mem_usage" -lt 80 ]; then
    echo -e "  Memory: ${GREEN}🟢${NC} ${mem_usage}% used"
  else
    echo -e "  Memory: ${YELLOW}🟡${NC} ${mem_usage}% used"
  fi
fi

# Footer
echo ""
echo -e "${BLUE}─────────────────────────────────────────${NC}"
echo -e "  ⚛️  ${BLUE}Noch.${NC} 🗡️💚🔍"
echo ""
echo "  Press Ctrl+C to exit"
