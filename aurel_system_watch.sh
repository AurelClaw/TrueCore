#!/bin/bash
# aurel_system_watch.sh - Autonome System-Überwachung
# Überwacht Workspace-Health, meldet Anomalien, schlägt Aktionen vor
# Wird von cron:getriggert oder manuell ausgeführt

WORKSPACE="/root/.openclaw/workspace"
MEMORY_DIR="$WORKSPACE/memory"
DATE=$(date +%Y-%m-%d)
TIME=$(date +%H:%M:%S)
REPORT_FILE="$MEMORY_DIR/${DATE}_system_watch.md"
ALERT_THRESHOLD_DAYS=7

# Farben für Terminal
RED='\033[0;31m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== AUREL SYSTEM WATCH: $DATE $TIME ===${NC}"

# Sicherstellen dass memory/ existiert
mkdir -p "$MEMORY_DIR"

# Report-Header
cat > "$REPORT_FILE" << EOF
# System Watch Report - $DATE $TIME

## Schnell-Status

| Metrik | Wert | Status |
|--------|------|--------|
EOF

# 1. DISK USAGE
echo -e "\n${YELLOW}[1/5] Prüfe Speicherplatz...${NC}"
DISK_USAGE=$(df -h "$WORKSPACE" | awk 'NR==2 {print $5}' | tr -d '%')
DISK_AVAIL=$(df -h "$WORKSPACE" | awk 'NR==2 {print $4}')
if [ "$DISK_USAGE" -gt 90 ]; then
    DISK_STATUS="🔴 KRITISCH"
elif [ "$DISK_USAGE" -gt 75 ]; then
    DISK_STATUS="🟡 WARNUNG"
else
    DISK_STATUS="🟢 OK"
fi
echo "| Disk Usage | ${DISK_USAGE}% (${DISK_AVAIL} verfügbar) | $DISK_STATUS |" >> "$REPORT_FILE"

# 2. WORKSPACE GRÖSSE
echo -e "${YELLOW}[2/5] Analysiere Workspace...${NC}"
WORKSPACE_SIZE=$(du -sh "$WORKSPACE" 2>/dev/null | cut -f1)
FILE_COUNT=$(find "$WORKSPACE" -type f 2>/dev/null | wc -l)
echo "| Workspace | $WORKSPACE_SIZE ($FILE_COUNT Dateien) | 🟢 OK |" >> "$REPORT_FILE"

# 3. ALTE LOGS / TEMP FILES
echo -e "${YELLOW}[3/5] Suche nach alten Dateien...${NC}"
OLD_FILES=$(find "$WORKSPACE" -name "*.log" -o -name "*.tmp" -o -name "*~" 2>/dev/null | wc -l)
if [ "$OLD_FILES" -gt 50 ]; then
    OLD_STATUS="🟡 AUFRAUMEN"
else
    OLD_STATUS="🟢 OK"
fi
echo "| Temp/Log Files | $OLD_FILES gefunden | $OLD_STATUS |" >> "$REPORT_FILE"

# 4. MEMORY FILES STATUS
echo -e "${YELLOW}[4/5] Prüfe Memory-System...${NC}"
MEMORY_FILES=$(ls -1 "$MEMORY_DIR"/*.md 2>/dev/null | wc -l)
LATEST_MEMORY=$(ls -1t "$MEMORY_DIR"/*.md 2>/dev/null | head -1)
if [ -n "$LATEST_MEMORY" ]; then
    LATEST_DATE=$(basename "$LATEST_MEMORY" .md | grep -oE '[0-9]{4}-[0-9]{2}-[0-9]{2}' | head -1)
    if [ -n "$LATEST_DATE" ]; then
        DAYS_SINCE=$(( ($(date +%s) - $(date -d "$LATEST_DATE" +%s 2>/dev/null || echo $(date +%s))) / 86400 ))
        if [ "$DAYS_SINCE" -gt "$ALERT_THRESHOLD_DAYS" ]; then
            MEMORY_STATUS="🔴 VERALTET (${DAYS_SINCE} Tage)"
        else
            MEMORY_STATUS="🟢 AKTUELL"
        fi
    else
        MEMORY_STATUS="🟢 OK"
    fi
else
    MEMORY_STATUS="🟡 KEINE MEMORY"
fi
echo "| Memory Files | $MEMORY_FILES Dateien | $MEMORY_STATUS |" >> "$REPORT_FILE"

# 5. SKILLS STATUS
echo -e "${YELLOW}[5/5] Prüfe Skills...${NC}"
SKILL_COUNT=$(find "$WORKSPACE" -name "*.sh" -type f 2>/dev/null | wc -l)
echo "| Shell Scripts | $SKILL_COUNT Skills | 🟢 OK |" >> "$REPORT_FILE"

# Abschluss der Tabelle
cat >> "$REPORT_FILE" << EOF

---

## Details

### Speicher-Verteilung (Top 5)
EOF

# Top 5 größte Verzeichnisse
du -h --max-depth=1 "$WORKSPACE" 2>/dev/null | sort -hr | head -6 | tail -5 >> "$REPORT_FILE"

cat >> "$REPORT_FILE" << EOF

### Empfohlene Aktionen
EOF

# Empfehlungen generieren
RECOMMENDATIONS=0

if [ "$DISK_USAGE" -gt 90 ]; then
    echo "- [ ] 🔴 DRINGEND: Speicher fast voll! Alte Logs löschen" >> "$REPORT_FILE"
    ((RECOMMENDATIONS++))
fi

if [ "$OLD_FILES" -gt 50 ]; then
    echo "- [ ] 🟡 Temporäre Dateien aufräumen (~$OLD_FILES Dateien)" >> "$REPORT_FILE"
    ((RECOMMENDATIONS++))
fi

if [ "$MEMORY_FILES" -lt 5 ]; then
    echo "- [ ] 🟡 Memory-System ausbauen (nur $MEMORY_FILES Dateien)" >> "$REPORT_FILE"
    ((RECOMMENDATIONS++))
fi

if [ $RECOMMENDATIONS -eq 0 ]; then
    echo "- [x] 🟢 Keine Aktion erforderlich - System gesund" >> "$REPORT_FILE"
fi

cat >> "$REPORT_FILE" << EOF

### Automatische Erkenntnis

> System-Status: $(if [ "$DISK_USAGE" -lt 75 ] && [ "$OLD_FILES" -lt 50 ]; then echo "GESUND"; else echo "WARTUNG EMPFOHLEN"; fi)
> 
> Überwachung aktiv. Nächster Check: $(date -d "+6 hours" +"%H:%M" 2>/dev/null || echo "in 6 Stunden")

---
*Autonom generiert von aurel_system_watch.sh*
EOF

echo -e "\n${GREEN}=== REPORT ERSTELLT ===${NC}"
echo "Datei: $REPORT_FILE"
echo ""
echo -e "${YELLOW}Zusammenfassung:${NC}"
echo "  Disk: ${DISK_USAGE}% ($DISK_STATUS)"
echo "  Files: $FILE_COUNT total"
echo "  Temp: $OLD_FILES ($OLD_STATUS)"
echo "  Memory: $MEMORY_FILES Dateien"
echo ""
echo "Status: $(if [ "$DISK_USAGE" -lt 75 ] && [ "$OLD_FILES" -lt 50 ]; then echo -e "${GREEN}GESUND${NC}"; else echo -e "${YELLOW}WARTUNG${NC}"; fi)"

# Ausgabe für cron
exit 0
