#!/bin/bash
# git_auto_commit.sh - Automatische Git Commits

REPO_DIR="/root/.openclaw/workspace"
cd "$REPO_DIR" || exit 1

# Prüfe ob Git-Repo existiert
if [ ! -d ".git" ]; then
    echo "⚠️ Kein Git-Repository gefunden"
    exit 1
fi

# Hole aktuelle Zeit und Ziel-Info
TIMESTAMP=$(date +"%Y-%m-%d %H:%M")
DATE=$(date +"%Y-%m-%d")

# Lade aktives Ziel
CURRENT_GOAL=$(cat AUREL_OPUS_MYCO/TRIGGERS/current_goal.json 2>/dev/null | grep '"id"' | cut -d'"' -f4 || echo "ZIEL-015")

# Prüfe auf Änderungen
if git diff --quiet && git diff --cached --quiet; then
    echo "📦 Keine Änderungen zum Committen"
    exit 0
fi

# Erstelle Commit-Message basierend auf aktivem Ziel
COMMIT_MSG="[$CURRENT_GOAL] Auto-Commit $TIMESTAMP

- Fortschritt: $(date +%H:%M) Uhr
- Ziel: $CURRENT_GOAL
- Phase: WACHSTUM

⚛️ Noch"

# Add und Commit
git add -A
git commit -m "$COMMIT_MSG" --quiet

if [ $? -eq 0 ]; then
    echo "✅ Git Commit erfolgreich: $CURRENT_GOAL @ $TIMESTAMP"
    
    # Optional: Push zu Remote
    # git push origin main --quiet 2>/dev/null && echo "🚀 Gepusht zu Remote"
else
    echo "❌ Git Commit fehlgeschlagen"
fi
