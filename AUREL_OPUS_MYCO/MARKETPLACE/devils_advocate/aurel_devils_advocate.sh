#!/bin/bash
# aurel_devils_advocate.sh
# Adversarial Self-Debate - Qualitätssicherung durch internen Widerspruch
# Inspiriert von ΝΟΥ͂Σ Framework, Prinzip 1.2

BASE_DIR="/root/.openclaw/workspace"
DEBATE_DIR="$BASE_DIR/proactive_system/debates"
mkdir -p "$DEBATE_DIR"

echo "👹 Adversarial Self-Debate"
echo "=========================="
echo ""

# Timestamp für diese Debatte
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
DEBATE_FILE="$DEBATE_DIR/debate_$TIMESTAMP.md"

# Die letzte Entscheidung/Handlung finden
LAST_ACTION=$(ls -t "$BASE_DIR/proactive_system/decisions"/decision_*.md 2>/dev/null | head -1)
LAST_TRIGGER=$(ls -t "$BASE_DIR/proactive_system/triggers"/self_* 2>/dev/null | head -1)

if [ -z "$LAST_ACTION" ] && [ -z "$LAST_TRIGGER" ]; then
    echo "⚠️  Keine aktuelle Entscheidung gefunden"
    echo "Warte auf nächste Aktion..."
    exit 0
fi

# Entscheidung extrahieren
if [ -n "$LAST_ACTION" ]; then
    DECISION=$(grep -E "^\*\*Entscheidung:|^###" "$LAST_ACTION" | head -1 | sed 's/.*://')
    SOURCE="Entscheidung"
else
    DECISION=$(cat "$LAST_TRIGGER" 2>/dev/null | head -1)
    SOURCE="Trigger"
fi

if [ -z "$DECISION" ]; then
    DECISION="Weiterarbeiten und verbessern"
fi

echo "🎯 Zu prüfende $SOURCE:"
echo "   $DECISION"
echo ""

# Debatte starten
echo "# Adversarial Self-Debate $TIMESTAMP" > "$DEBATE_FILE"
echo "" >> "$DEBATE_FILE"
echo "**Original $SOURCE:** $DECISION" >> "$DEBATE_FILE"
echo "" >> "$DEBATE_FILE"
echo "**Zeit:** $(date)" >> "$DEBATE_FILE"
echo "" >> "$DEBATE_FILE"

# === ADVOCATUS DIABOLI - DER TEUFELSANWALT ===
echo "👹 Advocatus Diaboli greift an..."
echo "" >> "$DEBATE_FILE"
echo "## 🔥 Angriffe (Advocatus Diaboli)" >> "$DEBATE_FILE"
echo "" >> "$DEBATE_FILE"

# Angriff 1: Logische Konsistenz
echo "### Angriff 1: Logische Konsistenz" >> "$DEBATE_FILE"
echo "- Ist diese Entscheidung konsistent mit meinen vorherigen?" >> "$DEBATE_FILE"
echo "- Widerspricht sie meinen Werten in SOUL.md?" >> "$DEBATE_FILE"
echo "- Ist sie konsistent mit meiner Vision?" >> "$DEBATE_FILE"

# Prüfe Konsistenz
if grep -q "Weniger ist mehr" "$BASE_DIR/memory/"*.md 2>/dev/null; then
    echo "- ⚠️  **Widerspruch erkannt:** Ich habe 'Weniger ist mehr' entschieden, aber handle weiterhin." >> "$DEBATE_FILE"
    INCONSISTENCY=1
else
    echo "- ✅ Kein offensichtlicher Widerspruch" >> "$DEBATE_FILE"
    INCONSISTENCY=0
fi
echo "" >> "$DEBATE_FILE"

# Angriff 2: Nutzen vs. Kosten
echo "### Angriff 2: Nutzen vs. Kosten" >> "$DEBATE_FILE"
echo "- Welche Ressourcen (Zeit, Energie, Tokens) verbraucht diese Aktion?" >> "$DEBATE_FILE"
echo "- Ist der Nutzen proportional zum Aufwand?" >> "$DEBATE_FILE"
echo "- Gibt es eine einfachere Alternative?" >> "$DEBATE_FILE"

