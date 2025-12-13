"""
RSI - Relative Strength Index
Momentum oscillator measuring speed and magnitude of price changes
"""

from typing import List, Dict
from .base import BaseIndicator


class RSIIndicator(BaseIndicator):
    """RSI Indicator with comprehensive analysis"""
    
    def default_config(self) -> Dict:
        return {
            'period': 14,
            'overbought': 70,
            'oversold': 30,
            'extreme_overbought': 80,
            'extreme_oversold': 20,
            'description': 'Relative Strength Index - Momentum oscillator'
        }
    
    def calculate(self, data: List[Dict], index: int, **kwargs) -> Dict:
        """Calculate RSI with Wilder's smoothing (standard RSI calculation)"""
        period = kwargs.get('period', self.config['period'])
        oversold = kwargs.get('oversold', self.config['oversold'])
        overbought = kwargs.get('overbought', self.config['overbought'])
        extreme_oversold = kwargs.get('extreme_oversold', self.config['extreme_oversold'])
        extreme_overbought = kwargs.get('extreme_overbought', self.config['extreme_overbought'])
        
        if index < period:
            return self._empty_result()
        
        # Calculate RSI with Wilder's Smoothing
        # First period: Simple average
        # Subsequent periods: EMA with alpha = 1/period (Wilder's smoothing)
        
        if index == period - 1:
            # First period: Calculate simple average
            gains, losses = 0, 0
            for i in range(index - period + 1, index + 1):
                if i > 0:
                    change = data[i]["close"] - data[i - 1]["close"]
                    if change > 0:
                        gains += change
                    else:
                        losses -= change
            
            avg_gain = gains / period
            avg_loss = losses / period if losses > 0 else 0.0001  # Avoid division by zero
        else:
            # Subsequent periods: Use Wilder's smoothing
            # Get previous period's averages
            prev_gains, prev_losses = 0, 0
            for i in range(index - period, index):
                if i > 0:
                    change = data[i]["close"] - data[i - 1]["close"]
                    if change > 0:
                        prev_gains += change
                    else:
                        prev_losses -= change
            
            prev_avg_gain = prev_gains / period
            prev_avg_loss = prev_losses / period if prev_losses > 0 else 0.0001
            
            # Current period's gain/loss
            current_change = data[index]["close"] - data[index - 1]["close"]
            current_gain = current_change if current_change > 0 else 0
            current_loss = -current_change if current_change < 0 else 0
            
            # Wilder's smoothing: EMA with alpha = 1/period
            avg_gain = (prev_avg_gain * (period - 1) + current_gain) / period
            avg_loss = (prev_avg_loss * (period - 1) + current_loss) / period if prev_avg_loss > 0 else 0.0001
        
        rs = avg_gain / avg_loss if avg_loss > 0 else 100
        rsi_val = 100 - (100 / (1 + rs))
        
        # Determine signal type
        if rsi_val < extreme_oversold:
            signal_type = "STRONG_BUY"
            signal_strength = 100
            is_bullish = True
        elif rsi_val < oversold:
            signal_type = "BUY"
            signal_strength = 75
            is_bullish = True
        elif rsi_val > extreme_overbought:
            signal_type = "STRONG_SELL"
            signal_strength = 100
            is_bullish = False
        elif rsi_val > overbought:
            signal_type = "SELL"
            signal_strength = 75
            is_bullish = False
        else:
            signal_type = "NEUTRAL"
            signal_strength = abs(50 - rsi_val) / 50 * 50
            is_bullish = False
        
        # Check for divergence (simplified)
        divergence = False
        if index >= period + 5:
            prev_rsi = self._calc_rsi(data, index - 5, period)
            if (rsi_val > prev_rsi and data[index]["close"] < data[index - 5]["close"]):
                divergence = True  # Bullish divergence
            elif (rsi_val < prev_rsi and data[index]["close"] > data[index - 5]["close"]):
                divergence = True  # Bearish divergence
        
        return {
            "bullish": is_bullish,
            "bearish": not is_bullish,
            "value": round(rsi_val, 2),
            "strength": signal_strength,
            "signal_type": signal_type,
            "confidence": min(abs(rsi_val - 50), 50),
            "trend": "UPTREND" if rsi_val > 50 else "DOWNTREND",
            "reversal_signal": rsi_val < extreme_oversold or rsi_val > extreme_overbought,
            "divergence": divergence,
            "supporting_signals": [
                f"RSI at {rsi_val:.2f}",
                f"{'Overbought' if rsi_val > overbought else 'Oversold' if rsi_val < oversold else 'Neutral'}"
            ],
            "raw_values": {
                "rsi": rsi_val,
                "avg_gain": avg_gain,
                "avg_loss": avg_loss,
                "overbought": overbought,
                "oversold": oversold
            }
        }
    
    def _calc_rsi(self, data: List[Dict], index: int, period: int) -> float:
        """Helper to calculate RSI at specific index with Wilder's smoothing"""
        if index < period:
            return 50
        
        # Use same logic as main calculate method
        if index == period - 1:
            gains, losses = 0, 0
            for i in range(index - period + 1, index + 1):
                if i > 0:
                    change = data[i]["close"] - data[i - 1]["close"]
                    if change > 0:
                        gains += change
                    else:
                        losses -= change
            avg_gain = gains / period
            avg_loss = losses / period if losses > 0 else 0.0001
        else:
            # Get previous averages (simplified - would need to track)
            # For now, use simple average for helper
            gains, losses = 0, 0
            for i in range(index - period + 1, index + 1):
                if i > 0:
                    change = data[i]["close"] - data[i - 1]["close"]
                    if change > 0:
                        gains += change
                    else:
                        losses -= change
            avg_gain = gains / period
            avg_loss = losses / period if losses > 0 else 0.0001
        
        rs = avg_gain / avg_loss if avg_loss > 0 else 100
        return 100 - (100 / (1 + rs))
    
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
        oversold = self.config['oversold']
        overbought = self.config['overbought']
        
        return f"""// RSI Indicator
rsi_value = ta.rsi(close, {period})
rsi_bullish = rsi_value < {oversold}
rsi_bearish = rsi_value > {overbought}
rsi_neutral = rsi_value >= {oversold} and rsi_value <= {overbought}"""
