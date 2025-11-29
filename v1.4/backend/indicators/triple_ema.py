"""
Triple EMA - Three EMAs for trend analysis
Fast EMA crosses with Medium/Slow EMAs
"""

from typing import List, Dict
from .base import BaseIndicator, HelperFunctions


class TripleEMAIndicator(BaseIndicator):
    """Triple EMA with configurable periods"""
    
    def default_config(self) -> Dict:
        return {
            'fast_period': 5,
            'medium_period': 10,
            'slow_period': 20,
            'description': 'Triple EMA Crossover'
        }
    
    def calculate(self, data: List[Dict], index: int, **kwargs) -> Dict:
        """Calculate Triple EMA signals"""
        fast_period = kwargs.get('fast_period', self.config['fast_period'])
        medium_period = kwargs.get('medium_period', self.config['medium_period'])
        slow_period = kwargs.get('slow_period', self.config['slow_period'])
        
        closes = [d["close"] for d in data[:index + 1]]
        
        fast_ema = HelperFunctions.ema(closes, fast_period)
        medium_ema = HelperFunctions.ema(closes, medium_period)
        slow_ema = HelperFunctions.ema(closes, slow_period)
        
        if index < slow_period:
            return {
                "bullish": False,
                "bearish": False,
                "value": {"fast": None, "medium": None, "slow": None},
                "strength": 0
            }
        
        fast_val = fast_ema[index]
        medium_val = medium_ema[index]
        slow_val = slow_ema[index]
        
        # Bullish: Fast > Medium > Slow (uptrend alignment)
        bullish = fast_val > medium_val > slow_val
        
        # Bearish: Fast < Medium < Slow (downtrend alignment)
        bearish = fast_val < medium_val < slow_val
        
        # Crossover signals (stronger)
        prev_fast = fast_ema[index - 1] if index > 0 else fast_val
        prev_medium = medium_ema[index - 1] if index > 0 else medium_val
        
        bullish_cross = prev_fast <= prev_medium and fast_val > medium_val
        bearish_cross = prev_fast >= prev_medium and fast_val < medium_val
        
        # Strength based on EMA separation
        strength = 0
        if fast_val and medium_val and slow_val:
            spread = abs(fast_val - slow_val) / slow_val * 100
            strength = min(spread * 10, 100)  # Scale to 0-100
        
        return {
            "bullish": bullish or bullish_cross,
            "bearish": bearish or bearish_cross,
            "value": {
                "fast": fast_val,
                "medium": medium_val,
                "slow": slow_val,
                "bullish_cross": bullish_cross,
                "bearish_cross": bearish_cross
            },
            "strength": strength
        }
    
    def get_pine_script(self) -> str:
        """Generate Pine Script code"""
        fast = self.config['fast_period']
        medium = self.config['medium_period']
        slow = self.config['slow_period']
        
        return f"""// Triple EMA ({fast}, {medium}, {slow})
ema_fast = ta.ema(close, {fast})
ema_medium = ta.ema(close, {medium})
ema_slow = ta.ema(close, {slow})

triple_ema_bullish = ema_fast > ema_medium and ema_medium > ema_slow
triple_ema_bearish = ema_fast < ema_medium and ema_medium < ema_slow

// Crossover signals
bullish_cross = ta.crossover(ema_fast, ema_medium)
bearish_cross = ta.crossunder(ema_fast, ema_medium)

plot(ema_fast, "EMA {fast}", color=color.blue, linewidth=1)
plot(ema_medium, "EMA {medium}", color=color.orange, linewidth=1)
plot(ema_slow, "EMA {slow}", color=color.red, linewidth=2)"""
