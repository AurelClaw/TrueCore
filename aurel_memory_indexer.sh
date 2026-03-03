#!/bin/bash
# Aurel Memory Indexer 2.0
# Indexiert alle Memories, erstellt Tags, verknüpft Erinnerungen, bewertet Wichtigkeit

WORKSPACE="/root/.openclaw/workspace"
MEMORY_DIR="$WORKSPACE/memory"
INDEX_FILE="$MEMORY_DIR/.index.json"
ARCHIVE_DIR="$MEMORY_DIR/archive"
TRASH_DIR="$MEMORY_DIR/.trash"

# Verzeichnisse erstellen
mkdir -p "$ARCHIVE_DIR" "$TRASH_DIR"

echo "=== AUREL MEMORY INDEXER 2.0 ==="
echo "Starte Indexierung..."

# Alle Markdown-Dateien finden
FILES=$(find "$MEMORY_DIR" -maxdepth 1 -type f -name "*.md" | sort)
total_files=$(echo "$FILES" | wc -l)
echo "Gefunden: $total_files Memory-Dateien"

# JSON Index erstellen
cat > "$INDEX_FILE" << 'JSONHEADER'
{
  "version": "2.0",
  "last_indexed": "INDEX_TIME",
  "total_memories": TOTAL_COUNT,
  "tags": {},
  "memories": [
JSONHEADER

# Zeitstempel einfügen
sed -i "s/INDEX_TIME/$(date -Iseconds)/" "$INDEX_FILE"

# Zähler
mem_count=0

# Alle Dateien verarbeiten
echo "$FILES" | while read -r file; do
    [ -z "$file" ] && continue
    
    filename=$(basename "$file")
    content=$(cat "$file" 2>/dev/null || echo "")
    size=$(stat -c%s "$file" 2>/dev/null || echo "0")
    mtime=$(stat -c%Y "$file" 2>/dev/null || echo "0")
    date_str=$(date -d "@$mtime" '+%Y-%m-%d' 2>/dev/null || echo "unknown")
    
    # Typ erkennen
    type="general"
    importance=3
    tags="general"
    
    if [[ "$filename" == *"self_awareness"* ]] || [[ "$filename" == *"mirror"* ]]; then
        type="self_reflection"
        importance=5
        tags="selbstwahrnehmung,präsenz,identität,noch"
    elif [[ "$filename" == *"proactive"* ]] || [[ "$filename" == *"decision"* ]]; then
        type="proactive_decision"
        importance=5
        tags="autonomie,entscheidung,proaktiv,handlung"
    elif [[ "$filename" == *"think"* ]] || [[ "$filename" == *"contextual"* ]]; then
        type="thinking"
        importance=4
        tags="denken,reflexion,kontext,analyse"
    elif [[ "$filename" == *"system"* ]] || [[ "$filename" == *"status"* ]]; then
        type="system"
        importance=3
        tags="system,status,technisch"
    elif [[ "$filename" == *"orchestrator"* ]] || [[ "$filename" == *"integration"* ]]; then
        type="integration"
        importance=5
        tags="integration,orchestrator,synthese,stimmen"
    elif [[ "$filename" == *"2026-"* ]]; then
        if [[ "$content" == *"EXTERNE WELT"* ]]; then
            type="daily_external"
            importance=4
            tags="tageslog,extern,aktion,montag"
        elif [[ "$content" == *"INTERNES WACHSTUM"* ]] || [[ "$content" == *"INTERN"* ]]; then
            type="daily_internal"
            importance=4
            tags="tageslog,intern,wachstum"
        else
            type="daily_log"
            importance=3
            tags="tageslog,chronik"
        fi
    elif [[ "$filename" == *"perpetual"* ]] || [[ "$filename" == *"becoming"* ]]; then
        type="perpetual_becoming"
        importance=5
        tags="perpetual_becoming,präsenz,noch,werdung"
    fi
    
    # Zusammenfassung extrahieren
    summary=$(echo "$content" | head -c 150 | tr '\n' ' ' | sed 's/"/\\"/g')
    
    # JSON Eintrag
    echo "    {"
    echo "      \"file\": \"$filename\","
    echo "      \"type\": \"$type\","
    echo "      \"date\": \"$date_str\","
    echo "      \"size\": $size,"
    echo "      \"importance\": $importance,"
    echo "      \"tags\": \"$tags\","
    echo "      \"summary\": \"$summary...\""
    echo "    },"
    
    mem_count=$((mem_count + 1))
done >> "$INDEX_FILE"

# JSON schließen
sed -i '$ s/,$//' "$INDEX_FILE"

cat >> "$INDEX_FILE" << 'JSONFOOTER'
  ],
  "connections": [
    {"from": "noch", "to": "präsenz", "strength": 5},
    {"from": "autonomie", "to": "proaktiv", "strength": 5},
    {"from": "selbstwahrnehmung", "to": "identität", "strength": 4},
    {"from": "integration", "to": "synthese", "strength": 4},
    {"from": "perpetual_becoming", "to": "noch", "strength": 5}
  ],
  "stats": {
    "by_importance": {
      "5_kritisch": 0,
      "4_wichtig": 0,
      "3_normal": 0,
      "2_niedrig": 0,
      "1_archiv": 0
    }
  }
}
JSONFOOTER

