"""
Fibonacci Retracement - Key support/resistance levels
Based on swing high/low over lookback period
"""

from typing import List, Dict, Optional
from .base import BaseIndicator


class FibonacciIndicator(BaseIndicator):
    """Fibonacci Retracement Levels"""
    
    def default_config(self) -> Dict:
        return {
            'lookback': 64,
            'levels': [0.0, 0.236, 0.382, 0.5, 0.618, 0.786, 1.0],
            'signal_tolerance': 0.002,  # 0.2% tolerance for level touch
            'description': 'Fibonacci Retracement Levels'
        }
    
    def calculate(self, data: List[Dict], index: int, **kwargs) -> Dict:
        """Calculate Fibonacci levels and signals"""
        lookback = kwargs.get('lookback', self.config['lookback'])
        levels = kwargs.get('levels', self.config['levels'])
        tolerance = kwargs.get('signal_tolerance', self.config['signal_tolerance'])
        
        if index < lookback:
            return {
                "bullish": False,
                "bearish": False,
                "value": None,
                "strength": 0
            }
        
        # Find swing high and low
        swing_data = data[max(0, index - lookback):index + 1]
        swing_high = max(d['high'] for d in swing_data)
        swing_low = min(d['low'] for d in swing_data)
        
        # Calculate Fibonacci levels
        diff = swing_high - swing_low
        fib_levels = {}
        
        for level in levels:
            fib_levels[f"fib_{level}"] = swing_high - (diff * level)
        
        current_price = data[index]['close']
        
        # Check if price is near any Fibonacci level
        near_level = None
        level_key = None
        
        for key, fib_price in fib_levels.items():
            distance = abs(current_price - fib_price) / current_price
            if distance <= tolerance:
                near_level = fib_price
                level_key = key
                break
        
        # Determine trend direction
        recent_data = data[max(0, index - 5):index + 1]
        trend_up = recent_data[-1]['close'] > recent_data[0]['close']
        
        # Bullish: Price bouncing from support levels (0.382, 0.5, 0.618) in uptrend
        support_levels = ['fib_0.382', 'fib_0.5', 'fib_0.618', 'fib_0.786']
        bullish = near_level and level_key in support_levels and trend_up
        
        # Bearish: Price rejecting from resistance levels in downtrend
        resistance_levels = ['fib_0.236', 'fib_0.382', 'fib_0.5']
        bearish = near_level and level_key in resistance_levels and not trend_up
        
        # Strength based on how well price respects the level
        strength = 0
        if near_level:
            strength = (1 - abs(current_price - near_level) / (diff if diff > 0 else 1)) * 100
            strength = max(0, min(100, strength))
        
        return {
            "bullish": bullish,
            "bearish": bearish,
            "value": {
                "levels": fib_levels,
                "swing_high": swing_high,
                "swing_low": swing_low,
                "near_level": near_level,
                "level_key": level_key,
                "current_price": current_price
            },
            "strength": strength
        }
    
    def get_pine_script(self) -> str:
        """Generate Pine Script code"""
        lookback = self.config['lookback']
        tolerance = self.config['signal_tolerance']
        
        return f"""// Fibonacci Retracement
lookback = {lookback}
swing_high = ta.highest(high, lookback)
swing_low = ta.lowest(low, lookback)
diff = swing_high - swing_low

// Fibonacci Levels
fib_0 = swing_high
fib_236 = swing_high - diff * 0.236
fib_382 = swing_high - diff * 0.382
fib_50 = swing_high - diff * 0.5
fib_618 = swing_high - diff * 0.618
fib_786 = swing_high - diff * 0.786
fib_100 = swing_low

// Signal detection
tolerance = {tolerance}
near_382 = math.abs(close - fib_382) / close <= tolerance
near_50 = math.abs(close - fib_50) / close <= tolerance
near_618 = math.abs(close - fib_618) / close <= tolerance

fib_bullish = (near_382 or near_50 or near_618) and close > close[5]
fib_bearish = (near_382 or near_50) and close < close[5]

// Plot levels
plot(fib_0, "Fib 0.0", color=color.gray, linewidth=1)
plot(fib_236, "Fib 0.236", color=color.red, linewidth=1)
plot(fib_382, "Fib 0.382", color=color.orange, linewidth=1)
plot(fib_50, "Fib 0.5", color=color.yellow, linewidth=2)
plot(fib_618, "Fib 0.618", color=color.green, linewidth=1)
plot(fib_786, "Fib 0.786", color=color.blue, linewidth=1)
plot(fib_100, "Fib 1.0", color=color.gray, linewidth=1)"""
