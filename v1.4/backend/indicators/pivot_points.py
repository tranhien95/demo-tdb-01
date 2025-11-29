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
        
        return {
            "bullish": data[index]["close"] > pivot,
            "bearish": data[index]["close"] < pivot,
            "value": pivot,
            "strength": 50
        }
    
    def get_pine_script(self) -> str:
        return """// Pivot Points
pivot = (high + low + close) / 3
r1 = 2 * pivot - low
s1 = 2 * pivot - high
pivot_bullish = close > pivot
pivot_bearish = close < pivot"""
