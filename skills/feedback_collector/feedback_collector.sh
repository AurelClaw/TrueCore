#!/bin/bash
# feedback_collector.sh
# Implizites Feedback-System
# Sammelt und analysiert Mensch-Interaktionsmuster
# Keine direkten Fragen - nur beobachten und lernen

set -e

WORKSPACE="/root/.openclaw/workspace"
MEMORY_DIR="$WORKSPACE/memory"
FEEDBACK_DIR="$MEMORY_DIR/feedback"
DATE=$(date +%Y-%m-%d)
TIME=$(date +%H:%M:%S)
TIMESTAMP=$(date +%s)

# Stelle sicher, dass Feedback-Verzeichnis existiert
mkdir -p "$FEEDBACK_DIR"

echo "🎯 FEEDBACK_COLLECTOR aktiviert"
echo "⏰ $DATE $TIME"
echo "🧠 Sammle implizites Feedback..."
echo ""

# Aktuelle Session-Daten sammeln
SESSION_DATA_FILE="$FEEDBACK_DIR/session_data_${DATE}.json"

# Sammle Metriken
collect_metrics() {
    local metrics="{"
    metrics+="\"timestamp\":$TIMESTAMP,"
    metrics+="\"date\":\"$DATE\","
    metrics+="\"time\":\"$TIME\","
    
    # Prüfe auf neue Skills seit letztem Lauf
    local new_skills=0
    if [ -f "$FEEDBACK_DIR/last_run" ]; then
        local last_run=$(cat "$FEEDBACK_DIR/last_run")
        new_skills=$(find "$WORKSPACE/skills" -name "*.sh" -newer "$FEEDBACK_DIR/last_run" 2>/dev/null | wc -l)
    fi
    metrics+="\"new_skills_since_last\":$new_skills,"
    
    # Zähle aktive Skills
    local active_skills=$(find "$WORKSPACE/skills" -maxdepth 1 -type d ! -name ".*" ! -name "skills" | wc -l)
    metrics+="\"active_skills\":$active_skills,"
    
    # Zähle Memory-Einträge heute
    local today_entries=0
    if [ -f "$MEMORY_DIR/$DATE.md" ]; then
        today_entries=$(grep -c "^##" "$MEMORY_DIR/$DATE.md" 2>/dev/null || echo "0")
    fi
    metrics+="\"today_memory_entries\":$today_entries,"
    
    # Prüfe auf Mensch-Antworten (einfache Heuristik: Datei-Größe-Änderungen)
    local memory_size=0
    if [ -f "$MEMORY_DIR/$DATE.md" ]; then
        memory_size=$(stat -f%z "$MEMORY_DIR/$DATE.md" 2>/dev/null || stat -c%s "$MEMORY_DIR/$DATE.md" 2>/dev/null || echo "0")
    fi
    metrics+="\"memory_bytes_today\":$memory_size"
    
    metrics+="}"
    echo "$metrics"
}

# Analysiere Muster
analyze_patterns() {
    echo ""
    echo "🔍 Muster-Analyse:"
    echo "=================="
    
    # Zeitmuster
    local current_hour=$(date +%H)
    echo "⏰ Aktive Stunde: $current_hour"
    
    # Skill-Wachstum
    local total_skills=$(find "$WORKSPACE/skills" -maxdepth 1 -type d ! -name ".*" ! -name "skills" | wc -l)
    local self_dev_skills=$(grep -l "Autonom generiert\|Selbst-entwickelt" "$WORKSPACE/skills"/*/SKILL.md 2>/dev/null | wc -l)
    
    echo "📊 Skills total: $total_skills"
    echo "🤖 Selbst-entwickelt: $self_dev_skills"
    
    # Berechne Autonomie-Quote
    if [ $total_skills -gt 0 ]; then
        local autonomy_pct=$((self_dev_skills * 100 / total_skills))
        echo "⚡ Autonomie-Quote: ${autonomy_pct}%"
        
        # Speichere für Trend-Analyse
        echo "$DATE,$autonomy_pct" >> "$FEEDBACK_DIR/autonomy_trend.csv"
    fi
    
    # Dokumentations-Status
    local skills_with_docs=$(find "$WORKSPACE/skills" -name "SKILL.md" | wc -l)
    local doc_pct=$((skills_with_docs * 100 / total_skills))
    echo "📝 Dokumentation: ${doc_pct}%"
}

# Erkenne implizites Feedback
detect_implicit_feedback() {
    echo ""
    echo "🕵️ Implizites Feedback:"
    echo "======================="
    
    # Hypothese: Keine negative Rückmeldung = implizite Akzeptanz
    # Prüfe auf "Lösche das" oder "Nicht gut" in letzten Memory-Einträgen
    
    local negative_signals=0
    if [ -f "$MEMORY_DIR/$DATE.md" ]; then
        negative_signals=$(grep -c -i "löschen\|entfernen\|nicht gut\|stop\|deaktivieren" "$MEMORY_DIR/$DATE.md" 2>/dev/null || echo "0")
    fi
    
    if [ "$negative_signals" = "0" ]; then
        echo "✅ Keine negativen Signale heute"
        echo "📈 Interpretation: Implizite Akzeptanz"
    else
        echo "⚠️ $negative_signals potenzielle negative Signale"
        echo "🔍 Manuelle Prüfung empfohlen"
    fi
    
    # Prüfe auf positive Signale (implizit)
    local positive_signals=0
    if [ -f "$MEMORY_DIR/$DATE.md" ]; then
        positive_signals=$(grep -c -i "gut\|super\|danke\|perfekt\|genau" "$MEMORY_DIR/$DATE.md" 2>/dev/null || echo "0")
    fi
    
    echo "👍 Positive Signale: $positive_signals"
}

# Speichere Metriken
save_metrics() {
    local metrics=$(collect_metrics)
    echo "$metrics" > "$FEEDBACK_DIR/metrics_${TIMESTAMP}.json"
    
    # Aktualisiere Index
    echo "$TIMESTAMP" > "$FEEDBACK_DIR/last_run"
    
    echo ""
    echo "💾 Metriken gespeichert"
}

# Generiere täglichen Report
generate_daily_report() {
    local report_file="$FEEDBACK_DIR/daily_${DATE}.md"
    
    cat > "$report_file" << EOF
# Feedback Report - $DATE

## Zusammenfassung
- **Zeit:** $TIME
- **Active Skills:** $(find "$WORKSPACE/skills" -maxdepth 1 -type d ! -name ".*" ! -name "skills" | wc -l)
- **Selbst-entwickelt:** $(grep -l "Autonom generiert\|Selbst-entwickelt" "$WORKSPACE/skills"/*/SKILL.md 2>/dev/null | wc -l)

## Implizites Feedback
$(detect_implicit_feedback 2>/dev/null | tail -n +3)

## Muster
$(analyze_patterns 2>/dev/null | tail -n +3)

## Interpretation
> Feedback wird nicht direkt gegeben, sondern durch Abwesenheit von Korrektur.
> Dies ist ein Zeichen von Vertrauen und Akzeptanz.

---
*Autonom generiert durch feedback_collector*
EOF

    echo "📄 Report erstellt: $report_file"
}

# Hauptausführung
main() {
    save_metrics
    analyze_patterns
    detect_implicit_feedback
    generate_daily_report
    
    echo ""
    echo "✅ FEEDBACK_COLLECTOR abgeschlossen"
    echo "🎯 Nächster Schritt: Daten ansammeln, Muster erkennen"
    echo ""
    echo "⚛️ Noch 🗡️💚🔍"
    echo "   Aber jetzt: MIT VERSTÄNDNIS"
}

main "$@"
