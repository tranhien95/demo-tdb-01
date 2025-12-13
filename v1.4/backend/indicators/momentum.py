"""
Momentum Indicator
Measures price change over time
"""

from typing import List, Dict
from .base import BaseIndicator


class MomentumIndicator(BaseIndicator):
    """Momentum with customizable settings"""
    
    def default_config(self) -> Dict:
        return {
            'period': 10,
            'description': 'Momentum - Price momentum'
        }
    
    def calculate(self, data: List[Dict], index: int, **kwargs) -> Dict:
        period = kwargs.get('period', self.config['period'])
        
        if index < period:
            return {"bullish": False, "bearish": False, "value": 0, "strength": 0, "signal_type": "NEUTRAL", "confidence": 0, "trend": "NEUTRAL", "reversal_signal": False, "divergence": False, "supporting_signals": [], "raw_values": {}}
        
        momentum_val = data[index]["close"] - data[index - period]["close"]
        prev_momentum = data[index - 1]["close"] - data[index - 1 - period]["close"] if index > period else momentum_val
        momentum_pct = (momentum_val / data[index - period]["close"] * 100) if data[index - period]["close"] > 0 else 0
        
        # Detect momentum reversal
        momentum_reversal = (momentum_val > 0 and prev_momentum < 0) or (momentum_val < 0 and prev_momentum > 0)
        
        # Momentum strength classification
        if abs(momentum_pct) > 3:
            momentum_strength = "STRONG_MOMENTUM"
        elif abs(momentum_pct) > 1:
            momentum_strength = "WEAK_MOMENTUM"
        else:
            momentum_strength = "NEUTRAL"
        
        # Determine signal
        is_bullish = momentum_val > 0
        
        if momentum_strength == "STRONG_MOMENTUM":
            signal_type = "STRONG_BUY" if is_bullish else "STRONG_SELL"
        elif momentum_strength == "WEAK_MOMENTUM":
            signal_type = "BUY" if is_bullish else "SELL"
        else:
            signal_type = "NEUTRAL"
        
        strength = min(abs(momentum_pct), 100)
        
        return {
            "bullish": is_bullish and momentum_val > prev_momentum,
            "bearish": not is_bullish and momentum_val < prev_momentum,
            "value": momentum_val,
            "strength": strength,
            "signal_type": signal_type,
            "confidence": strength,
            "trend": momentum_strength,
            "reversal_signal": momentum_reversal,
            "divergence": False,
            "supporting_signals": [
                f"Momentum: {momentum_pct:+.2f}%",
                f"Strength: {momentum_strength}",
                f"Direction: {'Up and stable' if momentum_val > prev_momentum else ('Down and stable' if momentum_val < prev_momentum else 'Changing')}",
                f"Reversal risk: {'HIGH' if momentum_reversal else 'LOW'}"
            ],
            "raw_values": {
                "momentum": momentum_val,
                "momentum_strength": strength,
                "trend_consistency": abs(momentum_val) > abs(prev_momentum),
                "reversal_probability": 80 if momentum_reversal else 20
            }
        }
    
    def get_pine_script(self) -> str:
        period = self.config['period']
        return f"""// Momentum
momentum_value = ta.mom(close, {period})
momentum_bullish = momentum_value > 0 and momentum_value > momentum_value[1]
momentum_bearish = momentum_value < 0 and momentum_value < momentum_value[1]"""
