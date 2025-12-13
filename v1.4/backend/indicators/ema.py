"""
EMA - Exponential Moving Average
Trend indicator giving more weight to recent prices
"""

from typing import List, Dict
from .base import BaseIndicator, HelperFunctions


class EMAIndicator(BaseIndicator):
    """EMA Indicator with customizable period"""
    
    def default_config(self) -> Dict:
        return {
            'period': 50,
            'description': 'Exponential Moving Average'
        }
    
    def calculate(self, data: List[Dict], index: int, **kwargs) -> Dict:
        """Calculate EMA value and signals"""
        period = kwargs.get('period', self.config['period'])
        
        closes = [d["close"] for d in data[:index + 1]]
        ema_vals = HelperFunctions.ema(closes, period)
        ema_val = ema_vals[index] if ema_vals[index] is not None else data[index]["close"]
        
        current_price = data[index]["close"]
        distance_percent = abs(current_price - ema_val) / ema_val * 100
        
        # Calculate EMA slope
        slope = 0
        if index > 0:
            prev_ema = ema_vals[index - 1] if ema_vals[index - 1] is not None else data[index - 1]["close"]
            slope = ((ema_val - prev_ema) / prev_ema * 100) if prev_ema > 0 else 0
        
        # Determine signal type based on distance and slope
        if current_price > ema_val:
            if distance_percent > 3:
                signal_type = "STRONG_BUY" if slope > 0 else "BUY"
            elif distance_percent > 1:
                signal_type = "BUY"
            else:
                signal_type = "NEUTRAL"
        elif current_price < ema_val:
            if distance_percent > 3:
                signal_type = "STRONG_SELL" if slope < 0 else "SELL"
            elif distance_percent > 1:
                signal_type = "SELL"
            else:
                signal_type = "NEUTRAL"
        else:
            signal_type = "NEUTRAL"
        
        # Check for crossover (reversal signal)
        crossover = False
        if index > 0:
            prev_price = data[index - 1]["close"]
            prev_ema = ema_vals[index - 1] if ema_vals[index - 1] is not None else data[index - 1]["close"]
            crossover = (prev_price <= prev_ema and current_price > ema_val) or (prev_price >= prev_ema and current_price < ema_val)
        
        # Trend classification
        trend = "UPTREND" if current_price > ema_val else ("DOWNTREND" if current_price < ema_val else "NEUTRAL")
        
        # Check for slope flattening (potential reversal)
        slope_flattening = False
        if index > 2:
            prev_slope = ((ema_vals[index - 1] - ema_vals[index - 2]) / ema_vals[index - 2] * 100) if ema_vals[index - 2] else 0
            slope_flattening = abs(slope) < abs(prev_slope) * 0.5
        
        confidence = min(distance_percent, 100)
        
        return {
            "bullish": current_price > ema_val,
            "bearish": current_price < ema_val,
            "value": ema_val,
            "strength": confidence,
            "signal_type": signal_type,
            "confidence": confidence,
            "trend": trend,
            "reversal_signal": crossover,
            "divergence": slope_flattening,
            "supporting_signals": [
                f"Price: {current_price:.2f}",
                f"EMA{period}: {ema_val:.2f}",
                f"Distance: {distance_percent:.2f}% ({'above' if current_price > ema_val else 'below'})",
                f"Slope: {slope:+.4f}% {'(increasing)' if slope > 0 else '(decreasing)' if slope < 0 else '(flat)'}"  + (" - Trend possible reversal" if slope_flattening else "")
            ],
            "raw_values": {
                "ema_value": ema_val,
                "ema_slope": slope,
                "distance_percent": distance_percent,
                "price_above_ema": current_price > ema_val,
                "slope_direction": "up" if slope > 0 else ("down" if slope < 0 else "flat")
            }
        }
    
    def get_pine_script(self) -> str:
        """Generate Pine Script code"""
        period = self.config['period']
        
        return f"""// EMA {period} Indicator
ema_{period} = ta.ema(close, {period})
ema{period}_bullish = close > ema_{period}
ema{period}_bearish = close < ema_{period}"""


class EMA50Indicator(EMAIndicator):
    """EMA 50 - Pre-configured"""
    
    def default_config(self) -> Dict:
        return {
            'period': 50,
            'description': 'Exponential Moving Average 50'
        }


class EMA200Indicator(EMAIndicator):
    """EMA 200 - Pre-configured"""
    
    def default_config(self) -> Dict:
        return {
            'period': 200,
            'description': 'Exponential Moving Average 200'
        }


class EMA12Indicator(EMAIndicator):
    """EMA 12 - Pre-configured"""
    
    def default_config(self) -> Dict:
        return {
            'period': 12,
            'description': 'Exponential Moving Average 12'
        }


class EMA26Indicator(EMAIndicator):
    """EMA 26 - Pre-configured"""
    
    def default_config(self) -> Dict:
        return {
            'period': 26,
            'description': 'Exponential Moving Average 26'
        }
