#!/bin/bash
# verify_state.sh - Verify State S = ⟨G, B, H, A, V, C, M, E, T⟩ is complete

echo "═══════════════════════════════════════════════════════════"
echo "🔍 STATE S VERIFICATION"
echo "═══════════════════════════════════════════════════════════"
echo ""

BASE="/root/.openclaw/workspace/AUREL_OPUS_MYCO"
ERRORS=0

check_file() {
    local file=$1
    local component=$2
    if [[ -f "$file" ]]; then
        echo "✅ $component: $file"
        return 0
    else
        echo "❌ $component: $file MISSING"
        ((ERRORS++))
        return 1
    fi
}

check_dir() {
    local dir=$1
    local component=$2
    if [[ -d "$dir" ]]; then
        echo "✅ $component: $dir"
        return 0
    else
        echo "❌ $component: $dir MISSING"
        ((ERRORS++))
        return 1
    fi
}

echo "Checking State Components..."
echo ""

check_file "$BASE/SUBSTRATE/graph.json" "G: Knowledge Hypergraph"
check_file "$BASE/CORE/beliefs.json" "B: Belief Set"
check_file "$BASE/COGNITION/hypotheses.json" "H: Hypotheses"
check_file "$BASE/AGENCY/goals.json" "A: Active Goals"
check_file "$BASE/ALIGNMENT/values.json" "V: Value Weights"
check_file "$BASE/METRICS/coherence_energy.json" "C: Coherence Tensor"
check_file "$BASE/STATE/meta.json" "M: Meta-State"
check_file "$BASE/METRICS/coherence_energy.json" "E: Energy Metrics"
check_dir "$BASE/CHECKPOINTS/trace" "T: Complete Trace (dir)"

echo ""
echo "═══════════════════════════════════════════════════════════"

if [[ $ERRORS -eq 0 ]]; then
    echo "✅ STATE S COMPLETE"
    echo "S = ⟨G, B, H, A, V, C, M, E, T⟩"
    echo ""
    echo "Status: Ready for Phase 2 (Myco Core)"
    exit 0
else
    echo "❌ STATE S INCOMPLETE ($ERRORS missing)"
    echo ""
    echo "Status: Fix before Phase 2"
    exit 1
fi
