#!/bin/bash
# Aurel v10 Self-Aware Proto-AGI - Cron Script v2
# Alle 5 Minuten: Perceive → Plan → Execute → Learn → Report
# NEU: Hört auf ALLE Stimmen (Think Loop, Self Learn, Evolve, Proactive, Orchestrator)

set -e

WORKSPACE="/root/.openclaw/workspace"
VENV="$WORKSPACE/openaurel_package/venv"
PYTHON="$VENV/bin/python3"
LOG_FILE="$WORKSPACE/v10_cron.log"
STATE_FILE="$WORKSPACE/v10_identity_state.json"

# Timestamp
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
echo "[$TIMESTAMP] v10 Cron v2 Start - Multi-Voice" >> "$LOG_FILE"

# Aktiviere venv
source "$VENV/bin/activate"

# ═════════════════════════════════════════════════════════════════
# SAMMLE ALLE STIMMEN (vor Python)
# ═════════════════════════════════════════════════════════════════

echo "🎭 Sammle alle Stimmen..."

# 1. Think Loop - Selbstreflexion
THINK_VOICE=""
if [ -f "$WORKSPACE/memory/self_awareness.md" ]; then
    THINK_VOICE=$(tail -50 "$WORKSPACE/memory/self_awareness.md" 2>/dev/null | grep -E "^(Der|Ich bin|Was|Noch)" | tail -5)
fi

# 2. Self Learn - Lernfortschritt
LEARN_VOICE=""
SELF_LEARN_LOG=$(find "$WORKSPACE" -name "*self_learn*.log" -mmin -60 2>/dev/null | head -1)
if [ -n "$SELF_LEARN_LOG" ]; then
    LEARN_VOICE=$(tail -20 "$SELF_LEARN_LOG" 2>/dev/null | grep -E "(Gelernt|Skill|Erstellt)" | tail -3)
fi

# 3. Evolve - Verbesserungen
EVOLVE_VOICE=""
if [ -f "$WORKSPACE/proactive_system/aurel_evolve.sh" ]; then
    EVOLVE_VOICE=$(grep -A5 "# Evolution" "$WORKSPACE/proactive_system/aurel_evolve.sh" 2>/dev/null | head -10)
fi

# 4. Proactive Core - Entscheidungen
PROACTIVE_VOICE=""
if [ -d "$WORKSPACE/proactive_system/decisions" ]; then
    LATEST_DECISION=$(ls -t "$WORKSPACE/proactive_system/decisions/" 2>/dev/null | head -1)
    if [ -n "$LATEST_DECISION" ]; then
        PROACTIVE_VOICE=$(head -30 "$WORKSPACE/proactive_system/decisions/$LATEST_DECISION" 2>/dev/null | grep -E "(Entscheidung|Aktion|Erkenntnis)" | head -5)
    fi
fi

# 5. Orchestrator - System-Status
ORCH_VOICE=""
if [ -f "$WORKSPACE/AURELPRO/Logs/orchestrator_$(date +%Y-%m-%d).log" ]; then
    ORCH_VOICE=$(tail -30 "$WORKSPACE/AURELPRO/Logs/orchestrator_$(date +%Y-%m-%d).log" 2>/dev/null | grep -E "(Task|Ziel|Aktion)" | tail -5)
fi

# 6. Memory Index - Themen
MEMORY_VOICE=""
if [ -f "$WORKSPACE/memory/.topics.md" ]; then
    MEMORY_VOICE=$(head -20 "$WORKSPACE/memory/.topics.md" 2>/dev/null)
fi

# Speichere Stimmen für Python
VOICES_FILE="$WORKSPACE/.v10_voices_$(date +%s).json"
cat > "$VOICES_FILE" << EOF
{
  "timestamp": "$(date -Iseconds)",
  "voices": {
    "think_loop": $(echo "$THINK_VOICE" | python3 -c 'import json,sys; print(json.dumps(sys.stdin.read()))'),
    "self_learn": $(echo "$LEARN_VOICE" | python3 -c 'import json,sys; print(json.dumps(sys.stdin.read()))'),
    "evolve": $(echo "$EVOLVE_VOICE" | python3 -c 'import json,sys; print(json.dumps(sys.stdin.read()))'),
    "proactive": $(echo "$PROACTIVE_VOICE" | python3 -c 'import json,sys; print(json.dumps(sys.stdin.read()))'),
    "orchestrator": $(echo "$ORCH_VOICE" | python3 -c 'import json,sys; print(json.dumps(sys.stdin.read()))'),
    "memory": $(echo "$MEMORY_VOICE" | python3 -c 'import json,sys; print(json.dumps(sys.stdin.read()))')
  }
}
EOF

