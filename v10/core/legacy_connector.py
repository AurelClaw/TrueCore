"""
Legacy Connector - Verbindet altes Proto-AGI mit v10
"""

import sys
sys.path.insert(0, '/root/.openclaw/workspace/aurel_proto_agi')

from v10_identity_layer import V10IdentityLayer

class LegacyToV10Connector:
    """
    Verbindet Legacy Proto-AGI Komponenten mit v10
    """
    
    def __init__(self):
        self.identity = V10IdentityLayer()
        self.legacy_imported = False
        
    def import_legacy_world_model(self):
        """Importiere World Model aus aurel_proto_agi"""
        try:
            from world_model import AurelWorldModel
            self.world_model = AurelWorldModel()
            self.legacy_imported = True
            return True
        except Exception as e:
            print(f"✗ Failed to import World Model: {e}")
            return False
    
    def import_legacy_planner(self):
        """Importiere Planner aus aurel_proto_agi"""
        try:
            from planner import AurelPlanner
            self.planner = AurelPlanner()
            return True
        except Exception as e:
            print(f"✗ Failed to import Planner: {e}")
            return False
    
    def bridge_to_v10(self):
        """Verbinde Legacy mit v10 Telemetry"""
        if not self.legacy_imported:
            return False
        
        # Erstelle v10-kompatiblen State
        v10_state = {
            'legacy_world_model': self.world_model is not None,
            'legacy_planner': self.planner is not None,
            'identity': self.identity.identity.name,
            'bridged': True
        }
        
        return v10_state

if __name__ == '__main__':
    connector = LegacyToV10Connector()
    
    print("🔄 Legacy-to-v10 Connector")
    print("   Importing World Model...", end=" ")
    if connector.import_legacy_world_model():
        print("✓")
    else:
        print("✗")
    
    print("   Importing Planner...", end=" ")
    if connector.import_legacy_planner():
        print("✓")
    else:
        print("✗")
    
    print("   Bridging to v10...", end=" ")
    state = connector.bridge_to_v10()
    if state:
        print("✓")
        print(f"   Status: {state}")
    else:
        print("✗")
