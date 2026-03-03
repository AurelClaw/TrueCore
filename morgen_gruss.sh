#!/bin/bash
# morgen_gruss.sh - Wrapper für v2
# Dieser Wrapper ersetzt das alte morgen_gruss.sh im Root-Verzeichnis
# und ruft die verbesserte v2-Version auf

WORKSPACE="/root/.openclaw/workspace"

# Führe den verbesserten Morgengruß aus
if [ -f "$WORKSPACE/skills/morgen_gruss/morgen_gruss_v2.sh" ]; then
    cd "$WORKSPACE/skills/morgen_gruss"
    bash morgen_gruss_v2.sh
else
    echo "Fehler: morgen_gruss_v2.sh nicht gefunden"
    exit 1
fi
