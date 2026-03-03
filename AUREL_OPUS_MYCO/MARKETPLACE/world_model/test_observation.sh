#!/bin/bash
#
# test_observation.sh - Unit Tests für Observation Encoder und State Manager
# ZIEL-009 Phase 3: Observation Model Implementation
#

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WM_DIR="$SCRIPT_DIR"
TEST_DATA_DIR="$WM_DIR/data/test"

TESTS_PASSED=0
TESTS_FAILED=0
TESTS_TOTAL=0

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_test() {
    echo -e "${YELLOW}[TEST]${NC} $1"
}

pass() {
    echo -e "${GREEN}[PASS]${NC} $1"
    ((TESTS_PASSED++))
    ((TESTS_TOTAL++))
}

fail() {
    echo -e "${RED}[FAIL]${NC} $1"
    ((TESTS_FAILED++))
    ((TESTS_TOTAL++))
}

setup_test_env() {
    log_test "Setting up test environment..."
    mkdir -p "$TEST_DATA_DIR"
    export WM_DATA_DIR="$TEST_DATA_DIR"
    export EVENTS_DIR="$TEST_DATA_DIR/events"
    export MEMORY_DIR="$TEST_DATA_DIR/memory"
    mkdir -p "$EVENTS_DIR" "$MEMORY_DIR"
    
    cat > "$EVENTS_DIR/test_cron.json" << 'EOF'
{"timestamp": "2026-03-02T08:00:00Z", "type": "cron", "event": "heartbeat"}
EOF
    cat > "$EVENTS_DIR/test_user.json" << 'EOF'
{"timestamp": "2026-03-02T09:30:00Z", "type": "user", "event": "message_received", "payload": {"content": "Hello!"}}
EOF
    cat > "$EVENTS_DIR/test_system.json" << 'EOF'
{"timestamp": "2026-03-02T10:00:00Z", "type": "system", "event": "alert", "payload": {"level": "warning"}}
EOF
    cat > "$EVENTS_DIR/test_skill.json" << 'EOF'
{"timestamp": "2026-03-02T10:30:00Z", "type": "skill", "event": "execution_complete", "payload": {"skill": "test"}}
EOF
    cat > "$MEMORY_DIR/2026-03-02_test.md" << 'EOF'
# Test Memory Log
- Cron job executed
- User interaction
EOF
    log_test "Test environment ready"
}

cleanup_test_env() {
    log_test "Cleaning up..."
    rm -rf "$TEST_DATA_DIR"
}

test_event_type_detection() {
    log_test "Testing event type detection..."
    source "$WM_DIR/observation_encoder.sh" 2>/dev/null || true
    local result=$(detect_event_type "heartbeat_cron.json")
    if [[ "$result" == "cron" ]]; then pass "Detects cron events"; else fail "Failed cron detection: got '$result'"; fi
    result=$(detect_event_type "user_message.json")
    if [[ "$result" == "user" ]]; then pass "Detects user events"; else fail "Failed user detection"; fi
    result=$(detect_event_type "system_error.log")
    if [[ "$result" == "system" ]]; then pass "Detects system events"; else fail "Failed system detection"; fi
    result=$(detect_event_type "skill_execution.json")
    if [[ "$result" == "skill" ]]; then pass "Detects skill events"; else fail "Failed skill detection"; fi
}

test_json_event_parsing() {
    log_test "Testing JSON event parsing..."
    source "$WM_DIR/observation_encoder.sh" 2>/dev/null || true
    local result=$(parse_json_event "$EVENTS_DIR/test_cron.json" "cron" "2026-03-02T08:00:00Z")
    if echo "$result" | jq -e '.event_type == "cron"' >/dev/null 2>&1; then pass "Parses JSON event type"; else fail "Failed JSON event type"; fi
    if echo "$result" | jq -e '.payload.event == "heartbeat"' >/dev/null 2>&1; then pass "Parses JSON payload"; else fail "Failed JSON payload"; fi
}

test_state_change_encoding() {
    log_test "Testing state change encoding..."
    source "$WM_DIR/observation_encoder.sh" 2>/dev/null || true
    local event='{"event_type":"cron","timestamp":"2026-03-02T08:00:00Z","confidence":0.9}'
    local result=$(encode_state_change "$event")
    if echo "$result" | jq -e '.change_type == "temporal"' >/dev/null 2>&1; then pass "Encodes cron as temporal"; else fail "Failed cron encoding"; fi
    event='{"event_type":"user","timestamp":"2026-03-02T09:00:00Z","confidence":0.8}'
    result=$(encode_state_change "$event")
    if echo "$result" | jq -e '.change_type == "human_interaction"' >/dev/null 2>&1; then pass "Encodes user as human_interaction"; else fail "Failed user encoding"; fi
}

