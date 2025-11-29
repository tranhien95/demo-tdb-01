"""
Example: Custom Indicator with Trading Logic
Ví dụ về cách tạo indicator với logic giao dịch riêng
"""

from typing import List, Dict
from .base import BaseIndicator, HelperFunctions


# ============ Example 1: Simple Custom Indicator ============
class CustomRSI_EMAIndicator(BaseIndicator):
    """
    Custom indicator kết hợp RSI và EMA
    Tín hiệu mua: RSI < 30 VÀ giá > EMA50
    Tín hiệu bán: RSI > 70 VÀ giá < EMA50
    """
    
    def default_config(self) -> Dict:
        return {
            'rsi_period': 14,
            'rsi_oversold': 30,
            'rsi_overbought': 70,
            'ema_period': 50,
            'weight_rsi': 0.6,
            'weight_ema': 0.4,
            'description': 'Custom RSI+EMA Combo Indicator'
        }
    
    def calculate(self, data: List[Dict], index: int, **kwargs) -> Dict:
        # Get config
        rsi_period = kwargs.get('rsi_period', self.config['rsi_period'])
        ema_period = kwargs.get('ema_period', self.config['ema_period'])
        oversold = self.config['rsi_oversold']
        overbought = self.config['rsi_overbought']
        
        if index < max(rsi_period, ema_period):
            return {"bullish": False, "bearish": False, "value": 0, "strength": 0}
        
        # Calculate RSI
        gains, losses = 0, 0
        for i in range(index - rsi_period + 1, index + 1):
            change = data[i]["close"] - data[i - 1]["close"]
            if change > 0:
                gains += change
            else:
                losses -= change
        
        avg_gain = gains / rsi_period
        avg_loss = losses / rsi_period
        rs = avg_gain / avg_loss if avg_loss != 0 else 100
        rsi_val = 100 - (100 / (1 + rs))
        
        # Calculate EMA
        closes = [d["close"] for d in data[:index + 1]]
        ema_vals = HelperFunctions.ema(closes, ema_period)
        ema_val = ema_vals[index] if ema_vals[index] is not None else data[index]["close"]
        
        # Trading logic
        price = data[index]["close"]
        
        # Bullish: RSI oversold AND price above EMA
        is_bullish = (rsi_val < oversold) and (price > ema_val)
        
        # Bearish: RSI overbought AND price below EMA
        is_bearish = (rsi_val > overbought) and (price < ema_val)
        
        # Calculate strength (weighted combination)
        rsi_strength = abs(50 - rsi_val) / 50 * 100
        ema_strength = abs(price - ema_val) / ema_val * 100
        combined_strength = (
            rsi_strength * self.config['weight_rsi'] + 
            ema_strength * self.config['weight_ema']
        )
        
        return {
            "bullish": is_bullish,
            "bearish": is_bearish,
            "value": rsi_val,
            "strength": combined_strength,
            "metadata": {
                "rsi": rsi_val,
                "ema": ema_val,
                "price": price
            }
        }
    
    def get_pine_script(self) -> str:
        rsi_period = self.config['rsi_period']
        ema_period = self.config['ema_period']
        oversold = self.config['rsi_oversold']
        overbought = self.config['rsi_overbought']
        
        return f"""// Custom RSI+EMA Indicator
// RSI Component
rsi_value = ta.rsi(close, {rsi_period})
rsi_oversold = rsi_value < {oversold}
rsi_overbought = rsi_value > {overbought}

// EMA Component
ema_value = ta.ema(close, {ema_period})
price_above_ema = close > ema_value
price_below_ema = close < ema_value

// Combined Signals
custom_bullish = rsi_oversold and price_above_ema
custom_bearish = rsi_overbought and price_below_ema

// Plotting
plot(rsi_value, "RSI", color=color.blue)
plot(ema_value, "EMA", color=color.orange)
bgcolor(custom_bullish ? color.new(color.green, 90) : na)
bgcolor(custom_bearish ? color.new(color.red, 90) : na)"""


