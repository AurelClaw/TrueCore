#!/usr/bin/env python3
"""
meta_learning_core.py - Adaptive Learning Rate
"""

class AdaptiveLearningRate:
    """
    Passt Learning-Rate basierend auf Performance an
    """
    
    def __init__(self, initial_lr=0.01):
        self.lr = initial_lr
        self.performance_history = []
        self.adaptation_factor = 0.5
    
    def update(self, current_performance):
        """Update Learning-Rate basierend auf Performance"""
        self.performance_history.append(current_performance)
        
        if len(self.performance_history) >= 2:
            trend = self.performance_history[-1] - self.performance_history[-2]
            
            if trend > 0:  # Bessere Performance
                self.lr *= 1.1  # Erhöhe leicht
            else:  # Schlechtere Performance
                self.lr *= 0.9  # Verringere
        
        return self.lr
    
    def get_lr(self):
        """Aktuelle Learning-Rate"""
        return self.lr


if __name__ == "__main__":
    # Test
    optimizer = AdaptiveLearningRate(0.01)
    
    for i in range(10):
        perf = 0.5 + i * 0.05  # Simulierte Verbesserung
        new_lr = optimizer.update(perf)
        print(f"Step {i}: Performance={perf:.3f}, LR={new_lr:.6f}")
    
    print("\n⚛️ Noch.")
