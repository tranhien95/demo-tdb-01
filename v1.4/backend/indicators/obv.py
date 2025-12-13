"""
OBV - On Balance Volume
Cumulative volume indicator
"""

from typing import List, Dict
from .base import BaseIndicator


class OBVIndicator(BaseIndicator):
    """On Balance Volume with customizable settings"""
    
    def default_config(self) -> Dict:
        return {
            'description': 'On Balance Volume - Cumulative volume indicator'
        }
    
    def calculate(self, data: List[Dict], index: int, **kwargs) -> Dict:
        obv_val = 0
        for i in range(1, index + 1):
            if data[i]["close"] > data[i - 1]["close"]:
                obv_val += data[i]["volume"]
            elif data[i]["close"] < data[i - 1]["close"]:
                obv_val -= data[i]["volume"]
        
        prev_obv = 0
        if index > 1:
            for i in range(1, index):
                if data[i]["close"] > data[i - 1]["close"]:
                    prev_obv += data[i]["volume"]
                elif data[i]["close"] < data[i - 1]["close"]:
                    prev_obv -= data[i]["volume"]
        
        # Calculate OBV slope
        obv_slope = 0
        if index > 0:
            obv_slope = ((obv_val - prev_obv) / abs(prev_obv) * 100) if prev_obv != 0 else 0
        
        # Calculate OBV moving average
        obv_period = 20
        obv_values = []
        for i in range(1, min(index + 1, obv_period + 1)):
            obv_temp = 0
            for j in range(1, i + 1):
                if data[j]["close"] > data[j - 1]["close"]:
                    obv_temp += data[j]["volume"]
                elif data[j]["close"] < data[j - 1]["close"]:
                    obv_temp -= data[j]["volume"]
            obv_values.append(obv_temp)
        
        obv_ma = sum(obv_values[-obv_period:]) / len(obv_values[-obv_period:]) if obv_values else 0
        
        # Check price vs OBV divergence
        price_direction = 1 if data[index]["close"] > data[max(0, index - 5)]["close"] else -1
        obv_direction = 1 if obv_val > prev_obv else -1
        divergence = price_direction != obv_direction
        
        # Determine signal
        is_bullish = obv_val > prev_obv
        obv_strength = min(abs(obv_slope), 100)
        
        if obv_strength > 5:
            signal_type = "STRONG_BUY" if is_bullish else "STRONG_SELL"
        elif obv_strength > 2:
            signal_type = "BUY" if is_bullish else "SELL"
        else:
            signal_type = "NEUTRAL"
        
        # Trend classification
        trend = "VOLUME_INCREASING" if obv_slope > 0 else ("VOLUME_DECREASING" if obv_slope < 0 else "NEUTRAL")
        
        return {
            "bullish": is_bullish,
            "bearish": not is_bullish,
            "value": obv_val,
            "strength": min(obv_strength, 100),
            "signal_type": signal_type,
            "confidence": min(abs(obv_slope), 100),
            "trend": trend,
            "reversal_signal": divergence,
            "divergence": divergence,
            "supporting_signals": [
                f"OBV: {obv_val:,.0f}",
                f"OBV Slope: {obv_slope:+.2f}% per bar",
                f"Trend Confirmation: {'YES' if not divergence else 'NO (DIVERGENCE!)'}",
                f"Accumulation: {'Strong' if obv_val > obv_ma else 'Weak'}"
            ],
            "raw_values": {
                "obv": obv_val,
                "obv_slope": obv_slope,
                "obv_ma": obv_ma,
                "price_obv_divergence": divergence,
                "volume_strength": obv_strength
            }
        }
    
    def get_pine_script(self) -> str:
        return """// OBV Indicator
obv_value = ta.obv
obv_bullish = obv_value > obv_value[1]
obv_bearish = obv_value < obv_value[1]"""
