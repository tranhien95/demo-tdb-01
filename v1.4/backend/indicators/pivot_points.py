"""
Pivot Points
Support and Resistance levels
"""

from typing import List, Dict
from .base import BaseIndicator


class PivotPointsIndicator(BaseIndicator):
    """Pivot Points with customizable settings"""
    
    def default_config(self) -> Dict:
        return {
            'description': 'Pivot Points - Support/Resistance levels'
        }
    
    def calculate(self, data: List[Dict], index: int, **kwargs) -> Dict:
        h = data[index]["high"]
        l = data[index]["low"]
        c = data[index]["close"]
        
        pivot = (h + l + c) / 3
        r1 = 2 * pivot - l
        r2 = pivot + (h - l)
        s1 = 2 * pivot - h
        s2 = pivot - (h - l)
        
        current_price = data[index]["close"]
        
        # Find nearest level
        levels = {"pivot": pivot, "r1": r1, "r2": r2, "s1": s1, "s2": s2}
        distances = {k: abs(current_price - v) for k, v in levels.items()}
        nearest_level = min(distances, key=distances.get)
        distance_to_nearest = distances[nearest_level]
        distance_percent = (distance_to_nearest / current_price * 100) if current_price > 0 else 0
        
        # Determine signal based on position
        if current_price > r1:
            if current_price > r2:
                signal_type = "STRONG_RESISTANCE"
                confidence = 90
            else:
                signal_type = "RESISTANCE"
                confidence = 75
        elif current_price < s1:
            if current_price < s2:
                signal_type = "STRONG_SUPPORT"
                confidence = 90
            else:
                signal_type = "SUPPORT"
                confidence = 75
        else:
            signal_type = "NEUTRAL"
            confidence = 50
        
        # Trend
        is_bullish = current_price > pivot
        trend = "LEVEL_STRONG" if distance_percent < 1 else "LEVEL_WEAK"
        
        # Breakout potential
        breakout_likelihood = 1 - min(distance_percent / 2, 1)
        
        return {
            "bullish": is_bullish,
            "bearish": not is_bullish,
            "value": pivot,
            "strength": confidence,
            "signal_type": signal_type,
            "confidence": confidence,
            "trend": trend,
            "reversal_signal": distance_percent < 0.5,  # At level
            "divergence": False,
            "supporting_signals": [
                f"Price: {current_price:.2f}",
                f"R1: {r1:.2f} ({abs(current_price - r1):.2f} away)",
                f"S1: {s1:.2f} ({abs(current_price - s1):.2f} away)",
                f"Pivot: {pivot:.2f} {'(active support)' if abs(current_price - pivot) < 0.1 * (h - l) else '(reference)'}",
                f"Level strength: {'Strong' if distance_percent < 1 else 'Weak'}"
            ],
            "raw_values": {
                "pivot": pivot,
                "r1": r1,
                "r2": r2,
                "s1": s1,
                "s2": s2,
                "nearest_level": nearest_level,
                "distance_to_nearest": distance_to_nearest,
                "level_strength": 100 - min(distance_percent * 10, 100),
                "breakout_likelihood": breakout_likelihood
            }
        }
    
    def get_pine_script(self) -> str:
        return """// Pivot Points
pivot = (high + low + close) / 3
r1 = 2 * pivot - low
s1 = 2 * pivot - high
pivot_bullish = close > pivot
pivot_bearish = close < pivot"""
