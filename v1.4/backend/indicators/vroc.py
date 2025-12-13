"""
VROC - Volume Rate of Change
Measures volume momentum as percentage change
"""

from typing import List, Dict
from .base import BaseIndicator


class VROCIndicator(BaseIndicator):
    """Volume Rate of Change with customizable settings"""
    
    def default_config(self) -> Dict:
        return {
            'period': 14,
            'description': 'Volume Rate of Change'
        }
    
    def calculate(self, data: List[Dict], index: int, **kwargs) -> Dict:
        period = kwargs.get('period', self.config['period'])
        
        if index < period:
            return {"bullish": False, "bearish": False, "value": 0, "strength": 0, "signal_type": "NEUTRAL", "confidence": 0, "trend": "NEUTRAL", "reversal_signal": False, "divergence": False, "supporting_signals": [], "raw_values": {}}
        
        prev_vol = data[index - period]["volume"]
        vroc_val = ((data[index]["volume"] - prev_vol) / prev_vol) * 100 if prev_vol > 0 else 0
        
        # Calculate momentum acceleration
        momentum_accel = 0
        if index > period + 1:
            prev_vroc = ((data[index - 1]["volume"] - data[index - 1 - period]["volume"]) / data[index - 1 - period]["volume"] * 100) if data[index - 1 - period]["volume"] > 0 else 0
            momentum_accel = vroc_val - prev_vroc
        
        # Price momentum for correlation
        price_roc = 0
        if index >= period:
            price_roc = ((data[index]["close"] - data[index - period]["close"]) / data[index - period]["close"] * 100) if data[index - period]["close"] > 0 else 0
        
        # Price/Volume correlation
        price_volume_corr = "aligned" if (vroc_val > 0 and price_roc > 0) or (vroc_val < 0 and price_roc < 0) else "diverged"
        
        # Momentum trend
        momentum_trend = "ACCELERATING" if momentum_accel > 0 else ("DECELERATING" if momentum_accel < 0 else "NEUTRAL")
        
        # Determine signal
        is_bullish = vroc_val > 0
        strength = min(abs(vroc_val), 100)
        
        if abs(vroc_val) > 10:
            signal_type = "STRONG_BUY" if is_bullish else "STRONG_SELL"
        elif abs(vroc_val) > 5:
            signal_type = "BUY" if is_bullish else "SELL"
        else:
            signal_type = "NEUTRAL"
        
        return {
            "bullish": is_bullish,
            "bearish": not is_bullish,
            "value": vroc_val,
            "strength": strength,
            "signal_type": signal_type,
            "confidence": strength,
            "trend": momentum_trend,
            "reversal_signal": abs(momentum_accel) > abs(vroc_val) * 0.5,
            "divergence": price_volume_corr == "diverged",
            "supporting_signals": [
                f"VROC: {vroc_val:+.2f}%",
                f"Trend: {momentum_trend}",
                f"Momentum: {('Positive' if vroc_val > 0 else 'Negative')}",
                f"Volume backing: {price_volume_corr.upper()}"
            ],
            "raw_values": {
                "vroc": vroc_val,
                "vroc_momentum": momentum_accel,
                "volume_acceleration": momentum_accel,
                "price_volume_corr": price_volume_corr,
                "price_roc": price_roc
            }
        }
    
    def get_pine_script(self) -> str:
        period = self.config['period']
        return f"""// VROC Indicator
vroc_value = (volume - volume[{period}]) / volume[{period}] * 100
vroc_bullish = vroc_value > 0
vroc_bearish = vroc_value < 0"""
