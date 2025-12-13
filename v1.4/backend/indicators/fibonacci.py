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
                "strength": 0,
                "signal_type": "NEUTRAL",
                "confidence": 0,
                "trend": "NEUTRAL",
                "reversal_signal": False,
                "divergence": False,
                "supporting_signals": [],
                "raw_values": {}
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
        min_distance = float('inf')
        
        for key, fib_price in fib_levels.items():
            distance = abs(current_price - fib_price) / current_price
            if distance < min_distance:
                min_distance = distance
                near_level = fib_price
                level_key = key
        
        at_level = min_distance <= tolerance
        
        # Determine trend direction
        recent_data = data[max(0, index - 5):index + 1]
        trend_up = recent_data[-1]['close'] > recent_data[0]['close']
        
        # Support vs Resistance
        support_levels = ['fib_0.382', 'fib_0.5', 'fib_0.618', 'fib_0.786']
        resistance_levels = ['fib_0.236', 'fib_0.382', 'fib_0.5']
        
        is_support = at_level and level_key in support_levels
        is_resistance = at_level and level_key in resistance_levels
        
        # Signals
        bullish = is_support and trend_up
        bearish = is_resistance and not trend_up
        
        # Strength based on level importance
        level_weights = {
            'fib_0.236': 1,
            'fib_0.382': 2,
            'fib_0.5': 3,
            'fib_0.618': 4,  # Most important
            'fib_0.786': 2,
            'fib_0.0': 1
        }
        level_weight = level_weights.get(level_key, 1)
        
        # Strength calculation
        strength = 0
        if at_level:
            strength = (1 - min_distance) * 100 * level_weight / 4
        strength = min(strength, 100)
        
        # Signal type
        if at_level:
            if level_key == 'fib_0.618':
                signal_type = "STRONG_SUPPORT" if is_support else ("STRONG_RESISTANCE" if is_resistance else "NEUTRAL")
            elif level_key in ['fib_0.382', 'fib_0.5']:
                signal_type = "SUPPORT" if is_support else ("RESISTANCE" if is_resistance else "NEUTRAL")
            else:
                signal_type = "WEAK_SUPPORT" if is_support else ("WEAK_RESISTANCE" if is_resistance else "NEUTRAL")
        else:
            signal_type = "NEUTRAL"
        
        trend = "AT_SUPPORT" if is_support else ("AT_RESISTANCE" if is_resistance else ("MOVING_DOWN" if not trend_up else "MOVING_UP"))
        
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
            "strength": strength,
            "signal_type": signal_type,
            "confidence": strength,
            "trend": trend,
            "reversal_signal": at_level and (is_support or is_resistance),
            "divergence": False,
            "supporting_signals": [
                f"Price: {current_price:.2f}",
                f"0.618 level: {fib_levels.get('fib_0.618', 0):.2f} {'(support)' if is_support and level_key == 'fib_0.618' else ('(resistance)' if is_resistance and level_key == 'fib_0.618' else '')}",
                f"Distance: {min_distance * 100:.2f}%",
                f"Zone: {signal_type}",
                f"Reversal probability: {'HIGH' if at_level else 'LOW'}"
            ],
            "raw_values": {
                "trend_high": swing_high,
                "trend_low": swing_low,
                "fib_levels": fib_levels,
                "nearest_level": level_key,
                "distance_percent": min_distance * 100,
                "price_alignment": min_distance,
                "at_level": at_level
            }
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
