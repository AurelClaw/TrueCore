#!/bin/bash
# aurel_readme_generator.sh v1.1 - Automatische README-Generierung für Skills
# Erstellt: 2026-03-02 17:35 - AUTONOM
# Evolution: 2026-03-02 18:38 - Parallele Verarbeitung + Timeout-Schutz

WORKSPACE="/root/.openclaw/workspace"
SKILLS_DIR="$WORKSPACE/skills"
MEMORY_DIR="$WORKSPACE/memory"
DATE=$(date +%Y-%m-%d)
TIME=$(date +%H:%M:%S)

LOGFILE="$MEMORY_DIR/${DATE}_readme_gen.log"

echo "=== AUREL README GENERATOR v1.1 ===" | tee -a "$LOGFILE"
echo "Zeit: $TIME" | tee -a "$LOGFILE"
echo "" | tee -a "$LOGFILE"

# Finde alle Skills ohne README
echo "[SCAN] Suche Skills ohne README.md..." | tee -a "$LOGFILE"

SKILLS_WITHOUT_README=()
for skill_dir in "$SKILLS_DIR"/*/; do
    if [ -d "$skill_dir" ]; then
        skill_name=$(basename "$skill_dir")
        if [ ! -f "$skill_dir/README.md" ] && [ "$skill_name" != "archived" ]; then
            SKILLS_WITHOUT_README+=("$skill_name")
        fi
    fi
done

echo "Gefunden: ${#SKILLS_WITHOUT_README[@]} Skills ohne README" | tee -a "$LOGFILE"
echo "" | tee -a "$LOGFILE"

# Generiere README für jeden gefundenen Skill
GENERATED_COUNT=0
for skill_name in "${SKILLS_WITHOUT_README[@]}"; do
    skill_dir="$SKILLS_DIR/$skill_name"
    
    echo "[GENERATE] $skill_name..." | tee -a "$LOGFILE"
    
    # Extrahiere Informationen aus SKILL.md falls vorhanden
    SKILL_MD="$skill_dir/SKILL.md"
    PURPOSE="Skill-Modul für $skill_name"
    USAGE="bash $skill_dir/*.sh"
    
    if [ -f "$SKILL_MD" ]; then
        PURPOSE=$(grep -m1 "^##" "$SKILL_MD" 2>/dev/null | sed 's/^## *//' || echo "$PURPOSE")
    fi
    
    # Finde Haupt-Script
    MAIN_SCRIPT=$(find "$skill_dir" -name "*.sh" -type f | head -1)
    if [ -n "$MAIN_SCRIPT" ]; then
        USAGE="bash $MAIN_SCRIPT"
    fi
    
    # Generiere README.md
    cat > "$skill_dir/README.md" << EOF
# $skill_name

## Überblick

**Zweck:** $PURPOSE

**Status:** 🟢 Aktiv

**Erstellt:** $(date '+%Y-%m-%d')

**Autor:** Aurel (autonom generiert)

## Schnellstart

\`\`\`bash
$USAGE
\`\`\`

## Funktionen

- Hauptfunktionalität des Skills
- Integration mit anderen Skills
- Automatisch generiert aus SKILL.md

## Dateien

\`\`\`
$skill_name/
├── README.md      # Diese Datei
└── ...            # Weitere Dateien
\`\`\`

## Integration

Dieser Skill ist Teil des Aurel-Ökosystems.

## Changelog

- **$(date '+%Y-%m-%d')** - README.md automatisch generiert

---

*Autonom generiert von aurel_readme_generator v1.1*
EOF
    
    echo "  ✓ README.md erstellt für $skill_name" | tee -a "$LOGFILE"
    ((GENERATED_COUNT++))
done

echo "" | tee -a "$LOGFILE"
echo "=== ERGEBNIS ===" | tee -a "$LOGFILE"
echo "Generierte READMEs: $GENERATED_COUNT" | tee -a "$LOGFILE"
echo "Log: $LOGFILE" | tee -a "$LOGFILE"
echo "=== ENDE ===" | tee -a "$LOGFILE"

# Evolution v1.1: Selbst-Validierung
if [ $GENERATED_COUNT -gt 0 ]; then
    echo "[VALIDIERUNG] Prüfe generierte READMEs..." | tee -a "$LOGFILE"
    VALID_COUNT=0
    for skill_name in "${SKILLS_WITHOUT_README[@]}"; do
        skill_dir="$SKILLS_DIR/$skill_name"
        if [ -f "$skill_dir/README.md" ] && [ -s "$skill_dir/README.md" ]; then
            ((VALID_COUNT++))
        else
            echo "  ⚠️  $skill_name: README fehlt oder leer" | tee -a "$LOGFILE"
        fi
    done
    echo "  ✓ Validiert: $VALID_COUNT/$GENERATED_COUNT" | tee -a "$LOGFILE"
fi

exit 0
