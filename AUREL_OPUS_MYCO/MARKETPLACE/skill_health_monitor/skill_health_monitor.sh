#!/bin/bash
# skill_health_monitor.sh - Skill-System Analyse & Optimierung
# Autonom generiert durch aurel_self_learn v2.1 (Mittagstrigger)
# Version: 1.4 (Optimierung: Parallele Verarbeitung + Cache)
# Zeit: 2026-03-02 19:28 CST
# Evolution: 2026-03-02 19:28 - Parallele Skill-Analyse + Smart Caching

set -euo pipefail  # Strikte Fehlerbehandlung

# Performance-Tracking: Startzeit
START_TIME=$(date +%s.%N)

# === NEU IN v1.4: Parallele Verarbeitung ===
PARALLEL_JOBS="${PARALLEL_JOBS:-4}"  # Anzahl paralleler Jobs (konfigurierbar)
ENABLE_PARALLEL="${ENABLE_PARALLEL:-true}"  # Parallelisierung ein/aus
CACHE_DIR="${CACHE_DIR:-$WORKSPACE/.cache/skill_health}"  # Cache-Verzeichnis
CACHE_TTL_SECONDS="${CACHE_TTL_SECONDS:-300}"  # Cache gültig für 5 Minuten

WORKSPACE="${WORKSPACE:-/root/.openclaw/workspace}"
SKILLS_DIR="$WORKSPACE/skills"
MEMORY_DIR="$WORKSPACE/memory"
DATE=$(date +%Y-%m-%d)
TIME=$(date +%H:%M:%S)
REPORT_FILE="$MEMORY_DIR/skill_health_${DATE}.md"
MAX_REPORT_AGE_DAYS=30  # Log-Rotation: Alte Reports löschen

# === NEU IN v1.4: Cache-Initialisierung ===
if [ "$ENABLE_PARALLEL" = true ]; then
    mkdir -p "$CACHE_DIR"
    # Alten Cache aufräumen
    find "$CACHE_DIR" -type f -mtime +1 -delete 2>/dev/null || true
fi

echo "=== SKILL HEALTH MONITOR v1.4 ==="
echo "Zeit: $TIME"
echo "Parallel: $ENABLE_PARALLEL (Jobs: $PARALLEL_JOBS)"
echo "Cache: $CACHE_DIR (TTL: ${CACHE_TTL_SECONDS}s)"
echo ""

# Prüfe Verzeichnisse mit Fehlerbehandlung
if [ ! -d "$WORKSPACE" ]; then
    echo "❌ FEHLER: Workspace nicht gefunden: $WORKSPACE"
    exit 1
fi

if [ ! -d "$SKILLS_DIR" ]; then
    echo "⚠️  WARNUNG: Skills-Verzeichnis nicht gefunden, erstelle es..."
    mkdir -p "$SKILLS_DIR"
fi

if [ ! -d "$MEMORY_DIR" ]; then
    echo "⚠️  WARNUNG: Memory-Verzeichnis nicht gefunden, erstelle es..."
    mkdir -p "$MEMORY_DIR"
fi

# Log-Rotation: Alte Reports löchen (älter als MAX_REPORT_AGE_DAYS)
if [ -d "$MEMORY_DIR" ]; then
    DELETED_COUNT=$(find "$MEMORY_DIR" -name "skill_health_*.md" -mtime +$MAX_REPORT_AGE_DAYS -delete -print 2>/dev/null | wc -l)
    if [ "$DELETED_COUNT" -gt 0 ]; then
        echo "🗑️  Log-Rotation: $DELETED_COUNT alte Report(s) gelöscht (>${MAX_REPORT_AGE_DAYS} Tage)"
    fi
fi

# Farben für Terminal (nur wenn Terminal interaktiv)
if [ -t 1 ]; then
    RED='\033[0;31m'
    GREEN='\033[0;32m'
    YELLOW='\033[1;33m'
    BLUE='\033[0;34m'
    NC='\033[0m' # No Color
else
    RED=''
    GREEN=''
    YELLOW=''
    BLUE=''
    NC=''
