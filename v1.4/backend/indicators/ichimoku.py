"""
Ichimoku Cloud - Japanese trend indicator
5 lines: Tenkan, Kijun, Senkou A, Senkou B, Chikou Span
"""

from typing import List, Dict
from .base import BaseIndicator


class IchimokuIndicator(BaseIndicator):
    """Ichimoku Cloud with configurable parameters"""
    
    def default_config(self) -> Dict:
        return {
            'tenkan_period': 9,      # Conversion Line
            'kijun_period': 26,      # Base Line
            'senkou_b_period': 52,   # Leading Span B
            'displacement': 26,       # Cloud displacement
            'description': 'Ichimoku Cloud'
        }
    
    def _midpoint(self, data: List[Dict], start_idx: int, period: int) -> float:
        """Calculate midpoint (highest high + lowest low) / 2"""
        if start_idx < 0:
            return 0
        
        subset = data[max(0, start_idx - period + 1):start_idx + 1]
        if not subset:
            return 0
            
        highest = max(d['high'] for d in subset)
        lowest = min(d['low'] for d in subset)
        return (highest + lowest) / 2
    
    def calculate(self, data: List[Dict], index: int, **kwargs) -> Dict:
        """Calculate Ichimoku Cloud signals"""
        tenkan_period = kwargs.get('tenkan_period', self.config['tenkan_period'])
        kijun_period = kwargs.get('kijun_period', self.config['kijun_period'])
        senkou_b_period = kwargs.get('senkou_b_period', self.config['senkou_b_period'])
        displacement = kwargs.get('displacement', self.config['displacement'])
        
        if index < senkou_b_period:
            return {
                "bullish": False,
                "bearish": False,
                "value": None,
                "strength": 0
            }
        
        # Tenkan-sen (Conversion Line)
        tenkan = self._midpoint(data, index, tenkan_period)
        
        # Kijun-sen (Base Line)
        kijun = self._midpoint(data, index, kijun_period)
        
        # Senkou Span A (Leading Span A) - displaced forward
        senkou_a = (tenkan + kijun) / 2
        
        # Senkou Span B (Leading Span B) - displaced forward
        senkou_b = self._midpoint(data, index, senkou_b_period)
        
        # Chikou Span (Lagging Span) - current close displaced backward
        chikou = data[index]['close']
        chikou_compare_idx = max(0, index - displacement)
        chikou_compare = data[chikou_compare_idx]['close']
        
        current_price = data[index]['close']
        
        # Cloud color (bullish if Senkou A > Senkou B)
        cloud_bullish = senkou_a > senkou_b
        
        # Price position relative to cloud
        cloud_top = max(senkou_a, senkou_b)
        cloud_bottom = min(senkou_a, senkou_b)
        
        price_above_cloud = current_price > cloud_top
        price_below_cloud = current_price < cloud_bottom
        price_in_cloud = not price_above_cloud and not price_below_cloud
        
        # TK Cross (Tenkan crosses Kijun)
        tk_bullish_cross = False
        tk_bearish_cross = False
        
        if index > 0:
            prev_tenkan = self._midpoint(data, index - 1, tenkan_period)
            prev_kijun = self._midpoint(data, index - 1, kijun_period)
            
            tk_bullish_cross = prev_tenkan <= prev_kijun and tenkan > kijun
            tk_bearish_cross = prev_tenkan >= prev_kijun and tenkan < kijun
        
        # Chikou Span confirmation (price vs price 26 periods ago)
        chikou_bullish = chikou > chikou_compare
        chikou_bearish = chikou < chikou_compare
        
        # Strong bullish signals
        bullish = (
            (price_above_cloud and cloud_bullish and chikou_bullish) or
            (tk_bullish_cross and cloud_bullish) or
            (price_above_cloud and tk_bullish_cross)
        )
        
        # Strong bearish signals
        bearish = (
            (price_below_cloud and not cloud_bullish and chikou_bearish) or
            (tk_bearish_cross and not cloud_bullish) or
            (price_below_cloud and tk_bearish_cross)
        )
        
        # Strength calculation
        strength = 0
        if price_above_cloud or price_below_cloud:
            cloud_distance = abs(current_price - cloud_top) if price_above_cloud else abs(current_price - cloud_bottom)
            strength = min((cloud_distance / current_price) * 1000, 100)
        
        return {
            "bullish": bullish,
            "bearish": bearish,
            "value": {
                "tenkan": tenkan,
                "kijun": kijun,
                "senkou_a": senkou_a,
                "senkou_b": senkou_b,
                "chikou": chikou,
                "cloud_bullish": cloud_bullish,
                "price_above_cloud": price_above_cloud,
                "price_below_cloud": price_below_cloud,
                "price_in_cloud": price_in_cloud,
                "tk_cross": "bullish" if tk_bullish_cross else "bearish" if tk_bearish_cross else "none"
            },
            "strength": strength
        }
    
    def get_pine_script(self) -> str:
        """Generate Pine Script code"""
        tenkan = self.config['tenkan_period']
        kijun = self.config['kijun_period']
        senkou_b = self.config['senkou_b_period']
        displacement = self.config['displacement']
        
        return f"""// Ichimoku Cloud
tenkan_period = {tenkan}
kijun_period = {kijun}
senkou_b_period = {senkou_b}

// Midpoint calculation
midpoint(len) =>
    math.avg(ta.highest(high, len), ta.lowest(low, len))

// Ichimoku lines
tenkan = midpoint(tenkan_period)
kijun = midpoint(kijun_period)
senkou_a = math.avg(tenkan, kijun)
senkou_b = midpoint(senkou_b_period)

// Plot lines
plot(tenkan, "Tenkan-sen", color=color.red, linewidth=1)
plot(kijun, "Kijun-sen", color=color.blue, linewidth=1)

// Cloud
senkou_a_plot = plot(senkou_a[{displacement}], "Senkou A", color=color.green, offset={displacement})
senkou_b_plot = plot(senkou_b[{displacement}], "Senkou B", color=color.red, offset={displacement})
fill(senkou_a_plot, senkou_b_plot, color=senkou_a[{displacement}] > senkou_b[{displacement}] ? color.new(color.green, 90) : color.new(color.red, 90))

// Chikou Span
plot(close, "Chikou Span", color=color.purple, offset=-{displacement}, linewidth=1)

// Signals
cloud_bullish = senkou_a > senkou_b
cloud_top = math.max(senkou_a, senkou_b)
cloud_bottom = math.min(senkou_a, senkou_b)

ichimoku_bullish = close > cloud_top and cloud_bullish and ta.crossover(tenkan, kijun)
ichimoku_bearish = close < cloud_bottom and not cloud_bullish and ta.crossunder(tenkan, kijun)"""
