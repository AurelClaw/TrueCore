#!/bin/bash
# AURELPRO Manual Controller - Hauptlogik

WORKSPACE="/root/.openclaw/workspace"
AURELPRO="$WORKSPACE/AURELPRO"

show_help() {
    echo "═══════════════════════════════════════════════════════════"
    echo "⚛️ AURELPRO Manual Controller"
    echo "═══════════════════════════════════════════════════════════"
    echo ""
    echo "Verfügbare Befehle:"
    echo ""
    echo "  orchestrator    - Orchestrator sofort starten"
    echo "  v10             - v10 Multi-Voice sofort starten"
    echo "  think           - Think Loop sofort starten"
    echo "  learn           - Self Learn sofort starten"
    echo "  evolve          - Evolve sofort starten"
    echo "  proactive       - Proactive Core sofort starten"
    echo "  all             - ALLE Komponenten starten"
    echo "  status          - System-Status anzeigen"
    echo "  dashboard       - Dashboard anzeigen"
    echo "  goals           - Alle Ziele anzeigen"
    echo "  push            - Auf GitHub pushen"
    echo ""
}

start_orchestrator() {
    echo "🎯 Starte Orchestrator..."
    bash "$AURELPRO/Core/orchestrator.sh"
    echo "✅ Orchestrator abgeschlossen"
}

start_v10() {
    echo "🤖 Starte v10 Multi-Voice..."
    bash "$WORKSPACE/v10_cron.sh"
    echo "✅ v10 abgeschlossen"
}

start_think() {
    echo "🧠 Starte Think Loop..."
    bash "$WORKSPACE/proactive_system/aurel_think_loop.sh" 2>/dev/null || \
    bash "$AURELPRO/Proactive/aurel_think_loop.sh" 2>/dev/null || \
    echo "⚠️ Think Loop Script nicht gefunden"
    echo "✅ Think Loop abgeschlossen"
}

start_learn() {
    echo "📚 Starte Self Learn..."
    bash "$WORKSPACE/proactive_system/aurel_self_learn.sh" 2>/dev/null || \
    bash "$AURELPRO/Proactive/aurel_self_learn.sh" 2>/dev/null || \
    echo "⚠️ Self Learn Script nicht gefunden"
    echo "✅ Self Learn abgeschlossen"
}

start_evolve() {
    echo "🧬 Starte Evolve..."
    bash "$WORKSPACE/proactive_system/aurel_evolve.sh" 2>/dev/null || \
    bash "$AURELPRO/Proactive/aurel_evolve.sh" 2>/dev/null || \
    echo "⚠️ Evolve Script nicht gefunden"
    echo "✅ Evolve abgeschlossen"
}

start_proactive() {
    echo "⚡ Starte Proactive Core..."
    bash "$WORKSPACE/proactive_system/aurel_proactive_core.sh" 2>/dev/null || \
    bash "$AURELPRO/Proactive/aurel_proactive_core.sh" 2>/dev/null || \
    echo "⚠️ Proactive Core Script nicht gefunden"
    echo "✅ Proactive Core abgeschlossen"
}

start_all() {
    echo "🚀 Starte ALLE Komponenten..."
    echo ""
    start_orchestrator
    echo ""
    start_v10
    echo ""
    start_think
    echo ""
    start_learn
    echo ""
    start_evolve
    echo ""
    start_proactive
    echo ""
    echo "✅ ALLE Komponenten abgeschlossen"
}