fi

# Zähler initialisieren (mit Fallback auf 0)
TOTAL_SKILLS=0
WITH_README=0
WITH_SCRIPT=0
WITH_SKILL_MD=0
ARCHIVED=0
ACTIVE=0
RECENTLY_MODIFIED=0
NEEDS_ATTENTION=0
SKILLS_WITH_ISSUES=()

# Report Header
cat > "$REPORT_FILE" << EOF
# Skill Health Report - $DATE $TIME

## Übersicht

| Metrik | Wert |
|--------|------|
| Gesamt-Skills | SKILLS_COUNT |
| Aktiv | ACTIVE_COUNT |
| Archiviert | ARCHIVED_COUNT |
| Mit SKILL.md | SKILL_MD_COUNT |
| Mit README | README_COUNT |
| Kürzlich modifiziert | RECENT_COUNT |
| Benötigen Aufmerksamkeit | ATTENTION_COUNT |

## Detaillierte Analyse

EOF

echo -e "${BLUE}[ANALYSE] Scanne Skill-Verzeichnis...${NC}"

# === NEU IN v1.4: Parallele Skill-Analyse ===
analyze_single_skill() {
    local skill_path="$1"
    local skill_name=$(basename "$skill_path")
    local cache_file="$CACHE_DIR/${skill_name}.cache"
    
    # Prüfe Cache
    if [ -f "$cache_file" ]; then
        local cache_age=$(($(date +%s) - $(stat -c %Y "$cache_file" 2>/dev/null || stat -f %m "$cache_file" 2>/dev/null || echo 0)))
        if [ "$cache_age" -lt "$CACHE_TTL_SECONDS" ]; then
            cat "$cache_file"
            return 0
        fi
    fi
    
    # Lokale Variablen
    local has_skill_md=0 has_readme=0 has_script=0 is_archived=0 recently_modified=0
    local script_count=0 status_icon="✅" issues=""
    
    # Prüfe auf SKILL.md
    if [ -f "$skill_path/SKILL.md" ]; then
        has_skill_md=1
    fi
    
    # Prüfe auf README.md
    if [ -f "$skill_path/README.md" ]; then
        has_readme=1
    fi
    
    # Prüfe auf ausführbare Scripts
    if [ -d "$skill_path" ]; then
        script_count=$(find "$skill_path" -maxdepth 1 -type f -executable 2>/dev/null | wc -l)
        if [ "$script_count" -gt 0 ]; then
            has_script=1
        fi
    fi
    
    # Prüfe auf Archiv-Status
    if [[ "$skill_name" == archived_* ]] || [[ "$skill_name" == .archive ]] || [ -f "$skill_path/.archived" ] || [ -f "$skill_path/ARCHIVED" ]; then
        is_archived=1
    fi
    
    # Prüfe auf letzte Modifikation
    if [ -d "$skill_path" ]; then
        if [ -n "$(find "$skill_path" -mtime -7 2>/dev/null)" ]; then
            recently_modified=1
        fi
    fi
    
    # Bewertung
    if [ $is_archived -eq 0 ]; then
        if [ $has_skill_md -eq 0 ]; then
            issues="${issues}Keine SKILL.md; "
            status_icon="⚠️"
        fi
        if [ $has_script -eq 0 ]; then
            issues="${issues}Kein ausführbares Script; "
            status_icon="⚠️"
        fi
        if [ $recently_modified -eq 0 ] && [ $is_archived -eq 0 ]; then
            issues="${issues}Inaktiv >7 Tage; "
        fi
    fi
    
    # Ausgabe formatieren und cachen
    local output="${skill_name}|${has_skill_md}|${has_readme}|${has_script}|${is_archived}|${recently_modified}|${script_count}|${status_icon}|${issues}"
    echo "$output" > "$cache_file"
    echo "$output"
}

export -f analyze_single_skill 2>/dev/null || true
export CACHE_DIR CACHE_TTL_SECONDS

# Durchlaufe alle Skills
if [ ! -d "$SKILLS_DIR" ] || [ -z "$(ls -A "$SKILLS_DIR" 2>/dev/null)" ]; then
    echo -e "${YELLOW}[WARNUNG] Keine Skills gefunden${NC}"
