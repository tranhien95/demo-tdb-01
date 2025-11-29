"""
ADX - Average Directional Index
Trend strength indicator
"""

from typing import List, Dict
from .base import BaseIndicator, HelperFunctions


class ADXIndicator(BaseIndicator):
    """ADX Indicator with customizable settings"""
    
    def default_config(self) -> Dict:
        return {
            'period': 14,
            'threshold': 25,
            'description': 'Average Directional Index - Trend strength'
        }
    
    def calculate(self, data: List[Dict], index: int, **kwargs) -> Dict:
        """Calculate ADX value and signals"""
        period = kwargs.get('period', self.config['period'])
        threshold = kwargs.get('threshold', self.config['threshold'])
        
        if index < period * 2:
            return {"bullish": False, "bearish": False, "value": 0, "strength": 0}
        
        plus_dm, minus_dm = 0, 0
        for i in range(index - period + 1, index + 1):
            up_move = data[i]["high"] - data[i - 1]["high"]
            down_move = data[i - 1]["low"] - data[i]["low"]
            
            if up_move > down_move and up_move > 0:
                plus_dm += up_move
            if down_move > up_move and down_move > 0:
                minus_dm += down_move
        
        atr_val = HelperFunctions.atr(data, index, period)
        plus_di = (plus_dm / atr_val * 100) if atr_val > 0 else 0
        minus_di = (minus_dm / atr_val * 100) if atr_val > 0 else 0
        adx_val = abs(plus_di - minus_di) / (plus_di + minus_di) * 100 if (plus_di + minus_di) > 0 else 0
        
        return {
            "bullish": plus_di > minus_di and adx_val > threshold,
            "bearish": minus_di > plus_di and adx_val > threshold,
            "value": adx_val,
            "strength": adx_val
        }
    
    def get_pine_script(self) -> str:
        """Generate Pine Script code"""
        period = self.config['period']
        threshold = self.config['threshold']
        
        return f"""// ADX Indicator
[plus_di, minus_di, adx_value] = ta.dmi({period}, {period})
adx_bullish = plus_di > minus_di and adx_value > {threshold}
adx_bearish = minus_di > plus_di and adx_value > {threshold}"""
