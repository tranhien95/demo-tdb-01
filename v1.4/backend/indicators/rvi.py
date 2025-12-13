"""
RVI - Relative Vigor Index
Measures conviction behind price moves
"""

from typing import List, Dict
from .base import BaseIndicator


class RVIIndicator(BaseIndicator):
    """Relative Vigor Index with customizable settings"""
    
    def default_config(self) -> Dict:
        return {
            'period': 10,
            'description': 'Relative Vigor Index'
        }
    
    def calculate(self, data: List[Dict], index: int, **kwargs) -> Dict:
        period = kwargs.get('period', self.config['period'])
        
        if index < period:
            return {"bullish": False, "bearish": False, "value": 50, "strength": 0, "signal_type": "NEUTRAL", "confidence": 0, "trend": "NEUTRAL", "reversal_signal": False, "divergence": False, "supporting_signals": [], "raw_values": {}}
        
        numerator, denominator = 0, 0
        for i in range(index - period + 1, index + 1):
            numerator += data[i]["close"] - data[i]["open"]
            denominator += data[i]["high"] - data[i]["low"]
        
        rvi_val = (numerator / denominator * 100) if denominator > 0 else 50
        
        # Calculate signal line (3-period SMA of RVI)
        rvi_values = []
        for i in range(max(0, index - period - 2), index + 1):
            num, denom = 0, 0
            start = max(0, i - period + 1)
            for j in range(start, i + 1):
                num += data[j]["close"] - data[j]["open"]
                denom += data[j]["high"] - data[j]["low"]
            rvi_values.append((num / denom * 100) if denom > 0 else 50)
        
        signal_val = sum(rvi_values[-3:]) / len(rvi_values[-3:]) if len(rvi_values) >= 3 else rvi_val
        
        # Close vs Open ratio
        close_open_ratio = (data[index]["close"] - data[index]["open"]) / (data[index]["high"] - data[index]["low"]) if (data[index]["high"] - data[index]["low"]) > 0 else 0
        
        # Detect signal line crossover
        rvi_signal_cross = False
        if index > 0:
            prev_rvi = rvi_values[-2] if len(rvi_values) >= 2 else rvi_val
            prev_signal = sum(rvi_values[-4:-1]) / len(rvi_values[-4:-1]) if len(rvi_values) >= 4 else prev_rvi
            rvi_signal_cross = (prev_rvi <= prev_signal and rvi_val > signal_val) or (prev_rvi >= prev_signal and rvi_val < signal_val)
        
        # Determine trend
        is_bullish = rvi_val > 50
        trend = "BULLISH_VIGOR" if rvi_val > 65 else ("BEARISH" if rvi_val < 35 else "NEUTRAL")
        
        # Signal type
        if rvi_val > 65:
            signal_type = "STRONG_BUY"
        elif rvi_val > 50:
            signal_type = "BUY"
        elif rvi_val < 35:
            signal_type = "STRONG_SELL"
        elif rvi_val < 50:
            signal_type = "SELL"
        else:
            signal_type = "NEUTRAL"
        
        strength = abs(50 - rvi_val) / 50 * 100
        
        return {
            "bullish": is_bullish,
            "bearish": not is_bullish,
            "value": rvi_val,
            "strength": strength,
            "signal_type": signal_type,
            "confidence": strength,
            "trend": trend,
            "reversal_signal": rvi_signal_cross,
            "divergence": False,
            "supporting_signals": [
                f"RVI: {rvi_val:.2f}",
                f"Signal: {signal_val:.2f}",
                f"Above signal: {'YES' if rvi_val > signal_val else 'NO'}",
                f"Vigor: {trend}",
                f"Close > Open: {'Strong' if close_open_ratio > 0.5 else 'Weak'}"
            ],
            "raw_values": {
                "rvi": rvi_val,
                "signal_line": signal_val,
                "rvi_signal_diff": rvi_val - signal_val,
                "close_open_ratio": close_open_ratio,
                "vigor_direction": "bullish" if is_bullish else "bearish"
            }
        }
    
    def get_pine_script(self) -> str:
        period = self.config['period']
        return f"""// RVI Indicator
rvi_value = ta.rvi({period})
rvi_bullish = rvi_value > 0
rvi_bearish = rvi_value < 0"""
