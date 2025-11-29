"""
Momentum Indicator
Measures price change over time
"""

from typing import List, Dict
from .base import BaseIndicator


class MomentumIndicator(BaseIndicator):
    """Momentum with customizable settings"""
    
    def default_config(self) -> Dict:
        return {
            'period': 10,
            'description': 'Momentum - Price momentum'
        }
    
    def calculate(self, data: List[Dict], index: int, **kwargs) -> Dict:
        period = kwargs.get('period', self.config['period'])
        
        if index < period:
            return {"bullish": False, "bearish": False, "value": 0, "strength": 0}
        
        momentum_val = data[index]["close"] - data[index - period]["close"]
        prev_momentum = data[index - 1]["close"] - data[index - 1 - period]["close"] if index > period else momentum_val
        
        return {
            "bullish": momentum_val > 0 and momentum_val > prev_momentum,
            "bearish": momentum_val < 0 and momentum_val < prev_momentum,
            "value": momentum_val,
            "strength": abs(momentum_val) / data[index]["close"] * 100
        }
    
    def get_pine_script(self) -> str:
        period = self.config['period']
        return f"""// Momentum
momentum_value = ta.mom(close, {period})
momentum_bullish = momentum_value > 0 and momentum_value > momentum_value[1]
momentum_bearish = momentum_value < 0 and momentum_value < momentum_value[1]"""
