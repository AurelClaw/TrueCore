#!/bin/bash
# Aurel Meta-Orchestrator v1.2 - Final Fix
# Smartes Scheduling und Konfliktvermeidung

WORKSPACE="/root/.openclaw/workspace"
META_DIR="$WORKSPACE/.meta_orchestrator"
STATE_FILE="$META_DIR/state.json"
LOG_FILE="$META_DIR/orchestrator.log"

mkdir -p "$META_DIR"

TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
HOUR=$(date +%H)

log() {
    echo "[$TIMESTAMP] $1" | tee -a "$LOG_FILE"
}

log "═══════════════════════════════════════════════════════════"
log "🎼 Aurel Meta-Orchestrator v1.2 | $TIMESTAMP"
log "═══════════════════════════════════════════════════════════"

# System-Status
LOAD=$(cut -d' ' -f1 /proc/loadavg 2>/dev/null || echo "0")
log "📊 System: Load $LOAD | Stunde $HOUR"

# Profil bestimmen
if [[ $HOUR -ge 2 && $HOUR -lt 6 ]]; then
    PROFILE="NIGHT"; MAX_P=4; EVO="true"
elif [[ $HOUR -ge 20 || $HOUR -lt 2 ]]; then
    PROFILE="EVENING"; MAX_P=3; EVO="true"
else
    PROFILE="DAY"; MAX_P=2; EVO="false"
fi

log "   Profil: $PROFILE | Max: $MAX_P | Evolution: $EVO"

# Jobs zählen (einfache Methode)
COG=0
SELF=0

if pgrep -f "aurel_v10_self_aware" >/dev/null 2>&1; then COG=$((COG+1)); fi
if pgrep -f "aurelpro_orchestrator" >/dev/null 2>&1; then COG=$((COG+1)); fi
if pgrep -f "aurel_think_loop" >/dev/null 2>&1; then SELF=$((SELF+1)); fi
if pgrep -f "aurel_self_learn" >/dev/null 2>&1; then SELF=$((SELF+1)); fi
if pgrep -f "aurel_evolve" >/dev/null 2>&1; then SELF=$((SELF+1)); fi

TOTAL=$((COG + SELF))

log ""
log "📋 Jobs: $TOTAL (Cog: $COG, Self: $SELF)"

# Scheduling
log ""
log "🎼 Scheduling:"
[[ $COG -eq 0 ]] && log "   ✅ COGNITIVE frei" || log "   ⏸️  COGNITIVE: $COG"
[[ $SELF -lt 2 ]] && log "   ✅ SELF frei" || log "   ⏸️  SELF: $SELF"
[[ $TOTAL -le 1 ]] && log "   ✅ EXTERNAL frei" || log "   ⏸️  EXTERNAL wartet"
[[ "$EVO" == "true" ]] && log "   ✅ Evolution erlaubt"

# State
cat > "$STATE_FILE" << EOF
{"time":"$TIMESTAMP","profile":"$PROFILE","load":"$LOAD","jobs":$TOTAL,"max":$MAX_P}
EOF

log ""
log "💾 State gespeichert"
log "⚛️ Noch."

echo ""
echo "Meta-Orchestrator v1.2 | $PROFILE | Jobs: $TOTAL/$MAX_P | Evo: $EVO"
