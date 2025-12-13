"""
MACD - Moving Average Convergence Divergence
Trend-following momentum indicator with enhanced analysis
"""

from typing import List, Dict
from .base import BaseIndicator, HelperFunctions


class MACDIndicator(BaseIndicator):
    """MACD Indicator with comprehensive trend analysis"""
    
    def default_config(self) -> Dict:
        return {
            'fast_period': 12,
            'slow_period': 26,
            'signal_period': 9,
            'description': 'Moving Average Convergence Divergence'
        }
    
    def calculate(self, data: List[Dict], index: int, **kwargs) -> Dict:
        """Calculate MACD with comprehensive signals"""
        fast = kwargs.get('fast_period', self.config['fast_period'])
        slow = kwargs.get('slow_period', self.config['slow_period'])
        signal = kwargs.get('signal_period', self.config['signal_period'])
        
        if index < slow:
            return self._empty_result()
        
        closes = [d["close"] for d in data[:index + 1]]
        ema_fast = HelperFunctions.ema(closes, fast)
        ema_slow = HelperFunctions.ema(closes, slow)
        
        # Calculate MACD line
        if ema_fast[index] is None or ema_slow[index] is None:
            return self._empty_result()
        
        macd_line = ema_fast[index] - ema_slow[index]
        
        # Calculate MACD values for signal line (keep index alignment)
        macd_vals = []
        for i in range(len(closes)):
            if ema_fast[i] is not None and ema_slow[i] is not None:
                macd_vals.append(ema_fast[i] - ema_slow[i])
            else:
                macd_vals.append(None)
        
        # Calculate signal line (EMA of MACD) - handle None values properly
        signal_line_vals = []
        multiplier = 2 / (signal + 1)
        
        for i in range(len(macd_vals)):
            if i < signal - 1:
                signal_line_vals.append(None)
            elif i == signal - 1:
                # First signal value: SMA of first signal MACD values
                first_vals = [v for v in macd_vals[i-signal+1:i+1] if v is not None]
                if len(first_vals) == signal:
                    signal_line_vals.append(sum(first_vals) / signal)
                else:
                    signal_line_vals.append(None)
            else:
                # EMA calculation
                if signal_line_vals[i-1] is not None and macd_vals[i] is not None:
                    signal_line_vals.append(
                        macd_vals[i] * multiplier + signal_line_vals[i-1] * (1 - multiplier)
                    )
                else:
                    signal_line_vals.append(None)
        
        signal_val = signal_line_vals[index] if signal_line_vals[index] is not None else 0
        histogram = macd_line - signal_val
        
        # Determine signal type based on histogram and line positions
        is_bullish = macd_line > signal_val
        histogram_positive = histogram > 0
        
        if is_bullish and histogram_positive:
            if index >= slow + signal and macd_vals[-signal - 1] and signal_line_vals[-signal - 1]:
                prev_histogram = macd_vals[index - signal] - signal_line_vals[-signal - 1]
                if prev_histogram < 0:
                    signal_type = "STRONG_BUY"  # Bullish crossover
                    strength = min(abs(histogram) * 100, 100)
                else:
                    signal_type = "BUY"
                    strength = min(abs(histogram) * 50, 75)
            else:
                signal_type = "BUY"
                strength = min(abs(histogram) * 50, 75)
        elif not is_bullish and not histogram_positive:
            signal_type = "SELL"
            strength = min(abs(histogram) * 50, 75)
        else:
            signal_type = "NEUTRAL"
            strength = min(abs(histogram) * 30, 50)
        
        # Trend determination
        if macd_line > signal_val > 0:
            trend = "UPTREND"
        elif macd_line < signal_val < 0:
            trend = "DOWNTREND"
        else:
            trend = "SIDEWAYS"
        
        return {
            "bullish": is_bullish,
            "bearish": not is_bullish,
            "value": round(macd_line, 4),
            "strength": strength,
            "signal_type": signal_type,
            "confidence": min(abs(histogram) * 100, 100),
            "trend": trend,
            "reversal_signal": abs(histogram) < 0.0001 and index >= slow + signal,  # Zero-line crossover
            "divergence": False,  # Would need price comparison
            "supporting_signals": [
                f"MACD: {macd_line:.4f}",
                f"Signal: {signal_val:.4f}",
                f"Histogram: {histogram:.4f}",
                f"{'Above' if histogram > 0 else 'Below'} signal line"
            ],
            "raw_values": {
                "macd_line": macd_line,
                "signal_line": signal_val,
                "histogram": histogram,
                "fast_ema": ema_fast[index] or 0,
                "slow_ema": ema_slow[index] or 0
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
        fast = self.config['fast_period']
        slow = self.config['slow_period']
        signal = self.config['signal_period']
        
        return f"""// MACD Indicator
[macd_line, signal_line, histogram] = ta.macd(close, {fast}, {slow}, {signal})
macd_bullish = macd_line > signal_line and histogram > 0
macd_bearish = macd_line < signal_line and histogram < 0
macd_neutral = macd_line == signal_line"""