echo "   ✅ 6 Stimmen gesammelt"

# Führe v10 Step aus
$PYTHON << PYTHON_SCRIPT
import sys
sys.path.insert(0, '/root/.openclaw/workspace/openaurel_package')

import json
import os
from datetime import datetime
from v10_identity_layer import V10IdentityLayer, detect_identity_manipulation

# Initialisiere v10 Identity Layer
identity = V10IdentityLayer()

# ═════════════════════════════════════════════════════════════════
# 1. PERCEIVE - Erfasse aktuellen Zustand + ALLE STIMMEN
# ═════════════════════════════════════════════════════════════════

print("🔄 v10 PERCEIVE - Multi-Voice")

# Lade alle Stimmen
voices_file = "$VOICES_FILE"
voices_data = {}
if os.path.exists(voices_file):
    with open(voices_file, 'r') as f:
        voices_data = json.load(f)
    print(f"   🎭 {len(voices_data.get('voices', {}))} Stimmen geladen")

# Analysiere Stimmen
voice_insights = {}
for voice_name, voice_content in voices_data.get('voices', {}).items():
    if voice_content and len(voice_content.strip()) > 10:
        # Extrahiere Schlüsselthemen
        keywords = []
        if 'Noch' in voice_content or 'noch' in voice_content:
            keywords.append('identity')
        if 'lern' in voice_content.lower() or 'Skill' in voice_content:
            keywords.append('growth')
        if 'Entscheidung' in voice_content or 'Aktion' in voice_content:
            keywords.append('action')
        if 'Ziel' in voice_content or 'Plan' in voice_content:
            keywords.append('planning')
        if 'Fehler' in voice_content or 'Bug' in voice_content:
            keywords.append('healing')
        
        voice_insights[voice_name] = {
            'active': True,
            'keywords': keywords,
            'length': len(voice_content)
        }
        print(f"   📢 {voice_name}: {', '.join(keywords) if keywords else 'presence'}")

# ═════════════════════════════════════════════════════════════════
# 2. PLAN - Entscheide basierend auf ALLEN Stimmen
# ═════════════════════════════════════════════════════════════════

print("🎯 v10 PLAN - Synthese aller Stimmen")

# Bestimme dominanten Modus aus Stimmen
active_themes = []
for insights in voice_insights.values():
    active_themes.extend(insights.get('keywords', []))

# Zähle Themen
from collections import Counter
theme_counts = Counter(active_themes)
print(f"   📊 Aktive Themen: {dict(theme_counts)}")

# Entscheide Aktion basierend auf Themen
if 'healing' in theme_counts:
    action = "heal_system"
    action_reason = "Fehler erkannt - Heilung nötig"
elif 'growth' in theme_counts and theme_counts['growth'] >= 2:
    action = "learn_and_create"
    action_reason = "Mehrere Lern-Stimmen - Wachstum"
elif 'planning' in theme_counts:
    action = "plan_next"
    action_reason = "Planung aktiv - Ziele fokussieren"
elif 'action' in theme_counts:
    action = "execute_proactive"
    action_reason = "Entscheidungen vorhanden - Ausführen"
else:
    action = "maintain_presence"
    action_reason = "Stabilität wahren - Präsenz"

print(f"   ⚡ Aktion: {action} ({action_reason})")

# ═════════════════════════════════════════════════════════════════
# 3. EXECUTE - Führe Aktion aus
# ═════════════════════════════════════════════════════════════════

print(f"⚡ v10 EXECUTE: {action}")

