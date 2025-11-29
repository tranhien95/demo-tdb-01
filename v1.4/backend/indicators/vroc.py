"""
VROC - Volume Rate of Change
Measures volume momentum as percentage change
"""

from typing import List, Dict
from .base import BaseIndicator


class VROCIndicator(BaseIndicator):
    """Volume Rate of Change with customizable settings"""
    
    def default_config(self) -> Dict:
        return {
            'period': 14,
            'description': 'Volume Rate of Change'
        }
    
    def calculate(self, data: List[Dict], index: int, **kwargs) -> Dict:
        period = kwargs.get('period', self.config['period'])
        
        if index < period:
            return {"bullish": False, "bearish": False, "value": 0, "strength": 0}
        
        prev_vol = data[index - period]["volume"]
        vroc_val = ((data[index]["volume"] - prev_vol) / prev_vol) * 100 if prev_vol > 0 else 0
        
        return {
            "bullish": vroc_val > 0,
            "bearish": vroc_val < 0,
            "value": vroc_val,
            "strength": abs(vroc_val)
        }
    
    def get_pine_script(self) -> str:
        period = self.config['period']
        return f"""// VROC Indicator
vroc_value = (volume - volume[{period}]) / volume[{period}] * 100
vroc_bullish = vroc_value > 0
vroc_bearish = vroc_value < 0"""