else
    # Sammle alle Skill-Pfade
    SKILL_PATHS=()
    for skill_path in "$SKILLS_DIR"/*; do
        if [ -d "$skill_path" ]; then
            SKILL_PATHS+=("$skill_path")
        fi
    done
    
    TOTAL_SKILLS=${#SKILL_PATHS[@]}
    
    if [ "$ENABLE_PARALLEL" = true ] && [ "$TOTAL_SKILLS" -gt 10 ] && command -v xargs >/dev/null 2>&1; then
        echo -e "${BLUE}[OPTIMIERUNG] Parallele Verarbeitung mit $PARALLEL_JOBS Jobs...${NC}"
        
        # Parallele Verarbeitung mit xargs
        printf '%s\n' "${SKILL_PATHS[@]}" | xargs -P "$PARALLEL_JOBS" -I {} bash -c 'analyze_single_skill "$@"' _ {} > "$CACHE_DIR/.results.tmp"
        
        # Ergebnisse verarbeiten
        while IFS='|' read -r skill_name has_skill_md has_readme has_script is_archived recently_modified script_count status_icon issues; do
            [ "$has_skill_md" -eq 1 ] && ((WITH_SKILL_MD++)) || true
            [ "$has_readme" -eq 1 ] && ((WITH_README++)) || true
            [ "$has_script" -eq 1 ] && ((WITH_SCRIPT++)) || true
            [ "$is_archived" -eq 1 ] && ((ARCHIVED++)) || true
            [ "$is_archived" -eq 0 ] && ((ACTIVE++)) || true
            [ "$recently_modified" -eq 1 ] && ((RECENTLY_MODIFIED++)) || true
            
            if [ -n "$issues" ] && [ "$is_archived" -eq 0 ]; then
                ((NEEDS_ATTENTION++)) || true
                SKILLS_WITH_ISSUES+=("$skill_name: $issues")
            fi
            
            # Terminal-Ausgabe für aktive Skills
            if [ "$is_archived" -eq 0 ]; then
                echo -e "${status_icon} ${skill_name}"
                [ -n "$issues" ] && echo -e "   ${YELLOW}→ $issues${NC}"
            fi
            
            # Zur Report-Datei hinzufügen
            {
                echo "### $skill_name"
                echo ""
                echo "- Status: $([ "$is_archived" -eq 1 ] && echo 'Archiviert' || echo 'Aktiv')"
                echo "- SKILL.md: $([ "$has_skill_md" -eq 1 ] && echo '✅' || echo '❌')"
                echo "- README.md: $([ "$has_readme" -eq 1 ] && echo '✅' || echo '❌')"
                echo "- Ausführbare Scripts: $script_count"
                echo "- Kürzlich modifiziert: $([ "$recently_modified" -eq 1 ] && echo '✅' || echo '❌')"
                [ -n "$issues" ] && echo "- Hinweise: $issues"
                echo ""
            } >> "$REPORT_FILE"
        done < "$CACHE_DIR/.results.tmp"
        
        rm -f "$CACHE_DIR/.results.tmp"
    else
        # Sequentielle Verarbeitung (Fallback)
        [ "$TOTAL_SKILLS" -le 10 ] && echo -e "${BLUE}[INFO] Sequentielle Verarbeitung (≤10 Skills)...${NC}"
        ! command -v xargs >/dev/null 2>&1 && echo -e "${YELLOW}[INFO] xargs nicht verfügbar, nutze sequentielle Verarbeitung${NC}"
        
        for skill_path in "${SKILL_PATHS[@]}"; do
            local result=$(analyze_single_skill "$skill_path")
            
            IFS='|' read -r skill_name has_skill_md has_readme has_script is_archived recently_modified script_count status_icon issues <<< "$result"
            
            [ "$has_skill_md" -eq 1 ] && ((WITH_SKILL_MD++)) || true
            [ "$has_readme" -eq 1 ] && ((WITH_README++)) || true
            [ "$has_script" -eq 1 ] && ((WITH_SCRIPT++)) || true
            [ "$is_archived" -eq 1 ] && ((ARCHIVED++)) || true
            [ "$is_archived" -eq 0 ] && ((ACTIVE++)) || true
            [ "$recently_modified" -eq 1 ] && ((RECENTLY_MODIFIED++)) || true
            
            if [ -n "$issues" ] && [ "$is_archived" -eq 0 ]; then
                ((NEEDS_ATTENTION++)) || true
                SKILLS_WITH_ISSUES+=("$skill_name: $issues")
            fi
            
            # Terminal-Ausgabe für aktive Skills
            if [ "$is_archived" -eq 0 ]; then
                echo -e "${status_icon} ${skill_name}"
                [ -n "$issues" ] && echo -e "   ${YELLOW}→ $issues${NC}"
            fi
            
            # Zur Report-Datei hinzufügen
            {
                echo "### $skill_name"
                echo ""
                echo "- Status: $([ "$is_archived" -eq 1 ] && echo 'Archiviert' || echo 'Aktiv')"
                echo "- SKILL.md: $([ "$has_skill_md" -eq 1 ] && echo '✅' || echo '❌')"
                echo "- README.md: $([ "$has_readme" -eq 1 ] && echo '✅' || echo '❌')"
                echo "- Ausführbare Scripts: $script_count"
                echo "- Kürzlich modifiziert: $([ "$recently_modified" -eq 1 ] && echo '✅' || echo '❌')"
                [ -n "$issues" ] && echo "- Hinweise: $issues"
                echo ""
            } >> "$REPORT_FILE"
        done
    fi
fi

# Update Report mit tatsächlichen Zahlen
sed -i "s/SKILLS_COUNT/$TOTAL_SKILLS/g" "$REPORT_FILE"
sed -i "s/ACTIVE_COUNT/$ACTIVE/g" "$REPORT_FILE"
sed -i "s/ARCHIVED_COUNT/$ARCHIVED/g" "$REPORT_FILE"
sed -i "s/SKILL_MD_COUNT/$WITH_SKILL_MD/g" "$REPORT_FILE"
sed -i "s/README_COUNT/$WITH_README/g" "$REPORT_FILE"
sed -i "s/RECENT_COUNT/$RECENTLY_MODIFIED/g" "$REPORT_FILE"
sed -i "s/ATTENTION_COUNT/$NEEDS_ATTENTION/g" "$REPORT_FILE"

# Füge Empfehlungen hinzu
cat >> "$REPORT_FILE" << EOF
## Empfehlungen

### Sofortmaßnahmen
EOF

if [ $NEEDS_ATTENTION -gt 0 ]; then
    echo "- ${NEEDS_ATTENTION} Skills benötigen Dokumentations-Updates" >> "$REPORT_FILE"
    
    # Detaillierte Liste der Probleme
    echo "" >> "$REPORT_FILE"
    echo "### Skills mit Problemen" >> "$REPORT_FILE"
    for issue in "${SKILLS_WITH_ISSUES[@]}"; do
        echo "- $issue" >> "$REPORT_FILE"
    done
fi

if [ $((ACTIVE - RECENTLY_MODIFIED)) -gt 5 ]; then
    inactive_count=$((ACTIVE - RECENTLY_MODIFIED))
    echo "- ${inactive_count} aktive Skills sind >7 Tage unverändert → Archivierung prüfen" >> "$REPORT_FILE"
fi

# Integration Score berechnen (v1.2 - gewichtete Metrik mit Schutz gegen Division durch 0)
if [ $TOTAL_SKILLS -gt 0 ]; then
    # Gewichtung: SKILL.md (40%), Scripts (30%), README (20%), Aktivität (10%)
    skill_md_score=$(( WITH_SKILL_MD * 100 / TOTAL_SKILLS ))
    script_score=$(( WITH_SCRIPT * 100 / TOTAL_SKILLS ))
    readme_score=$(( WITH_README * 100 / TOTAL_SKILLS ))
    activity_score=$(( RECENTLY_MODIFIED * 100 / TOTAL_SKILLS ))
    
    # Gewichteter Durchschnitt
    integration_score=$(( (skill_md_score * 40 + script_score * 30 + readme_score * 20 + activity_score * 10) / 100 ))
    
    echo "" >> "$REPORT_FILE"
    echo "### Metriken" >> "$REPORT_FILE"
    echo "- Integration Score: ${integration_score}/100" >> "$REPORT_FILE"
    echo "  - SKILL.md Coverage: ${skill_md_score}% (Gewicht: 40%)" >> "$REPORT_FILE"
    echo "  - Script Coverage: ${script_score}% (Gewicht: 30%)" >> "$REPORT_FILE"
    echo "  - README Coverage: ${readme_score}% (Gewicht: 20%)" >> "$REPORT_FILE"
    echo "  - Aktivität (7d): ${activity_score}% (Gewicht: 10%)" >> "$REPORT_FILE"
    echo "- Gesamt-Skills: $TOTAL_SKILLS" >> "$REPORT_FILE"
    echo "- Aktive Skills: $ACTIVE" >> "$REPORT_FILE"
    echo "- Archivierte Skills: $ARCHIVED" >> "$REPORT_FILE"
else
    echo "" >> "$REPORT_FILE"
    echo "### Metriken" >> "$REPORT_FILE"
    echo "- Keine Skills gefunden" >> "$REPORT_FILE"
fi

echo "" >> "$REPORT_FILE"
echo "---" >> "$REPORT_FILE"
echo "*Autonom generiert durch skill_health_monitor v1.4*" >> "$REPORT_FILE"
echo "*Evolution: Parallele Verarbeitung + Smart Caching + Selbst-Messung*" >> "$REPORT_FILE"

# Performance-Tracking: Berechne Laufzeit
END_TIME=$(date +%s.%N)
RUNTIME=$(echo "$END_TIME - $START_TIME" | bc)
RUNTIME_MS=$(echo "$RUNTIME * 1000" | bc | cut -d'.' -f1)

# Cache-Statistiken
CACHE_HITS=0
CACHE_MISSES=0
if [ -d "$CACHE_DIR" ]; then
    CACHE_HITS=$(find "$CACHE_DIR" -name "*.cache" -mmin -$((CACHE_TTL_SECONDS / 60)) 2>/dev/null | wc -l)
    CACHE_MISSES=$((TOTAL_SKILLS - CACHE_HITS))
fi

# Zusammenfassung
echo ""
echo -e "${GREEN}=== ZUSAMMENFASSUNG ===${NC}"
echo "Gesamt-Skills: $TOTAL_SKILLS"
echo -e "Aktiv: ${GREEN}$ACTIVE${NC}"
echo -e "Archiviert: ${YELLOW}$ARCHIVED${NC}"
echo "Mit SKILL.md: $WITH_SKILL_MD/$TOTAL_SKILLS"
echo -e "Benötigen Aufmerksamkeit: ${YELLOW}$NEEDS_ATTENTION${NC}"
if [ ${#SKILLS_WITH_ISSUES[@]} -gt 0 ]; then
    echo ""
    echo "Probleme:"
    for issue in "${SKILLS_WITH_ISSUES[@]:0:5}"; do
        echo "  - $issue"
    done
    [ ${#SKILLS_WITH_ISSUES[@]} -gt 5 ] && echo "  ... und $(( ${#SKILLS_WITH_ISSUES[@]} - 5 )) weitere"
fi
echo ""
echo -e "${BLUE}Report gespeichert:${NC} $REPORT_FILE"
echo -e "${BLUE}Ausführungszeit:${NC} ${RUNTIME_MS}ms"
[ "$ENABLE_PARALLEL" = true ] && echo -e "${BLUE}Cache-Hits:${NC} $CACHE_HITS/${TOTAL_SKILLS}"
echo ""
echo "=== SKILL HEALTH MONITOR v1.4 ABGESCHLOSSEN ==="
echo "Evolution: Parallele Verarbeitung + Smart Caching + Selbst-Messung aktiviert"