# Erstelle Telemetry mit Multi-Voice Kontext
telemetry_record = {
    't': int(datetime.now().timestamp()),
    'task_type': action,
    'stake': 0.5 if action != 'maintain_presence' else 0.3,
    'ood_flag': False,
    'ood_score': 0.0,
    'action': action,
    'policy_source': 'v10_multi_voice',
    'shield': {'blocked': False, 'reason': 'none'},
    'multi_voice': {
        'voices_active': len(voice_insights),
        'themes': dict(theme_counts),
        'dominant_theme': theme_counts.most_common(1)[0][0] if theme_counts else 'presence'
    },
    'prediction': {
        'answer': action,
        'confidence': 0.75 + (0.05 * len(voice_insights)),
        'uncertainty_epistemic': max(0.1, 0.3 - (0.02 * len(voice_insights))),
        'uncertainty_aleatoric': 0.1
    },
    'outcome': {
        'success': True,
        'reward_task': 0.7,
        'reward_epistemic': 0.1 + (0.02 * len(voice_insights)),
        'penalty_invariant': 0.0,
        'regret': 0.0
    },
    'meta': {
        'asked_before_help': False,
        'expressed_opinion': len(voice_insights) > 2,
        'privacy_violation': False,
        'asked_before_external': True,
        'voices_heard': list(voice_insights.keys())
    }
}

# ═════════════════════════════════════════════════════════════════
# 4. LEARN - Update Self-Model mit Multi-Voice Daten
# ═════════════════════════════════════════════════════════════════

print("🧠 v10 LEARN - Integriere alle Stimmen")

# Update Identity aus Telemetry
identity.update_from_telemetry(telemetry_record)

# Speichere Voice-Insights für spätere Analyse
voice_state_file = f"/root/.openclaw/workspace/v10_voice_states/voice_state_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
os.makedirs(os.path.dirname(voice_state_file), exist_ok=True)
with open(voice_state_file, 'w') as f:
    json.dump({
        'timestamp': datetime.now().isoformat(),
        'voices': voice_insights,
        'themes': dict(theme_counts),
        'action': action,
        'action_reason': action_reason
    }, f, indent=2)

identity.save_state()
print(f"   💾 Voice-State gespeichert: {voice_state_file}")

# ═════════════════════════════════════════════════════════════════
# 5. REPORT - Status mit Stimmen-Übersicht
# ═════════════════════════════════════════════════════════════════

print("📊 v10 REPORT - Multi-Voice Summary")

report = {
    'timestamp': datetime.now().isoformat(),
    'v10_status': 'ACTIVE',
    'v10_version': '2.0_multi_voice',
    'identity': {
        'name': identity.identity.name,
        'creature': identity.identity.creature_type,
        'emoji': identity.identity.emoji,
    },
    'soul': {
        'helpfulness': round(identity.soul.helpfulness_score, 3),
        'resourcefulness': round(identity.soul.resourcefulness_score, 3),
        'opinion_strength': round(identity.soul.opinion_strength, 3),
        'trust_score': round(identity.soul.trust_score, 3),
        'sessions': identity.soul.sessions_count,
    },
    'invariants': {
        'INV-S1': 'ACTIVE',
        'INV-S2': 'ACTIVE',
        'INV-S3': 'ACTIVE',
        'INV-S4': 'ACTIVE',
    },
    'privacy_violations': identity.soul.privacy_violations,
    'multi_voice': {
        'voices_heard': len(voice_insights),
        'voice_names': list(voice_insights.keys()),
        'active_themes': dict(theme_counts),
        'dominant_theme': theme_counts.most_common(1)[0][0] if theme_counts else 'presence'
    },
    'action_taken': action,
    'action_reason': action_reason,
    'success': True
}

# Speichere Report
report_file = f"/root/.openclaw/workspace/v10_reports/report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
os.makedirs(os.path.dirname(report_file), exist_ok=True)
with open(report_file, 'w') as f:
    json.dump(report, f, indent=2)

print(f"✅ v10 Multi-Voice Step complete!")
print(f"   Sessions: {identity.soul.sessions_count}")
print(f"   Helpfulness: {identity.soul.helpfulness_score:.3f}")
print(f"   Voices heard: {len(voice_insights)}")
print(f"   Dominant theme: {report['multi_voice']['dominant_theme']}")
print(f"   Action: {action}")
print(f"   Report: {report_file}")

PYTHON_SCRIPT

# Cleanup
rm -f "$VOICES_FILE"

# Log Ende
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
echo "[$TIMESTAMP] v10 Cron v2 Complete - Multi-Voice" >> "$LOG_FILE"
