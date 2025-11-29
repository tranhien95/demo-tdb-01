"""
ICT Concepts - Inner Circle Trader concepts
Order Blocks, Fair Value Gaps, Liquidity Sweeps, Premium/Discount
"""

from typing import List, Dict
from .base import BaseIndicator


class ICTConceptsIndicator(BaseIndicator):
    """ICT (Inner Circle Trader) Concepts"""
    
    def default_config(self) -> Dict:
        return {
            'ob_lookback': 20,           # Order Block lookback
            'fvg_threshold': 0.0005,     # FVG minimum gap (0.05%)
            'liquidity_lookback': 50,    # Liquidity sweep lookback
            'premium_discount': True,    # Enable premium/discount zones
            'description': 'ICT Trading Concepts'
        }
    
    def _detect_order_block(self, data: List[Dict], index: int, lookback: int) -> Dict:
        """Detect bullish/bearish order blocks"""
        if index < lookback + 3:
            return {"bullish_ob": False, "bearish_ob": False, "ob_zone": None}
        
        # Bullish OB: Last bearish candle before strong bullish move
        bullish_ob = False
        bullish_ob_zone = None
        
        # Look for strong bullish move (3+ consecutive bullish candles)
        recent_bullish = 0
        for i in range(index - 2, index + 1):
            if data[i]['close'] > data[i]['open']:
                recent_bullish += 1
        
        if recent_bullish >= 3:
            # Find last bearish candle before the move
            for i in range(index - 3, max(0, index - lookback), -1):
                if data[i]['close'] < data[i]['open']:
                    bullish_ob = True
                    bullish_ob_zone = {
                        'high': data[i]['high'],
                        'low': data[i]['low'],
                        'index': i
                    }
                    break
        
        # Bearish OB: Last bullish candle before strong bearish move
        bearish_ob = False
        bearish_ob_zone = None
        
        recent_bearish = 0
        for i in range(index - 2, index + 1):
            if data[i]['close'] < data[i]['open']:
                recent_bearish += 1
        
        if recent_bearish >= 3:
            for i in range(index - 3, max(0, index - lookback), -1):
                if data[i]['close'] > data[i]['open']:
                    bearish_ob = True
                    bearish_ob_zone = {
                        'high': data[i]['high'],
                        'low': data[i]['low'],
                        'index': i
                    }
                    break
        
        return {
            "bullish_ob": bullish_ob,
            "bearish_ob": bearish_ob,
            "bullish_zone": bullish_ob_zone,
            "bearish_zone": bearish_ob_zone
        }
    
    def _detect_fvg(self, data: List[Dict], index: int, threshold: float) -> Dict:
        """Detect Fair Value Gaps (imbalances)"""
        if index < 2:
            return {"bullish_fvg": False, "bearish_fvg": False, "fvg_zone": None}
        
        candle_0 = data[index - 2]
        candle_1 = data[index - 1]
        candle_2 = data[index]
        
        # Bullish FVG: Gap between candle_0 high and candle_2 low
        bullish_fvg = False
        bullish_fvg_zone = None
        
        if candle_2['low'] > candle_0['high']:
            gap_size = (candle_2['low'] - candle_0['high']) / candle_1['close']
            if gap_size >= threshold:
                bullish_fvg = True
                bullish_fvg_zone = {
                    'top': candle_2['low'],
                    'bottom': candle_0['high'],
                    'size': gap_size
                }
        
        # Bearish FVG: Gap between candle_0 low and candle_2 high
        bearish_fvg = False
        bearish_fvg_zone = None
        
        if candle_2['high'] < candle_0['low']:
            gap_size = (candle_0['low'] - candle_2['high']) / candle_1['close']
            if gap_size >= threshold:
                bearish_fvg = True
                bearish_fvg_zone = {
                    'top': candle_0['low'],
                    'bottom': candle_2['high'],
                    'size': gap_size
                }
        
        return {
            "bullish_fvg": bullish_fvg,
            "bearish_fvg": bearish_fvg,
            "bullish_zone": bullish_fvg_zone,
            "bearish_zone": bearish_fvg_zone
        }
    
    def _detect_liquidity_sweep(self, data: List[Dict], index: int, lookback: int) -> Dict:
        """Detect liquidity sweeps (stop hunts)"""
        if index < lookback:
            return {"buy_side_sweep": False, "sell_side_sweep": False}
        
        recent_data = data[max(0, index - lookback):index + 1]
        current = data[index]
        
        # Find recent swing high/low
        swing_high = max(d['high'] for d in recent_data[:-1])
        swing_low = min(d['low'] for d in recent_data[:-1])
        
        # Buy-side liquidity sweep: Price spikes above recent high then reverses
        buy_side_sweep = False
        if current['high'] > swing_high:
            # Check if price closed back below the high (false breakout)
            if current['close'] < swing_high:
                buy_side_sweep = True
        
        # Sell-side liquidity sweep: Price spikes below recent low then reverses
        sell_side_sweep = False
        if current['low'] < swing_low:
            # Check if price closed back above the low
            if current['close'] > swing_low:
                sell_side_sweep = True
        
        return {
            "buy_side_sweep": buy_side_sweep,
            "sell_side_sweep": sell_side_sweep,
            "swing_high": swing_high,
            "swing_low": swing_low
        }
    
    def _premium_discount_zones(self, data: List[Dict], index: int, lookback: int = 50) -> Dict:
        """Calculate premium and discount zones"""
        if index < lookback:
            return {"in_premium": False, "in_discount": False, "in_equilibrium": False}
        
        recent_data = data[max(0, index - lookback):index + 1]
        range_high = max(d['high'] for d in recent_data)
        range_low = min(d['low'] for d in recent_data)
        
        range_size = range_high - range_low
        equilibrium = (range_high + range_low) / 2
        
        # Premium zone: Upper 50%
        premium_threshold = equilibrium + (range_size * 0.2)
        
        # Discount zone: Lower 50%
        discount_threshold = equilibrium - (range_size * 0.2)
        
        current_price = data[index]['close']
        
        in_premium = current_price > premium_threshold
        in_discount = current_price < discount_threshold
        in_equilibrium = not in_premium and not in_discount
        
        return {
            "in_premium": in_premium,
            "in_discount": in_discount,
            "in_equilibrium": in_equilibrium,
            "equilibrium": equilibrium,
            "range_high": range_high,
            "range_low": range_low
        }
    
    def calculate(self, data: List[Dict], index: int, **kwargs) -> Dict:
        """Calculate ICT Concepts"""
        ob_lookback = kwargs.get('ob_lookback', self.config['ob_lookback'])
        fvg_threshold = kwargs.get('fvg_threshold', self.config['fvg_threshold'])
        liq_lookback = kwargs.get('liquidity_lookback', self.config['liquidity_lookback'])
        
        if index < 10:
            return {
                "bullish": False,
                "bearish": False,
                "value": {},
                "strength": 0
            }
        
        # Detect all ICT concepts
        order_blocks = self._detect_order_block(data, index, ob_lookback)
        fvg = self._detect_fvg(data, index, fvg_threshold)
        liquidity = self._detect_liquidity_sweep(data, index, liq_lookback)
        zones = self._premium_discount_zones(data, index, liq_lookback)
        
        # Bullish signals
        bullish_score = 0
        if order_blocks['bullish_ob']:
            bullish_score += 25
        if fvg['bullish_fvg']:
            bullish_score += 20
        if liquidity['sell_side_sweep']:  # Sweep of sell-side = bullish
            bullish_score += 30
        if zones['in_discount']:  # Buy in discount zone
            bullish_score += 15
        
        # Bearish signals
        bearish_score = 0
        if order_blocks['bearish_ob']:
            bearish_score += 25
        if fvg['bearish_fvg']:
            bearish_score += 20
        if liquidity['buy_side_sweep']:  # Sweep of buy-side = bearish
            bearish_score += 30
        if zones['in_premium']:  # Sell in premium zone
            bearish_score += 15
        
        bullish = bullish_score > bearish_score and bullish_score >= 30
        bearish = bearish_score > bullish_score and bearish_score >= 30
        
        return {
            "bullish": bullish,
            "bearish": bearish,
            "value": {
                "order_blocks": order_blocks,
                "fair_value_gaps": fvg,
                "liquidity_sweeps": liquidity,
                "zones": zones,
                "bullish_score": bullish_score,
                "bearish_score": bearish_score
            },
            "strength": max(bullish_score, bearish_score)
        }
    
    def get_pine_script(self) -> str:
        """Generate Pine Script code"""
        
        return """// ICT Concepts
lookback = 50

// Premium/Discount Zones
range_high = ta.highest(high, lookback)
range_low = ta.lowest(low, lookback)
equilibrium = (range_high + range_low) / 2
range_size = range_high - range_low

premium_zone = equilibrium + range_size * 0.25
discount_zone = equilibrium - range_size * 0.25

in_premium = close > premium_zone
in_discount = close < discount_zone

// Fair Value Gap (FVG)
bullish_fvg = low > high[2] and (low - high[2]) / close > 0.0005
bearish_fvg = high < low[2] and (low[2] - high) / close > 0.0005

// Liquidity Sweep
swing_high = ta.highest(high, lookback)
swing_low = ta.lowest(low, lookback)

buy_side_sweep = high > swing_high[1] and close < swing_high[1]
sell_side_sweep = low < swing_low[1] and close > swing_low[1]

// Order Blocks (simplified)
is_bullish_ob = close[3] < open[3] and close > open and close[1] > open[1] and close[2] > open[2]
is_bearish_ob = close[3] > open[3] and close < open and close[1] < open[1] and close[2] < open[2]

// Combined signals
ict_bullish = (bullish_fvg or sell_side_sweep or is_bullish_ob) and in_discount
ict_bearish = (bearish_fvg or buy_side_sweep or is_bearish_ob) and in_premium

// Plot zones
bgcolor(in_premium ? color.new(color.red, 95) : na, title="Premium Zone")
bgcolor(in_discount ? color.new(color.green, 95) : na, title="Discount Zone")
plot(equilibrium, "Equilibrium", color=color.gray, linewidth=1, style=plot.style_circles)

plotshape(bullish_fvg, "Bull FVG", shape.square, location.belowbar, color.green, size=size.tiny)
plotshape(bearish_fvg, "Bear FVG", shape.square, location.abovebar, color.red, size=size.tiny)
plotshape(sell_side_sweep, "Sell Sweep", shape.diamond, location.belowbar, color.aqua, size=size.small)
plotshape(buy_side_sweep, "Buy Sweep", shape.diamond, location.abovebar, color.orange, size=size.small)"""
