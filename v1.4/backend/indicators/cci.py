"""
CCI - Commodity Channel Index
Measures deviation from average price
"""

from typing import List, Dict
from .base import BaseIndicator


class CCIIndicator(BaseIndicator):
    """CCI Indicator with customizable settings"""
    
    def default_config(self) -> Dict:
        return {
            'period': 20,
            'overbought': 100,
            'oversold': -100,
            'description': 'Commodity Channel Index'
        }
    
    def calculate(self, data: List[Dict], index: int, **kwargs) -> Dict:
        period = kwargs.get('period', self.config['period'])
        oversold = kwargs.get('oversold', self.config['oversold'])
        overbought = kwargs.get('overbought', self.config['overbought'])
        
        if index < period:
            return {"bullish": False, "bearish": False, "value": 0, "strength": 0, "signal_type": "NEUTRAL", "confidence": 0, "trend": "NEUTRAL", "reversal_signal": False, "divergence": False, "supporting_signals": [], "raw_values": {}}
        
        tp_list = [(d["high"] + d["low"] + d["close"]) / 3 for d in data[index - period + 1:index + 1]]
        sma_tp = sum(tp_list) / period
        tp = (data[index]["high"] + data[index]["low"] + data[index]["close"]) / 3
        
        mad = sum(abs(tp - sma_tp) for tp in tp_list) / period
        cci_val = (tp - sma_tp) / (0.015 * mad) if mad > 0 else 0
        
        # Extreme levels
        is_extreme = cci_val > 200 or cci_val < -200
        
        # Strength level (0-5)
        if abs(cci_val) > 200:
            strength_level = 5
        elif abs(cci_val) > 100:
            strength_level = 4
        elif abs(cci_val) > overbought:
            strength_level = 3
        else:
            strength_level = 1
        
        # Determine signal
        if cci_val > 200:
            signal_type = "STRONG_BUY"
        elif cci_val > overbought:
            signal_type = "BUY"
        elif cci_val < -200:
            signal_type = "STRONG_SELL"
        elif cci_val < oversold:
            signal_type = "SELL"
        else:
            signal_type = "NEUTRAL"
        
        # Trend
        is_bullish = cci_val < oversold  # CCI inverted: oversold is bullish
        trend = "EXTREME_BUY" if cci_val < -200 else ("STRONG_BUY" if cci_val < oversold else ("EXTREME_SELL" if cci_val > 200 else ("STRONG_SELL" if cci_val > overbought else "NEUTRAL")))
        
        strength = min(abs(cci_val) / 200 * 100, 100)
        
        return {
            "bullish": is_bullish,
            "bearish": not is_bullish,
            "value": cci_val,
            "strength": strength,
            "signal_type": signal_type,
            "confidence": strength,
            "trend": trend,
            "reversal_signal": is_extreme,
            "divergence": False,
            "supporting_signals": [
                f"CCI: {cci_val:.2f}",
                f"Strength: {['Neutral', 'Weak', 'Medium', 'Strong', 'Very Strong', 'Extreme'][min(strength_level, 5)]}",
                f"Zone: {'Overbought extreme' if cci_val > 200 else ('Oversold extreme' if cci_val < -200 else ('Overbought' if cci_val > overbought else ('Oversold' if cci_val < oversold else 'Normal')))}",
                f"Reversal risk: {'HIGH' if is_extreme else 'LOW'}"
            ],
            "raw_values": {
                "cci": cci_val,
                "strength_level": strength_level,
                "typical_price": tp,
                "deviation": mad,
                "extreme_level": is_extreme
            }
        }
    
    def get_pine_script(self) -> str:
        period = self.config['period']
        return f"""// CCI Indicator
cci_value = ta.cci(close, {period})
cci_bullish = cci_value < {self.config['oversold']}
cci_bearish = cci_value > {self.config['overbought']}"""
