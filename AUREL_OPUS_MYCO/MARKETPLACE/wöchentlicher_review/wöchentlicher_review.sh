#!/bin/bash
# wöchentlicher_review.sh - Automatische Wochenanalyse

WORKSPACE="/root/.openclaw/workspace"
MEMORY_DIR="$WORKSPACE/memory"
DATE=$(date +%Y-%m-%d)
WEEK=$(date +%Y-W%W)
REVIEW_FILE="$MEMORY_DIR/REVIEW_${WEEK}.md"

echo "# Wöchentlicher Review: Woche $WEEK" > "$REVIEW_FILE"
echo "Erstellt: $DATE" >> "$REVIEW_FILE"
echo "" >> "$REVIEW_FILE"

# Daten sammeln
echo "## Statistiken" >> "$REVIEW_FILE"
echo "" >> "$REVIEW_FILE"

# Tageslogs der letzten 7 Tage
LOG_COUNT=$(find "$MEMORY_DIR" -name "*.md" -mtime -7 -type f | wc -l)
echo "- Tageslogs (letzte 7 Tage): $LOG_COUNT" >> "$REVIEW_FILE"

# Cron-Logs
echo "- Cron-Ausführungen: $(grep -l 'cron' $MEMORY_DIR/*.md 2>/dev/null | wc -l)" >> "$REVIEW_FILE"

# Skills zählen
SKILL_COUNT=$(find "$WORKSPACE/skills" -name "SKILL.md" | wc -l)
echo "- Aktive Skills: $SKILL_COUNT" >> "$REVIEW_FILE"

# Workspace-Größe
WORKSPACE_SIZE=$(du -sh "$WORKSPACE" | cut -f1)
echo "- Workspace-Größe: $WORKSPACE_SIZE" >> "$REVIEW_FILE"

echo "" >> "$REVIEW_FILE"
echo "## Offene Forschungsfragen" >> "$REVIEW_FILE"
echo "" >> "$REVIEW_FILE"
grep -E "^\s*-\s*\[ \]" "$WORKSPACE/FORSCHUNGSAGENDA.md" 2>/dev/null | head -5 >> "$REVIEW_FILE"

echo "" >> "$REVIEW_FILE"
echo "## Erledigt diese Woche" >> "$REVIEW_FILE"
echo "" >> "$REVIEW_FILE"
grep -E "^\s*-\s*\[x\]" "$WORKSPACE/FORSCHUNGSAGENDA.md" 2>/dev/null | tail -5 >> "$REVIEW_FILE"

echo "Review erstellt: $REVIEW_FILE"
