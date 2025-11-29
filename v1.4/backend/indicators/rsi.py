"""
RSI - Relative Strength Index
Momentum oscillator measuring speed and magnitude of price changes
"""

from typing import List, Dict
from .base import BaseIndicator


class RSIIndicator(BaseIndicator):
    """RSI Indicator with customizable settings"""
    
    def default_config(self) -> Dict:
        return {
            'period': 14,
            'overbought': 70,
            'oversold': 30,
            'description': 'Relative Strength Index - Momentum oscillator'
        }
    
    def calculate(self, data: List[Dict], index: int, **kwargs) -> Dict:
        """Calculate RSI value and signals"""
        period = kwargs.get('period', self.config['period'])
        oversold = kwargs.get('oversold', self.config['oversold'])
        overbought = kwargs.get('overbought', self.config['overbought'])
        
        if index < period:
            return {"bullish": False, "bearish": False, "value": 50, "strength": 0}
        
        gains, losses = 0, 0
        for i in range(index - period + 1, index + 1):
            change = data[i]["close"] - data[i - 1]["close"]
            if change > 0:
                gains += change
            else:
                losses -= change
        
        avg_gain = gains / period
        avg_loss = losses / period
        rs = avg_gain / avg_loss if avg_loss != 0 else 100
        rsi_val = 100 - (100 / (1 + rs))
        
        return {
            "bullish": rsi_val < oversold,
            "bearish": rsi_val > overbought,
            "value": rsi_val,
            "strength": abs(50 - rsi_val) / 50 * 100
        }
    
    def get_pine_script(self) -> str:
        """Generate Pine Script code"""
        period = self.config['period']
        oversold = self.config['oversold']
        overbought = self.config['overbought']
        
        return f"""// RSI Indicator
rsi_value = ta.rsi(close, {period})
rsi_bullish = rsi_value < {oversold}
rsi_bearish = rsi_value > {overbought}"""
