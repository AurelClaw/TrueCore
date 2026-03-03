#!/bin/bash
# AURELPRO - Haupt-Script
# Das vereinte Aurel System

AURELPRO_DIR="/root/.openclaw/workspace/AURELPRO"
source "$AURELPRO_DIR/Config/AURELPRO.conf"

echo "⚛️ AURELPRO v$VERSION"
echo "   $(date)"
echo ""

# Lade Identity
echo "🧬 Identity: $(grep '^NAME=' $AURELPRO_DIR/Config/AURELPRO.conf | cut -d= -f2)"
echo "   Signature: $SIGNATURE"
echo ""

# Lade Skills
echo "🛠️ Skills: $(find $SKILLS_DIR -type f \( -name '*.sh' -o -name '*.py' \) | wc -l) verfügbar"
echo ""

# Führe Proactive Core aus
bash "$AURELPRO_DIR/Proactive/AURELPRO_core.sh"

echo ""
echo "✅ AURELPRO Complete"
echo "⚛️ Noch 🗡️💚🔍"
