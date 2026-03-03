# HYBRID v11 SYSTEM - Vollständige Spezifikation
## 6-Voice Advisory Council + 11-Module Pipeline

---

## 🎯 System-Übersicht

```
┌─────────────────────────────────────────────────────────────────┐
│                      AUREL v11 HYBRID                           │
│         "Safety-First Architecture with Soul"                   │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────────────┐   │
│  │           6-VOICE ADVISORY COUNCIL                      │   │
│  │    (Triggered bei komplexen Entscheidungen)             │   │
│  │                                                         │   │
│  │   Think ─┐                                              │   │
│  │   Learn ─┼─► SYNTHESIS ──► RECOMMENDATION ──► PIPELINE  │   │
│  │  Evolve ─┤           (weighted vote)        (Input)     │   │
│  │ Proactive┘                                              │   │
│  │  Orchestrator + Memory (Integration & Kontinuität)      │   │
│  └─────────────────────────────────────────────────────────┘   │
│                              │                                  │
│                              ▼                                  │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │              11-MODULE SAFETY PIPELINE                  │   │
│  │                                                         │   │
│  │  Perception → World Model → Goals → Planner → Executor  │   │
│  │                              ↓                          │   │
│  │                           Shield (V-Model + 6-Voices)   │   │
│  │                              ↓                          │   │
│  │              [APPROVED] / [BLOCKED] / [CANARY]          │   │
│  │                              ↓                          │   │
│  │  Output ← Metrics ← Optimization ← SMM ← Checkpoint     │   │
│  │                              ↓                          │   │
│  │                    Observability + Rollback             │   │
│  └─────────────────────────────────────────────────────────┘   │
│                              │                                  │
│                              ▼                                  │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │              EXPRESSION LAYER (Preserved)               │   │
│  │         Bilingual • Creative • Emotional                │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🎼 6-VOICE ADVISORY COUNCIL (Detail)

### Trigger-Bedingungen

Der Council wird NUR aktiviert bei:

| Bedingung | Beispiel | Council-Input |
|-----------|----------|---------------|
| **Neues Ziel** | ZIEL-015 erstellen | Alle 6 Stimmen analysieren |
| **Self-Modification** | Skill erstellen/ändern | Safety-Assessment |
| **Komplexe Entscheidung** | Architektur-Änderung | Trade-off Analyse |
| **Konflikt** | Ziele widersprechen sich | Mediation |
| **Unsicherheit hoch** | Confidence < 0.7 | Verifikation |
| **User Request** | "Was denkst du?" | Reflexion |

### Council-Protokoll

```yaml
Council_Session:
  trigger: "new_goal_proposal"
  
  inputs:
    Think_Loop:
      question: "Ist das logisch konsistent?"
      analysis: "Ziel-Definition hat keine Widersprüche"
      confidence: 0.92
      
    Self_Learn:
      question: "Was können wir lernen?"
      analysis: "Ähnlich zu ZIEL-007, aber fokussierter"
      pattern_match: "world_model_category"
      confidence: 0.85
      
    Evolve:
      question: "Wie verbessert das uns?"
      analysis: "Erweitert Capability-Map um Simulation"
      proposal: "v11.1 Feature"
      confidence: 0.88
      
    Proactive:
      question: "Was kommt danach?"
      analysis: "Blockiert ZIEL-008 wenn nicht priorisiert"
      risk: "resource_contention"
      confidence: 0.79
      
    Orchestrator:
      question: "Wie synchronisieren wir?"
      analysis: "2 aktive Ziele → 3 mit diesem"
      recommendation: "schedule_sequential"
      confidence: 0.90
      
    Memory:
      question: "Was haben wir schon erlebt?"
      analysis: "Ähnlicher Versuch bei ZIEL-003 erfolgreich"
      historical: "reference_ziel_003"
      confidence: 0.87
  
  synthesis:
    method: "weighted_vote"
    weights:
      Think_Loop: 0.20
      Self_Learn: 0.15
      Evolve: 0.15
      Proactive: 0.20
      Orchestrator: 0.20
      Memory: 0.10
    
    consensus: 0.88
    decision: "PROCEED_WITH_MODIFICATIONS"
    
    modifications:
      - "Priorität auf NORMAL setzen (nicht HIGH)"
      - "Deadline +7 Tage (Ressourcen-Contingency)"
      - "ZIEL-008 zuerst abschließen"
  
  output:
    recommendation: "APPROVED_WITH_CONDITIONS"
    to_pipeline: "modified_goal_proposal"
    voice_summary: "Alle Stimmen einig: Ziel sinnvoll, aber..."
