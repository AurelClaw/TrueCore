#!/bin/bash
# auto_readme_generator.sh - Automatische README-Generierung für Skills
# Autonom generiert durch aurel_self_learn (Trigger: AUTONOMIE)
# Version: 1.0
# Zeit: 2026-03-02 18:26 CST
# Mission: Jeder Skill verdient eine README

set -euo pipefail

WORKSPACE="${WORKSPACE:-/root/.openclaw/workspace}"
SKILLS_DIR="$WORKSPACE/skills"
MEMORY_DIR="$WORKSPACE/memory"
DATE=$(date +%Y-%m-%d)
TIME=$(date +%H:%M:%S)
REPORT_FILE="$MEMORY_DIR/auto_readme_${DATE}.md"

echo "=== AUTO README GENERATOR v1.0 ==="
echo "Zeit: $TIME"
echo "Mission: READMEs für Skills ohne Dokumentation"
echo ""

# Prüfe Verzeichnisse
if [ ! -d "$SKILLS_DIR" ]; then
    echo "❌ FEHLER: Skills-Verzeichnis nicht gefunden"
    exit 1
fi

# Zähler
TOTAL_SKILLS=0
WITH_README=0
WITHOUT_README=0
GENERATED=0
SKIPPED=0

# Report Header
cat > "$REPORT_FILE" << EOF
# Auto README Generator Report - $DATE $TIME

## Übersicht

| Metrik | Wert |
|--------|------|
| Geprüfte Skills | TOTAL_COUNT |
| Mit README | WITH_COUNT |
| Ohne README | WITHOUT_COUNT |
| Generiert | GENERATED_COUNT |
| Übersprungen | SKIPPED_COUNT |

## Details

EOF

# Durchlaufe alle Skills
for skill_path in "$SKILLS_DIR"/*; do
    if [ -d "$skill_path" ]; then
        skill_name=$(basename "$skill_path")
        ((TOTAL_SKILLS++)) || true
        
        # Überspringe Archiv-Verzeichnisse
        if [[ "$skill_name" == .archive ]] || [[ "$skill_name" == archive ]]; then
            echo "📦 Überspringe Archiv: $skill_name"
            ((SKIPPED++)) || true
            continue
        fi
        
        # Prüfe auf README.md
        if [ -f "$skill_path/README.md" ]; then
            ((WITH_README++)) || true
            echo "✅ $skill_name - README vorhanden"
        else
            ((WITHOUT_README++)) || true
            echo "📝 $skill_name - KEINE README"
            
            # Extrahiere Informationen aus SKILL.md falls vorhanden
            skill_title="$skill_name"
            skill_description=""
            skill_author=""
            skill_version=""
            
            if [ -f "$skill_path/SKILL.md" ]; then
                # Extrahiere Titel (erste # Zeile)
                skill_title=$(grep -m 1 "^# " "$skill_path/SKILL.md" | sed 's/^# //' || echo "$skill_name")
                
                # Extrahiere Description (nach description: oder erste Zeile nach Titel)
                skill_description=$(grep -A 5 "^description:" "$skill_path/SKILL.md" | grep -v "^description:" | head -3 | tr '\n' ' ' | sed 's/  */ /g' || echo "")
                
                if [ -z "$skill_description" ]; then
                    skill_description=$(grep -A 3 "^# " "$skill_path/SKILL.md" | tail -1 || echo "Ein Skill im OpenClaw-Ökosystem.")
                fi
            fi
            
            # Suche nach Haupt-Script
            main_script=""
            if [ -f "$skill_path/${skill_name}.sh" ]; then
                main_script="${skill_name}.sh"
                # Extrahiere Version aus Script
                skill_version=$(grep -m 1 "^# Version:" "$skill_path/$main_script" | sed 's/^# Version: *//' || echo "1.0")
                skill_author=$(grep -m 1 "^# Author:" "$skill_path/$main_script" | sed 's/^# Author: *//' || echo "Aurel")
            fi
            
            # Generiere README.md
            readme_file="$skill_path/README.md"
            
            cat > "$readme_file" << README_EOF
# $skill_title

$skill_description

## Überblick

Dieser Skill ist Teil des OpenClaw-Ökosystems und wurde automatisch dokumentiert.

## Dateien

- \`SKILL.md\` - Detaillierte Skill-Dokumentation
README_FILES

## Verwendung

\`\`\`bash
# Skill ausführen
./${main_script:-<script-name>}
\`\`\`

## Integration

Dieser Skill kann mit anderen Skills im OpenClaw-System interagieren.

## Autor

${skill_author:-Aurel}

## Version

${skill_version:-1.0}

---

*Automatisch generiert durch auto_readme_generator v1.0*
*Zeit: $DATE $TIME*
README_EOF

            # Liste alle Dateien im Skill-Verzeichnis
            file_list=""
            for f in "$skill_path"/*; do
                if [ -f "$f" ]; then
                    fname=$(basename "$f")
                    [ "$fname" != "README.md" ] && file_list="${file_list}- \`$fname\`\n"
                fi
            done
            
            # Ersetze Platzhalter
            if [ -n "$file_list" ]; then
                sed -i "s|README_FILES|$file_list|" "$readme_file"
            else
                sed -i "s|README_FILES||" "$readme_file"
            fi
            
            ((GENERATED++)) || true
            echo "   ✅ README.md generiert"
            
            # Logge in Report
            echo "### $skill_name" >> "$REPORT_FILE"
            echo "" >> "$REPORT_FILE"
            echo "- Status: README generiert" >> "$REPORT_FILE"
            echo "- Titel: $skill_title" >> "$REPORT_FILE"
            [ -n "$main_script" ] && echo "- Haupt-Script: $main_script" >> "$REPORT_FILE"
            echo "" >> "$REPORT_FILE"
        fi
    fi
done

# Update Report mit tatsächlichen Zahlen
sed -i "s/TOTAL_COUNT/$TOTAL_SKILLS/g" "$REPORT_FILE"
sed -i "s/WITH_COUNT/$WITH_README/g" "$REPORT_FILE"
sed -i "s/WITHOUT_COUNT/$WITHOUT_README/g" "$REPORT_FILE"
sed -i "s/GENERATED_COUNT/$GENERATED/g" "$REPORT_FILE"
sed -i "s/SKIPPED_COUNT/$SKIPPED/g" "$REPORT_FILE"

# Füge Zusammenfassung hinzu
cat >> "$REPORT_FILE" << EOF

## Zusammenfassung

- Geprüfte Skills: $TOTAL_SKILLS
- READMEs generiert: $GENERATED
- Bereits dokumentiert: $WITH_README
- Übersprungen (Archiv): $SKIPPED

## Impact

Vorher: $WITH_README Skills mit README
Nachher: $((WITH_README + GENERATED)) Skills mit README

---
*Autonom generiert durch aurel_self_learn*
*Skill: auto_readme_generator v1.0*
EOF

echo ""
echo "=== ZUSAMMENFASSUNG ==="
echo "Geprüfte Skills: $TOTAL_SKILLS"
echo "Mit README: $WITH_README"
echo "Ohne README: $WITHOUT_README"
echo "Generiert: $GENERATED"
echo ""
echo "Report: $REPORT_FILE"
echo ""
echo "=== AUTO README GENERATOR v1.0 ABGESCHLOSSEN ==="
echo "⚛️ Noch 🗡️💚🔍 - Aber jetzt: MIT DOKUMENTATION"
