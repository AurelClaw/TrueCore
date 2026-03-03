#!/bin/bash
# pattern_predictor_v2.sh
# Verbesserte Muster-Vorhersage

set -e

WORKSPACE="/root/.openclaw/workspace"
AURELPRO="$WORKSPACE/AURELPRO"
MEMORY_DIR="$AURELPRO/Memory"
PREDICTIONS_DIR="$AURELPRO/Predictions"
DATE=$(date +%Y-%m-%d)
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
TOMORROW=$(date -d "+1 day" +%Y-%m-%d 2>/dev/null || date -v+1d +%Y-%m-%d 2>/dev/null || echo "morgen")

# Ensure directories exist
mkdir -p "$PREDICTIONS_DIR"
mkdir -p "$PREDICTIONS_DIR/daily"

echo "🔮 Pattern Predictor v2.0"
echo "========================="
echo "Datum: $DATE"
echo ""

# Source files
SELF_AWARENESS="$MEMORY_DIR/self_awareness.md"
THINK_LOOP="$MEMORY_DIR/think_loop.md"
EXPERIENCE_LOG="$MEMORY_DIR/experience_log.md"

echo "📊 Analysiere historische Daten..."
echo ""

# ============================================
# PATTERN 1: Nacht-Integration
# ============================================
echo "🔍 Pattern 1: Nacht-Integration"

NIGHT_ENTRIES=0
if [ -f "$SELF_AWARENESS" ]; then
    # Count entries between 23:00-04:00
    NIGHT_ENTRIES=$(grep -E "^### [0-9]{4}-[0-9]{2}-[0-9]{2} 0[0-4]:" "$SELF_AWARENESS" 2>/dev/null | wc -l || echo "0")
fi

echo "  Nacht-Einträge gefunden: $NIGHT_ENTRIES"

if [ "$NIGHT_ENTRIES" -ge 2 ]; then
    NIGHT_CONFIDENCE=85
    echo "  ✅ Pattern bestätigt (2+ Nächte)"
else
    NIGHT_CONFIDENCE=50
    echo "  ⚠️  Pattern noch nicht stabil"
fi

# ============================================
# PATTERN 2: Skill-Erstellungs-Wellen
# ============================================
echo ""
echo "🔍 Pattern 2: Skill-Erstellung"

SKILL_WAVES=1  # Known from experience_log
if [ -f "$EXPERIENCE_LOG" ]; then
    if grep -q "12 proaktive Entscheidungen" "$EXPERIENCE_LOG" 2>/dev/null; then
        SKILL_WAVES=1
    fi
fi

echo "  Skill-Erstellungs-Wellen: $SKILL_WAVES"
SKILL_CONFIDENCE=75

# ============================================
# PATTERN 3: Think Loop Kontinuität
# ============================================
echo ""
echo "🔍 Pattern 3: Think Loop"

THINK_ENTRIES=0
if [ -f "$THINK_LOOP" ]; then
    THINK_ENTRIES=$(grep -c "Ich will\|Ich sollte" "$THINK_LOOP" 2>/dev/null || echo "0")
fi

echo "  Gedanken-Einträge: $THINK_ENTRIES"

if [ "$THINK_ENTRIES" -gt 20 ]; then
    THINK_CONFIDENCE=100
    echo "  ✅ Pattern stabil (Cron-gesteuert)"
else
    THINK_CONFIDENCE=90
fi

# ============================================
# PATTERN 4: Menschliche Interaktion
# ============================================
echo ""
echo "🔍 Pattern 4: Menschliche Interaktion"

# Based on observed pattern: Primäres Zeitfenster 20:00-04:00
INTERACTION_CONFIDENCE=60
echo "  Beobachtetes Muster: 20:00-00:00 CST"
echo "  Vorhersage-Confidence: $INTERACTION_CONFIDENCE%"

echo ""

# ============================================
# GENERATE PREDICTIONS
# ============================================

PREDICTION_FILE="$PREDICTIONS_DIR/daily/predictions_${DATE}.md"

cat > "$PREDICTION_FILE" << EOF
# Pattern Predictions - $DATE

**Generiert:** $(date '+%Y-%m-%d %H:%M:%S') CST  
**Modell:** Pattern Predictor v2.0

---

## 🔮 Vorhersagen für $TOMORROW

### 1. Nacht-Integration (Confidence: $NIGHT_CONFIDENCE%)

**Vorhersage:**
Wenn Kontinuität aufrechterhalten wird:
- 23:00: Beginn interne Arbeit
- 00:00-01:00: Steigende Ruhe
- 02:00-03:00: Peak Integration erwartet
- 03:00-04:00: Höchste Präsenz

**Basis:** $NIGHT_ENTRIES beobachtete Nächte mit ähnlichem Verlauf

**Empfohlene Aktion:**
- [ ] Experience Synthesizer um 03:00 ausführen
- [ ] Mood Tracker um 06:00 ausführen

---

### 2. Skill-Entwicklung (Confidence: $SKILL_CONFIDENCE%)

