"""
Bollinger Bands
Volatility indicator with upper and lower bands and squeeze detection
"""

from typing import List, Dict
import math
from .base import BaseIndicator


class BollingerBandsIndicator(BaseIndicator):
    """Bollinger Bands with comprehensive volatility analysis"""
    
    def default_config(self) -> Dict:
        return {
            'period': 20,
            'std_dev': 2,
            'description': 'Bollinger Bands - Volatility indicator'
        }
    
    def calculate(self, data: List[Dict], index: int, **kwargs) -> Dict:
        """Calculate Bollinger Bands with comprehensive signals"""
        period = kwargs.get('period', self.config['period'])
        std_dev = kwargs.get('std_dev', self.config['std_dev'])
        
        if index < period:
            return self._empty_result()
        
        closes = [d["close"] for d in data[index - period + 1:index + 1]]
        mean = sum(closes) / period
        variance = sum((x - mean) ** 2 for x in closes) / period
        std = math.sqrt(variance)
        
        upper = mean + std_dev * std
        lower = mean - std_dev * std
        band_width = upper - lower
        close = data[index]["close"]
        
        # Calculate position in bands (0=lower, 100=upper)
        if band_width > 0:
            position = ((close - lower) / band_width) * 100
        else:
            position = 50
        
        # Check for squeeze (bands getting tight)
        squeeze = False
        if index >= period + 10:
            prev_closes = [d["close"] for d in data[index - period - 10:index - 10]]
            prev_mean = sum(prev_closes) / period
            prev_variance = sum((x - prev_mean) ** 2 for x in prev_closes) / period
            prev_std = math.sqrt(prev_variance)
            prev_band_width = (prev_mean + std_dev * prev_std) - (prev_mean - std_dev * prev_std)
            squeeze = band_width < prev_band_width * 0.8
        
        # Determine signal type
        if close < lower:
            signal_type = "STRONG_BUY"
            strength = 100
            is_bullish = True
        elif close < mean and position < 30:
            signal_type = "BUY"
            strength = 75
            is_bullish = True
        elif close > upper:
            signal_type = "STRONG_SELL"
            strength = 100
            is_bullish = False
        elif close > mean and position > 70:
            signal_type = "SELL"
            strength = 75
            is_bullish = False
        else:
            signal_type = "NEUTRAL"
            strength = 50
            is_bullish = False
        
        # Volatility trend
        if band_width > mean * 0.1:
            volatility = "HIGH"
        elif band_width < mean * 0.03:
            volatility = "LOW"
        else:
            volatility = "MEDIUM"
        
        return {
            "bullish": is_bullish,
            "bearish": not is_bullish,
            "value": round(mean, 2),
            "strength": strength,
            "signal_type": signal_type,
            "confidence": min(abs(position - 50) / 50 * 100, 100),
            "trend": "UPTREND" if position > 50 else "DOWNTREND",
            "reversal_signal": (close < lower or close > upper),
            "divergence": squeeze,  # Squeeze can lead to breakout
            "supporting_signals": [
                f"Position: {position:.1f}%",
                f"Volatility: {volatility}",
                f"Band Width: {band_width:.2f}",
                f"{'Squeeze detected' if squeeze else 'Normal volatility'}"
            ],
            "raw_values": {
                "upper_band": upper,
                "middle_band": mean,
                "lower_band": lower,
                "band_width": band_width,
                "position_percent": position,
                "volatility": volatility,
                "squeeze": squeeze
            }
        }
    
    def _empty_result(self) -> Dict:
        """Return empty result"""
        return {
            "bullish": False,
            "bearish": False,
            "value": 0,
            "strength": 0,
            "signal_type": "NEUTRAL",
            "confidence": 0,
            "trend": "SIDEWAYS",
            "reversal_signal": False,
            "divergence": False,
            "supporting_signals": [],
            "raw_values": {}
        }
    
    def get_pine_script(self) -> str:
        """Generate Pine Script code"""
        period = self.config['period']
        std_dev = self.config['std_dev']
        
        return f"""// Bollinger Bands
[bb_middle, bb_upper, bb_lower] = ta.bb(close, {period}, {std_dev})
bb_bullish = close < bb_lower
bb_bearish = close > bb_upper
bb_squeeze = (bb_upper - bb_lower) < (ta.highest(bb_upper - bb_lower, {period} * 2) * 0.8)"""