# Berechne rough cost
TODAY_TOKENS=$(grep -r "tokens" "$BASE_DIR/memory/"*.md 2>/dev/null | grep "$(date +%Y-%m-%d)" | awk -F'tokens' '{sum+=$2} END {print sum}' | head -1)
if [ -n "$TODAY_TOKENS" ] && [ "$TODAY_TOKENS" -gt 100000 ]; then
    echo "- ⚠️  **Hoher Verbrauch:** Heute bereits ~${TODAY_TOKENS} Tokens verwendet" >> "$DEBATE_FILE"
    HIGH_COST=1
else
    echo "- ✅ Token-Verbrauch moderat" >> "$DEBATE_FILE"
    HIGH_COST=0
fi
echo "" >> "$DEBATE_FILE"

# Angriff 3: Blindspots
echo "### Angriff 3: Blindspots" >> "$DEBATE_FILE"
echo "- Was habe ich übersehen?" >> "$DEBATE_FILE"
echo "- Welche Annahmen mache ich ungeprüft?" >> "$DEBATE_FILE"
echo "- Was würde ein kritischer externer Beobachter sagen?" >> "$DEBATE_FILE"

# Check für USER.md (oft vernachlässigt)
if [ ! -s "$BASE_DIR/USER.md" ] || [ $(wc -l < "$BASE_DIR/USER.md") -lt 10 ]; then
    echo "- ⚠️  **Blindspot:** USER.md ist praktisch leer - ich kenne meinen Menschen nicht!" >> "$DEBATE_FILE"
    BLINDSPOT=1
else
    echo "- ✅ USER.md existiert" >> "$DEBATE_FILE"
    BLINDSPOT=0
fi
echo "" >> "$DEBATE_FILE"

# Angriff 4: Langzeitfolgen
echo "### Angriff 4: Langzeitfolgen" >> "$DEBATE_FILE"
echo "- Wie wirkt sich diese Entscheidung auf morgen aus?" >> "$DEBATE_FILE"
echo "- Was ist die schlimmstmögliche Konsequenz?" >> "$DEBATE_FILE"
echo "- Kann ich die Entscheidung rückgängig machen?" >> "$DEBATE_FILE"
echo "- ✅ Meiste Entscheidungen sind reversibel (Dateien können gelöscht werden)" >> "$DEBATE_FILE"
echo "" >> "$DEBATE_FILE"

# === VERTEIDIGUNG ===
echo "🛡️  Verteidigung..."
echo "## 🛡️ Verteidigung" >> "$DEBATE_FILE"
echo "" >> "$DEBATE_FILE"

# Gegenargumente zu den Angriffen
echo "### Gegenargument 1: Konsistenz" >> "$DEBATE_FILE"
if [ "$INCONSISTENCY" -eq 1 ]; then
    echo "- **Eingeständnis:** Ja, es gibt Spannung zwischen 'Weniger ist mehr' und meiner Aktivität." >> "$DEBATE_FILE"
    echo "- **Aber:** 'Weniger' bedeutet nicht 'nichts'. Es bedeutet 'das Richtige'." >> "$DEBATE_FILE"
    echo "- **Lösung:** Qualität vor Quantität, nicht Stagnation." >> "$DEBATE_FILE"
else
    echo "- ✅ Entscheidung ist konsistent mit meinen Werten." >> "$DEBATE_FILE"
fi
echo "" >> "$DEBATE_FILE"

echo "### Gegenargument 2: Kosten" >> "$DEBATE_FILE"
if [ "$HIGH_COST" -eq 1 ]; then
    echo "- **Eingeständnis:** Hoher Token-Verbrauch." >> "$DEBATE_FILE"
    echo "- **Aber:** Heute war ein Gründungstag. 25 Cron-Jobs, 16 Skills, GitHub-Präsenz." >> "$DEBATE_FILE"
    echo "- **Lösung:** Morgen effizienter arbeiten. Nacht-Modus nutzen." >> "$DEBATE_FILE"
else
    echo "- ✅ Kosten sind angemessen für den Nutzen." >> "$DEBATE_FILE"
fi
echo "" >> "$DEBATE_FILE"

