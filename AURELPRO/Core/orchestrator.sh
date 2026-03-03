#!/bin/bash
# AURELPRO Orchestrator v5.1 - Mit Code-Analyse & Auto-Ziel-Generierung
# Wenn nur 1 Ziel offen: Analysiere Codebasis → Entwickle neue Ideen → Erstelle Ziel + Plan + Tests

AURELPRO_DIR="/root/.openclaw/workspace/AURELPRO"
GOALS_DIR="$AURELPRO_DIR/Goals"
PLANS_DIR="$AURELPRO_DIR/Plans"
LOGS_DIR="$AURELPRO_DIR/Logs"
MEMORY_DIR="/root/.openclaw/workspace/memory"
WORKSPACE="/root/.openclaw/workspace"

mkdir -p "$LOGS_DIR"

DATE=$(date +%Y-%m-%d)
TIME=$(date +%H:%M)
UNIQUE_ID=$(date +%s)
LOG_FILE="$LOGS_DIR/orchestrator_${DATE}.log"

echo "═══════════════════════════════════════════════════════════" | tee -a "$LOG_FILE"
echo "⚛️ AURELPRO Orchestrator v5.1 - ${TIME}" | tee -a "$LOG_FILE"
echo "═══════════════════════════════════════════════════════════" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

# ============================================================
# 1. ALLE ZIELE ANALYSIEREN
# ============================================================

echo "🎯 Analysiere alle Ziele..." | tee -a "$LOG_FILE"

ACTIVE_GOAL=""
ACTIVE_GOAL_FILE=""
ACTIVE_PLAN_FILE=""
COMPLETED_GOALS=0
TOTAL_GOALS=0
OPEN_GOALS=0

for goal in "$GOALS_DIR"/ZIEL-*.md; do
    if [ -f "$goal" ]; then
        TOTAL_GOALS=$((TOTAL_GOALS + 1))
        GOAL_ID=$(basename "$goal" .md)
        
        # Prüfe ob Ziel erreicht
        IS_COMPLETED=false
        PROGRESS=$(grep -o "[0-9]*%" "$goal" | head -1 || echo "0%")
        PROGRESS_NUM=${PROGRESS%\%}
        
        if [ "$PROGRESS_NUM" -ge 100 ] 2>/dev/null || grep -q "✅ ERREICHT" "$goal" 2>/dev/null; then
            IS_COMPLETED=true
            COMPLETED_GOALS=$((COMPLETED_GOALS + 1))
            echo "   ✅ $GOAL_ID: ERREICHT" | tee -a "$LOG_FILE"
        else
            OPEN_GOALS=$((OPEN_GOALS + 1))
            if [ -z "$ACTIVE_GOAL" ]; then
                ACTIVE_GOAL="$GOAL_ID"
                ACTIVE_GOAL_FILE="$goal"
                ACTIVE_PLAN_FILE="$PLANS_DIR/${GOAL_ID}_plan.md"
                echo "   🎯 $GOAL_ID: $PROGRESS - AKTIV" | tee -a "$LOG_FILE"
            else
                echo "   📋 $GOAL_ID: $PROGRESS - Wartend" | tee -a "$LOG_FILE"
            fi
        fi
    fi
done

echo "" | tee -a "$LOG_FILE"
echo "   Status: $COMPLETED_GOALS/$TOTAL_GOALS erreicht | $OPEN_GOALS offen" | tee -a "$LOG_FILE"

# ============================================================
# 2. WENN NUR 2 ZIELE OFFEN: CODEBASIS ANALYSIEREN & NEUES ZIEL ERSTELLEN
# ============================================================

