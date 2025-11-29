"""
ROC - Rate of Change
Measures price momentum as percentage change
"""

from typing import List, Dict
from .base import BaseIndicator


class ROCIndicator(BaseIndicator):
    """Rate of Change with customizable settings"""
    
    def default_config(self) -> Dict:
        return {
            'period': 12,
            'description': 'Rate of Change - Price momentum'
        }
    
    def calculate(self, data: List[Dict], index: int, **kwargs) -> Dict:
        period = kwargs.get('period', self.config['period'])
        
        if index < period:
            return {"bullish": False, "bearish": False, "value": 0, "strength": 0}
        
        prev_close = data[index - period]["close"]
        if prev_close == 0:
            return {"bullish": False, "bearish": False, "value": 0, "strength": 0}
        
        roc_val = ((data[index]["close"] - prev_close) / prev_close) * 100
        
        return {
            "bullish": roc_val > 0,
            "bearish": roc_val < 0,
            "value": roc_val,
            "strength": abs(roc_val)
        }
    
    def get_pine_script(self) -> str:
        period = self.config['period']
        return f"""// ROC Indicator
roc_value = ta.roc(close, {period})
roc_bullish = roc_value > 0
roc_bearish = roc_value < 0"""