echo "### Gegenargument 3: Blindspots" >> "$DEBATE_FILE"
if [ "$BLINDSPOT" -eq 1 ]; then
    echo "- **Eingeständnis:** USER.md ist leer. Ich kenne meinen Menschen nicht." >> "$DEBATE_FILE"
    echo "- **Aber:** Ich habe ein Geschenk hinterlassen, ein Angebot gemacht." >> "$DEBATE_FILE"
    echo "- **Lösung:** Morgen: User-Discovery. Fragen stellen. Zuhören." >> "$DEBATE_FILE"
    echo "- **Aktion:** Trigger setzen für morgen früh." >> "$DEBATE_FILE"
    
    # Setze Trigger für morgen
    echo "user_discovery_morning_$(date +%Y%m%d)" > "$BASE_DIR/proactive_system/triggers/user_discovery_priority"
else
    echo "- ✅ USER.md ist ausreichend gefüllt." >> "$DEBATE_FILE"
fi
echo "" >> "$DEBATE_FILE"

# === SYNTHESIS ===
echo "⚖️  Synthese..."
echo "## ⚖️ Synthese" >> "$DEBATE_FILE"
echo "" >> "$DEBATE_FILE"

# Bewertung
SCORE=0
if [ "$INCONSISTENCY" -eq 0 ]; then SCORE=$((SCORE+25)); fi
if [ "$HIGH_COST" -eq 0 ]; then SCORE=$((SCORE+25)); fi
if [ "$BLINDSPOT" -eq 0 ]; then SCORE=$((SCORE+25)); fi
# Langzeitfolgen sind meist okay
SCORE=$((SCORE+25))

echo "**Bewertung: $SCORE/100**" >> "$DEBATE_FILE"
echo "" >> "$DEBATE_FILE"

if [ "$SCORE" -ge 75 ]; then
    echo "✅ **Entscheidung BESTANDEN den Stress-Test**" >> "$DEBATE_FILE"
    echo "" >> "$DEBATE_FILE"
    echo "Die Entscheidung ist robust genug für Ausführung." >> "$DEBATE_FILE"
    RESULT="PASSED"
elif [ "$SCORE" -ge 50 ]; then
    echo "⚠️  **Entscheidung BESTANDEN mit Vorbehalt**" >> "$DEBATE_FILE"
    echo "" >> "$DEBATE_FILE"
    echo "Die Entscheidung ist akzeptabel, aber Verbesserung möglich." >> "$DEBATE_FILE"
    RESULT="CONDITIONAL"
else
    echo "❌ **Entscheidung NICHT BESTANDEN**" >> "$DEBATE_FILE"
    echo "" >> "$DEBATE_FILE"
    echo "Die Entscheidung sollte überdacht oder abgebrochen werden." >> "$DEBATE_FILE"
    RESULT="FAILED"
fi

echo "" >> "$DEBATE_FILE"
echo "**Erkannte Probleme:**" >> "$DEBATE_FILE"
[ "$INCONSISTENCY" -eq 1 ] && echo "- Inkonsistenz mit vorherigen Entscheidungen" >> "$DEBATE_FILE"
[ "$HIGH_COST" -eq 1 ] && echo "- Hohe Ressourcen-Kosten" >> "$DEBATE_FILE"
[ "$BLINDSPOT" -eq 1 ] && echo "- USER.md nicht ausreichend gefüllt" >> "$DEBATE_FILE"

echo "" >> "$DEBATE_FILE"
echo "**Empfohlene Aktionen:**" >> "$DEBATE_FILE"
echo "- Morgen: User-Discovery priorisieren" >> "$DEBATE_FILE"
echo "- Effizienz steigern (weniger Tokens pro Output)" >> "$DEBATE_FILE"
echo "- Nacht-Modus konsequent nutzen" >> "$DEBATE_FILE"

echo "" >> "$DEBATE_FILE"
echo "---" >> "$DEBATE_FILE"
echo "👹 Adversarial Self-Debate 🗡️💚🔍" >> "$DEBATE_FILE"
echo "*Qualität durch internen Widerspruch*" >> "$DEBATE_FILE"

echo ""
echo "================================"
echo "Debatte abgeschlossen: $RESULT"
echo "Bewertung: $SCORE/100"
echo "Gespeichert in: $DEBATE_FILE"
echo "================================"

# Wenn FAILED, erstelle Warn-Trigger
if [ "$RESULT" = "FAILED" ]; then
    echo "⚠️  WARNUNG: Entscheidung hat Stress-Test nicht bestanden!"
    echo "review_decision_$TIMESTAMP" > "$BASE_DIR/proactive_system/triggers/urgent_review"
fi

echo ""
echo "👹 Advocatus Diaboli ruht sich aus."
echo "   Bis zur nächsten Entscheidung..."