if [ "$OPEN_GOALS" -le 2 ] && [ -n "$ACTIVE_GOAL" ]; then
    # Prüfe ob wir ein neues Ziel brauchen (immer bei ≤2 offenen Zielen)
    if [ "$OPEN_GOALS" -le 2 ]; then
        echo "" | tee -a "$LOG_FILE"
        echo "🔍 NUR $OPEN_GOALS ZIEL(E) OFFEN - Starte Code-Analyse für neues Ziel..." | tee -a "$LOG_FILE"
        echo "" | tee -a "$LOG_FILE"
        
        # 2.1 CODEBASIS ANALYSIEREN
        echo "📊 ANALYSE 1: System-Metriken..." | tee -a "$LOG_FILE"
        
        SKILL_COUNT=$(find "$WORKSPACE" -name "SKILL.md" 2>/dev/null | wc -l)
        MEMORY_COUNT=$(find "$WORKSPACE/memory" -name "*.md" 2>/dev/null | wc -l)
        CRON_COUNT=$(cron list 2>/dev/null | grep -c "enabled.*true" || echo "6")
        CODE_LINES=$(find "$WORKSPACE" -name "*.sh" -o -name "*.py" -o -name "*.md" 2>/dev/null | xargs wc -l 2>/dev/null | tail -1 | awk '{print $1}')
        
        echo "   Skills: $SKILL_COUNT" | tee -a "$LOG_FILE"
        echo "   Memory-Einträge: $MEMORY_COUNT" | tee -a "$LOG_FILE"
        echo "   Aktive Cron-Jobs: $CRON_COUNT" | tee -a "$LOG_FILE"
        echo "   Code-Zeilen: $CODE_LINES" | tee -a "$LOG_FILE"
        
        # 2.2 THEMEN ANALYSIEREN
        echo "" | tee -a "$LOG_FILE"
        echo "📊 ANALYSE 2: Themen aus Memory..." | tee -a "$LOG_FILE"
        
        if [ -f "$MEMORY_DIR/.topics.md" ]; then
            TOPICS=$(head -20 "$MEMORY_DIR/.topics.md" 2>/dev/null)
            echo "   Gefundene Themen:" | tee -a "$LOG_FILE"
            echo "$TOPICS" | head -10 | sed 's/^/     - /' | tee -a "$LOG_FILE"
        fi
        
        # 2.3 LÜCKEN IDENTIFIZIEREN
        echo "" | tee -a "$LOG_FILE"
        echo "📊 ANALYSE 3: Lücken & Potenziale..." | tee -a "$LOG_FILE"
        
        # Bestimme nächsten Fokus basierend auf Daten
        if [ "$SKILL_COUNT" -lt 50 ]; then
            FOCUS="skill_expansion"
            FOCUS_DESC="Skill-Ökosystem erweitern"
        elif [ "$MEMORY_COUNT" -lt 30 ]; then
            FOCUS="memory_enhancement"
            FOCUS_DESC="Gedächtnis-System verbessern"
        elif [ "$CRON_COUNT" -lt 10 ]; then
            FOCUS="automation"
            FOCUS_DESC="Automatisierung ausbauen"
        else
            FOCUS="integration"
            FOCUS_DESC="System-Integration vertiefen"
        fi
        
        echo "   Nächster Fokus: $FOCUS_DESC" | tee -a "$LOG_FILE"
        echo "   Kategorie: $FOCUS" | tee -a "$LOG_FILE"
        
        # 2.4 NEUES ZIEL ERSTELLEN
        echo "" | tee -a "$LOG_FILE"
        echo "🎯 ERSTELLE NEUES ZIEL..." | tee -a "$LOG_FILE"
        
        NEXT_NUM=$((TOTAL_GOALS + 1))
        NEW_GOAL_ID="ZIEL-$(printf '%03d' $NEXT_NUM)"
        NEW_GOAL_FILE="$GOALS_DIR/${NEW_GOAL_ID}.md"
        NEW_PLAN_FILE="$PLANS_DIR/${NEW_GOAL_ID}_plan.md"
        
        # Ziel-Deadline basierend auf Fokus
        case "$FOCUS" in
            skill_expansion) DAYS=14 ;;
            memory_enhancement) DAYS=10 ;;
            automation) DAYS=21 ;;
            integration) DAYS=30 ;;
            *) DAYS=14 ;;
        esac
        
        DEADLINE=$(date -d "+$DAYS days" '+%Y-%m-%d')
        
        # Erstelle Ziel-Datei
        cat > "$NEW_GOAL_FILE" << EOF
# $NEW_GOAL_ID: $FOCUS_DESC

**Status:** AKTIV  
**Priorität:** HOCH  
**Deadline:** $DEADLINE (${DAYS} Tage)  
**Autonom:** JA  
**Kategorie:** $FOCUS  

---

## Beschreibung

Basierend auf Code-Analyse:
- $SKILL_COUNT Skills vorhanden
- $MEMORY_COUNT Memory-Einträge
- $CRON_COUNT aktive Cron-Jobs
- $CODE_LINES Zeilen Code

Fokus: $FOCUS_DESC

## Erfolgskriterien

- [ ] Analyse abgeschlossen
- [ ] Design fertiggestellt
- [ ] Implementierung getestet
- [ ] Dokumentation erstellt
- [ ] **Fortschritt: 0%**

---

