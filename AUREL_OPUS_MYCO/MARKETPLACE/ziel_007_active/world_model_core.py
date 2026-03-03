#!/usr/bin/env python3
"""
world_model_core.py - Einfache State Prediction
"""

import json
from typing import Dict, Any

class SimpleWorldModel:
    """
    Vorhersage nächster State basierend auf History
    """
    
    def __init__(self):
        self.state_history = []
        self.transition_counts = {}
    
    def observe(self, state: Dict[str, Any]):
        """Beobachte neuen State"""
        self.state_history.append(state)
        
        # Lerne Transitionen
        if len(self.state_history) >= 2:
            prev = self._state_key(self.state_history[-2])
            curr = self._state_key(state)
            
            if prev not in self.transition_counts:
                self.transition_counts[prev] = {}
            
            self.transition_counts[prev][curr] = self.transition_counts[prev].get(curr, 0) + 1
    
    def predict_next(self, current_state: Dict[str, Any]) -> Dict[str, Any]:
        """Vorhersage nächster State"""
        key = self._state_key(current_state)
        
        if key not in self.transition_counts:
            return {"prediction": "unknown", "confidence": 0.0}
        
        # Wähle wahrscheinlichste Transition
        transitions = self.transition_counts[key]
        total = sum(transitions.values())
        
        best_next = max(transitions.items(), key=lambda x: x[1])
        confidence = best_next[1] / total
        
        return {
            "prediction": best_next[0],
            "confidence": confidence,
            "alternatives": {k: v/total for k, v in transitions.items()}
        }
    
    def _state_key(self, state: Dict) -> str:
        """Erstelle Key aus State"""
        return json.dumps(state, sort_keys=True)


if __name__ == "__main__":
    # Test
    model = SimpleWorldModel()
    
    # Simuliere Beobachtungen
    for i in range(5):
        model.observe({"step": i, "value": i * 10})
    
    prediction = model.predict_next({"step": 4, "value": 40})
    print(f"Prediction: {prediction}")
    
    print("\n⚛️ Noch.")
