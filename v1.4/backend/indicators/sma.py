"""
SMA - Simple Moving Average
Trend indicator using arithmetic mean of prices
"""

from typing import List, Dict
from .base import BaseIndicator, HelperFunctions


class SMAIndicator(BaseIndicator):
    """SMA Indicator with customizable period"""
    
    def default_config(self) -> Dict:
        return {
            'period': 50,
            'description': 'Simple Moving Average'
        }
    
    def calculate(self, data: List[Dict], index: int, **kwargs) -> Dict:
        """Calculate SMA value and signals"""
        period = kwargs.get('period', self.config['period'])
        
        if index < period - 1:
            return self._empty_result()
        
        closes = [d["close"] for d in data[index - period + 1:index + 1]]
        sma_val = sum(closes) / period
        
        current_price = data[index]["close"]
        distance_percent = abs(current_price - sma_val) / sma_val * 100 if sma_val > 0 else 0
        
        # Calculate SMA slope
        slope = 0
        if index >= period:
            prev_closes = [d["close"] for d in data[index - period:index]]
            prev_sma = sum(prev_closes) / period
            slope = ((sma_val - prev_sma) / prev_sma * 100) if prev_sma > 0 else 0
        
        # Determine signal type based on distance and slope
        if current_price > sma_val:
            if distance_percent > 3:
                signal_type = "STRONG_BUY" if slope > 0 else "BUY"
            elif distance_percent > 1:
                signal_type = "BUY"
            else:
                signal_type = "NEUTRAL"
        elif current_price < sma_val:
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
        if index >= period:
            prev_price = data[index - 1]["close"]
            prev_closes = [d["close"] for d in data[index - period:index]]
            prev_sma = sum(prev_closes) / period
            crossover = (prev_price <= prev_sma and current_price > sma_val) or (prev_price >= prev_sma and current_price < sma_val)
        
        # Trend classification
        trend = "UPTREND" if current_price > sma_val else ("DOWNTREND" if current_price < sma_val else "NEUTRAL")
        
        confidence = min(distance_percent, 100)
        
        return {
            "bullish": current_price > sma_val,
            "bearish": current_price < sma_val,
            "value": round(sma_val, 2),
            "strength": confidence,
            "signal_type": signal_type,
            "confidence": confidence,
            "trend": trend,
            "reversal_signal": crossover,
            "divergence": False,
            "supporting_signals": [
                f"Price: {current_price:.2f}",
                f"SMA{period}: {sma_val:.2f}",
                f"Distance: {distance_percent:.2f}% ({'above' if current_price > sma_val else 'below'})",
                f"Slope: {slope:+.4f}%"
            ],
            "raw_values": {
                "sma_value": sma_val,
                "sma_slope": slope,
                "distance_percent": distance_percent,
                "price_above_sma": current_price > sma_val
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
        
        return f"""// SMA {period} Indicator
sma_{period} = ta.sma(close, {period})
sma{period}_bullish = close > sma_{period}
sma{period}_bearish = close < sma_{period}"""


class SMA50Indicator(SMAIndicator):
    """SMA 50 - Pre-configured"""
    
    def default_config(self) -> Dict:
        return {
            'period': 50,
            'description': 'Simple Moving Average 50'
        }


class SMA200Indicator(SMAIndicator):
    """SMA 200 - Pre-configured"""
    
    def default_config(self) -> Dict:
        return {
            'period': 200,
            'description': 'Simple Moving Average 200'
        }

