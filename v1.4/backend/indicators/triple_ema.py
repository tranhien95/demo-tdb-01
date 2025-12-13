"""
Triple EMA - Three EMAs for trend analysis
Fast EMA crosses with Medium/Slow EMAs
"""

from typing import List, Dict
from .base import BaseIndicator, HelperFunctions


class TripleEMAIndicator(BaseIndicator):
    """Triple EMA with configurable periods"""
    
    def default_config(self) -> Dict:
        return {
            'fast_period': 5,
            'medium_period': 10,
            'slow_period': 20,
            'description': 'Triple EMA Crossover'
        }
    
    def calculate(self, data: List[Dict], index: int, **kwargs) -> Dict:
        """Calculate Triple EMA signals"""
        fast_period = kwargs.get('fast_period', self.config['fast_period'])
        medium_period = kwargs.get('medium_period', self.config['medium_period'])
        slow_period = kwargs.get('slow_period', self.config['slow_period'])
        
        closes = [d["close"] for d in data[:index + 1]]
        
        fast_ema = HelperFunctions.ema(closes, fast_period)
        medium_ema = HelperFunctions.ema(closes, medium_period)
        slow_ema = HelperFunctions.ema(closes, slow_period)
        
        if index < slow_period:
            return {
                "bullish": False,
                "bearish": False,
                "value": {"fast": None, "medium": None, "slow": None},
                "strength": 0,
                "signal_type": "NEUTRAL",
                "confidence": 0,
                "trend": "NEUTRAL",
                "reversal_signal": False,
                "divergence": False,
                "supporting_signals": [],
                "raw_values": {}
            }
        
        fast_val = fast_ema[index]
        medium_val = medium_ema[index]
        slow_val = slow_ema[index]
        
        # Determine EMA ordering
        ema_order = []
        if fast_val > medium_val > slow_val:
            ema_order = "fast > medium > slow"
            bullish = True
        elif fast_val < medium_val < slow_val:
            ema_order = "fast < medium < slow"
            bullish = False
        else:
            ema_order = "mixed"
            bullish = fast_val > medium_val
        
        # Crossover signals (stronger)
        prev_fast = fast_ema[index - 1] if index > 0 else fast_val
        prev_medium = medium_ema[index - 1] if index > 0 else medium_val
        prev_slow = slow_ema[index - 1] if index > 0 else slow_val
        
        bullish_cross = prev_fast <= prev_medium and fast_val > medium_val
        bearish_cross = prev_fast >= prev_medium and fast_val < medium_val
        
        # EMA spacing analysis
        spacing_fast_medium = abs(fast_val - medium_val) / medium_val * 100
        spacing_medium_slow = abs(medium_val - slow_val) / slow_val * 100
        total_spacing = spacing_fast_medium + spacing_medium_slow
        
        # Calculate alignment percentage
        components_aligned = 0
        if fast_val > medium_val > slow_val:
            components_aligned = 100
        elif fast_val < medium_val < slow_val:
            components_aligned = 100
        else:
            # Partial alignment
            if (fast_val > medium_val and medium_val > slow_val) or (fast_val < medium_val and medium_val < slow_val):
                components_aligned = 66
            elif fast_val > slow_val and medium_val > slow_val:
                components_aligned = 50
            else:
                components_aligned = 25
        
        # Calculate slopes
        fast_slope = ((fast_val - prev_fast) / prev_fast * 100) if prev_fast > 0 else 0
        medium_slope = ((medium_val - prev_medium) / prev_medium * 100) if prev_medium > 0 else 0
        slow_slope = ((slow_val - prev_slow) / prev_slow * 100) if prev_slow > 0 else 0
        
        # Strength based on EMA separation
        strength = 0
        if fast_val and medium_val and slow_val:
            spread = abs(fast_val - slow_val) / slow_val * 100
            strength = min(spread * 10, 100)  # Scale to 0-100
        
        # Determine signal type
        if components_aligned == 100:
            signal_type = "TRIPLE_BUY" if bullish else "TRIPLE_SELL"
        elif components_aligned >= 66:
            signal_type = "BUY" if bullish else "SELL"
        elif bullish_cross:
            signal_type = "BUY"
        elif bearish_cross:
            signal_type = "SELL"
        else:
            signal_type = "NEUTRAL"
        
        # Trend classification (5 levels)
        if fast_val > medium_val > slow_val:
            trend = "STRONG_UP"
        elif fast_val > medium_val and medium_val > slow_val * 0.95:
            trend = "WEAK_UP"
        elif fast_val < medium_val < slow_val:
            trend = "STRONG_DOWN"
        elif fast_val < medium_val and medium_val < slow_val * 1.05:
            trend = "WEAK_DOWN"
        else:
            trend = "SIDEWAYS"
        
        confidence = components_aligned
        
        return {
            "bullish": bullish or bullish_cross,
            "bearish": (not bullish) or bearish_cross,
            "value": {
                "fast": fast_val,
                "medium": medium_val,
                "slow": slow_val,
                "bullish_cross": bullish_cross,
                "bearish_cross": bearish_cross
            },
            "strength": strength,
            "signal_type": signal_type,
            "confidence": confidence,
            "trend": trend,
            "reversal_signal": bullish_cross or bearish_cross,
            "divergence": False,
            "supporting_signals": [
                f"EMA5: {fast_val:.2f} ({'fastest, above all' if fast_val > medium_val > slow_val else ('fastest, below all' if fast_val < medium_val < slow_val else 'fastest')})",
                f"EMA10: {medium_val:.2f}",
                f"EMA20: {slow_val:.2f} ({'slowest, support' if slow_val < medium_val else 'slowest, resistance'})",
                f"Order: {ema_order} ({'TRIPLE BUY' if ema_order == 'fast > medium > slow' else ('TRIPLE SELL' if ema_order == 'fast < medium < slow' else 'MIXED')})",
                f"Alignment: {components_aligned:.0f}% ({'all bullish' if bullish else 'all bearish' if not bullish else 'mixed'})"
            ],
            "raw_values": {
                "ema5": fast_val,
                "ema10": medium_val,
                "ema20": slow_val,
                "ema_order": ema_order,
                "ema_spacing": {
                    "fast_medium": spacing_fast_medium,
                    "medium_slow": spacing_medium_slow,
                    "total": total_spacing
                },
                "ema_slopes": {
                    "fast_slope": fast_slope,
                    "medium_slope": medium_slope,
                    "slow_slope": slow_slope
                },
                "alignment_percent": components_aligned,
                "trend_strength": strength
            }
        }
    
    def get_pine_script(self) -> str:
        """Generate Pine Script code"""
        fast = self.config['fast_period']
        medium = self.config['medium_period']
        slow = self.config['slow_period']
        
        return f"""// Triple EMA ({fast}, {medium}, {slow})
ema_fast = ta.ema(close, {fast})
ema_medium = ta.ema(close, {medium})
ema_slow = ta.ema(close, {slow})

triple_ema_bullish = ema_fast > ema_medium and ema_medium > ema_slow
triple_ema_bearish = ema_fast < ema_medium and ema_medium < ema_slow

// Crossover signals
bullish_cross = ta.crossover(ema_fast, ema_medium)
bearish_cross = ta.crossunder(ema_fast, ema_medium)

plot(ema_fast, "EMA {fast}", color=color.blue, linewidth=1)
plot(ema_medium, "EMA {medium}", color=color.orange, linewidth=1)
plot(ema_slow, "EMA {slow}", color=color.red, linewidth=2)"""
