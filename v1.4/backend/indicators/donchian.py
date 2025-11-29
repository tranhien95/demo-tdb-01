"""
Donchian Channel
Price channel breakout indicator
"""

from typing import List, Dict
from .base import BaseIndicator


class DonchianIndicator(BaseIndicator):
    """Donchian Channel with customizable settings"""
    
    def default_config(self) -> Dict:
        return {
            'period': 20,
            'description': 'Donchian Channel - Breakout indicator'
        }
    
    def calculate(self, data: List[Dict], index: int, **kwargs) -> Dict:
        period = kwargs.get('period', self.config['period'])
        
        if index < period:
            return {"bullish": False, "bearish": False, "value": 0, "strength": 0}
        
        high = max(d["high"] for d in data[index - period + 1:index + 1])
        low = min(d["low"] for d in data[index - period + 1:index + 1])
        mid = (high + low) / 2
        
        return {
            "bullish": data[index]["close"] > mid,
            "bearish": data[index]["close"] < mid,
            "value": mid,
            "strength": 50
        }
    
    def get_pine_script(self) -> str:
        period = self.config['period']
        return f"""// Donchian Channel
donchian_high = ta.highest(high, {period})
donchian_low = ta.lowest(low, {period})
donchian_mid = (donchian_high + donchian_low) / 2
donchian_bullish = close > donchian_mid
donchian_bearish = close < donchian_mid"""