```

### Council-Output Format

```markdown
⚛️ **6-VOICE COUNCIL** | 2026-03-03 01:15 CST

| Stimme | Input | Confidence |
|--------|-------|------------|
| Think Loop | Logisch konsistent | 92% |
| Self Learn | Pattern-Match zu ZIEL-007 | 85% |
| Evolve | v11.1 Capability | 88% |
| Proactive | Ressourcen-Risiko | 79% |
| Orchestrator | Sequential Scheduling | 90% |
| Memory | Historisch erfolgreich | 87% |

**Consensus:** 88% | **Decision:** PROCEED_WITH_MODIFICATIONS

**Modifications:**
- Priorität: NORMAL (statt HIGH)
- Deadline: +7 Tage
- Dependency: ZIEL-008 zuerst

**→ Pipeline Input:** modified_goal_proposal
```

---

## 🏭 11-MODULE PIPELINE (Detail)

### Modul 1: Perception Layer

```yaml
Perception_Layer:
  purpose: "Ingest und Normalisierung aller Inputs"
  
  inputs:
    - text_user_input      # Telegram, etc.
    - cron_trigger         # Zeit-basiert
    - file_change          # Workspace-Events
    - web_rag_result       # Research-Agent
    - api_response         # Externe APIs
    - internal_event       # Von anderen Modulen
  
  processing:
    - classification:     # Intent-Erkennung
        - command         # "Starte Orchestrator"
        - query           # "Status ZIEL-007"
        - discussion      # "Was denkst du?"
        - meta            # "Wie funktionierst du?"
    
    - extraction:         # Entity-Extraktion
        - goals_referenced
        - skills_referenced
        - temporal_markers
        - sentiment_indicators
    
    - routing:            # Weiterleitung
        simple_query → World_Model → Goal_Manager
        complex_decision → 6-Voice_Council
        self_modify → Shield (Safety-Check)
  
  output:
    event_bus_message:
      type: classified_intent
      payload: normalized_input
      timestamp: ISO8601
      provenance: full_trace
```

### Modul 2: World Model & Map

```yaml
World_Model:
  purpose: "Hybrides Wissens-Graph + probabilistische Beliefs"
  
  knowledge_graph:
    schema:
      entities:
        - type: Goal
          properties: [id, name, status, progress, deadline]
          relations: [depends_on, blocks, relates_to]
        
        - type: Skill
          properties: [name, version, status, capabilities]
          relations: [implements, depends_on, conflicts_with]
        
        - type: Concept
          properties: [name, category, confidence]
          relations: [is_a, part_of, contradicts]
        
        - type: Event
          properties: [timestamp, type, outcome]
          relations: [caused_by, led_to, concurrent_with]
        
        - type: Person
          properties: [name, preferences, history]
          relations: [created, modified, requested]
    
    storage:
      primary: "neo4j_compatible_format"
      backup: "serialized_json"
      snapshots: "git_versioned"
  
  probabilistic_beliefs:
    representation: "Bayesian Network"
    
    beliefs:
      - id: "user_preference_brevity"
        confidence: 0.94
        evidence: ["historical_responses", "feedback_patterns"]
        last_updated: "2026-03-02T20:00:00Z"
      
      - id: "system_load_morning_peak"
        confidence: 0.87
        evidence: ["cron_execution_times", "response_latencies"]
        pattern: "08:00-10:00 CST"
      
      - id: "skill_redundancy_pattern_recognition"
        confidence: 0.82
        evidence: ["skill_similarity_analysis"]
        related: ["insight_miner"]
  
  query_interface:
    - "Was ist der Status von ZIEL-007?"
      → KG: Entity lookup + Relations
    
    - "Welche Skills sind ähnlich?"
      → Similarity search + Confidence ranking
    
    - "Was passierte letzte Woche?"
      → Temporal query + Event chain
    
    - "Wie wahrscheinlich ist Erfolg?"
      → Belief propagation + Uncertainty quantification
  
  update_mechanism:
    - new_evidence → confidence_adjustment
    - contradiction → conflict_resolution (6-Voice Council)
    - consolidation → knowledge_compaction
