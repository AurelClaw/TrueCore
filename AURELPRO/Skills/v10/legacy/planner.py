#!/usr/bin/env python3
# v10 Legacy Wrapper: planner
# Module: aurel_proto_agi.planner
# Description: MPC Planner for action selection

import sys
import json
import time
from datetime import datetime

sys.path.insert(0, '/root/.openclaw/workspace/aurel_proto_agi')

# v10 Telemetry
def log_telemetry(status, extra={}{}):
    entry = {
        'skill': 'planner',
        'type': 'legacy_python',
        'status': status,
        'timestamp': time.time(),
        **extra
    }
    with open('/root/.openclaw/workspace/v10_skill_telemetry.jsonl', 'a') as f:
        f.write(json.dumps(entry) + '\n')

print("🤖 v10 Legacy Python: planner")
print("   MPC Planner for action selection")
print()

log_telemetry('starting')

try:
    # Import legacy module
    from planner import AurelPlanner
    print(f"✓ Imported {capability.function_name}")
    
    # Instantiate
    instance = AurelPlanner()
    print(f"✓ Created instance")
    
    log_telemetry('success', {'instantiated': True})
    
except Exception as e:
    print(f"✗ Error: {e}")
    log_telemetry('failed', {'error': str(e)})
    sys.exit(1)