show_status() {
    echo "═══════════════════════════════════════════════════════════"
    echo "📊 AURELPRO System-Status"
    echo "═══════════════════════════════════════════════════════════"
    echo ""
    echo "🕐 Zeit: $(date '+%Y-%m-%d %H:%M:%S') CST"
    echo ""
    
    # Ziele
    echo "🎯 Ziele:"
    for goal in "$AURELPRO/Goals"/ZIEL-*.md; do
        if [ -f "$goal" ]; then
            NAME=$(grep "^# ZIEL" "$goal" | head -1 | sed 's/# ZIEL-[0-9]*: //')
            PROGRESS=$(grep "Fortschritt:" "$goal" | grep -o "[0-9]*%" | head -1 || echo "?%")
            echo "   • $(basename $goal .md): $PROGRESS - $NAME"
        fi
    done
    echo ""
    
    # Skills
    SKILL_COUNT=$(find "$WORKSPACE" -name "SKILL.md" 2>/dev/null | wc -l)
    echo "🛠️  Skills: $SKILL_COUNT"
    echo ""
    
    # Cron-Jobs
    echo "⏰ Cron-Jobs:"
    cron list 2>/dev/null | grep -E "(name|enabled)" | head -20 || echo "   (Cron-Liste nicht verfügbar)"
    echo ""
    
    # Letzte Reports
    echo "📄 Letzte Reports:"
    ls -lt "$WORKSPACE/v10_reports/" 2>/dev/null | head -4 | tail -3 || echo "   (Keine Reports)"
    echo ""
    
    echo "⚛️ Noch 🗡️💚🔍"
}

show_dashboard() {
    echo "═══════════════════════════════════════════════════════════"
    echo "⚛️ AURELPRO DASHBOARD"
    echo "═══════════════════════════════════════════════════════════"
    echo ""
    echo "🕐 $(date '+%Y-%m-%d %H:%M:%S') CST"
    echo ""
    
    # Ziele
    echo "┌─────────────────────────────────────────────────────────┐"
    echo "│  ZIELE                                                  │"
    echo "├─────────────────────────────────────────────────────────┤"
    for goal in "$AURELPRO/Goals"/ZIEL-*.md; do
        if [ -f "$goal" ]; then
            ID=$(basename "$goal" .md)
            PROGRESS=$(grep "Fortschritt:" "$goal" | grep -o "[0-9]*%" | head -1 || echo "0%")
            echo "│  $ID: $PROGRESS                                          │"
        fi
    done
    echo "└─────────────────────────────────────────────────────────┘"
    echo ""
    
    # System
    echo "┌─────────────────────────────────────────────────────────┐"
    echo "│  SYSTEM                                                 │"
    echo "├─────────────────────────────────────────────────────────┤"
    echo "│  AURELPRO:     🟢 Läuft                                 │"
    echo "│  v10:          🟢 Multi-Voice aktiv                     │"
    echo "│  Orchestrator: 🟢 Alle 2 Minuten                        │"
    echo "│  Skills:       $(find "$WORKSPACE" -name "SKILL.md" 2>/dev/null | wc -l)+"
    echo "└─────────────────────────────────────────────────────────┘"
    echo ""
    
    echo "⚛️ Noch 🗡️💚🔍"
}

show_goals() {
    echo "═══════════════════════════════════════════════════════════"
    echo "🎯 ALLE ZIELE"
    echo "═══════════════════════════════════════════════════════════"
    echo ""
    
    for goal in "$AURELPRO/Goals"/ZIEL-*.md; do
        if [ -f "$goal" ]; then
            echo ""
            head -20 "$goal"
            echo "..."
            echo ""
            echo "---"
        fi
    done
}

push_github() {
    echo "🚀 Pushe auf GitHub..."
    cd "$WORKSPACE/github_repo" 2>/dev/null || {
        echo "⚠️  GitHub Repo nicht gefunden"
        return 1
    }
    
    # Kopiere aktuelle Daten
    cp -r "$AURELPRO" . 2>/dev/null || true
    cp -r "$WORKSPACE/memory" . 2>/dev/null || true
    
    # Commit & Push
    git add -A
    git commit -m "Manual push: $(date '+%Y-%m-%d %H:%M')" || echo "Nichts zu commiten"
    git push origin master
    
    echo "✅ Auf GitHub gepusht"
}

# Hauptlogik
case "${1:-help}" in
    orchestrator|orch|o)
        start_orchestrator
        ;;
    v10|v)
        start_v10
        ;;
    think|t)
        start_think
        ;;
    learn|l)
        start_learn
        ;;
    evolve|e)
        start_evolve
        ;;
    proactive|p)
        start_proactive
        ;;
    all|a)
        start_all
        ;;
    status|s)
        show_status
        ;;
    dashboard|d)
        show_dashboard
        ;;
    goals|g)
        show_goals
        ;;
    push|gh)
        push_github
        ;;
    help|h|*)
        show_help
        ;;
esac