# ============ Example 2: Advanced Indicator with Multiple Conditions ============
class TrendFollowingIndicator(BaseIndicator):
    """
    Advanced trend-following indicator
    Sử dụng nhiều điều kiện để xác định xu hướng
    """
    
    def default_config(self) -> Dict:
        return {
            'ema_fast': 12,
            'ema_slow': 26,
            'rsi_period': 14,
            'volume_period': 20,
            'volume_multiplier': 1.5,
            'adx_period': 14,
            'adx_threshold': 25,
            'description': 'Advanced Trend Following Strategy'
        }
    
    def calculate(self, data: List[Dict], index: int, **kwargs) -> Dict:
        if index < 50:
            return {"bullish": False, "bearish": False, "value": 0, "strength": 0}
        
        # 1. EMA Trend
        closes = [d["close"] for d in data[:index + 1]]
        ema_fast = HelperFunctions.ema(closes, self.config['ema_fast'])
        ema_slow = HelperFunctions.ema(closes, self.config['ema_slow'])
        
        ema_bullish = ema_fast[index] > ema_slow[index]
        ema_bearish = ema_fast[index] < ema_slow[index]
        
        # 2. RSI Filter (avoid overbought/oversold)
        gains, losses = 0, 0
        for i in range(index - self.config['rsi_period'] + 1, index + 1):
            change = data[i]["close"] - data[i - 1]["close"]
            if change > 0:
                gains += change
            else:
                losses -= change
        
        avg_gain = gains / self.config['rsi_period']
        avg_loss = losses / self.config['rsi_period']
        rs = avg_gain / avg_loss if avg_loss != 0 else 100
        rsi_val = 100 - (100 / (1 + rs))
        
        rsi_ok_for_long = rsi_val < 70
        rsi_ok_for_short = rsi_val > 30
        
        # 3. Volume Confirmation
        vol_period = self.config['volume_period']
        vol_ma = sum([data[i]['volume'] for i in range(index - vol_period, index)]) / vol_period
        volume_confirmed = data[index]['volume'] > vol_ma * self.config['volume_multiplier']
        
        # 4. ADX Trend Strength
        atr_val = HelperFunctions.atr(data, index, self.config['adx_period'])
        plus_dm, minus_dm = 0, 0
        for i in range(index - self.config['adx_period'] + 1, index + 1):
            up_move = data[i]["high"] - data[i - 1]["high"]
            down_move = data[i - 1]["low"] - data[i]["low"]
            
            if up_move > down_move and up_move > 0:
                plus_dm += up_move
            if down_move > up_move and down_move > 0:
                minus_dm += down_move
        
        plus_di = (plus_dm / atr_val * 100) if atr_val > 0 else 0
        minus_di = (minus_dm / atr_val * 100) if atr_val > 0 else 0
        adx_val = abs(plus_di - minus_di) / (plus_di + minus_di) * 100 if (plus_di + minus_di) > 0 else 0
        
        strong_trend = adx_val > self.config['adx_threshold']
        
        # Combine all conditions
        is_bullish = (
            ema_bullish and 
            rsi_ok_for_long and 
            volume_confirmed and 
            strong_trend
        )
        
        is_bearish = (
            ema_bearish and 
            rsi_ok_for_short and 
            volume_confirmed and 
            strong_trend
        )
        
        # Calculate overall strength
        strength = 0
        if is_bullish or is_bearish:
            strength = (
                (30 if ema_bullish or ema_bearish else 0) +
                (20 if rsi_ok_for_long or rsi_ok_for_short else 0) +
                (25 if volume_confirmed else 0) +
                (25 if strong_trend else 0)
            )
        
        return {
            "bullish": is_bullish,
            "bearish": is_bearish,
            "value": adx_val,
            "strength": strength,
            "metadata": {
                "ema_bullish": ema_bullish,
                "rsi": rsi_val,
                "volume_confirmed": volume_confirmed,
                "adx": adx_val,
                "trend_strength": "Strong" if strong_trend else "Weak"
            }
        }
    
    def get_pine_script(self) -> str:
        return f"""// Advanced Trend Following Strategy
// EMA Trend
ema_fast = ta.ema(close, {self.config['ema_fast']})
ema_slow = ta.ema(close, {self.config['ema_slow']})
ema_bullish = ema_fast > ema_slow
ema_bearish = ema_fast < ema_slow

// RSI Filter
rsi = ta.rsi(close, {self.config['rsi_period']})
rsi_ok_long = rsi < 70
rsi_ok_short = rsi > 30

// Volume Confirmation
vol_ma = ta.sma(volume, {self.config['volume_period']})
vol_confirmed = volume > vol_ma * {self.config['volume_multiplier']}

// ADX Trend Strength
[plus_di, minus_di, adx] = ta.dmi({self.config['adx_period']}, {self.config['adx_period']})
strong_trend = adx > {self.config['adx_threshold']}

// Combined Signals
trend_bullish = ema_bullish and rsi_ok_long and vol_confirmed and strong_trend
trend_bearish = ema_bearish and rsi_ok_short and vol_confirmed and strong_trend

// Plotting
plot(ema_fast, "EMA Fast", color=color.green)
plot(ema_slow, "EMA Slow", color=color.red)
bgcolor(trend_bullish ? color.new(color.green, 85) : na)
bgcolor(trend_bearish ? color.new(color.red, 85) : na)"""


# ============ How to use these custom indicators ============
if __name__ == "__main__":
    """
    Cách sử dụng custom indicators
    """
    
    # 1. Import
    from indicators import indicator_manager, INDICATOR_REGISTRY
    
    # 2. Đăng ký custom indicator
    INDICATOR_REGISTRY['Custom_RSI_EMA'] = CustomRSI_EMAIndicator
    INDICATOR_REGISTRY['Trend_Following'] = TrendFollowingIndicator
    
    # 3. Re-initialize manager
    indicator_manager._initialize_indicators()
    
    # 4. Sử dụng
    print("Available indicators:", indicator_manager.list_indicators())
    
    # Sample data
    data = []
    for i in range(100):
        data.append({
            'open': 100 + i * 0.1,
            'high': 105 + i * 0.1,
            'low': 95 + i * 0.1,
            'close': 102 + i * 0.1,
            'volume': 1000 + i * 10
        })
    
    # Calculate signal
    signal = indicator_manager.calculate_indicator('Custom_RSI_EMA', data, 50)
    print("\nCustom RSI+EMA Signal:")
    print(f"  Bullish: {signal['bullish']}")
    print(f"  Bearish: {signal['bearish']}")
    print(f"  Strength: {signal['strength']:.2f}")
    print(f"  Metadata: {signal.get('metadata', {})}")
    
    # Get Pine Script
    pine_code = indicator_manager.get_pine_script(['Custom_RSI_EMA'])
    print("\nPine Script Code:")
    print(pine_code)
    
    # Update config
    indicator_manager.update_indicator_config('Custom_RSI_EMA', {
        'rsi_period': 21,
        'ema_period': 100,
        'weight_rsi': 0.7
    })
    
    print("\nConfig updated!")
    print("New config:", indicator_manager.get_indicator_config('Custom_RSI_EMA'))
