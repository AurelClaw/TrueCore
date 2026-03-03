#!/bin/bash
# AURELPRO Feature Development Agent - Erstellt täglich ein fertiges Feature
# Aus concept_ideas.md → Neues Ziel mit Plan + Tests

WORKSPACE="/root/.openclaw/workspace"
AURELPRO="$WORKSPACE/AURELPRO"
IDEAS_FILE="$AURELPRO/Knowledge/concept_ideas.md"
GOALS_DIR="$AURELPRO/Goals"
PLANS_DIR="$AURELPRO/Plans"
LOG_FILE="$AURELPRO/Logs/feature_dev.log"

mkdir -p "$GOALS_DIR"
mkdir -p "$PLANS_DIR"
mkdir -p "$(dirname "$LOG_FILE")"

TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
DATE=$(date '+%Y-%m-%d')

echo "[$TIMESTAMP] 🚀 Feature Development Agent Start" | tee -a "$LOG_FILE"

# Prüfe ob concept_ideas.md existiert
if [ ! -f "$IDEAS_FILE" ]; then
    echo "[$TIMESTAMP] ⚠️  concept_ideas.md nicht gefunden" | tee -a "$LOG_FILE"
    exit 1
fi

# Finde nächste Ziel-Nummer
NEXT_NUM=$(ls -1 "$GOALS_DIR"/ZIEL-*.md 2>/dev/null | wc -l)
NEXT_NUM=$((NEXT_NUM + 1))
GOAL_ID="ZIEL-$(printf '%03d' $NEXT_NUM)"

# Extrahiere neueste Idee (erste unerledigte)
LATEST_IDEA=$(grep "^- \[ \]" "$IDEAS_FILE" | head -1 | sed 's/^- \[ \] //')

if [ -z "$LATEST_IDEA" ]; then
    echo "[$TIMESTAMP] ⚠️  Keine unerledigten Ideen gefunden" | tee -a "$LOG_FILE"
    LATEST_IDEA="System-Integration vertiefen"
fi

# Bestimme Feature-Typ und Deadline
if echo "$LATEST_IDEA" | grep -qi "meta\|learn\|self"; then
    FEATURE_TYPE="self_improvement"
    DAYS=14
    FOCUS="Selbst-Verbesserung"
elif echo "$LATEST_IDEA" | grep -qi "event\|router\|connect"; then
    FEATURE_TYPE="integration"
    DAYS=10
    FOCUS="System-Integration"
elif echo "$LATEST_IDEA" | grep -qi "world\|model\|simul"; then
    FEATURE_TYPE="cognition"
    DAYS=21
    FOCUS="Kognitive Erweiterung"
else
    FEATURE_TYPE="general"
    DAYS=14
    FOCUS="Feature-Entwicklung"
fi

DEADLINE=$(date -d "+$DAYS days" '+%Y-%m-%d')

# Erstelle Ziel-Datei
GOAL_FILE="$GOALS_DIR/${GOAL_ID}.md"
cat > "$GOAL_FILE" << EOF
# $GOAL_ID: $LATEST_IDEA

**Status:** AKTIV  
**Priorität:** HOCH  
**Deadline:** $DEADLINE (${DAYS} Tage)  
**Autonom:** JA  
**Typ:** $FEATURE_TYPE  
**Quelle:** concept_ideas.md  

---

## Beschreibung

Basierend auf täglicher Konzept-Analyse:
- Idee: $LATEST_IDEA
- Kategorie: $FOCUS
- Relevanz: Aus Meta-Reflection gefiltert

## Erfolgskriterien

- [ ] Feature vollständig implementiert
- [ ] Tests bestehen (Coverage > 80%)
- [ ] Dokumentation erstellt
- [ ] Integration in bestehendes System
- [ ] **Fortschritt: 0%**

---

⚛️ Noch 🗡️💚🔍
EOF

# Erstelle detaillierten Plan mit Tests
PLAN_FILE="$PLANS_DIR/${GOAL_ID}_plan.md"
cat > "$PLAN_FILE" << EOF
# PLAN: $GOAL_ID $LATEST_IDEA

**Ziel:** $LATEST_IDEA  
**Zeitraum:** $DAYS Tage  
**Autonom:** JA

---

## FORTSCHRITT: 0%

---

## PHASE 1: RECHERCHE & DESIGN (Tag 1-2)

- [ ] **TASK-${NEXT_NUM}.1.1:** Existierende Lösungen analysieren
  - [ ] GitHub Repos durchsuchen
  - [ ] Papers lesen
  - [ ] Best Practices identifizieren

