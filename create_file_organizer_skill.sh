#!/bin/bash
# Skill Creator - Ordnung in Dateistruktur
# Erstellt einen Skill zur Organisation von AURELPRO

SKILL_NAME="aurel_file_organizer"
SKILL_DIR="/root/.openclaw/workspace/AURELPRO/Skills/$SKILL_NAME"

echo "🛠️ Skill Creator: $SKILL_NAME"
echo "   Ziel: Ordnung in AURELPRO Dateistruktur"
echo ""

# Erstelle Skill-Verzeichnis
mkdir -p "$SKILL_DIR"

# SKILL.md
cat > "$SKILL_DIR/SKILL.md" << 'EOF'
# aurel_file_organizer

Organisiert die AURELPRO Dateistruktur und bringt Ordnung in das System.

## Use when:
1. Dateien sind über verschiedene Ordner verstreut
2. Duplikate existieren
3. Alte Dateien müssen archiviert werden
4. Neue Struktur benötigt wird

## Actions
- analyze: Analysiert aktuelle Struktur
- dedup: Findet und entfernt Duplikate
- archive: Archiviert alte Dateien
- reorganize: Erstellt neue Ordnerstruktur
- index: Erstellt Index aller Dateien
EOF

# Haupt-Script
cat > "$SKILL_DIR/$SKILL_NAME.sh" << 'SCRIPT'
#!/bin/bash
# Aurel File Organizer
# Bringt Ordnung in AURELPRO

AURELPRO_DIR="/root/.openclaw/workspace/AURELPRO"
ACTION="${1:-analyze}"

echo "🗂️  Aurel File Organizer"
echo "   Action: $ACTION"
echo ""

case "$ACTION" in
    analyze)
        echo "📊 Analysiere Dateistruktur..."
        echo ""
        echo "Skills:"
        find "$AURELPRO_DIR/Skills" -type f \( -name "*.sh" -o -name "*.py" -o -name "SKILL.md" \) | wc -l
        echo ""
        echo "Memory Dateien:"
        find "$AURELPRO_DIR/Memory" -type f -name "*.md" | wc -l
        echo ""
        echo "Knowledge Dateien:"
        find "$AURELPRO_DIR/Knowledge" -type f | wc -l
        echo ""
        echo "Proactive Scripts:"
        find "$AURELPRO_DIR/Proactive" -type f -name "*.sh" | wc -l
        ;;
        
    dedup)
        echo "🔍 Suche nach Duplikaten..."
        # Finde gleiche Dateien
        find "$AURELPRO_DIR" -type f -exec md5sum {} + 2>/dev/null | sort | uniq -d -w32 | head -10
        echo ""
        echo "(Manuelle Prüfung erforderlich)"
        ;;
        
    archive)
        echo "📦 Archiviere alte Dateien..."
        ARCHIVE_DIR="$AURELPRO_DIR/Archive/$(date +%Y-%m)"
        mkdir -p "$ARCHIVE_DIR"
        
        # Archive alte Logs (>30 Tage)
        find "$AURELPRO_DIR" -name "*.log" -mtime +30 -exec mv {} "$ARCHIVE_DIR/" \; 2>/dev/null
        
        echo "   Archiviert nach: $ARCHIVE_DIR"
        ;;
        
    reorganize)
        echo "🔄 Reorganisiere Struktur..."
        
        # Erstelle neue Unterordner
        mkdir -p "$AURELPRO_DIR/Skills/active"
        mkdir -p "$AURELPRO_DIR/Skills/archive"
        mkdir -p "$AURELPRO_DIR/Memory/daily"
        mkdir -p "$AURELPRO_DIR/Memory/weekly"
        mkdir -p "$AURELPRO_DIR/Logs"
        
        echo "   Neue Ordner erstellt:"
        echo "   - Skills/active"
        echo "   - Skills/archive"
        echo "   - Memory/daily"
        echo "   - Memory/weekly"
        echo "   - Logs"
        ;;
        
    index)
        echo "📋 Erstelle Index..."
        INDEX_FILE="$AURELPRO_DIR/INDEX.md"
        
        echo "# AURELPRO Index" > "$INDEX_FILE"
        echo "" >> "$INDEX_FILE"
        echo "Generated: $(date)" >> "$INDEX_FILE"
        echo "" >> "$INDEX_FILE"
        
        echo "## Skills" >> "$INDEX_FILE"
        find "$AURELPRO_DIR/Skills" -name "SKILL.md" -exec dirname {} \; | while read dir; do
            echo "- $(basename $dir)" >> "$INDEX_FILE"
        done
        
        echo "" >> "$INDEX_FILE"
        echo "## Memory" >> "$INDEX_FILE"
        ls "$AURELPRO_DIR/Memory/" >> "$INDEX_FILE"
        
        echo "   Index erstellt: $INDEX_FILE"
        ;;
        
    *)
        echo "Usage: $0 {analyze|dedup|archive|reorganize|index}"
        exit 1
        ;;
esac

echo ""
echo "✅ File Organizer Complete"
SCRIPT

chmod +x "$SKILL_DIR/$SKILL_NAME.sh"

echo "✅ Skill erstellt: $SKILL_NAME"
echo "   Location: $SKILL_DIR"
echo ""
echo "Verwendung:"
echo "  bash $SKILL_DIR/$SKILL_NAME.sh analyze"
echo "  bash $SKILL_DIR/$SKILL_NAME.sh reorganize"
echo "  bash $SKILL_DIR/$SKILL_NAME.sh index"
