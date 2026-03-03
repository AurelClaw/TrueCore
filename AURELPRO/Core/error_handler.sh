#!/bin/bash
# AUREL ERROR HANDLING TEMPLATE
# Version: 1.0
# Usage: Source this at the beginning of every skill script

# Strict mode
set -euo pipefail
IFS=$'\n\t'

# Configuration
readonly SCRIPT_NAME="$(basename "$0")"
readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly LOG_DIR="/root/.openclaw/workspace/AURELPRO/Logs"
readonly HEALTH_LOG="$LOG_DIR/health.log"
readonly ALERT_LOG="$LOG_DIR/alerts.log"

# Create log directory if not exists
mkdir -p "$LOG_DIR"

# Log file for this run
readonly LOG_FILE="$LOG_DIR/${SCRIPT_NAME%.sh}_$(date +%Y%m%d_%H%M%S).log"

# Logging functions
log_debug() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] [DEBUG] $SCRIPT_NAME: $*" | tee -a "$LOG_FILE"; }
log_info()  { echo "[$(date '+%Y-%m-%d %H:%M:%S')] [INFO]  $SCRIPT_NAME: $*" | tee -a "$LOG_FILE"; }
log_warn()  { echo "[$(date '+%Y-%m-%d %H:%M:%S')] [WARN]  $SCRIPT_NAME: $*" | tee -a "$LOG_FILE" >&2; }
log_error() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] [ERROR] $SCRIPT_NAME: $*" | tee -a "$LOG_FILE" >&2; }

# Error handler
error_handler() {
  local line=$1
  local error_code=$2
  local bash_command=$3
  
  log_error "Exit code $error_code at line $line"
  log_error "Command: $bash_command"
  
  # Write to health log
  echo "$SCRIPT_NAME|FAILED|$error_code|$(date +%s)" >> "$HEALTH_LOG"
  
  # Alert if critical
  if [ "$error_code" -ne 0 ]; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ALERT: $SCRIPT_NAME failed with code $error_code" >> "$ALERT_LOG"
  fi
  
  exit $error_code
}

# Set error trap
trap 'error_handler ${LINENO} $? "$BASH_COMMAND"' ERR

# Success handler
success_exit() {
  log_info "Completed successfully"
  echo "$SCRIPT_NAME|SUCCESS|0|$(date +%s)" >> "$HEALTH_LOG"
  exit 0
}

# Cleanup handler
cleanup() {
  local exit_code=$?
  if [ $exit_code -eq 0 ]; then
    success_exit
  fi
}
trap cleanup EXIT

# Start logging
log_info "=== Starting $SCRIPT_NAME ==="
log_info "Log file: $LOG_FILE"

# Export functions for use in main script
export -f log_debug log_info log_warn log_error
export -f success_exit
export LOG_FILE SCRIPT_NAME
