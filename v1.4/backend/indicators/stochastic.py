"""
Stochastic Oscillator
Momentum indicator comparing closing price to price range
"""

from typing import List, Dict
from .base import BaseIndicator


class StochasticIndicator(BaseIndicator):
    """Stochastic Oscillator with customizable settings"""
    
    def default_config(self) -> Dict:
        return {
            'period': 14,
            'overbought': 80,
            'oversold': 20,
            'description': 'Stochastic Oscillator'
        }
    
    def calculate(self, data: List[Dict], index: int, **kwargs) -> Dict:
        """Calculate Stochastic value and signals"""
        period = kwargs.get('period', self.config['period'])
        oversold = kwargs.get('oversold', self.config['oversold'])
        overbought = kwargs.get('overbought', self.config['overbought'])
        
        if index < period:
            return {"bullish": False, "bearish": False, "value": 50, "strength": 0}
        
        high = max(d["high"] for d in data[index - period + 1:index + 1])
        low = min(d["low"] for d in data[index - period + 1:index + 1])
        k = ((data[index]["close"] - low) / (high - low) * 100) if (high - low) != 0 else 50
        
        return {
            "bullish": k < oversold,
            "bearish": k > overbought,
            "value": k,
            "strength": abs(50 - k) / 50 * 100
        }
    
    def get_pine_script(self) -> str:
        """Generate Pine Script code"""
        period = self.config['period']
        oversold = self.config['oversold']
        overbought = self.config['overbought']
        
        return f"""// Stochastic Oscillator
k_value = ta.stoch(close, high, low, {period})
stoch_bullish = k_value < {oversold}
stoch_bearish = k_value > {overbought}"""