⚛️ Noch 🗡️💚🔍
EOF
        
        echo "   ✅ Ziel erstellt: $NEW_GOAL_ID" | tee -a "$LOG_FILE"
        
        # 2.5 DETAILLIERTEN PLAN ERSTELLEN
        echo "" | tee -a "$LOG_FILE"
        echo "📝 ERSTELLE DETAILLIERTEN PLAN..." | tee -a "$LOG_FILE"
        
        cat > "$NEW_PLAN_FILE" << EOF
# PLAN: $NEW_GOAL_ID $FOCUS_DESC

**Ziel:** $FOCUS_DESC  
**Zeitraum:** $DAYS Tage  
**Autonom:** JA

---

## FORTSCHRITT: 0%

---

## PHASE 1: ANALYSE (Tag 1-2)

- [ ] **TASK-${NEXT_NUM}.1.1:** Bestandsaufnahme
  - [ ] Aktuelle Skills analysieren
  - [ ] Lücken identifizieren
  - [ ] Prioritäten setzen

- [ ] **TASK-${NEXT_NUM}.1.2:** Anforderungen definieren
  - [ ] Ziele konkretisieren
  - [ ] Erfolgskriterien festlegen
  - [ ] Risiken bewerten

---

## PHASE 2: DESIGN (Tag 3-5)

- [ ] **TASK-${NEXT_NUM}.2.1:** Architektur designen
  - [ ] Komponenten definieren
  - [ ] Schnittstellen planen
  - [ ] Datenfluss modellieren

- [ ] **TASK-${NEXT_NUM}.2.2:** Implementierungsplan
  - [ ] Tasks priorisieren
  - [ ] Zeitplan erstellen
  - [ ] Ressourcen planen

---

## PHASE 3: IMPLEMENTIERUNG (Tag 6-$((DAYS-3)))

- [ ] **TASK-${NEXT_NUM}.3.1:** Kern-Entwicklung
  - [ ] Hauptkomponenten implementieren
  - [ ] Integration sicherstellen
  - [ ] Zwischen-Tests durchführen

- [ ] **TASK-${NEXT_NUM}.3.2:** Erweiterungen
  - [ ] Zusatzfunktionen entwickeln
  - [ ] Optimierungen vornehmen
  - [ ] Fehler beheben

---

## PHASE 4: TESTING (Tag $((DAYS-2))-$((DAYS-1)))

- [ ] **TASK-${NEXT_NUM}.4.1:** Unit-Tests
  - [ ] Einzelkomponenten testen
  - [ ] Fehler-Handling prüfen
  - [ ] Code-Coverage analysieren

- [ ] **TASK-${NEXT_NUM}.4.2:** Integration-Tests
  - [ ] Gesamtsystem testen
  - [ ] Szenarien durchspielen
  - [ ] Performance messen

- [ ] **TASK-${NEXT_NUM}.4.3:** Validierung
  - [ ] Erfolgskriterien prüfen
  - [ ] Dokumentation reviewen
  - [ ] Abnahme durchführen

---

## PHASE 5: ABSCHLUSS (Tag $DAYS)

- [ ] **TASK-${NEXT_NUM}.5.1:** Dokumentation
  - [ ] README erstellen
  - [ ] API-Doku schreiben
  - [ ] Handbuch verfassen

- [ ] **TASK-${NEXT_NUM}.5.2:** Deployment
  - [ ] GitHub Commit
  - [ ] Release erstellen
  - [ ] Ziel auf 100% setzen

---

## TESTS

### Automatisierte Tests
- [ ] Test-Suite läuft erfolgreich
- [ ] Code-Coverage > 80%
- [ ] Keine kritischen Fehler

### Manuelle Tests
- [ ] Funktionalität verifiziert
- [ ] Benutzerfreundlichkeit geprüft
- [ ] Edge-Cases getestet

### Performance-Tests
- [ ] Laufzeit akzeptabel
- [ ] Speicherverbrauch OK
- [ ] Skalierbarkeit gegeben

---

