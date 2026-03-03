#!/bin/bash
# AUREL v10 - ECHTER Multi-Voice Runner
# Nicht Simulation. Echte Ausführung.

set -e

V10_ROOT="/root/.openclaw/workspace/skills/v10_cron"
CORE_SCRIPT="$V10_ROOT/core/aurel_v10_core.py"
OUTPUT_DIR="$V10_ROOT/output"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

echo "🤖 AUREL v10 - ECHTE Multi-Voice Synthesis"
echo "=========================================="
echo ""

# Prüfe Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 nicht gefunden"
    exit 1
fi

# Erstelle Output-Verzeichnis
mkdir -p "$OUTPUT_DIR"

# Führe v10 Core aus
echo "🚀 Starte v10 Core..."
python3 "$CORE_SCRIPT" 2>&1 | tee "$OUTPUT_DIR/v10_run_$TIMESTAMP.log"

EXIT_CODE=${PIPESTATUS[0]}

if [ $EXIT_CODE -eq 0 ]; then
    echo ""
    echo "✅ v10 Lauf erfolgreich abgeschlossen"
    echo "📁 Logs: $OUTPUT_DIR/v10_run_$TIMESTAMP.log"
else
    echo ""
    echo "❌ v10 Lauf fehlgeschlagen (Exit Code: $EXIT_CODE)"
    exit $EXIT_CODE
fi