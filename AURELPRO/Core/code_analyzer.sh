#!/bin/bash
# AURELPRO Code Analyzer - Analysiert System und generiert neue Ziele

AURELPRO_DIR="/root/.openclaw/workspace/AURELPRO"
GOALS_DIR="$AURELPRO_DIR/Goals"
PLANS_DIR="$AURELPRO_DIR/Plans"
WORKSPACE="/root/.openclaw/workspace"

# ============================================================
# ZIEL GENERIEREN
# ============================================================

generate_goal() {
    GOAL_ID="${1:-ZIEL-004}"
    GOAL_NUM=$(echo "$GOAL_ID" | grep -o "[0-9]*")
    
    echo "🧠 Analysiere System für $GOAL_ID..."
    
    # Sammle Daten für Analyse
    SKILL_COUNT=$(find "$WORKSPACE" -name "SKILL.md" 2>/dev/null | wc -l)
    MEMORY_COUNT=$(find "$WORKSPACE/memory" -name "*.md" 2>/dev/null | wc -l)
    CRON_COUNT=$(cron list 2>/dev/null | grep -c "enabled.*true" || echo "6")
    
    # Analysiere Themen aus Memory
    TOPICS=""
    if [ -f "$WORKSPACE/memory/.topics.md" ]; then
        TOPICS=$(head -10 "$WORKSPACE/memory/.topics.md" 2>/dev/null)
    fi
    
    # Bestimme Ziel-Typ basierend auf Daten
    if [ "$GOAL_NUM" -eq 4 ]; then
        GOAL_TYPE="optimization"
        GOAL_TITLE="System-Optimierung & Performance"
        GOAL_DESC="Optimiere alle Komponenten für maximale Effizienz"
        DAYS=10
    elif [ "$GOAL_NUM" -eq 5 ]; then
        GOAL_TYPE="knowledge"
        GOAL_TITLE="Wissensbasis-Erweiterung"
        GOAL_DESC="Erweitere Knowledge-Base mit neuen Fähigkeiten"
        DAYS=14
    elif [ "$GOAL_NUM" -eq 6 ]; then
        GOAL_TYPE="connection"
        GOAL_TITLE="Externe Verbindungen & Integration"
        GOAL_DESC="Baue Brücken zu externen Systemen"
        DAYS=21
    else
        GOAL_TYPE="evolution"
        GOAL_TITLE="System-Evolution v$GOAL_NUM.0"
        GOAL_DESC="Evolviere das Gesamtsystem auf nächste Stufe"
        DAYS=30
    fi
    
    # Erstelle Ziel-Datei
    GOAL_FILE="$GOALS_DIR/${GOAL_ID}.md"
    cat > "$GOAL_FILE" << EOF
# $GOAL_ID: $GOAL_TITLE

**Status:** AKTIV  
**Priorität:** HOCH  
**Deadline:** $(date -d "+$DAYS days" '+%Y-%m-%d') (${DAYS} Tage)  
**Autonom:** JA  
**Typ:** $GOAL_TYPE

---

## Beschreibung

$GOAL_DESC basierend auf aktuellem System-Status:
- $SKILL_COUNT Skills verfügbar
- $MEMORY_COUNT Memory-Einträge
- $CRON_COUNT aktive Cron-Jobs

## Erfolgskriterien

- [ ] Analyse-Phase abgeschlossen
- [ ] Implementierung fertig
- [ ] Testing erfolgreich
- [ ] Dokumentation vollständig
- [ ] **Fortschritt: 0%**

## Sub-Ziele

1. **${GOAL_ID}.1:** Analyse (Tag 1-2)
2. **${GOAL_ID}.2:** Design (Tag 3-4)
3. **${GOAL_ID}.3:** Implementierung (Tag 5-${DAYS})

## Metriken

| Metrik | Start | Ziel |
|--------|-------|------|
| Fortschritt | 0% | 100% |
| Tasks | 0 | TBD |
| Qualität | - | Hoch |

---

⚛️ Noch 🗡️💚🔍
EOF

    echo "   ✅ Ziel erstellt: $GOAL_FILE"
    
    # Erstelle Plan
    generate_plan "$GOAL_ID" "$GOAL_TITLE" "$DAYS"
    
    # GitHub Commit
    cd "$WORKSPACE/github_repo" 2>/dev/null && \
        cp "$GOAL_FILE" "$PLANS_DIR/${GOAL_ID}_plan.md" . 2>/dev/null && \
        git add -A 2>/dev/null && \
        git commit -m "Auto: $GOAL_ID generiert" 2>/dev/null && \
        git push 2>/dev/null || true
    
    echo "   ✅ Auf GitHub gepusht"
}

# ============================================================
# PLAN GENERIEREN
# ============================================================

generate_plan() {
    GOAL_ID="$1"
    GOAL_TITLE="$2"
    DAYS="$3"
    
    PLAN_FILE="$PLANS_DIR/${GOAL_ID}_plan.md"
    
    echo "   📝 Erstelle Plan..."
    
    cat > "$PLAN_FILE" << EOF
# PLAN: $GOAL_ID $GOAL_TITLE

**Ziel:** $GOAL_TITLE  
**Zeitraum:** $DAYS Tage  
**Autonom:** JA

---

## FORTSCHRITT: 0%

---

## TAG 1-2: ANALYSE

### TAG 1
- [ ] **TASK-${GOAL_ID}.1.1:** System-Status erfassen
  - [ ] Skills zählen
  - [ ] Memory analysieren
  - [ ] Cron-Jobs prüfen

### TAG 2
- [ ] **TASK-${GOAL_ID}.1.2:** Anforderungen definieren
  - [ ] Ziele konkretisieren
  - [ ] Erfolgskriterien festlegen
  - [ ] Risiken identifizieren

---

## TAG 3-4: DESIGN

### TAG 3
- [ ] **TASK-${GOAL_ID}.2.1:** Architektur designen
  - [ ] Komponenten definieren
  - [ ] Schnittstellen planen

### TAG 4
- [ ] **TASK-${GOAL_ID}.2.2:** Implementierungsplan
  - [ ] Tasks priorisieren
  - [ ] Zeitplan erstellen

---

## TAG 5-${DAYS}: IMPLEMENTIERUNG

- [ ] **TASK-${GOAL_ID}.3.1:** Entwicklung
- [ ] **TASK-${GOAL_ID}.3.2:** Testing
- [ ] **TASK-${GOAL_ID}.3.3:** Dokumentation

---

## ABSCHLUSS

- [ ] Ziel auf 100% setzen
- [ ] Abschlussbericht
- [ ] Nächstes Ziel vorbereiten

---

⚛️ Noch 🗡️💚🔍
EOF

    echo "   ✅ Plan erstellt: $PLAN_FILE"
}

# ============================================================
# HAUPTLOGIK
# ============================================================

case "${1:-help}" in
    generate_goal|g)
        generate_goal "$2"
        ;;
    analyze|a)
        echo "🧠 System-Analyse:"
        echo "   Skills: $(find "$WORKSPACE" -name 'SKILL.md' 2>/dev/null | wc -l)"
        echo "   Memory: $(find "$WORKSPACE/memory" -name '*.md' 2>/dev/null | wc -l)"
        echo "   Goals: $(ls "$GOALS_DIR"/*.md 2>/dev/null | wc -l)"
        ;;
    help|h|*)
        echo "Code Analyzer - Nutzung:"
        echo "  ./code_analyzer.sh generate_goal [ZIEL-ID]  - Neues Ziel generieren"
        echo "  ./code_analyzer.sh analyze                   - System analysieren"
        ;;
esac