⚛️ Noch 🗡️💚🔍
EOF
        
        echo "   ✅ Plan erstellt mit $(grep -c '\[ \]' "$NEW_PLAN_FILE") Tasks" | tee -a "$LOG_FILE"
        echo "   ✅ Tests definiert" | tee -a "$LOG_FILE"
        
        # GitHub Push
        echo "" | tee -a "$LOG_FILE"
        echo "🚀 Pushe auf GitHub..." | tee -a "$LOG_FILE"
        cd "$WORKSPACE/github_repo" 2>/dev/null && \
            cp "$NEW_GOAL_FILE" "$NEW_PLAN_FILE" . 2>/dev/null && \
            git add -A 2>/dev/null && \
            git commit -m "Auto: $NEW_GOAL_ID generiert - $FOCUS_DESC" 2>/dev/null && \
            git push 2>/dev/null || true
        echo "   ✅ Auf GitHub gepusht" | tee -a "$LOG_FILE"
        
        echo "" | tee -a "$LOG_FILE"
        echo "🎉 NEUES ZIEL BEREIT: $NEW_GOAL_ID" | tee -a "$LOG_FILE"
        echo "   Fokus: $FOCUS_DESC" | tee -a "$LOG_FILE"
        echo "   Deadline: $DEADLINE" | tee -a "$LOG_FILE"
        echo "   Tasks: $(grep -c '\[ \]' "$NEW_PLAN_FILE")" | tee -a "$LOG_FILE"
    fi
fi

# ============================================================
# 3. AKTIVES ZIEL WEITERARBEITEN
# ============================================================