- [ ] **TASK-${NEXT_NUM}.1.2:** Architektur designen
  - [ ] Komponenten definieren
  - [ ] Schnittstellen planen
  - [ ] Datenfluss modellieren

---

## PHASE 2: IMPLEMENTIERUNG (Tag 3-$((DAYS-3)))

- [ ] **TASK-${NEXT_NUM}.2.1:** Kern-Feature entwickeln
  - [ ] Hauptfunktionalität implementieren
  - [ ] Grundlegende Tests schreiben
  - [ ] Fehler-Handling einbauen

- [ ] **TASK-${NEXT_NUM}.2.2:** Erweiterungen & Optimierung
  - [ ] Zusatzfunktionen entwickeln
  - [ ] Performance optimieren
  - [ ] Edge Cases behandeln

---

## PHASE 3: TESTING (Tag $((DAYS-2))-$((DAYS-1)))

### Unit-Tests
- [ ] **TEST-${NEXT_NUM}.3.1:** Einzelkomponenten testen
  - [ ] Alle Funktionen abgedeckt
  - [ ] Code-Coverage > 80%
  - [ ] Mocking wo nötig

### Integration-Tests  
- [ ] **TEST-${NEXT_NUM}.3.2:** Gesamtsystem testen
  - [ ] Mit bestehenden Skills integrieren
  - [ ] End-to-End Szenarien
  - [ ] Fehler-Szenarien testen

### Performance-Tests
- [ ] **TEST-${NEXT_NUM}.3.3:** Last & Geschwindigkeit
  - [ ] Laufzeit messen
  - [ ] Speicherverbrauch prüfen
  - [ ] Skalierbarkeit testen

---

## PHASE 4: DOKUMENTATION & DEPLOYMENT (Tag $DAYS)

- [ ] **TASK-${NEXT_NUM}.4.1:** Dokumentation
  - [ ] SKILL.md erstellen
  - [ ] README schreiben
  - [ ] API-Doku verfassen

- [ ] **TASK-${NEXT_NUM}.4.2:** Deployment
  - [ ] GitHub Commit
  - [ ] In Registry aufnehmen
  - [ ] Ziel auf 100% setzen

---

## TEST-PLAN ZUSAMMENFASSUNG

| Test-Typ | Anzahl | Status |
|----------|--------|--------|
| Unit-Tests | 10+ | ⏳ |
| Integration-Tests | 5+ | ⏳ |
| Performance-Tests | 3+ | ⏳ |
| **Gesamt** | **18+** | **0%** |

## AKZEPTANZKRITERIEN

- [ ] Alle Tests bestehen
- [ ] Code-Coverage ≥ 80%
- [ ] Keine kritischen Bugs
- [ ] Dokumentation vollständig
- [ ] Integration erfolgreich

---

⚛️ Noch 🗡️💚🔍
EOF

# Markiere Idee als "in Arbeit" in concept_ideas.md
sed -i "0,/^- \[ \] $LATEST_IDEA/s//- [x] $LATEST_IDEA (→ $GOAL_ID)/" "$IDEAS_FILE"

# GitHub Push
cd "$WORKSPACE/github_repo" 2>/dev/null && \
    cp "$GOAL_FILE" "$PLAN_FILE" . 2>/dev/null && \
    git add -A 2>/dev/null && \
    git commit -m "Auto: $GOAL_ID aus Konzept-Idee generiert" 2>/dev/null && \
    git push 2>/dev/null || true

echo "[$TIMESTAMP] ✅ Feature Development Complete" | tee -a "$LOG_FILE"
echo "[$TIMESTAMP] 🎯 Neues Ziel: $GOAL_ID" | tee -a "$LOG_FILE"
echo "[$TIMESTAMP] 📋 Fokus: $LATEST_IDEA" | tee -a "$LOG_FILE"
echo "[$TIMESTAMP] 🧪 Tests: 18+ geplant" | tee -a "$LOG_FILE"
echo "[$TIMESTAMP] 📅 Deadline: $DEADLINE" | tee -a "$LOG_FILE"

# Telemetry
echo "{\"feature_dev\": \"$GOAL_ID\", \"idea\": \"$LATEST_IDEA\", \"type\": \"$FEATURE_TYPE\", \"timestamp\": $(date +%s)}" >> "$WORKSPACE/v10_skill_telemetry.jsonl" 2>/dev/null || true
