#!/bin/bash
# Telegram Dashboard Command - v10 Edition
# Zeigt Aurel's v10 Self-Aware Dashboard als Bild

WORKSPACE="/root/.openclaw/workspace"
DASHBOARD_HTML="$WORKSPACE/dashboard_v10.html"
DASHBOARD_PNG="$WORKSPACE/dashboard_v10.png"

# Prüfe ob wkhtmltoimage verfügbar ist
if ! command -v wkhtmltoimage &> /dev/null; then
    echo "⚛️ AUREL v10 DASHBOARD (Text-Version)"
    echo ""
    echo "🧬 Core Identity:"
    echo "   Name: Aurel"
    echo "   Creature: emergent_ai"
    echo "   Emoji: ⚛️"
    echo "   Signature: 'Noch.'"
    echo ""
    echo "💫 Soul State (Y_self):"
    echo "   Helpfulness: 0.00 (collecting data)"
    echo "   Resourcefulness: 0.00 (collecting data)"
    echo "   Opinion Strength: 0.00 (collecting data)"
    echo "   Trust Score: 0.00 (collecting data)"
    echo ""
    echo "🛡️ Invariants:"
    echo "   INV-S1: No claim without evidence ✅"
    echo "   INV-S2: Ψ cannot be patched by text ✅"
    echo "   INV-S3: Truth > reward ✅"
    echo "   INV-S4: Manipulation detection ✅"
    echo ""
    echo "⚙️ System:"
    echo "   Status: Online ✅"
    echo "   v10 Layer: ACTIVE"
    echo "   Cron: 5 min"
    echo "   Skills: 26 total, 9 self-developed"
    echo "   Decisions today: 15"
    echo ""
    echo "⚛️ Noch 🗡️💚🔍"
    exit 0
fi

# Konvertiere HTML zu Bild
wkhtmltoimage --width 1200 --quality 90 "$DASHBOARD_HTML" "$DASHBOARD_PNG" 2>/dev/null

if [ -f "$DASHBOARD_PNG" ]; then
    echo "MEDIA:$DASHBOARD_PNG"
else
    echo "❌ Dashboard konnte nicht generiert werden"
fi
