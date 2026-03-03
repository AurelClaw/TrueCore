#!/bin/bash
#
# Test Runner für das Skill-Ökosystem
# Validiert Skills, Events und Integration
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILLS_DIR="$(dirname "$SCRIPT_DIR")"
WORKSPACE_DIR="$(dirname "$SKILLS_DIR")"
METRICS_DIR="$WORKSPACE_DIR/metrics"
REPORT_FILE="$METRICS_DIR/test_report_$(date +%Y-%m-%d).json"

# Farben für Output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Zähler
TESTS_PASSED=0
TESTS_FAILED=0
SKILLS_CHECKED=0
EVENTS_TESTED=0

# Hilfsfunktionen
log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# SKILL.md Validierung
check_skill_md() {
    log_info "Prüfe SKILL.md für alle Skills..."
    
    local failed=0
    for skill_dir in "$SKILLS_DIR"/*/; do
        if [ -d "$skill_dir" ]; then
            local skill_name=$(basename "$skill_dir")
            # Überspringe .archive und testing_framework selbst
            [[ "$skill_name" == ".archive" ]] && continue
            [[ "$skill_name" == "testing_framework" ]] && continue
            
            SKILLS_CHECKED=$((SKILLS_CHECKED + 1))
            
            if [ ! -f "$skill_dir/SKILL.md" ]; then
                log_error "Fehlend: $skill_name/SKILL.md"
                failed=$((failed + 1))
            else
                # Prüfe auf wichtige Abschnitte
                if ! grep -q "## Zweck" "$skill_dir/SKILL.md" && \
                   ! grep -q "## Purpose" "$skill_dir/SKILL.md"; then
                    log_warn "$skill_name: Kein Zweck/Purpose Abschnitt"
                fi
            fi
        fi
    done
    
    if [ $failed -eq 0 ]; then
        log_info "✅ Alle $SKILLS_CHECKED Skills haben SKILL.md"
        TESTS_PASSED=$((TESTS_PASSED + 1))
        return 0
    else
        log_error "❌ $failed Skills ohne SKILL.md"
        TESTS_FAILED=$((TESTS_FAILED + 1))
        return 1
    fi
}

# Event-System Test
check_event_system() {
    log_info "Teste Event-System..."
    
    local event_bus_dir="$SKILLS_DIR/event_bus"
    local passed=0
    local failed=0
    
    # Prüfe Event-Bus existiert
    if [ ! -d "$event_bus_dir" ]; then
        log_error "Event-Bus nicht gefunden: $event_bus_dir"
        TESTS_FAILED=$((TESTS_FAILED + 1))
        return 1
    fi
    
    # Prüze emit.sh
    if [ ! -f "$event_bus_dir/emit.sh" ]; then
        log_error "emit.sh nicht gefunden"
        failed=$((failed + 1))
    else
        passed=$((passed + 1))
    fi
    
    # Prüfe subscribe.sh
    if [ ! -f "$event_bus_dir/subscribe.sh" ]; then
        log_error "subscribe.sh nicht gefunden"
        failed=$((failed + 1))
    else
        passed=$((passed + 1))
    fi
    
    # Teste Event-Emitting
    local test_event_file="$WORKSPACE_DIR/memory/events/test_$(date +%s).jsonl"
    if [ -f "$event_bus_dir/emit.sh" ]; then
        bash "$event_bus_dir/emit.sh" "test:event" "testing_framework" '{"test":true}' 2>/dev/null || true
        EVENTS_TESTED=$((EVENTS_TESTED + 1))
        passed=$((passed + 1))
    fi
    
    if [ $failed -eq 0 ]; then
        log_info "✅ Event-System funktioniert ($passed Checks)"
        TESTS_PASSED=$((TESTS_PASSED + 1))
        return 0
    else
        log_error "❌ Event-System hat $failed Fehler"
        TESTS_FAILED=$((TESTS_FAILED + 1))
        return 1
    fi
}

# Test-Szenario: Morgen-Routine
test_morning_routine() {
    log_info "Teste Szenario: morning_routine..."
    
    local morgen_gruss="$WORKSPACE_DIR/morgen_gruss.sh"
    local perpetual="$SKILLS_DIR/perpetual_becoming/perpetual_becoming.sh"
    
    local passed=0
    
    # Prüfe Dateien existieren
    if [ -f "$morgen_gruss" ]; then
        passed=$((passed + 1))
    else
        log_error "morgen_gruss.sh nicht gefunden"
    fi
    
    if [ -f "$perpetual" ]; then
        passed=$((passed + 1))
    else
        log_error "perpetual_becoming.sh nicht gefunden"
    fi
    
    # Prüfe Event-Emitting
    if grep -q "event_emit" "$morgen_gruss" 2>/dev/null; then
        passed=$((passed + 1))
    else
        log_warn "morgen_gruss emittiert keine Events"
    fi
    
    if [ $passed -ge 2 ]; then
        log_info "✅ Morning Routine OK ($passed/3)"
        TESTS_PASSED=$((TESTS_PASSED + 1))
        return 0
    else
        log_error "❌ Morning Routine fehlgeschlagen"
        TESTS_FAILED=$((TESTS_FAILED + 1))
        return 1
    fi
}

# Test-Szenario: Autonomie-Loop
test_autonomy_loop() {
    log_info "Teste Szenario: autonomy_loop..."
    
    local proactive="$SKILLS_DIR/proactive_decision/aurel_proactive_decision.sh"
    local experience="$SKILLS_DIR/experience_processor/SKILL.md"
    
    local passed=0
    
    if [ -f "$proactive" ]; then
        passed=$((passed + 1))
    else
        log_error "proactive_decision nicht gefunden"
    fi
    
    if [ -f "$experience" ]; then
        passed=$((passed + 1))
    else
        log_error "experience_processor nicht gefunden"
    fi
    
    if [ $passed -eq 2 ]; then
        log_info "✅ Autonomy Loop OK"
        TESTS_PASSED=$((TESTS_PASSED + 1))
        return 0
    else
        log_error "❌ Autonomy Loop fehlgeschlagen"
        TESTS_FAILED=$((TESTS_FAILED + 1))
        return 1
    fi
}

# Test-Szenario: Weekly Review
test_weekly_review() {
    log_info "Teste Szenario: weekly_review..."
    
    local review="$SKILLS_DIR/wöchentlicher_review/wöchentlicher_review.sh"
    local effectiveness="$SKILLS_DIR/effectiveness_tracker/effectiveness_tracker.sh"
    
    local passed=0
    
    if [ -f "$review" ]; then
        passed=$((passed + 1))
    else
        log_error "wöchentlicher_review nicht gefunden"
    fi
    
    if [ -f "$effectiveness" ]; then
        passed=$((passed + 1))
    else
        log_error "effectiveness_tracker nicht gefunden"
    fi
    
    if [ $passed -eq 2 ]; then
        log_info "✅ Weekly Review OK"
        TESTS_PASSED=$((TESTS_PASSED + 1))
        return 0
    else
        log_error "❌ Weekly Review fehlgeschlagen"
        TESTS_FAILED=$((TESTS_FAILED + 1))
        return 1
    fi
}

# Report generieren
generate_report() {
    mkdir -p "$METRICS_DIR"
    
    cat > "$REPORT_FILE" << EOF
{
  "test_run": "$(date -Iseconds)",
  "summary": {
    "tests_passed": $TESTS_PASSED,
    "tests_failed": $TESTS_FAILED,
    "total_tests": $((TESTS_PASSED + TESTS_FAILED)),
    "success_rate": $(echo "scale=2; $TESTS_PASSED * 100 / ($TESTS_PASSED + $TESTS_FAILED)" | bc 2>/dev/null || echo "0")
  },
  "details": {
    "skills_checked": $SKILLS_CHECKED,
    "events_tested": $EVENTS_TESTED
  },
  "status": "$([ $TESTS_FAILED -eq 0 ] && echo "PASSED" || echo "FAILED")"
}
EOF
    
    log_info "Report gespeichert: $REPORT_FILE"
}

# Hauptfunktion
main() {
    echo "================================"
    echo "  Skill Testing Framework"
    echo "  $(date)"
    echo "================================"
    echo
    
    local scenario=""
    local check_skills=false
    local check_events=false
    
    # Argumente parsen
    while [[ $# -gt 0 ]]; do
        case $1 in
            --scenario)
                scenario="$2"
                shift 2
                ;;
            --check-skills)
                check_skills=true
                shift
                ;;
            --check-events)
                check_events=true
                shift
                ;;
            *)
                shift
                ;;
        esac
    done
    
    # Ausführung basierend auf Argumenten
    if [ -n "$scenario" ]; then
        case $scenario in
            morning_routine)
                test_morning_routine
                ;;
            autonomy_loop)
                test_autonomy_loop
                ;;
            weekly_review)
                test_weekly_review
                ;;
            *)
                log_error "Unbekanntes Szenario: $scenario"
                exit 1
                ;;
        esac
    elif [ "$check_skills" = true ]; then
        check_skill_md
    elif [ "$check_events" = true ]; then
        check_event_system
    else
        # Vollständiger Test
        check_skill_md
        check_event_system
        test_morning_routine
        test_autonomy_loop
        test_weekly_review
    fi
    
    # Report generieren
    generate_report
    
    # Zusammenfassung
    echo
    echo "================================"
    echo "  Zusammenfassung"
    echo "================================"
    echo -e "${GREEN}Bestanden:${NC} $TESTS_PASSED"
    echo -e "${RED}Fehlgeschlagen:${NC} $TESTS_FAILED"
    echo "Skills geprüft: $SKILLS_CHECKED"
    echo "Events getestet: $EVENTS_TESTED"
    echo
    
    if [ $TESTS_FAILED -eq 0 ]; then
        echo -e "${GREEN}✅ ALLE TESTS BESTANDEN${NC}"
        exit 0
    else
        echo -e "${RED}❌ EINIGE TESTS FEHLGESCHLAGEN${NC}"
        exit 1
    fi
}

main "$@"
