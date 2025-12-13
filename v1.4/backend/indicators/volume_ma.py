"""
Volume MA - Volume Moving Average
Compares current volume to average
"""

from typing import List, Dict
from .base import BaseIndicator


class VolumeMaIndicator(BaseIndicator):
    """Volume Moving Average with customizable settings"""
    
    def default_config(self) -> Dict:
        return {
            'period': 20,
            'volume_multiplier': 1.2,
            'description': 'Volume Moving Average'
        }
    
    def calculate(self, data: List[Dict], index: int, **kwargs) -> Dict:
        period = kwargs.get('period', self.config['period'])
        multiplier = kwargs.get('volume_multiplier', self.config['volume_multiplier'])
        
        if index < period:
            return {"bullish": False, "bearish": False, "value": 0, "strength": 0, "signal_type": "NEUTRAL", "confidence": 0, "trend": "NEUTRAL", "reversal_signal": False, "divergence": False, "supporting_signals": [], "raw_values": {}}
        
        vol_ma = sum(d["volume"] for d in data[index - period + 1:index + 1]) / period
        current_vol = data[index]["volume"]
        
        # Calculate volume percent above/below average
        vol_percent = ((current_vol - vol_ma) / vol_ma * 100) if vol_ma > 0 else 0
        
        # Spike detection (volume > 150% of MA)
        spike_threshold = vol_ma * 1.5
        spike_detected = current_vol > spike_threshold
        
        # Volume trend
        volume_trend = "HIGH_VOLUME" if current_vol > vol_ma * multiplier else ("LOW_VOLUME" if current_vol < vol_ma / multiplier else "NORMAL")
        
        # Determine signal
        is_bullish = current_vol > vol_ma * multiplier
        
        if spike_detected:
            signal_type = "HIGH_VOLUME" if is_bullish else "SPIKE"
            confidence = min(vol_percent, 100)
        elif is_bullish:
            signal_type = "BUY"
            confidence = min(vol_percent / multiplier * 100, 100)
        elif current_vol < vol_ma / multiplier:
            signal_type = "SELL"
            confidence = min(abs(vol_percent) / multiplier * 100, 100)
        else:
            signal_type = "NEUTRAL"
            confidence = 50
        
        # Check for volume trend change
        vol_trend_change = False
        if index > 5:
            recent_avg = sum(d["volume"] for d in data[index - 5:index + 1]) / 6
            older_avg = sum(d["volume"] for d in data[max(0, index - 10):index - 5]) / min(5, index - 4) if index >= 10 else vol_ma
            vol_trend_change = (current_vol > recent_avg) != (recent_avg > older_avg)
        
        return {
            "bullish": is_bullish,
            "bearish": current_vol < vol_ma / multiplier,
            "value": vol_ma,
            "strength": confidence,
            "signal_type": signal_type,
            "confidence": confidence,
            "trend": volume_trend,
            "reversal_signal": spike_detected or vol_trend_change,
            "divergence": False,
            "supporting_signals": [
                f"Current Volume: {current_vol:,.0f}",
                f"Average: {vol_ma:,.0f}",
                f"Above Average: {vol_percent:+.1f}%",
                f"Spike detected: {'YES' if spike_detected else 'NO'}",
                f"Strength: {volume_trend}"
            ],
            "raw_values": {
                "current_volume": current_vol,
                "volume_ma": vol_ma,
                "volume_percent": vol_percent,
                "spike_threshold": spike_threshold,
                "spike_detected": spike_detected,
                "volume_trend": volume_trend
            }
        }
    
    def get_pine_script(self) -> str:
        period = self.config['period']
        return f"""// Volume MA
vol_ma = ta.sma(volume, {period})
vol_bullish = volume > vol_ma * {self.config['volume_multiplier']}
vol_bearish = volume < vol_ma / {self.config['volume_multiplier']}"""