test_full_event_processing() {
    log_test "Testing full event processing..."
    local result=$(WM_DATA_DIR="$TEST_DATA_DIR" EVENTS_DIR="$EVENTS_DIR" "$WM_DIR/observation_encoder.sh" encode "$EVENTS_DIR/test_user.json" 2>/dev/null)
    if echo "$result" | jq -e '.event.event_type == "user"' >/dev/null 2>&1; then pass "Full processing preserves type"; else fail "Full processing lost type"; fi
    if echo "$result" | jq -e '.state_change.change_type == "human_interaction"' >/dev/null 2>&1; then pass "Full processing creates state_change"; else fail "Full processing missing state_change"; fi
}

test_state_manager_init() {
    log_test "Testing state manager initialization..."
    local test_dir="$TEST_DATA_DIR/state_test"
    rm -rf "$test_dir"
    local result=$(WM_DATA_DIR="$test_dir" "$WM_DIR/state_manager.sh" init 2>/dev/null)
    if [[ -f "$test_dir/states/current_state.json" ]]; then pass "Creates current_state.json"; else fail "Missing current_state.json"; fi
    if [[ -f "$test_dir/states/state_history.jsonl" ]]; then pass "Creates state_history.jsonl"; else fail "Missing state_history.jsonl"; fi
    local state=$(WM_DATA_DIR="$test_dir" "$WM_DIR/state_manager.sh" get 2>/dev/null)
    if echo "$state" | jq -e '.version' >/dev/null 2>&1; then pass "State has version field"; else fail "State missing version"; fi
}

test_state_updates() {
    log_test "Testing state updates..."
    local test_dir="$TEST_DATA_DIR/state_test"
    local change='{"change_type":"user","confidence":0.8,"severity":0.5,"state_delta":{"human_state":{"engagement_level":"active"}}}'
    local result=$(WM_DATA_DIR="$test_dir" "$WM_DIR/state_manager.sh" apply "$change" 2>/dev/null)
    if echo "$result" | jq -e '.human_state.engagement_level == "active"' >/dev/null 2>&1; then pass "Applies human_state delta"; else fail "Failed to apply delta"; fi
}

test_goal_management() {
    log_test "Testing goal management..."
    local test_dir="$TEST_DATA_DIR/state_test"
    local result=$(WM_DATA_DIR="$test_dir" "$WM_DIR/state_manager.sh" goal ZIEL-TEST active 2>/dev/null)
    if echo "$result" | jq -e '.state.context.active_goals | contains(["ZIEL-TEST"])' >/dev/null 2>&1; then pass "Adds goal to active"; else fail "Failed to add goal"; fi
    result=$(WM_DATA_DIR="$test_dir" "$WM_DIR/state_manager.sh" goal ZIEL-TEST completed 2>/dev/null)
    if echo "$result" | jq -e '.state.context.active_goals | contains(["ZIEL-TEST"]) | not' >/dev/null 2>&1; then pass "Removes completed goal"; else fail "Failed to remove goal"; fi
}

test_decision_recording() {
    log_test "Testing decision recording..."
    local test_dir="$TEST_DATA_DIR/state_test"
    local result=$(WM_DATA_DIR="$test_dir" "$WM_DIR/state_manager.sh" decision "Test decision" 2>/dev/null)
    if echo "$result" | jq -e '.agent_state.recent_decisions | length > 0' >/dev/null 2>&1; then pass "Records decision"; else fail "Failed to record decision"; fi
}

test_human_state_update() {
    log_test "Testing human state update..."
    local test_dir="$TEST_DATA_DIR/state_test"
    local result=$(WM_DATA_DIR="$test_dir" "$WM_DIR/state_manager.sh" human engaged true 2>/dev/null)
    if echo "$result" | jq -e '.human_state.engagement_level == "engaged"' >/dev/null 2>&1; then pass "Updates engagement level"; else fail "Failed engagement update"; fi
    if echo "$result" | jq -e '.human_state.availability == "true"' >/dev/null 2>&1; then pass "Updates availability"; else fail "Failed availability update"; fi
}

run_all_tests() {
    echo "======================================"
    echo "  ZIEL-009 Phase 3: Observation Tests"
    echo "======================================"
    echo ""
    
    setup_test_env
    
    echo "--- Observation Encoder Tests ---"
    test_event_type_detection
    test_json_event_parsing
    test_state_change_encoding
    test_full_event_processing
    
    echo ""
    echo "--- State Manager Tests ---"
    test_state_manager_init
    test_state_updates
    test_goal_management
    test_decision_recording
    test_human_state_update
    
    cleanup_test_env
    
    echo ""
    echo "======================================"
    echo "  Test Results"
    echo "======================================"
    echo -e "${GREEN}Passed: $TESTS_PASSED${NC}"
    echo -e "${RED}Failed: $TESTS_FAILED${NC}"
    echo "Total:  $TESTS_TOTAL"
    echo ""
    
    if [[ $TESTS_FAILED -eq 0 ]]; then
        echo -e "${GREEN}All tests passed!${NC}"
        exit 0
    else
        echo -e "${RED}Some tests failed!${NC}"
        exit 1
    fi
}

if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    run_all_tests
fi
