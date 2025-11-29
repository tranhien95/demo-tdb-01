"""
Bollinger Bands
Volatility indicator with upper and lower bands
"""

from typing import List, Dict
import math
from .base import BaseIndicator


class BollingerBandsIndicator(BaseIndicator):
    """Bollinger Bands with customizable settings"""
    
    def default_config(self) -> Dict:
        return {
            'period': 20,
            'std_dev': 2,
            'description': 'Bollinger Bands - Volatility indicator'
        }
    
    def calculate(self, data: List[Dict], index: int, **kwargs) -> Dict:
        """Calculate Bollinger Bands value and signals"""
        period = kwargs.get('period', self.config['period'])
        std_dev = kwargs.get('std_dev', self.config['std_dev'])
        
        if index < period:
            return {"bullish": False, "bearish": False, "value": 0, "strength": 0}
        
        closes = [d["close"] for d in data[index - period + 1:index + 1]]
        mean = sum(closes) / period
        variance = sum((x - mean) ** 2 for x in closes) / period
        std = math.sqrt(variance)
        
        upper = mean + std_dev * std
        lower = mean - std_dev * std
        
        return {
            "bullish": data[index]["close"] < lower,
            "bearish": data[index]["close"] > upper,
            "value": mean,
            "strength": 50
        }
    
    def get_pine_script(self) -> str:
        """Generate Pine Script code"""
        period = self.config['period']
        std_dev = self.config['std_dev']
        
        return f"""// Bollinger Bands
[bb_middle, bb_upper, bb_lower] = ta.bb(close, {period}, {std_dev})
bb_bullish = close < bb_lower
bb_bearish = close > bb_upper"""
