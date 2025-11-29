"""
RVI - Relative Vigor Index
Measures conviction behind price moves
"""

from typing import List, Dict
from .base import BaseIndicator


class RVIIndicator(BaseIndicator):
    """Relative Vigor Index with customizable settings"""
    
    def default_config(self) -> Dict:
        return {
            'period': 10,
            'description': 'Relative Vigor Index'
        }
    
    def calculate(self, data: List[Dict], index: int, **kwargs) -> Dict:
        period = kwargs.get('period', self.config['period'])
        
        if index < period:
            return {"bullish": False, "bearish": False, "value": 50, "strength": 0}
        
        numerator, denominator = 0, 0
        for i in range(index - period + 1, index + 1):
            numerator += data[i]["close"] - data[i]["open"]
            denominator += data[i]["high"] - data[i]["low"]
        
        rvi_val = (numerator / denominator * 100) if denominator > 0 else 50
        
        return {
            "bullish": rvi_val > 50,
            "bearish": rvi_val < 50,
            "value": rvi_val,
            "strength": abs(50 - rvi_val) / 50 * 100
        }
    
    def get_pine_script(self) -> str:
        period = self.config['period']
        return f"""// RVI Indicator
rvi_value = ta.rvi({period})
rvi_bullish = rvi_value > 0
rvi_bearish = rvi_value < 0"""