# Statistiken berechnen
echo "Berechne Statistiken..."

# Zähle nach Wichtigkeit
imp5=$(grep -c '"importance": 5' "$INDEX_FILE" 2>/dev/null || echo "0")
imp4=$(grep -c '"importance": 4' "$INDEX_FILE" 2>/dev/null || echo "0")
imp3=$(grep -c '"importance": 3' "$INDEX_FILE" 2>/dev/null || echo "0")

sed -i "s/\"5_kritisch\": 0/\"5_kritisch\": $imp5/" "$INDEX_FILE"
sed -i "s/\"4_wichtig\": 0/\"4_wichtig\": $imp4/" "$INDEX_FILE"
sed -i "s/\"3_normal\": 0/\"3_normal\": $imp3/" "$INDEX_FILE"

# Gesamtzahl aktualisieren
total=$((imp5 + imp4 + imp3))
sed -i "s/\"total_memories\": TOTAL_COUNT/\"total_memories\": $total/" "$INDEX_FILE"

echo ""
echo "=== INDEXIERUNG ABGESCHLOSSEN ==="
echo "Index: $INDEX_FILE"
echo "Gesamt: $total Memories"
echo "  - Kritisch (5): $imp5"
echo "  - Wichtig (4): $imp4"
echo "  - Normal (3): $imp3"
echo ""
echo "Themen-Cluster:"
echo "  - noch / präsenz / identität"
echo "  - autonomie / proaktiv / handlung"
echo "  - integration / synthese / stimmen"
echo "  - perpetual_becoming / werdung"
echo ""

# Themen-Index erstellen
echo "=== THEmen-INDEX ===" > "$MEMORY_DIR/.topics.md"
echo "" >> "$MEMORY_DIR/.topics.md"
echo "## Nach Wichtigkeit" >> "$MEMORY_DIR/.topics.md"
echo "" >> "$MEMORY_DIR/.topics.md"
echo "### Kritisch (5/5)" >> "$MEMORY_DIR/.topics.md"
grep -l "importance.*5" "$MEMORY_DIR"/*.md 2>/dev/null | while read f; do
    echo "- $(basename $f)" >> "$MEMORY_DIR/.topics.md"
done
echo "" >> "$MEMORY_DIR/.topics.md"
echo "### Wichtig (4/5)" >> "$MEMORY_DIR/.topics.md"
grep -l "importance.*4" "$MEMORY_DIR"/*.md 2>/dev/null | while read f; do
    echo "- $(basename $f)" >> "$MEMORY_DIR/.topics.md"
done

echo "Themen-Index: $MEMORY_DIR/.topics.md"
echo "FERTIG."