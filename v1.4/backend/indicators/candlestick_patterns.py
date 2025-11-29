"""
Candlestick Patterns - Recognition of all major patterns
Bullish and Bearish patterns separated
"""

from typing import List, Dict
from .base import BaseIndicator


class CandlestickPatternsIndicator(BaseIndicator):
    """Recognition of major candlestick patterns"""
    
    def default_config(self) -> Dict:
        return {
            'body_size_threshold': 0.6,  # 60% for strong body
            'small_body_threshold': 0.3,  # 30% for small body (doji)
            'shadow_ratio': 2.0,          # Shadow/body ratio for hammers
            'description': 'Candlestick Pattern Recognition'
        }
    
    def _candle_info(self, candle: Dict) -> Dict:
        """Extract candle information"""
        open_price = candle['open']
        close_price = candle['close']
        high_price = candle['high']
        low_price = candle['low']
        
        body = abs(close_price - open_price)
        upper_shadow = high_price - max(open_price, close_price)
        lower_shadow = min(open_price, close_price) - low_price
        total_range = high_price - low_price
        
        is_bullish = close_price > open_price
        is_bearish = close_price < open_price
        
        body_ratio = body / total_range if total_range > 0 else 0
        
        return {
            'body': body,
            'upper_shadow': upper_shadow,
            'lower_shadow': lower_shadow,
            'total_range': total_range,
            'body_ratio': body_ratio,
            'is_bullish': is_bullish,
            'is_bearish': is_bearish,
            'open': open_price,
            'close': close_price,
            'high': high_price,
            'low': low_price
        }
    
    def calculate(self, data: List[Dict], index: int, **kwargs) -> Dict:
        """Detect candlestick patterns"""
        
        if index < 2:
            return {
                "bullish": False,
                "bearish": False,
                "value": {"patterns": []},
                "strength": 0
            }
        
        current = self._candle_info(data[index])
        prev = self._candle_info(data[index - 1])
        prev2 = self._candle_info(data[index - 2]) if index >= 2 else None
        
        patterns = []
        bullish_score = 0
        bearish_score = 0
        
        # === BULLISH PATTERNS ===
        
        # 1. Hammer (Bullish reversal)
        if (current['lower_shadow'] > current['body'] * 2 and 
            current['upper_shadow'] < current['body'] * 0.3 and
            current['body_ratio'] < 0.4):
            patterns.append("Hammer")
            bullish_score += 15
        
        # 2. Inverted Hammer
        if (current['upper_shadow'] > current['body'] * 2 and 
            current['lower_shadow'] < current['body'] * 0.3 and
            current['body_ratio'] < 0.4):
            patterns.append("Inverted Hammer")
            bullish_score += 12
        
        # 3. Bullish Engulfing
        if (prev['is_bearish'] and current['is_bullish'] and
            current['close'] > prev['open'] and current['open'] < prev['close']):
            patterns.append("Bullish Engulfing")
            bullish_score += 20
        
        # 4. Morning Star (3 candles)
        if prev2 and (prev2['is_bearish'] and prev['body_ratio'] < 0.3 and 
                      current['is_bullish'] and current['close'] > prev2['close']):
            patterns.append("Morning Star")
            bullish_score += 25
        
        # 5. Piercing Pattern
        if (prev['is_bearish'] and current['is_bullish'] and
            current['open'] < prev['low'] and 
            current['close'] > (prev['open'] + prev['close']) / 2 and
            current['close'] < prev['open']):
            patterns.append("Piercing Pattern")
            bullish_score += 18
        
        # 6. Three White Soldiers
        if (prev2 and prev2['is_bullish'] and prev['is_bullish'] and current['is_bullish'] and
            current['close'] > prev['close'] > prev2['close'] and
            current['body_ratio'] > 0.6 and prev['body_ratio'] > 0.6):
            patterns.append("Three White Soldiers")
            bullish_score += 30
        
        # 7. Bullish Harami
        if (prev['is_bearish'] and current['is_bullish'] and
            current['open'] > prev['close'] and current['close'] < prev['open'] and
            current['body'] < prev['body']):
            patterns.append("Bullish Harami")
            bullish_score += 15
        
        # 8. Tweezer Bottom
        if prev['is_bearish'] and current['is_bullish'] and abs(prev['low'] - current['low']) < prev['total_range'] * 0.05:
            patterns.append("Tweezer Bottom")
            bullish_score += 12
        
        # === BEARISH PATTERNS ===
        
        # 1. Hanging Man (Bearish reversal)
        if (current['lower_shadow'] > current['body'] * 2 and 
            current['upper_shadow'] < current['body'] * 0.3 and
            current['body_ratio'] < 0.4 and current['is_bearish']):
            patterns.append("Hanging Man")
            bearish_score += 15
        
        # 2. Shooting Star
        if (current['upper_shadow'] > current['body'] * 2 and 
            current['lower_shadow'] < current['body'] * 0.3 and
            current['body_ratio'] < 0.4 and current['is_bearish']):
            patterns.append("Shooting Star")
            bearish_score += 18
        
        # 3. Bearish Engulfing
        if (prev['is_bullish'] and current['is_bearish'] and
            current['close'] < prev['open'] and current['open'] > prev['close']):
            patterns.append("Bearish Engulfing")
            bearish_score += 20
        
        # 4. Evening Star (3 candles)
        if prev2 and (prev2['is_bullish'] and prev['body_ratio'] < 0.3 and 
                      current['is_bearish'] and current['close'] < prev2['close']):
            patterns.append("Evening Star")
            bearish_score += 25
        
        # 5. Dark Cloud Cover
        if (prev['is_bullish'] and current['is_bearish'] and
            current['open'] > prev['high'] and 
            current['close'] < (prev['open'] + prev['close']) / 2 and
            current['close'] > prev['open']):
            patterns.append("Dark Cloud Cover")
            bearish_score += 18
        
        # 6. Three Black Crows
        if (prev2 and prev2['is_bearish'] and prev['is_bearish'] and current['is_bearish'] and
            current['close'] < prev['close'] < prev2['close'] and
            current['body_ratio'] > 0.6 and prev['body_ratio'] > 0.6):
            patterns.append("Three Black Crows")
            bearish_score += 30
        
        # 7. Bearish Harami
        if (prev['is_bullish'] and current['is_bearish'] and
            current['open'] < prev['close'] and current['close'] > prev['open'] and
            current['body'] < prev['body']):
            patterns.append("Bearish Harami")
            bearish_score += 15
        
        # 8. Tweezer Top
        if prev['is_bullish'] and current['is_bearish'] and abs(prev['high'] - current['high']) < prev['total_range'] * 0.05:
            patterns.append("Tweezer Top")
            bearish_score += 12
        
        # 9. Doji (Indecision - context dependent)
        if current['body_ratio'] < 0.1:
            patterns.append("Doji")
            # Doji alone is neutral, context matters
        
        # 10. Spinning Top (Indecision)
        if 0.1 < current['body_ratio'] < 0.3 and current['upper_shadow'] > current['body'] and current['lower_shadow'] > current['body']:
            patterns.append("Spinning Top")
        
        # 11. Marubozu (Strong trend)
        if current['body_ratio'] > 0.9:
            if current['is_bullish']:
                patterns.append("Bullish Marubozu")
                bullish_score += 15
            else:
                patterns.append("Bearish Marubozu")
                bearish_score += 15
        
        bullish = bullish_score > bearish_score and bullish_score > 10
        bearish = bearish_score > bullish_score and bearish_score > 10
        strength = max(bullish_score, bearish_score)
        
        return {
            "bullish": bullish,
            "bearish": bearish,
            "value": {
                "patterns": patterns,
                "bullish_score": bullish_score,
                "bearish_score": bearish_score
            },
            "strength": min(strength, 100)
        }
    
    def get_pine_script(self) -> str:
        """Generate Pine Script code"""
        
        return """// Candlestick Patterns
body = math.abs(close - open)
upper_shadow = high - math.max(open, close)
lower_shadow = math.min(open, close) - low
total_range = high - low
body_ratio = body / total_range

is_bullish_candle = close > open
is_bearish_candle = close < open

// Hammer
is_hammer = lower_shadow > body * 2 and upper_shadow < body * 0.3 and body_ratio < 0.4

// Shooting Star
is_shooting_star = upper_shadow > body * 2 and lower_shadow < body * 0.3 and body_ratio < 0.4

// Bullish Engulfing
bullish_engulfing = close[1] < open[1] and is_bullish_candle and close > open[1] and open < close[1]

// Bearish Engulfing
bearish_engulfing = close[1] > open[1] and is_bearish_candle and close < open[1] and open > close[1]

// Doji
is_doji = body_ratio < 0.1

// Pattern signals
candle_bullish = is_hammer or bullish_engulfing
candle_bearish = is_shooting_star or bearish_engulfing

plotshape(is_hammer, "Hammer", shape.labelup, location.belowbar, color.green, text="H", size=size.tiny)
plotshape(is_shooting_star, "Shooting Star", shape.labeldown, location.abovebar, color.red, text="SS", size=size.tiny)
plotshape(bullish_engulfing, "Bull Engulf", shape.triangleup, location.belowbar, color.green, size=size.small)
plotshape(bearish_engulfing, "Bear Engulf", shape.triangledown, location.abovebar, color.red, size=size.small)"""