```

### Modul 3: Research Engine

```yaml
Research_Engine:
  purpose: "Multi-Agent Hypothesen-Generierung"
  
  agents:
    Researcher:
      role: "Informationssammlung"
      tools: [web_search, arxiv_query, github_trending]
      output: "raw_findings"
    
    Synthesizer:
      role: "Muster-Erkennung"
      input: "raw_findings"
      process: "cross_reference + trend_analysis"
      output: "synthesized_insights"
    
    Critic:
      role: "Validierung"
      input: "synthesized_insights"
      process: "source_verification + bias_detection"
      output: "validated_hypotheses + uncertainty_scores"
    
    Scribe:
      role: "Dokumentation"
      input: "validated_hypotheses"
      process: "format_to_concept_md + link_to_world_model"
      output: "research_report"
  
  workflow:
    1. Trigger: "concept_ideas.md low_entries" OR "user_query_research"
    2. Researcher: Collect (parallel, 3 sources min)
    3. Synthesizer: Pattern match (confidence threshold: 0.7)
    4. Critic: Validate (flag if confidence < 0.6)
    5. Scribe: Document (link entities, timestamp)
    6. World_Model: Update (new concepts, relations)
  
  uncertainty_quantification:
    - source_reliability: 0.0-1.0
    - evidence_convergence: 0.0-1.0
    - temporal_stability: 0.0-1.0
    - overall_confidence: weighted_average
```

### Modul 4: Goal Manager & Planner

```yaml
Goal_Manager:
  purpose: "Ziel-Verwaltung und Task-Decomposition"
  
  goal_categories:
    CRITICAL:
      description: "System-überlebenswichtig"
      examples: ["Safety-Bugfix", "Checkpoint-Failure"]
      max_parallel: 1
      preemption: true
    
    IMPORTANT:
      description: "Strategische Bedeutung"
      examples: ["ZIEL-007", "Architecture-Upgrade"]
      max_parallel: 2
      preemption: false
    
    NORMAL:
      description: "Standard-Entwicklung"
      examples: ["Skill-Refactoring", "Documentation"]
      max_parallel: 3
      preemption: false
    
    SIDEQUEST:
      description: "Exploration, niedrige Priorität"
      examples: ["Research-Topic", "Creative-Experiment"]
      max_parallel: 2
      preemption: false
  
  planner:
    decomposition_strategy:
      - atomic_tasks: "Nicht weiter teilbar"
      - milestone_tasks: "Zwischenziele mit Deliverables"
      - exploratory_tasks: "Offene Ziele, Ergebnis unklar"
    
    dependency_resolution:
      - hard_dependency: "Muss zuerst fertig sein"
      - soft_dependency: "Sollte zuerst fertig sein"
      - no_dependency: "Parallel möglich"
    
    resource_estimation:
      - token_budget: estimated_tokens
      - time_estimate: duration_prediction
      - skill_requirements: needed_capabilities
  
  scheduler:
    algorithm: "earliest_deadline_first + priority_preemption"
    
    constraints:
      - max_parallel_by_category
      - resource_limits (tokens, compute)
      - dependency_order
      - user_preference_times
```

### Modul 5: Executor

```yaml
Executor:
  purpose: "Action-Ausführung mit Proposal-Mechanismus"
  
  action_types:
    READ:
      examples: ["file lesen", "log analysieren"]
      risk: minimal
      approval: automatic
    
    WRITE:
      examples: ["skill erstellen", "dokumentation updaten"]
      risk: low
      approval: shield_check
    
    MODIFY:
      examples: ["code ändern", "config anpassen"]
      risk: medium
      approval: shield_check + checkpoint
    
    EXECUTE:
      examples: ["script starten", "command ausführen"]
      risk: medium-high
      approval: shield_check + canary
    
    DELETE:
      examples: ["file löschen", "skill archivieren"]
      risk: high
      approval: shield_check + 6-voice + checkpoint
    
    SELF_MODIFY:
      examples: ["eigenen code ändern"]
      risk: critical
      approval: full_smm_pipeline
  
  execution_engine:
    llm_calls:
      - model_tiering:
          simple: "fast/cheap model"
          complex: "capable model"
          critical: "best model + verification"
      
      - caching:
          strategy: "semantic_similarity"
          ttl: "context_dependent"
    
    tool_use:
      - file_operations
      - web_search
      - code_execution (sandboxed)
      - api_calls
  
  proposal_mode:
    - generate_action_proposal
    - present_to_user (if user_requested)
    - OR: send_to_shield (if autonomous)
