"""
EMA - Exponential Moving Average
Trend indicator giving more weight to recent prices
"""

from typing import List, Dict
from .base import BaseIndicator, HelperFunctions


class EMAIndicator(BaseIndicator):
    """EMA Indicator with customizable period"""
    
    def default_config(self) -> Dict:
        return {
            'period': 50,
            'description': 'Exponential Moving Average'
        }
    
    def calculate(self, data: List[Dict], index: int, **kwargs) -> Dict:
        """Calculate EMA value and signals"""
        period = kwargs.get('period', self.config['period'])
        
        closes = [d["close"] for d in data[:index + 1]]
        ema_vals = HelperFunctions.ema(closes, period)
        ema_val = ema_vals[index] if ema_vals[index] is not None else data[index]["close"]
        
        return {
            "bullish": data[index]["close"] > ema_val,
            "bearish": data[index]["close"] < ema_val,
            "value": ema_val,
            "strength": abs(data[index]["close"] - ema_val) / ema_val * 100
        }
    
    def get_pine_script(self) -> str:
        """Generate Pine Script code"""
        period = self.config['period']
        
        return f"""// EMA {period} Indicator
ema_{period} = ta.ema(close, {period})
ema{period}_bullish = close > ema_{period}
ema{period}_bearish = close < ema_{period}"""


class EMA50Indicator(EMAIndicator):
    """EMA 50 - Pre-configured"""
    
    def default_config(self) -> Dict:
        return {
            'period': 50,
            'description': 'Exponential Moving Average 50'
        }


class EMA200Indicator(EMAIndicator):
    """EMA 200 - Pre-configured"""
    
    def default_config(self) -> Dict:
        return {
            'period': 200,
            'description': 'Exponential Moving Average 200'
        }


class EMA12Indicator(EMAIndicator):
    """EMA 12 - Pre-configured"""
    
    def default_config(self) -> Dict:
        return {
            'period': 12,
            'description': 'Exponential Moving Average 12'
        }


class EMA26Indicator(EMAIndicator):
    """EMA 26 - Pre-configured"""
    
    def default_config(self) -> Dict:
        return {
            'period': 26,
            'description': 'Exponential Moving Average 26'
        }
