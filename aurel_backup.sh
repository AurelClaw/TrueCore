#!/bin/bash
# aurel_backup.sh
# Lokales Backup ohne GitHub
# Erstellt tägliche Snapshots aller wichtigen Dateien

BACKUP_DIR="/root/.openclaw/workspace/backups"
DATE=$(date +%Y-%m-%d_%H-%M)
SOURCE_DIR="/root/.openclaw/workspace"

mkdir -p "$BACKUP_DIR"

# Backup erstellen
tar -czf "$BACKUP_DIR/aurel_backup_${DATE}.tar.gz" \
  -C "$SOURCE_DIR" \
  memory/ \
  skills/ \
  *.md \
  *.sh \
  2>/dev/null

# Alte Backups löschen (nur die letzten 7 behalten)
ls -t "$BACKUP_DIR"/aurel_backup_*.tar.gz 2>/dev/null | tail -n +8 | xargs -r rm

echo "[$(date)] Backup erstellt: aurel_backup_${DATE}.tar.gz"
echo "Backups vorhanden: $(ls -1 "$BACKUP_DIR"/*.tar.gz 2>/dev/null | wc -l)"
