"""
Williams %R
Momentum oscillator measuring overbought/oversold levels
Similar to Stochastic but inverted scale
"""

from typing import List, Dict
from .base import BaseIndicator


class WilliamsRIndicator(BaseIndicator):
    """Williams %R Indicator"""
    
    def default_config(self) -> Dict:
        return {
            'period': 14,
            'overbought': -20,
            'oversold': -80,
            'extreme_overbought': -10,
            'extreme_oversold': -90,
            'description': 'Williams %R - Momentum oscillator'
        }
    
    def calculate(self, data: List[Dict], index: int, **kwargs) -> Dict:
        """Calculate Williams %R"""
        period = kwargs.get('period', self.config['period'])
        oversold = kwargs.get('oversold', self.config['oversold'])
        overbought = kwargs.get('overbought', self.config['overbought'])
        extreme_oversold = kwargs.get('extreme_oversold', self.config['extreme_oversold'])
        extreme_overbought = kwargs.get('extreme_overbought', self.config['extreme_overbought'])
        
        if index < period - 1:
            return self._empty_result()
        
        # Get high, low, close for the period
        period_data = data[index - period + 1:index + 1]
        highest_high = max([d["high"] for d in period_data])
        lowest_low = min([d["low"] for d in period_data])
        current_close = data[index]["close"]
        
        # Calculate Williams %R
        # Formula: %R = (Highest High - Close) / (Highest High - Lowest Low) * -100
        if highest_high == lowest_low:
            williams_r = -50  # Neutral when no range
        else:
            williams_r = ((highest_high - current_close) / (highest_high - lowest_low)) * -100
        
        # Determine signal type
        if williams_r < extreme_oversold:
            signal_type = "STRONG_BUY"
            signal_strength = 100
            is_bullish = True
        elif williams_r < oversold:
            signal_type = "BUY"
            signal_strength = 75
            is_bullish = True
        elif williams_r > extreme_overbought:
            signal_type = "STRONG_SELL"
            signal_strength = 100
            is_bullish = False
        elif williams_r > overbought:
            signal_type = "SELL"
            signal_strength = 75
            is_bullish = False
        else:
            signal_type = "NEUTRAL"
            signal_strength = abs(williams_r + 50) / 50 * 50
            is_bullish = False
        
        # Check for divergence (simplified)
        divergence = False
        if index >= period + 5:
            prev_period_data = data[index - period - 4:index - 4]
            prev_highest = max([d["high"] for d in prev_period_data])
            prev_lowest = min([d["low"] for d in prev_period_data])
            prev_close = data[index - 5]["close"]
            if prev_highest != prev_lowest:
                prev_wr = ((prev_highest - prev_close) / (prev_highest - prev_lowest)) * -100
                if (williams_r > prev_wr and current_close < data[index - 5]["close"]):
                    divergence = True  # Bullish divergence
                elif (williams_r < prev_wr and current_close > data[index - 5]["close"]):
                    divergence = True  # Bearish divergence
        
        return {
            "bullish": is_bullish,
            "bearish": not is_bullish,
            "value": round(williams_r, 2),
            "strength": signal_strength,
            "signal_type": signal_type,
            "confidence": min(abs(williams_r + 50), 50),
            "trend": "UPTREND" if williams_r < -50 else "DOWNTREND",
            "reversal_signal": williams_r < extreme_oversold or williams_r > extreme_overbought,
            "divergence": divergence,
            "supporting_signals": [
                f"Williams %R: {williams_r:.2f}",
                f"{'Overbought' if williams_r > overbought else 'Oversold' if williams_r < oversold else 'Neutral'}"
            ],
            "raw_values": {
                "williams_r": williams_r,
                "highest_high": highest_high,
                "lowest_low": lowest_low,
                "overbought": overbought,
                "oversold": oversold
            }
        }
    
    def _empty_result(self) -> Dict:
        """Return empty result"""
        return {
            "bullish": False,
            "bearish": False,
            "value": -50,
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
        oversold = self.config['oversold']
        overbought = self.config['overbought']
        
        return f"""// Williams %R Indicator
williams_r = ta.wpr({period})
williams_r_bullish = williams_r < {oversold}
williams_r_bearish = williams_r > {overbought}
williams_r_neutral = williams_r >= {oversold} and williams_r <= {overbought}"""

