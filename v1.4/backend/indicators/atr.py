"""
ATR - Average True Range
Measures market volatility
"""

from typing import List, Dict
from .base import BaseIndicator, HelperFunctions


class ATRIndicator(BaseIndicator):
    """Average True Range with customizable settings"""
    
    def default_config(self) -> Dict:
        return {
            'period': 14,
            'threshold': 0.5,
            'description': 'Average True Range - Volatility measure'
        }
    
    def calculate(self, data: List[Dict], index: int, **kwargs) -> Dict:
        period = kwargs.get('period', self.config['period'])
        threshold = kwargs.get('threshold', self.config['threshold'])
        
        atr_val = HelperFunctions.atr(data, index, period)
        
        return {
            "bullish": atr_val > threshold,
            "bearish": False,
            "value": atr_val,
            "strength": min(atr_val * 10, 100)
        }
    
    def get_pine_script(self) -> str:
        period = self.config['period']
        return f"""// ATR Indicator
atr_value = ta.atr({period})
atr_high = atr_value > {self.config['threshold']}"""
