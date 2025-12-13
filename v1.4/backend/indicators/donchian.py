"""
Donchian Channel
Price channel breakout indicator
"""

from typing import List, Dict
from .base import BaseIndicator


class DonchianIndicator(BaseIndicator):
    """Donchian Channel with customizable settings"""
    
    def default_config(self) -> Dict:
        return {
            'period': 20,
            'description': 'Donchian Channel - Breakout indicator'
        }
    
    def calculate(self, data: List[Dict], index: int, **kwargs) -> Dict:
        period = kwargs.get('period', self.config['period'])
        
        if index < period:
            return {"bullish": False, "bearish": False, "value": 0, "strength": 0, "signal_type": "NEUTRAL", "confidence": 0, "trend": "NEUTRAL", "reversal_signal": False, "divergence": False, "supporting_signals": [], "raw_values": {}}
        
        high = max(d["high"] for d in data[index - period + 1:index + 1])
        low = min(d["low"] for d in data[index - period + 1:index + 1])
        mid = (high + low) / 2
        
        current_price = data[index]["close"]
        band_width = high - low
        
        # Position in band (0-100%)
        position_percent = ((current_price - low) / band_width * 100) if band_width > 0 else 50
        
        # Previous band width for squeeze detection
        if index >= period * 2:
            prev_high = max(d["high"] for d in data[index - period * 2 + 1:index - period + 1])
            prev_low = min(d["low"] for d in data[index - period * 2 + 1:index - period + 1])
            prev_band_width = prev_high - prev_low
            squeeze_level = band_width / prev_band_width if prev_band_width > 0 else 1
            squeeze = squeeze_level < 0.8  # Bands compressed to 80% of previous width
        else:
            squeeze = False
        
        # Breakout detection
        breakout = False
        breakout_direction = "NONE"
        if index > 0:
            prev_price = data[index - 1]["close"]
            if current_price > high:
                breakout = True
                breakout_direction = "UP"
            elif current_price < low:
                breakout = True
                breakout_direction = "DOWN"
        
        # Determine signal
        is_bullish = current_price > mid
        
        if breakout:
            signal_type = "BREAKOUT" if breakout_direction == "UP" else "BREAKDOWN"
            confidence = min(abs(current_price - high if breakout_direction == "UP" else current_price - low) / band_width * 100, 100)
        elif squeeze:
            signal_type = "SQUEEZE"
            confidence = 70
        else:
            signal_type = "NORMAL"
            confidence = min(position_percent if is_bullish else 100 - position_percent, 100)
        
        # Trend
        trend = "EXPANDING_UP" if (position_percent > 50 and not squeeze) else ("EXPANDING_DOWN" if (position_percent < 50 and not squeeze) else ("CONTRACTING" if squeeze else "NEUTRAL"))
        
        strength = confidence
        
        return {
            "bullish": is_bullish,
            "bearish": not is_bullish,
            "value": mid,
            "strength": strength,
            "signal_type": signal_type,
            "confidence": confidence,
            "trend": trend,
            "reversal_signal": breakout,
            "divergence": squeeze,
            "supporting_signals": [
                f"Upper: {high:.2f}",
                f"Lower: {low:.2f}",
                f"Width: {band_width:.2f} ({'normal' if not squeeze else 'SQUEEZED!'})",
                f"Position: {position_percent:.0f}% ({'mid-high' if position_percent > 60 else ('mid-low' if position_percent < 40 else 'middle')})",
                f"Status: {'Breakout imminent' if squeeze else ('BREAKOUT!' if breakout else 'Trading normally')}"
            ],
            "raw_values": {
                "upper_band": high,
                "lower_band": low,
                "band_width": band_width,
                "position_percent": position_percent,
                "squeeze_level": squeeze,
                "breakout_potential": breakout_direction,
                "breakout_confirmation": breakout
            }
        }
    
    def get_pine_script(self) -> str:
        period = self.config['period']
        return f"""// Donchian Channel
donchian_high = ta.highest(high, {period})
donchian_low = ta.lowest(low, {period})
donchian_mid = (donchian_high + donchian_low) / 2
donchian_bullish = close > donchian_mid
donchian_bearish = close < donchian_mid"""
