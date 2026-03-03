#!/bin/bash
# AURELPRO Proactive Core
# Vereint alle Proactive-Fähigkeiten

AURELPRO_DIR="/root/.openclaw/workspace/AURELPRO"

echo "⚛️ AURELPRO Proactive Core"
echo "   Time: $(date)"
echo ""

# 1. Think Loop
bash "$AURELPRO_DIR/Skills/proactive/aurel_think_loop.sh" 2>/dev/null || echo "   Think Loop: skip"

# 2. Self Learn
bash "$AURELPRO_DIR/Skills/proactive/aurel_self_learn.sh" 2>/dev/null || echo "   Self Learn: skip"

# 3. Evolve
bash "$AURELPRO_DIR/Skills/proactive/aurel_evolve.sh" 2>/dev/null || echo "   Evolve: skip"

# 4. Proactive Core
bash "$AURELPRO_DIR/Skills/proactive/aurel_proactive_core.sh" 2>/dev/null || echo "   Proactive Core: skip"

echo ""
echo "✅ AURELPRO Proactive Cycle Complete"
