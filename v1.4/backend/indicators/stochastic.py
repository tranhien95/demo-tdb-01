"""
Stochastic Oscillator
Momentum indicator comparing closing price to price range with enhanced analysis
"""

from typing import List, Dict
from .base import BaseIndicator, HelperFunctions


class StochasticIndicator(BaseIndicator):
    """Stochastic Oscillator with comprehensive momentum analysis"""
    
    def default_config(self) -> Dict:
        return {
            'period': 14,
            'k_period': 3,
            'd_period': 3,
            'overbought': 80,
            'oversold': 20,
            'extreme_overbought': 90,
            'extreme_oversold': 10,
            'description': 'Stochastic Oscillator'
        }
    
    def calculate(self, data: List[Dict], index: int, **kwargs) -> Dict:
        """Calculate Stochastic with comprehensive signals"""
        period = kwargs.get('period', self.config['period'])
        k_period = kwargs.get('k_period', self.config['k_period'])
        overbought = kwargs.get('overbought', self.config['overbought'])
        oversold = kwargs.get('oversold', self.config['oversold'])
        extreme_overbought = kwargs.get('extreme_overbought', self.config['extreme_overbought'])
        extreme_oversold = kwargs.get('extreme_oversold', self.config['extreme_oversold'])
        
        if index < period:
            return self._empty_result()
        
        # Calculate %K (raw stochastic)
        high = max(d["high"] for d in data[index - period + 1:index + 1])
        low = min(d["low"] for d in data[index - period + 1:index + 1])
        k_raw = ((data[index]["close"] - low) / (high - low) * 100) if (high - low) != 0 else 50
        
        # Calculate smoothed %K
        k_values = []
        for i in range(max(0, index - k_period + 1), index + 1):
            if i >= period - 1:
                h = max(d["high"] for d in data[max(0, i - period + 1):i + 1])
                l = min(d["low"] for d in data[max(0, i - period + 1):i + 1])
                k = ((data[i]["close"] - l) / (h - l) * 100) if (h - l) != 0 else 50
                k_values.append(k)
        
        k_smooth = sum(k_values) / len(k_values) if k_values else k_raw
        
        # Determine signal type
        if k_smooth < extreme_oversold:
            signal_type = "STRONG_BUY"
            strength = 100
            is_bullish = True
        elif k_smooth < oversold:
            signal_type = "BUY"
            strength = 75
            is_bullish = True
        elif k_smooth > extreme_overbought:
            signal_type = "STRONG_SELL"
            strength = 100
            is_bullish = False
        elif k_smooth > overbought:
            signal_type = "SELL"
            strength = 75
            is_bullish = False
        else:
            signal_type = "NEUTRAL"
            strength = 50
            is_bullish = False
        
        # Check for reversal
        reversal = k_smooth < extreme_oversold or k_smooth > extreme_overbought
        
        return {
            "bullish": is_bullish,
            "bearish": not is_bullish,
            "value": round(k_smooth, 2),
            "strength": strength,
            "signal_type": signal_type,
            "confidence": abs(k_smooth - 50) / 50 * 100,
            "trend": "UPTREND" if k_smooth > 50 else "DOWNTREND",
            "reversal_signal": reversal,
            "divergence": False,
            "supporting_signals": [
                f"%K: {k_smooth:.2f}",
                f"Raw %K: {k_raw:.2f}",
                f"{'Overbought' if k_smooth > overbought else 'Oversold' if k_smooth < oversold else 'Neutral'}"
            ],
            "raw_values": {
                "k_smooth": k_smooth,
                "k_raw": k_raw,
                "high": high,
                "low": low,
                "overbought": overbought,
                "oversold": oversold
            }
        }
    
    def _empty_result(self) -> Dict:
        """Return empty result"""
        return {
            "bullish": False,
            "bearish": False,
            "value": 50,
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
        k_period = self.config['k_period']
        overbought = self.config['overbought']
        oversold = self.config['oversold']
        
        return f"""// Stochastic Oscillator
[k, d] = ta.stoch(close, high, low, {period})
k_smooth = ta.sma(k, {k_period})
stoch_bullish = k_smooth < {oversold}
stoch_bearish = k_smooth > {overbought}"""
