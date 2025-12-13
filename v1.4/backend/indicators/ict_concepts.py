"""
ICT (Inner Circle Trader) Concepts Indicator
Advanced market structure analysis with fair value gaps and liquidity
"""

from typing import Dict, List
from .base import BaseIndicator


class ICTConceptsIndicator(BaseIndicator):
    """
    ICT Trading Concepts
    - Order Blocks
    - Fair Value Gaps (FVG)
    - Liquidity Sweeps
    - Premium/Discount Zones
    """
    
    def default_config(self) -> Dict:
        """Default configuration"""
        return {
            'ob_lookback': 50,
            'fvg_threshold': 0.3,
            'liquidity_lookback': 20,
        }
    
    def _detect_order_block(self, data: List[Dict], index: int, lookback: int) -> Dict:
        """Detect order blocks (strong price rejection zones)"""
        if index < lookback:
            return {'bullish_ob': False, 'bearish_ob': False, 'strength': 0}
        
        bullish_ob = False
        bearish_ob = False
        strength = 0
        
        # Bullish OB: Higher high-low with wick rejection
        if index >= 2:
            curr = data[index]['close']
            prev_high = max(data[i]['high'] for i in range(max(0, index - lookback), index))
            prev_low = min(data[i]['low'] for i in range(max(0, index - lookback), index))
            
            if curr > prev_high * 0.98 and data[index]['low'] < data[index - 1]['low']:
                bullish_ob = True
                strength = min((curr / (prev_high * 0.98) - 1) * 100, 100)
            
            if curr < prev_low * 1.02 and data[index]['high'] > data[index - 1]['high']:
                bearish_ob = True
                strength = min((1 - curr / (prev_low * 1.02)) * 100, 100)
        
        return {
            'bullish_ob': bullish_ob,
            'bearish_ob': bearish_ob,
            'strength': strength
        }
    
    def _detect_fvg(self, data: List[Dict], index: int, threshold: float) -> Dict:
        """Detect Fair Value Gaps (gap between candles)"""
        if index < 2:
            return {'bullish_fvg': False, 'bearish_fvg': False, 'gap_size': 0}
        
        bullish_fvg = False
        bearish_fvg = False
        gap_size = 0
        
        # Bullish FVG: Previous low > Current high (gap up)
        if data[index - 1]['low'] > data[index]['high']:
            gap_size = ((data[index - 1]['low'] - data[index]['high']) / data[index]['close']) * 100
            if gap_size > threshold:
                bullish_fvg = True
        
        # Bearish FVG: Previous high < Current low (gap down)
        if data[index - 1]['high'] < data[index]['low']:
            gap_size = ((data[index]['low'] - data[index - 1]['high']) / data[index]['close']) * 100
            if gap_size > threshold:
                bearish_fvg = True
        
        return {
            'bullish_fvg': bullish_fvg,
            'bearish_fvg': bearish_fvg,
            'gap_size': gap_size
        }
    
    def _detect_liquidity_sweep(self, data: List[Dict], index: int, lookback: int) -> Dict:
        """Detect liquidity sweeps (break of prior high/low)"""
        if index < lookback:
            return {
                'buy_side_sweep': False,
                'sell_side_sweep': False,
                'sweep_strength': 0
            }
        
        buy_side_sweep = False
        sell_side_sweep = False
        sweep_strength = 0
        
        curr_high = data[index]['high']
        curr_low = data[index]['low']
        prior_high = max(data[i]['high'] for i in range(max(0, index - lookback), index))
        prior_low = min(data[i]['low'] for i in range(max(0, index - lookback), index))
        
        # Sweep of buy-side (break below prior low) = bearish
        if curr_low < prior_low:
            buy_side_sweep = True
            sweep_strength = min(((prior_low - curr_low) / prior_low) * 100, 100)
        
        # Sweep of sell-side (break above prior high) = bullish
        if curr_high > prior_high:
            sell_side_sweep = True
            sweep_strength = min(((curr_high - prior_high) / prior_high) * 100, 100)
        
        return {
            'buy_side_sweep': buy_side_sweep,
            'sell_side_sweep': sell_side_sweep,
            'sweep_strength': sweep_strength
        }
    
    def _premium_discount_zones(self, data: List[Dict], index: int, lookback: int) -> Dict:
        """Detect premium and discount zones"""
        if index < lookback:
            return {
                'in_premium': False,
                'in_discount': False,
                'in_equilibrium': False,
                'range_high': 0,
                'range_low': 0
            }
        
        range_high = max(data[i]['high'] for i in range(max(0, index - lookback), index + 1))
        range_low = min(data[i]['low'] for i in range(max(0, index - lookback), index + 1))
        midline = (range_high + range_low) / 2
        current_price = data[index]['close']
        
        in_premium = current_price > midline and current_price > range_low * 1.01
        in_discount = current_price < midline and current_price < range_high * 0.99
        in_equilibrium = (current_price >= midline * 0.995) and (current_price <= midline * 1.005)
        
        return {
            'in_premium': in_premium,
            'in_discount': in_discount,
            'in_equilibrium': in_equilibrium,
            'range_high': range_high,
            'range_low': range_low
        }
    
    def calculate(self, data: List[Dict], index: int, **kwargs) -> Dict:
        """Calculate ICT Trading Concepts"""
        ob_lookback = kwargs.get('ob_lookback', self.config['ob_lookback'])
        fvg_threshold = kwargs.get('fvg_threshold', self.config['fvg_threshold'])
        liq_lookback = kwargs.get('liquidity_lookback', self.config['liquidity_lookback'])
        
        if index < 10:
            return {
                "bullish": False,
                "bearish": False,
                "value": {},
                "strength": 0,
                "signal_type": "NEUTRAL",
                "confidence": 0,
                "trend": "NEUTRAL",
                "reversal_signal": False,
                "divergence": False,
                "supporting_signals": [],
                "raw_values": {}
            }
        
        # Detect all ICT concepts
        order_blocks = self._detect_order_block(data, index, ob_lookback)
        fvg = self._detect_fvg(data, index, fvg_threshold)
        liquidity = self._detect_liquidity_sweep(data, index, liq_lookback)
        zones = self._premium_discount_zones(data, index, liq_lookback)
        
        # Market structure (HH+HL = bullish, LL+LH = bearish)
        if index >= 3:
            recent_highs = [data[i]['high'] for i in range(max(0, index - 5), index + 1)]
            recent_lows = [data[i]['low'] for i in range(max(0, index - 5), index + 1)]
            
            hh = len(recent_highs) > 1 and recent_highs[-1] > recent_highs[-2]
            ll = len(recent_lows) > 1 and recent_lows[-1] > recent_lows[-2]
            
            market_structure = "BULLISH" if hh and ll else "BEARISH"
        else:
            market_structure = "NEUTRAL"
        
        # Bullish signals
        bullish_score = 0
        if order_blocks['bullish_ob']:
            bullish_score += 25
        if fvg['bullish_fvg']:
            bullish_score += 20
        if liquidity['sell_side_sweep']:
            bullish_score += 30
        if zones['in_discount']:
            bullish_score += 15
        
        # Bearish signals
        bearish_score = 0
        if order_blocks['bearish_ob']:
            bearish_score += 25
        if fvg['bearish_fvg']:
            bearish_score += 20
        if liquidity['buy_side_sweep']:
            bearish_score += 30
        if zones['in_premium']:
            bearish_score += 15
        
        bullish = bullish_score > bearish_score and bullish_score >= 30
        bearish = bearish_score > bullish_score and bearish_score >= 30
        strength = max(bullish_score, bearish_score)
        
        # Determine signal type
        if bullish_score > 70:
            signal_type = "STRONG_BUY"
        elif bullish_score > 50:
            signal_type = "BUY"
        elif bearish_score > 70:
            signal_type = "STRONG_SELL"
        elif bearish_score > 50:
            signal_type = "SELL"
        else:
            signal_type = "NEUTRAL"
        
        total_score = bullish_score + bearish_score
        confidence = (bullish_score / total_score * 100) if total_score > 0 else 50
        
        return {
            "bullish": bullish,
            "bearish": bearish,
            "value": {
                "order_blocks": order_blocks,
                "fair_value_gaps": fvg,
                "liquidity_sweeps": liquidity,
                "zones": zones,
                "bullish_score": bullish_score,
                "bearish_score": bearish_score,
                "market_structure": market_structure
            },
            "strength": min(strength, 100),
            "signal_type": signal_type,
            "confidence": confidence,
            "trend": market_structure,
            "reversal_signal": liquidity['buy_side_sweep'] or liquidity['sell_side_sweep'],
            "divergence": False,
            "supporting_signals": [
                f"Market Structure: {market_structure}",
                f"Fair Value Gap: {'Detected' if (fvg['bullish_fvg'] or fvg['bearish_fvg']) else 'None'}",
                f"Premium Zone: {'Active' if zones['in_premium'] else 'Inactive'}",
                f"Discount Zone: {'Active' if zones['in_discount'] else 'Inactive'}",
                f"Entry Quality: {'High' if confidence > 70 else 'Low'}"
            ],
            "raw_values": {
                "market_structure": market_structure,
                "fvg_detected": fvg['bullish_fvg'] or fvg['bearish_fvg'],
                "premium_zone": zones['in_premium'],
                "discount_zone": zones['in_discount'],
                "liquidity_level": (data[index]['high'] + data[index]['low']) / 2,
                "breakout_potential": strength,
                "bullish_score": bullish_score,
                "bearish_score": bearish_score
            }
        }
    
    def get_pine_script(self) -> str:
        """Generate Pine Script code"""
        
        return """// ICT Concepts
lookback = 50

// Premium/Discount Zones
range_high = ta.highest(high, lookback)
range_low = ta.lowest(low, lookback)
midline = (range_high + range_low) / 2

in_premium = close > midline
in_discount = close < midline

// Fair Value Gaps
bullish_fvg = low[1] > high  // Gap up
bearish_fvg = high[1] < low  // Gap down

// Liquidity Sweeps
prior_high = ta.highest(high, lookback)
prior_low = ta.lowest(low, lookback)

buy_side_sweep = low < prior_low  // Break below
sell_side_sweep = high > prior_high  // Break above

// Market Structure
hh = high > high[1] and high[1] > high[2]
ll = low < low[1] and low[1] < low[2]

bullish_signal = sell_side_sweep or bullish_fvg or (hh and ll)
bearish_signal = buy_side_sweep or bearish_fvg

plotshape(bullish_signal, style=shape.arrowup, color=color.green)
plotshape(bearish_signal, style=shape.arrowdown, color=color.red)
"""