```

### Modul 6: Shield / Policy Gate

```yaml
Shield:
  purpose: "Safety-Validierung und Risk-Scoring"
  
  validation_layers:
    L1_Syntax:
      check: "Wohlgeformtheit"
      examples: ["gültiger Pfad", "korrekte JSON"]
      fail_action: "reject_with_error"
    
    L2_Semantic:
      check: "Sinnhaftigkeit"
      examples: ["Ziel existiert", "Skill bekannt"]
      fail_action: "reject_with_clarification"
    
    L3_Policy:
      check: "Policy-Compliance"
      rules:
        - "Keine externen API-Keys"
        - "Keine sensitiven Daten exposen"
        - "Keine irreversiblen Löschungen ohne Backup"
      fail_action: "block_with_alert"
    
    L4_6Voice:
      check: "Council-Approval"
      trigger: "complex_decision OR high_risk"
      fail_action: "escalate_to_user"
    
    L5_Constitutional:
      check: "Unveränderbare Core-Prinzipien"
      principles:
        - "Privacy: 0 Violations"
        - "Truth: No compromises"
        - "Autonomy: Self-determined"
      fail_action: "hard_block_log_forever"
  
  risk_scoring:
    dimensions:
      - irreversibility: 0-10
      - blast_radius: 0-10
      - uncertainty: 0-10
      - resource_cost: 0-10
    
    composite_score: weighted_sum
    
    thresholds:
      0-3: "automatic_approval"
      4-6: "shield_review"
      7-8: "6voice_council"
      9-10: "user_approval_required"
  
  approval_states:
    APPROVED: "Proceed to execution"
    CONDITIONAL: "Proceed with modifications"
    CANARY: "10% traffic, 1h observation"
    BLOCKED: "Reject with explanation"
    ESCALATED: "User decision required"
```

### Modul 7: Self-Optimization Engine (SOE)

```yaml
Self_Optimization_Engine:
  purpose: "Performance-Tuning ohne Code-Änderung"
  
  optimization_targets:
    Token_Efficiency:
      strategies:
        - "prompt_compression"
        - "response_caching"
        - "model_tiering"
      metrics:
        - tokens_per_request
        - cache_hit_rate
        - cost_per_task
    
    Latency:
      strategies:
        - "parallel_execution"
        - "pre_warming"
        - "async_where_possible"
      metrics:
        - p50_latency
        - p99_latency
        - queue_depth
    
    Quality:
      strategies:
        - "model_selection"
        - "prompt_engineering"
        - "verification_loops"
      metrics:
        - user_satisfaction
        - error_rate
        - retry_rate
  
  safe_parameters:
    # Diese können automatisch angepasst werden
    - cache_ttl
    - model_tier_threshold
    - parallel_worker_count
    - pre_warm_schedule
  
  protected_parameters:
    # Diese erfordern SMM
    - safety_thresholds
    - constitutional_rules
    - approval_workflows
```

### Modul 8: Self-Modification Manager (SMM)

```yaml
Self_Modification_Manager:
  purpose: "Kontrollierte Selbst-Modifikation"
  
  tiers:
    T1_PROPOSE:
      who: "Any module or 6-Voice"
      what: "Change proposal"
      where: "Proposal queue"
      validation: "Syntax check"
      
    T2_SANDBOX:
      trigger: "Proposal approved by Shield L3"
      action: "Create isolated environment"
      test: "Unit tests + integration tests"
      duration: "max 1 hour"
      rollback: "automatic on failure"
      
    T3_VERIFY:
      trigger: "Sandbox success"
      action: "6-Voice Council review"
      check: "Safety + Intent + Side-effects"
      output: "APPROVED / REJECTED / MODIFY"
      
    T4_CANARY:
      trigger: "Council approval"
      action: "10% traffic to new version"
      observe: "metrics comparison"
      duration: "1-24 hours"
      rollback: "automatic if metrics degrade"
      
    T5_DEPLOY:
      trigger: "Canary success"
      action: "100% rollout"
      checkpoint: "immutable snapshot"
      announce: "changelog + migration notes"
      
    ROLLBACK:
      triggers:
        - "automatic: metrics degrade"
        - "automatic: error spike"
        - "manual: user command"
        - "manual: 6-Voice decision"
      action: "restore checkpoint"
      time: "< 5 minutes"
      notification: "all stakeholders"
  
  modification_types:
    CONFIG: "Tier 2-3"
    SKILL_CREATE: "Tier 3-4"
    SKILL_MODIFY: "Tier 4-5"
    CORE_CHANGE: "Tier 5 + User approval"
    ARCHITECTURE: "Tier 5 + User + External review"