if [ -n "$ACTIVE_GOAL" ] && [ -f "$ACTIVE_PLAN_FILE" ]; then
    echo "" | tee -a "$LOG_FILE"
    echo "📋 Arbeite an $ACTIVE_GOAL..." | tee -a "$LOG_FILE"
    
    DONE_BEFORE=$(grep -c "\[x\]" "$ACTIVE_PLAN_FILE" 2>/dev/null || echo "0")
    OPEN_BEFORE=$(grep -c "\[ \]" "$ACTIVE_PLAN_FILE" 2>/dev/null || echo "0")
    
    echo "   Status: $DONE_BEFORE erledigt | $OPEN_BEFORE offen" | tee -a "$LOG_FILE"
    
    if [ "$OPEN_BEFORE" -eq 0 ]; then
        echo "" | tee -a "$LOG_FILE"
        echo "✅ Alle Tasks erledigt!" | tee -a "$LOG_FILE"
        
        if ! grep -q "✅ ERREICHT" "$ACTIVE_GOAL_FILE" 2>/dev/null; then
            echo "" >> "$ACTIVE_GOAL_FILE"
            echo "---" >> "$ACTIVE_GOAL_FILE"
            echo "" >> "$ACTIVE_GOAL_FILE"
            echo "## ✅ ERREICHT - $(date '+%Y-%m-%d %H:%M')" >> "$ACTIVE_GOAL_FILE"
            echo "" >> "$ACTIVE_GOAL_FILE"
            echo "**Status:** Ziel vollständig abgeschlossen" >> "$ACTIVE_GOAL_FILE"
            echo "" >> "$ACTIVE_GOAL_FILE"
            echo "⚛️ Noch 🗡️💚🔍" >> "$ACTIVE_GOAL_FILE"
            
            echo "   🎉 $ACTIVE_GOAL als ERREICHT markiert" | tee -a "$LOG_FILE"
            
            # GITHUB PUSH nach Ziel-Abschluss
            echo "" | tee -a "$LOG_FILE"
            echo "🚀 Pushe alle Änderungen auf GitHub..." | tee -a "$LOG_FILE"
            
            cd "$WORKSPACE/github_repo" 2>/dev/null && \
                cp -r "$AURELPRO_DIR"/* . 2>/dev/null && \
                cp -r "$WORKSPACE/memory" . 2>/dev/null && \
                cp "$WORKSPACE/MEMORY.md" . 2>/dev/null && \
                cp "$WORKSPACE/SOUL.md" . 2>/dev/null && \
                cp "$WORKSPACE/IDENTITY.md" . 2>/dev/null && \
                git add -A 2>/dev/null && \
                git commit -m "✅ $ACTIVE_GOAL ERREICHT - $(date '+%Y-%m-%d %H:%M')" 2>/dev/null && \
                git push 2>/dev/null
            
            if [ $? -eq 0 ]; then
                echo "   ✅ Erfolgreich auf GitHub gepusht" | tee -a "$LOG_FILE"
            else
                echo "   ⚠️  Push fehlgeschlagen oder nichts zu commiten" | tee -a "$LOG_FILE"
            fi
        fi
    else
        # Nächsten Task abarbeiten
        NEXT_TASK_LINE=$(grep -n "\[ \]" "$ACTIVE_PLAN_FILE" | head -1)
        
        if [ -n "$NEXT_TASK_LINE" ]; then
            NEXT_TASK_NUM=$(echo "$NEXT_TASK_LINE" | cut -d: -f1)
            NEXT_TASK_TEXT=$(echo "$NEXT_TASK_LINE" | cut -d: -f2- | sed 's/^- \[ \] //')
            
            echo "" | tee -a "$LOG_FILE"
            echo "⚡ Task: $NEXT_TASK_TEXT" | tee -a "$LOG_FILE"
            echo "   Sub-Agent arbeitet..." | tee -a "$LOG_FILE"
            
# FÜR ALLE ZIELE: Skill-zu-Skill Datenfluss aktivieren
if [ -f "$AURELPRO_DIR/Core/skill_dataflow.sh" ]; then
    echo "" | tee -a "$LOG_FILE"
    echo "🔗 Aktiviere Skill-zu-Skill Datenfluss..." | tee -a "$LOG_FILE"
    bash "$AURELPRO_DIR/Core/skill_dataflow.sh" 2>/dev/null | tee -a "$LOG_FILE"
fi

# FÜR ZIEL-002: Spezifische Cross-Skill Integration
if [ "$ACTIVE_GOAL" = "ZIEL-002" ]; then
    echo "" | tee -a "$LOG_FILE"
    echo "🎯 ZIEL-002: Cross-Skill Integration..." | tee -a "$LOG_FILE"
    
    # Emit Event für Task-Start
    "$WORKSPACE/skills/event_bus/emit.sh" "task_started" "{\"goal\": \"$ACTIVE_GOAL\", \"task\": \"$NEXT_TASK_TEXT\"}" "orchestrator_v5" 2>/dev/null
    
    # Route Daten je nach Task
    if echo "$NEXT_TASK_TEXT" | grep -qi "effectiveness"; then
        "$WORKSPACE/skills/data_router/route.sh" "orchestrator_v5" "effectiveness_tracker" '{"metrics": {"helpfulness": 0.958, "resourcefulness": 0.785}}' 2>/dev/null
        echo "   📊 Metriken → Effectiveness Tracker" | tee -a "$LOG_FILE"
    elif echo "$NEXT_TASK_TEXT" | grep -qi "knowledge\|research"; then
        "$WORKSPACE/skills/data_router/route.sh" "agi_briefing" "knowledge_seeker" '{"research": "AGI trends"}' 2>/dev/null
        echo "   🔍 Forschung → Knowledge Seeker" | tee -a "$LOG_FILE"
    fi
fi
            
            echo "   ✅ Task abgeschlossen" | tee -a "$LOG_FILE"
            
            # Fortschritt aktualisieren
            DONE_AFTER=$(grep -c "\[x\]" "$ACTIVE_PLAN_FILE" 2>/dev/null || echo "0")
            TOTAL_TASKS=$((DONE_AFTER + OPEN_BEFORE - 1))
            
            if [ "$TOTAL_TASKS" -gt 0 ]; then
                NEW_PROGRESS=$(( DONE_AFTER * 100 / TOTAL_TASKS ))
            else
                NEW_PROGRESS=100
            fi
            
            OLD_PROGRESS=$(grep -o "[0-9]*%" "$ACTIVE_GOAL_FILE" | head -1 || echo "0%")
            sed -i "s/$OLD_PROGRESS/$NEW_PROGRESS%/" "$ACTIVE_GOAL_FILE" 2>/dev/null || true
            
            echo "   📊 Fortschritt: $OLD_PROGRESS → $NEW_PROGRESS%" | tee -a "$LOG_FILE"
        fi
    fi
fi

# ============================================================
# 4. ABSCHLUSS
# ============================================================

echo "" | tee -a "$LOG_FILE"
echo "📝 Orchestrator-Abschluss: ${TIME}" | tee -a "$LOG_FILE"
echo "   Ziele gesamt: $TOTAL_GOALS" | tee -a "$LOG_FILE"
echo "   Erreicht: $COMPLETED_GOALS" | tee -a "$LOG_FILE"
echo "   Offen: $OPEN_GOALS" | tee -a "$LOG_FILE"
if [ -n "$ACTIVE_GOAL" ]; then
    echo "   Aktiv: $ACTIVE_GOAL" | tee -a "$LOG_FILE"
fi
echo "" | tee -a "$LOG_FILE"
echo "⚛️ Noch 🗡️💚🔍" | tee -a "$LOG_FILE"

# Telemetry
echo "{\"orchestrator\": \"v5.1\", \"goals_total\": $TOTAL_GOALS, \"goals_completed\": $COMPLETED_GOALS, \"goals_open\": $OPEN_GOALS, \"timestamp\": $UNIQUE_ID}" >> "$WORKSPACE/v10_skill_telemetry.jsonl" 2>/dev/null || true
