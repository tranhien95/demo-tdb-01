"""
ATR - Average True Range
Measures market volatility
"""

from typing import List, Dict
from .base import BaseIndicator, HelperFunctions


class ATRIndicator(BaseIndicator):
    """Average True Range with customizable settings"""
    
    def default_config(self) -> Dict:
        return {
            'period': 14,
            'threshold': 0.5,
            'description': 'Average True Range - Volatility measure'
        }
    
    def calculate(self, data: List[Dict], index: int, **kwargs) -> Dict:
        period = kwargs.get('period', self.config['period'])
        threshold = kwargs.get('threshold', self.config['threshold'])
        
        atr_val = HelperFunctions.atr(data, index, period)
        
        # Calculate ATR as percentage of price
        atr_percent = (atr_val / data[index]["close"] * 100) if data[index]["close"] > 0 else 0
        
        # Volatility classification
        if atr_percent > 3:
            volatility_level = "HIGH"
        elif atr_percent > 1.5:
            volatility_level = "MEDIUM"
        else:
            volatility_level = "LOW"
        
        # Volatility trend
        volatility_trend = "EXPANDING"
        if index > 1:
            prev_atr = HelperFunctions.atr(data, index - 1, period)
            prev_atr_pct = (prev_atr / data[index - 1]["close"] * 100) if data[index - 1]["close"] > 0 else 0
            if atr_percent < prev_atr_pct:
                volatility_trend = "CONTRACTING"
        
        # Volatility spike
        volatility_spike = atr_percent > 5
        
        # Stop-loss sizing (1.5x ATR typical)
        stop_loss_size = atr_val * 1.5
        
        # Recent average ATR
        recent_atr_vals = [HelperFunctions.atr(data, i, period) for i in range(max(0, index - 4), index + 1)]
        recent_atr_avg = sum(recent_atr_vals) / len(recent_atr_vals) if recent_atr_vals else atr_val
        
        # Determine signal
        is_bullish = atr_val > threshold
        
        if volatility_level == "HIGH":
            signal_type = "HIGH_VOLATILITY"
            confidence = min(atr_percent, 100)
        elif volatility_level == "MEDIUM":
            signal_type = "NORMAL"
            confidence = 50
        else:
            signal_type = "LOW_VOLATILITY"
            confidence = 30
        
        strength = min(atr_val * 10, 100)
        
        return {
            "bullish": is_bullish,
            "bearish": False,
            "value": atr_val,
            "strength": strength,
            "signal_type": signal_type,
            "confidence": confidence,
            "trend": volatility_trend,
            "reversal_signal": volatility_spike,
            "divergence": False,
            "supporting_signals": [
                f"ATR: {atr_val:.4f}",
                f"ATR%: {atr_percent:.2f}% ({'high' if atr_percent > 3 else ('medium' if atr_percent > 1.5 else 'normal')})",
                f"Volatility: {volatility_trend}",
                f"Risk unit: ${atr_val:.4f}",
                f"Spike: {'YES' if volatility_spike else 'NO'}"
            ],
            "raw_values": {
                "atr": atr_val,
                "atr_percent": atr_percent,
                "volatility_level": volatility_level,
                "volatility_trend": volatility_trend,
                "stop_loss_size": stop_loss_size,
                "recent_atr_avg": recent_atr_avg
            }
        }
    
    def get_pine_script(self) -> str:
        period = self.config['period']
        return f"""// ATR Indicator
atr_value = ta.atr({period})
atr_high = atr_value > {self.config['threshold']}"""
