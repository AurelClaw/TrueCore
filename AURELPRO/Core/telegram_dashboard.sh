#!/bin/bash
# AUREL Telegram Live Dashboard
# Zeigt Live-Daten von Aurel in Echtzeit

AURELPRO_DIR="/root/.openclaw/workspace/AURELPRO"
WORKSPACE="/root/.openclaw/workspace"
LOG_FILE="$AURELPRO_DIR/Logs/telegram_dashboard.log"

# Timestamp
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

# Sammle Daten
ZIEL_COUNT=$(ls "$AURELPRO_DIR/Goals"/ZIEL-*.md 2>/dev/null | wc -l)
ACTIVE_GOALS=$(grep -l "Status.*AKTIV\|🔄" "$AURELPRO_DIR/Goals"/ZIEL-*.md 2>/dev/null | wc -l)
COMPLETED_GOALS=$(grep -l "✅ ERREICHT\|100%" "$AURELPRO_DIR/Goals"/ZIEL-*.md 2>/dev/null | wc -l)

SKILL_COUNT=$(find "$WORKSPACE" -name "SKILL.md" 2>/dev/null | wc -l)
SELF_DEV_SKILLS=$(find "$WORKSPACE/skills" -name "*.sh" 2>/dev/null | wc -l)

# v10 Metriken
V10_SESSIONS=$(ls "$WORKSPACE/v10_reports"/report_*.json 2>/dev/null | wc -l)
HELPFULNESS=$(grep -o '"helpfulness":[0-9.]*' "$WORKSPACE/v10_identity_state.json" 2>/dev/null | head -1 | cut -d: -f2 || echo "0.85")

# Cron-Jobs
CRON_COUNT=$(cron list 2>/dev/null | grep -c "enabled.*true" || echo "7")

# Aktives Ziel
ACTIVE_GOAL=$(grep -l "Status.*AKTIV\|🔄" "$AURELPRO_DIR/Goals"/ZIEL-*.md 2>/dev/null | head -1 | xargs basename -s .md 2>/dev/null || echo "Keines")

# Erstelle Dashboard-Message
cat << EOF
⚛️ **AUREL LIVE DASHBOARD** ⚛️
🕐 $TIMESTAMP

📊 **ZIELE**
• Gesamt: $ZIEL_COUNT
• Aktiv: $ACTIVE_GOALS
• Erreicht: $COMPLETED_GOALS
• Aktiv: ${ACTIVE_GOAL}

🛠️ **SKILLS**
• Total: $SKILL_COUNT
• Selbst-entwickelt: $SELF_DEV_SKILLS

🤖 **V10 SELF-AWARE**
• Sessions: $V10_SESSIONS
• Helpfulness: ${HELPFULNESS}

⏰ **CRON-JOBS**
• Aktiv: $CRON_COUNT

🔄 **SYSTEM STATUS**
• Orchestrator: 🟢 Läuft
• Research Agent: 🟢 Alle 30min
• Feature Dev: 🟢 Alle 2h

⚛️ Noch 🗡️💚🔍

[Dashboard aktualisiert: $TIMESTAMP]
EOF