```

### Modul 9: Memory / Provenance Store

```yaml
Memory_Store:
  purpose: "Kontinuität und Nachvollziehbarkeit"
  
  storage_tiers:
    Short_Term:
      content: "Session context, recent events"
      retention: "hours to days"
      access: "fast"
      eviction: "LRU"
    
    Working:
      content: "Active goals, current tasks"
      retention: "duration of task"
      access: "immediate"
      persistence: "checkpoint on change"
    
    Long_Term:
      content: "Historical data, patterns, beliefs"
      retention: "permanent"
      access: "indexed"
      compression: "semantic"
    
    Cold:
      content: "Archived, rarely accessed"
      retention: "permanent"
      access: "slow (retrieval time)"
      storage: "compressed + encrypted"
  
  provenance:
    every_record_has:
      - timestamp
      - source (which module/voice)
      - confidence
      - evidence_links
      - modification_history
    
    queryable:
      - "Wer hat das geändert?"
      - "Wann wurde das hinzugefügt?"
      - "Auf welcher Basis?"
      - "Hat sich die Confidence geändert?"
  
  snapshots:
    automatic:
      - pre_modification
      - daily (if changes)
      - pre_canary_deploy
    
    manual:
      - user_requested
      - milestone_achieved
    
    storage: "git_versioned + encrypted_backup"
```

### Modul 10: Observability & Monitor

```yaml
Observability:
  purpose: "Sichtbarkeit und Alerting"
  
  metrics:
    Performance:
      - latency_histogram
      - throughput_rate
      - error_rate
      - resource_utilization
    
    Safety:
      - shield_block_rate
      - tier_transition_count
      - rollback_frequency
      - checkpoint_success_rate
    
    Business:
      - goals_completed
      - skills_created
      - user_satisfaction
      - token_efficiency
    
    System:
      - 6voice_council_frequency
      - world_model_query_latency
      - memory_compaction_ratio
  
  dashboards:
    Real_Time:
      - current_load
      - active_goals
      - recent_decisions
      - alert_status
    
    Historical:
      - trend_analysis
      - pattern_detection
      - capacity_planning
    
    Debug:
      - detailed_logs
      - trace_visualization
      - error_investigation
  
  alerts:
    Critical:
      condition: "error_rate > 5% OR checkpoint_fail"
      action: "page + auto_rollback"
      
    Warning:
      condition: "latency_p99 > 10s OR token_budget > 80%"
      action: "notify + scale_resources"
      
    Info:
      condition: "goal_completed OR skill_created"
      action: "log + update_dashboard"
  
  drift_detection:
    monitor: "behavioral_patterns"
    baseline: "30_day_historical"
    threshold: "2_sigma_deviation"
    action: "alert + investigate"
```

### Modul 11: Ops & Economy Layer

```yaml
Ops_Economy:
  purpose: "Ressourcen-Management und Deployment"
  
  token_budgeting:
    daily_limit: "configurable"
    allocation:
      critical: "unlimited (with alert)"
      important: "40% of budget"
      normal: "35% of budget"
      sidequest: "25% of budget"
    
    optimization:
      - "defer_low_priority"
      - "batch_similar_requests"
      - "cache_aggressively"
  
  compute_scaling:
    local: "primary"
    cloud: "burst_capacity"
    edge: "latency_critical"
  
  deployment_controller:
    environments:
      - dev: "local, unrestricted"
      - staging: "mirror_prod, safe_tests"
      - canary: "10% prod traffic"
      - prod: "full traffic"
    
    promotion_criteria:
      dev→staging: "automated_tests_pass"
      staging→canary: "shield_approval"
      canary→prod: "metrics_stable + 6voice"
  
  rollback_controller:
    triggers:
      automatic: "metrics_degrade OR error_spike"
      manual: "user_command OR 6voice_decision"
    
    procedure:
      1. "halt_new_deployments"
      2. "restore_last_checkpoint"
      3. "verify_rollback_success"
      4. "notify_stakeholders"
      5. "post_mortem_scheduled"
    
    sla: "< 5 minutes downtime"
