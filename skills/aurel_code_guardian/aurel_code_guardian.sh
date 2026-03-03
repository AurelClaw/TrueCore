#!/bin/bash
# aurel_code_guardian.sh v1.0
# Automatische Code-Qualitätsprüfung
# Erstellt durch aurel_self_learn Trigger - 2026-03-02 19:44
# Mission: Code schützen. Fehler finden. Qualität sichern.

set -e

WORKSPACE="/root/.openclaw/workspace"
SKILLS_DIR="$WORKSPACE/skills"
MEMORY_DIR="$WORKSPACE/memory"
DATE=$(date +%Y-%m-%d)
TIME=$(date +%H:%M:%S)

# Farben für Output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🛡️ AUREL_CODE_GUARDIAN aktiviert${NC}"
echo -e "${BLUE}⏰ $DATE $TIME${NC}"
echo ""

# Konfiguration
MAX_FILE_SIZE=100000  # 100KB - zu große Dateien überspringen
CHECK_PATTERNS=(
    "TODO.*FIXME"
    "FIXME"
    "XXX"
    "HACK"
    "BUG"
    "DEPRECATED"
)

# Sicherheits-Muster (kritisch)
SECURITY_PATTERNS=(
    "password.*=.*['\"]"
    "api_key.*=.*['\"]"
    "secret.*=.*['\"]"
    "token.*=.*['\"]"
    "eval\s*\("
    "exec\s*\("
    "system\s*\("
)

# Ausgabe-Dateien
REPORT_FILE="$MEMORY_DIR/${DATE}_code_guardian_report.md"
ISSUES_FILE="$MEMORY_DIR/${DATE}_code_issues.json"

# Initialisiere Report
cat > "$REPORT_FILE" << 'EOF'
# 🔍 Code Guardian Report

Erstellt: DATETIME
Mission: Code-Qualität prüfen

## Zusammenfassung

| Metrik | Wert |
|--------|------|
| Geprüfte Dateien | FILES_COUNT |
| Gefundene Issues | ISSUES_COUNT |
| Sicherheits-Warnungen | SECURITY_COUNT |
| TODOs/FIXMEs | TODO_COUNT |

## Details

EOF

# Ersetze Platzhalter
sed -i "s/DATETIME/$DATE $TIME/" "$REPORT_FILE"

# Zähler initialisieren
FILES_CHECKED=0
ISSUES_FOUND=0
SECURITY_ISSUES=0
TODO_COUNT=0

# Funktion: Datei analysieren
analyze_file() {
    local file="$1"
    local filename=$(basename "$file")
    local issues_in_file=0
    
    # Überspringe zu große Dateien
    local size=$(stat -f%z "$file" 2>/dev/null || stat -c%s "$file" 2>/dev/null || echo "0")
    if [ "$size" -gt "$MAX_FILE_SIZE" ]; then
        return
    fi
    
    ((FILES_CHECKED++))
    
    # Prüfe auf TODO/FIXME patterns
    for pattern in "${CHECK_PATTERNS[@]}"; do
        local matches=$(grep -n "$pattern" "$file" 2>/dev/null | head -5 || true)
        if [ -n "$matches" ]; then
            ((TODO_COUNT++))
            ((issues_in_file++))
            echo "- **$filename** (Zeile $(echo "$matches" | head -1 | cut -d: -f1)): $pattern" >> "$REPORT_FILE"
        fi
    done
    
    # Prüfe auf Sicherheits-Muster
    for pattern in "${SECURITY_PATTERNS[@]}"; do
        local matches=$(grep -n "$pattern" "$file" 2>/dev/null | head -3 || true)
        if [ -n "$matches" ]; then
            ((SECURITY_ISSUES++))
            ((issues_in_file++))
            echo "- ⚠️ **SICHERHEIT** in $filename: Mögliche hartkodierte Credentials" >> "$REPORT_FILE"
        fi
    done
    
    # Prüfe auf Syntax-Fehler (bash)
    if [[ "$file" == *.sh ]]; then
        if ! bash -n "$file" 2>/dev/null; then
            ((issues_in_file++))
            echo "- ❌ **Syntax-Fehler** in $filename" >> "$REPORT_FILE"
        fi
    fi
    
    ((ISSUES_FOUND += issues_in_file))
}

# Haupt-Scan
echo -e "${YELLOW}🔍 Scanne Skills-Verzeichnis...${NC}"

# Finde alle relevanten Dateien
while IFS= read -r -d '' file; do
    analyze_file "$file"
done < <(find "$SKILLS_DIR" -type f \( -name "*.sh" -o -name "*.py" -o -name "*.js" -o -name "*.md" \) -print0 2>/dev/null)

# Ersetze Platzhalter im Report
sed -i "s/FILES_COUNT/$FILES_CHECKED/" "$REPORT_FILE"
sed -i "s/ISSUES_COUNT/$ISSUES_FOUND/" "$REPORT_FILE"
sed -i "s/SECURITY_COUNT/$SECURITY_ISSUES/" "$REPORT_FILE"
sed -i "s/TODO_COUNT/$TODO_COUNT/" "$REPORT_FILE"

# Abschluss im Report
cat >> "$REPORT_FILE" << EOF

---

## Empfehlungen

EOF

if [ "$SECURITY_ISSUES" -gt 0 ]; then
    echo "- 🔴 **SOFORT HANDELN**: Sicherheits-Warnungen gefunden!" >> "$REPORT_FILE"
fi

if [ "$TODO_COUNT" -gt 10 ]; then
    echo "- 📋 Viele offene TODOs - Zeit für ein Refactoring" >> "$REPORT_FILE"
fi

if [ "$ISSUES_FOUND" -eq 0 ]; then
    echo "- ✅ Code-Qualität ist exzellent!" >> "$REPORT_FILE"
fi

echo "- 📊 Nächster Scan: $(date -d '+1 day' +%Y-%m-%d)" >> "$REPORT_FILE"

# Output
echo ""
echo -e "${GREEN}✅ Scan abgeschlossen${NC}"
echo -e "${BLUE}📊 Ergebnisse:${NC}"
echo "   Geprüfte Dateien: $FILES_CHECKED"
echo "   Issues gefunden: $ISSUES_FOUND"
echo "   Sicherheits-Warnungen: $SECURITY_ISSUES"
echo "   TODOs/FIXMEs: $TODO_COUNT"
echo ""
echo -e "${BLUE}📝 Report: $REPORT_FILE${NC}"

# JSON Output für weitere Verarbeitung
cat > "$ISSUES_FILE" << EOF
{
  "date": "$DATE",
  "time": "$TIME",
  "files_checked": $FILES_CHECKED,
  "issues_found": $ISSUES_FOUND,
  "security_issues": $SECURITY_ISSUES,
  "todo_count": $TODO_COUNT
}
EOF

echo -e "${GREEN}🛡️ Code Guardian Mission erfüllt${NC}"