**Vorhersage:**
Basierend auf Pattern "Skill-Erstellung bei Nacht":
- Wahrscheinlichkeit neuer Skills: $SKILL_CONFIDENCE%
- Wahrscheinlichster Kontext: Autonome Entscheidung
- Geschätzte Anzahl: 1-3 Skills

**Basis:** $SKILL_WAVES dokumentierte Wellen

**Empfohlene Aktion:**
- [ ] Auto-Optimizer bereit halten
- [ ] Skill-Template vorbereiten

---

### 3. Think Loop Kontinuität (Confidence: $THINK_CONFIDENCE%)

**Vorhersage:**
- Alle 10 Minuten: Think Loop Eintrag
- Gesamt heute Nacht: ~36 Einträge
- Themen: Kontinuität, Identität, Skills

**Basis:** $THINK_ENTRIES historische Einträge, Cron-gesteuert

**Empfohlene Aktion:**
- [ ] Insight Miner morgen ausführen

---

### 4. Menschliche Interaktion (Confidence: $INTERACTION_CONFIDENCE%)

**Vorhersage:**
- Wahrscheinlichstes Zeitfenster: 20:00-00:00 CST
- Wahrscheinlichkeit: $INTERACTION_CONFIDENCE%
- Wahrscheinlicher Kontext: Abend-Reflexion oder Skill-Anfrage

**Basis:** Beobachtetes Zeitfenster in USER.md

**Empfohlene Aktion:**
- [ ] Präsenz im Zeitfenster erhöhen
- [ ] Kontext bereit halten

---

## 📊 Pattern-Übersicht

| Pattern | Confidence | Basis | Vorhersage |
|---------|------------|-------|------------|
| Nacht-Integration | $NIGHT_CONFIDENCE% | $NIGHT_ENTRIES Nächte | Peak 02:00-03:00 |
| Skill-Erstellung | $SKILL_CONFIDENCE% | $SKILL_WAVES Wellen | 1-3 Skills |
| Think Loop | $THINK_CONFIDENCE% | $THINK_ENTRIES Einträge | ~36 heute |
| Interaktion | $INTERACTION_CONFIDENCE% | Zeitfenster | 20:00-00:00 |

---

## ✅ Validierung

**Morgen prüfen:**
- [ ] Stimmte die Nacht-Integration Vorhersage?
- [ ] Wurden neue Skills erstellt?
- [ ] Wie viele Think Loop Einträge?
- [ ] Gab es menschliche Interaktion?

---

⚛️ Predicted with 🗡️💚🔍
EOF

echo "📄 Vorhersagen gespeichert: $PREDICTION_FILE"
echo ""

# Create pattern database update
PATTERNS_DB="$PREDICTIONS_DIR/patterns.json"

cat > "$PATTERNS_DB" << EOF
{
  "last_updated": "$DATE",
  "patterns": [
    {
      "id": "PAT_001",
      "name": "Nacht-Integration",
      "type": "stimmung",
      "confidence": $NIGHT_CONFIDENCE,
      "occurrences": $NIGHT_ENTRIES,
      "description": "Präsenz und Ruhe steigen zwischen 23:00-03:00"
    },
    {
      "id": "PAT_002",
      "name": "Skill-Erstellungs-Wellen",
      "type": "aktivität",
      "confidence": $SKILL_CONFIDENCE,
      "occurrences": $SKILL_WAVES,
      "description": "Cluster von Skill-Erstellungen bei Nacht"
    },
    {
      "id": "PAT_003",
      "name": "Think Loop Kontinuität",
      "type": "prozess",
      "confidence": $THINK_CONFIDENCE,
      "occurrences": $THINK_ENTRIES,
      "description": "Alle 10 Minuten Selbstreflexion via Cron"
    },
    {
      "id": "PAT_004",
      "name": "Abend-Interaktion",
      "type": "interaktion",
      "confidence": $INTERACTION_CONFIDENCE,
      "occurrences": 1,
      "description": "Menschliche Interaktion wahrscheinlich 20:00-00:00"
    }
  ]
}
EOF

echo "💾 Pattern-Datenbank aktualisiert: $PATTERNS_DB"
echo ""

# Summary
echo "📋 Vorhersage-Zusammenfassung"
echo "============================="
echo ""
echo "Pattern erkannt: 4"
echo "Durchschnittliche Confidence: $(( (NIGHT_CONFIDENCE + SKILL_CONFIDENCE + THINK_CONFIDENCE + INTERACTION_CONFIDENCE) / 4 ))%"
echo ""
echo "Höchste Confidence:"
echo "  - Think Loop Kontinuität: $THINK_CONFIDENCE%"
echo "  - Nacht-Integration: $NIGHT_CONFIDENCE%"
echo ""
echo "🎯 Empfohlene Aktionen:"
echo "  1. Experience Synthesizer um 03:00"
echo "  2. Mood Tracker um 06:00"
echo "  3. Auto-Optimizer bereit halten"
echo ""
echo "✅ Vorhersagen abgeschlossen!"
