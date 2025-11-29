"""
MACD - Moving Average Convergence Divergence
Trend-following momentum indicator
"""

from typing import List, Dict
from .base import BaseIndicator, HelperFunctions


class MACDIndicator(BaseIndicator):
    """MACD Indicator with customizable settings"""
    
    def default_config(self) -> Dict:
        return {
            'fast_period': 12,
            'slow_period': 26,
            'signal_period': 9,
            'description': 'Moving Average Convergence Divergence'
        }
    
    def calculate(self, data: List[Dict], index: int, **kwargs) -> Dict:
        """Calculate MACD value and signals"""
        fast = kwargs.get('fast_period', self.config['fast_period'])
        slow = kwargs.get('slow_period', self.config['slow_period'])
        signal = kwargs.get('signal_period', self.config['signal_period'])
        
        if index < slow:
            return {"bullish": False, "bearish": False, "value": 0, "strength": 0}
        
        closes = [d["close"] for d in data[:index + 1]]
        ema_fast = HelperFunctions.ema(closes, fast)
        ema_slow = HelperFunctions.ema(closes, slow)
        
        macd_line = (ema_fast[index] or 0) - (ema_slow[index] or 0)
        
        macd_vals = []
        for i in range(len(closes)):
            if ema_fast[i] and ema_slow[i]:
                macd_vals.append(ema_fast[i] - ema_slow[i])
            else:
                macd_vals.append(None)
        
        signal_line_vals = HelperFunctions.ema([v for v in macd_vals if v is not None], signal)
        signal_val = signal_line_vals[-1] if signal_line_vals and signal_line_vals[-1] is not None else 0
        histogram = macd_line - signal_val
        
        return {
            "bullish": macd_line > signal_val and histogram > 0,
            "bearish": macd_line < signal_val and histogram < 0,
            "value": macd_line,
            "strength": abs(histogram) * 10
        }
    
    def get_pine_script(self) -> str:
        """Generate Pine Script code"""
        fast = self.config['fast_period']
        slow = self.config['slow_period']
        signal = self.config['signal_period']
        
        return f"""// MACD Indicator
[macd_line, signal_line, _] = ta.macd(close, {fast}, {slow}, {signal})
macd_bullish = macd_line > signal_line
macd_bearish = macd_line < signal_line"""