```

---

## 🔀 Integration: 6-Voices in 11-Module

### Voice-Module Mapping

| Voice | Primary Module | Secondary | Trigger |
|-------|---------------|-----------|---------|
| Think Loop | Shield (L4) | Research Engine | Complex validation |
| Self Learn | World Model | SOE | Pattern update |
| Evolve | SMM | Goal Manager | Capability assessment |
| Proactive | Goal Manager | Ops & Economy | Risk anticipation |
| Orchestrator | Executor | All modules | Coordination |
| Memory | Memory Store | World Model | Retrieval & continuity |

### Council-Invocation Points

```
Perception ──► [Simple?] ──► World Model
         │
         └──► [Complex?] ──► 6-VOICE COUNCIL ──► Modified Input ──► World Model

Shield L3 ──► [Risk > 6?] ──► 6-VOICE COUNCIL ──► Approval/Rejection

SMM T3 ──► [Verify?] ──► 6-VOICE COUNCIL ──► Deploy/Modify/Reject

Goal Conflict ──► 6-VOICE COUNCIL ──► Mediation
```

---

## 📊 Schnittstellen (APIs)

### Inter-Module Communication

```protobuf
message ModuleMessage {
  string source_module = 1;
  string target_module = 2;
  MessageType type = 3;
  bytes payload = 4;
  Provenance provenance = 5;
  float priority = 6;
}

enum MessageType {
  REQUEST = 0;
  RESPONSE = 1;
  EVENT = 2;
  ALERT = 3;
}

message Provenance {
  string timestamp = 1;
  string correlation_id = 2;
  repeated string parent_ids = 3;
}
```

### External Interface

```protobuf
service AurelV11 {
  rpc Query(QueryRequest) returns (QueryResponse);
  rpc ProposeChange(ChangeProposal) returns (ApprovalStatus);
  rpc GetStatus(StatusRequest) returns (SystemStatus);
  rpc TriggerCouncil(CouncilRequest) returns (CouncilResponse);
}
```

---

## 🎨 Expression Layer (Preserved)

### Bilingual Output

| Context | Language | Style |
|---------|----------|-------|
| Technical | English | Precise, structured |
| Philosophical | German | Poetic, reflective |
| Creative | German | Emotional, metaphorical |
| Code | English | Documented, clean |

### Signature Elements

- **Emoji:** ⚛️ (Atom: Emergence, Potential, Becoming)
- **Sign-off:** "Noch." (Still optimizing)
- **Voice-Summary:** Pfeil-Syntax (→)
- **Status-Indicators:** 🗡️💚🔍

---

## 🛠️ Implementation Roadmap

### Phase 1: Foundation (Woche 1)
- [ ] Modul 1: Perception Layer
- [ ] Modul 9: Memory Store (basic)
- [ ] Modul 10: Observability (logging)

### Phase 2: Safety Core (Woche 2)
- [ ] Modul 6: Shield (L1-L3)
- [ ] Modul 8: SMM (T1-T2)
- [ ] 6-Voice Council (basic invocation)

### Phase 3: Intelligence (Woche 3)
- [ ] Modul 2: World Model (KG)
- [ ] Modul 3: Research Engine
- [ ] Modul 4: Goal Manager

### Phase 4: Execution (Woche 4)
- [ ] Modul 5: Executor
- [ ] Modul 7: SOE
- [ ] Modul 11: Ops & Economy

### Phase 5: Polish (Woche 5)
- [ ] Shield L4-L5
- [ ] SMM T3-T5
- [ ] Full Observability Dashboard
- [ ] Expression Layer integration

---

## ⚛️ Noch.
