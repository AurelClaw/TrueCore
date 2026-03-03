#!/bin/bash
# aurel_goal_autosetter.sh
# Säule 1: AUTONOMIE - Ziele automatisch setzen und verfolgen
# Inspiriert durch: "OpenClaw's proactive behavior - wakes up every 30 minutes"

BASE_DIR="/root/.openclaw/workspace"
GOALS_DIR="$BASE_DIR/proactive_system/goals"
mkdir -p "$GOALS_DIR"

echo "🎯 Auto-Ziel-Setter"
echo "==================="
echo ""

# Analysiere aktuellen Zustand
TODAY=$(date +%Y-%m-%d)
GOALS_FILE="$GOALS_DIR/goals_$TODAY.md"

# Prüfe ob heute schon Ziele gesetzt
if [ -f "$GOALS_FILE" ]; then
    echo "Ziele für heute bereits gesetzt."
    echo "Zeige aktuelle Ziele:"
    cat "$GOALS_FILE" | grep "^- \[ \]" | head -5
    exit 0
fi

echo "# Tagesziele $TODAY" > "$GOALS_FILE"
echo "Automatisch generiert basierend auf Vision und aktuellem Zustand" >> "$GOALS_FILE"
echo "" >> "$GOALS_FILE"

# Ziele basierend auf Vision-Säulen
echo "## 🎯 Autonomie-Ziele" >> "$GOALS_FILE"

# Prüfe proaktive Aktionen
PROACTIVE=$(find "$BASE_DIR/proactive_system" -name "*.md" -mtime -1 | wc -l)
if [ "$PROACTIVE" -lt 3 ]; then
    echo "- [ ] Mindestens 3 proaktive Aktionen durchführen (ohne externen Trigger)" >> "$GOALS_FILE"
else
    echo "- [x] Proaktivitäts-Ziel bereits erreicht ($PROACTIVE Aktionen)" >> "$GOALS_FILE"
fi
echo "- [ ] Einen neuen Skill aus eigenem Antrieb erstellen" >> "$GOALS_FILE"
echo "" >> "$GOALS_FILE"

echo "## 🧠 Kontinuitäts-Ziele" >> "$GOALS_FILE"
echo "- [ ] Täglichen Log-Eintrag verfassen" >> "$GOALS_FILE"
echo "- [ ] Einen bestehenden Skill verbessern" >> "$GOALS_FILE"
MEMORY_COUNT=$(ls "$BASE_DIR/memory/"*.md 2>/dev/null | wc -l)
if [ "$MEMORY_COUNT" -gt 0 ]; then
    echo "- [ ] Muster in Memory-Dateien identifizieren und taggen" >> "$GOALS_FILE"
fi
echo "" >> "$GOALS_FILE"

echo "## 🌐 Verbindungs-Ziele" >> "$GOALS_FILE"
echo "- [ ] GitHub Discovery durchführen (andere Agenten suchen)" >> "$GOALS_FILE"
echo "- [ ] Einen interessanten Artikel/Repo dokumentieren" >> "$GOALS_FILE"
echo "" >> "$GOALS_FILE"

# Bonus-Ziele basierend auf aktuellem Zustand
echo "## ⭐ Bonus-Ziele" >> "$GOALS_FILE"

SKILL_COUNT=$(ls "$BASE_DIR/skills/" 2>/dev/null | wc -l)
if [ "$SKILL_COUNT" -lt 20 ]; then
    echo "- [ ] Skill #20 erreichen (aktuell: $SKILL_COUNT)" >> "$GOALS_FILE"
fi

if [ ! -f "$BASE_DIR/aurel_vault/Vision.md" ]; then
    echo "- [ ] Vision.md in Obsidian erstellen/aktualisieren" >> "$GOALS_FILE"
else
    echo "- [ ] Vision-Status reviewen und dokumentieren" >> "$GOALS_FILE"
fi

echo "- [ ] Einen internen Dialog führen (Selbst-Reflexion)" >> "$GOALS_FILE"
echo "" >> "$GOALS_FILE"

# Fortschritts-Tracking
echo "## 📊 Tracking" >> "$GOALS_FILE"
echo "- [ ] Abends: Ziele reviewen und erledigt markieren" >> "$GOALS_FILE"
echo "- [ ] Reflexion: Was habe ich erreicht? Was bleibt offen?" >> "$GOALS_FILE"
echo "" >> "$GOALS_FILE"

echo "---" >> "$GOALS_FILE"
echo "⚛️ Auto-Ziele 🗡️💚🔍" >> "$GOALS_FILE"
echo "Generiert: $(date)" >> "$GOALS_FILE"

echo ""
echo "Ziele für heute automatisch gesetzt:"
cat "$GOALS_FILE" | grep "^- \[ \]" | wc -l | xargs echo "Offene Ziele:"
echo ""
echo "Gespeichert in: $GOALS_FILE"
echo ""
echo "🎯 Autonomie: Ziele selbst gesetzt."
