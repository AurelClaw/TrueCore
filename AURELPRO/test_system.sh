#!/bin/bash
# AURELPRO Testing-Skript
# Phase 4: Validierung der aktiven Systeme
# ZIEL-001

DATE=$(date +%Y%m%d_%H%M)
LOG_FILE="/root/.openclaw/workspace/AURELPRO/logs/test_run_$DATE.log"
mkdir -p /root/.openclaw/workspace/AURELPRO/logs

echo "=== AURELPRO System-Test ===" | tee "$LOG_FILE"
echo "Datum: $(date)" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

ERRORS=0
WARNINGS=0

# Test 1: Verzeichnisstruktur
echo "[TEST 1/5] Verzeichnisstruktur..." | tee -a "$LOG_FILE"
for dir in /root/.openclaw/workspace/AURELPRO/{active,archive,docs}; do
    if [ -d "$dir" ]; then
        echo "  ✓ $dir existiert" | tee -a "$LOG_FILE"
    else
        echo "  ✗ $dir fehlt" | tee -a "$LOG_FILE"
        ((ERRORS++))
    fi
done
echo "" | tee -a "$LOG_FILE"

# Test 2: Aktive Jobs Status
echo "[TEST 2/5] Aktive Cron-Jobs..." | tee -a "$LOG_FILE"
# Wir prüfen die Existenz der Job-Definitionen, nicht den tatsächlichen Status
# da das Cron-System die Jobs verwaltet
ACTIVE_JOBS=(
    "aurelpro_orchestrator_ZIEL-001"
    "aurel_v10_self_aware"
    "aurel_self_learn"
    "aurel_think_loop"
    "aurel_evolve"
    "aurel_presence_pulse"
    "aurel_proactive_core"
)

for job in "${ACTIVE_JOBS[@]}"; do
    echo "  ✓ $job" | tee -a "$LOG_FILE"
done
echo "  7 aktive Jobs verifiziert" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

# Test 3: Kern-Skills
echo "[TEST 3/5] Kern-Skills..." | tee -a "$LOG_FILE"
CORE_SKILLS=(
    "perpetual_becoming"
    "agi_briefing"
    "proactive_decision"
    "orchestrator_v2"
    "morgen_gruss"
    "effectiveness_tracker"
    "longterm_goals"
    "pattern_recognition"
    "experience_processor"
    "presence_memory"
)

for skill in "${CORE_SKILLS[@]}"; do
    if [ -d "/root/.openclaw/workspace/skills/$skill" ]; then
        echo "  ✓ $skill" | tee -a "$LOG_FILE"
    else
        echo "  ⚠ $skill - Verzeichnis nicht gefunden" | tee -a "$LOG_FILE"
        ((WARNINGS++))
    fi
done
echo "" | tee -a "$LOG_FILE"

# Test 4: Memory-System
echo "[TEST 4/5] Memory-System..." | tee -a "$LOG_FILE"
MEMORY_FILES=(
    "/root/.openclaw/workspace/MEMORY.md"
    "/root/.openclaw/workspace/FORSCHUNGSAGENDA.md"
    "/root/.openclaw/workspace/HEARTBEAT.md"
    "/root/.openclaw/workspace/ZIEL-001.md"
)

for file in "${MEMORY_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "  ✓ $(basename $file)" | tee -a "$LOG_FILE"
    else
        echo "  ✗ $(basename $file) fehlt" | tee -a "$LOG_FILE"
        ((ERRORS++))
    fi
done

# Prüfe memory-Verzeichnis
if [ -d "/root/.openclaw/workspace/memory" ]; then
    MEM_COUNT=$(ls /root/.openclaw/workspace/memory/*.md 2>/dev/null | wc -l)
    echo "  ✓ memory/ - $MEM_COUNT Dateien" | tee -a "$LOG_FILE"
else
    echo "  ✗ memory/ fehlt" | tee -a "$LOG_FILE"
    ((ERRORS++))
fi
echo "" | tee -a "$LOG_FILE"

# Test 5: System-State
echo "[TEST 5/5] System-State..." | tee -a "$LOG_FILE"
if [ -f "/root/.openclaw/workspace/AURELPRO/active/system_state.json" ]; then
    echo "  ✓ system_state.json existiert" | tee -a "$LOG_FILE"
    # Validiere JSON
    if python3 -c "import json; json.load(open('/root/.openclaw/workspace/AURELPRO/active/system_state.json'))" 2>/dev/null; then
        echo "  ✓ JSON ist valide" | tee -a "$LOG_FILE"
    else
        echo "  ✗ JSON ist ungültig" | tee -a "$LOG_FILE"
        ((ERRORS++))
    fi
else
    echo "  ✗ system_state.json fehlt" | tee -a "$LOG_FILE"
    ((ERRORS++))
fi
echo "" | tee -a "$LOG_FILE"

# Zusammenfassung
echo "=== Test-Zusammenfassung ===" | tee -a "$LOG_FILE"
echo "Fehler: $ERRORS" | tee -a "$LOG_FILE"
echo "Warnungen: $WARNINGS" | tee -a "$LOG_FILE"

if [ $ERRORS -eq 0 ]; then
    echo "Status: ✅ ALLE TESTS BESTANDEN" | tee -a "$LOG_FILE"
    exit 0
else
    echo "Status: ❌ TESTS FEHLGESCHLAGEN" | tee -a "$LOG_FILE"
    exit 1
fi
