"""
SuperTrend - Volatility-based trend indicator
Uses ATR to calculate dynamic support/resistance
"""

from typing import List, Dict
from .base import BaseIndicator, HelperFunctions


class SuperTrendIndicator(BaseIndicator):
    """SuperTrend Indicator with customizable settings"""
    
    def default_config(self) -> Dict:
        return {
            'period': 10,
            'multiplier': 3.0,
            'description': 'SuperTrend - Volatility-based trend indicator'
        }
    
    def calculate(self, data: List[Dict], index: int, **kwargs) -> Dict:
        period = kwargs.get('period', self.config['period'])
        multiplier = kwargs.get('multiplier', self.config['multiplier'])
        
        if index < period:
            return {"bullish": False, "bearish": False, "value": 0, "strength": 0}
        
        hl2 = (data[index]["high"] + data[index]["low"]) / 2
        atr_val = HelperFunctions.atr(data, index, period)
        
        basic_ub = hl2 + multiplier * atr_val
        basic_lb = hl2 - multiplier * atr_val
        
        final_ub = basic_ub
        final_lb = basic_lb
        
        if index > 0:
            prev_close = data[index - 1]["close"]
            if basic_ub < final_ub or prev_close > final_ub:
                final_ub = basic_ub
            if basic_lb > final_lb or prev_close < final_lb:
                final_lb = basic_lb
        
        supertrend_val = final_ub if data[index]["close"] <= final_ub else final_lb
        
        return {
            "bullish": data[index]["close"] > supertrend_val,
            "bearish": data[index]["close"] < supertrend_val,
            "value": supertrend_val,
            "strength": 50
        }
    
    def get_pine_script(self) -> str:
        period = self.config['period']
        multiplier = self.config['multiplier']
        return f"""// SuperTrend
[supertrend, direction] = ta.supertrend({multiplier}, {period})
st_bullish = direction < 0
st_bearish = direction > 0"""
