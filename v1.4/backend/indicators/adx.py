"""
ADX - Average Directional Index
Trend strength and direction indicator with comprehensive analysis
"""

from typing import List, Dict
from .base import BaseIndicator, HelperFunctions


class ADXIndicator(BaseIndicator):
    """ADX Indicator with comprehensive trend analysis"""
    
    def default_config(self) -> Dict:
        return {
            'period': 14,
            'strong_trend': 25,
            'very_strong_trend': 40,
            'description': 'Average Directional Index - Trend strength'
        }
    
    def calculate(self, data: List[Dict], index: int, **kwargs) -> Dict:
        """Calculate ADX with comprehensive trend signals"""
        period = kwargs.get('period', self.config['period'])
        strong_trend = kwargs.get('strong_trend', self.config['strong_trend'])
        very_strong_trend = kwargs.get('very_strong_trend', self.config['very_strong_trend'])
        
        if index < period * 2:
            return self._empty_result()
        
        plus_dm, minus_dm = 0, 0
        for i in range(index - period + 1, index + 1):
            up_move = data[i]["high"] - data[i - 1]["high"]
            down_move = data[i - 1]["low"] - data[i]["low"]
            
            if up_move > down_move and up_move > 0:
                plus_dm += up_move
            if down_move > up_move and down_move > 0:
                minus_dm += down_move
        
        atr_val = HelperFunctions.atr(data, index, period)
        plus_di = (plus_dm / atr_val * 100) if atr_val > 0 else 0
        minus_di = (minus_dm / atr_val * 100) if atr_val > 0 else 0
        adx_val = abs(plus_di - minus_di) / (plus_di + minus_di) * 100 if (plus_di + minus_di) > 0 else 0
        
        # Determine trend strength and signal
        if adx_val > very_strong_trend:
            if plus_di > minus_di:
                signal_type = "STRONG_BUY"
                strength = 100
                trend = "STRONG_UPTREND"
                is_bullish = True
            else:
                signal_type = "STRONG_SELL"
                strength = 100
                trend = "STRONG_DOWNTREND"
                is_bullish = False
        elif adx_val > strong_trend:
            if plus_di > minus_di:
                signal_type = "BUY"
                strength = 75
                trend = "UPTREND"
                is_bullish = True
            else:
                signal_type = "SELL"
                strength = 75
                trend = "DOWNTREND"
                is_bullish = False
        else:
            signal_type = "NEUTRAL"
            strength = 50
            trend = "WEAK_TREND"
            is_bullish = False
        
        # DI divergence (potential reversal)
        di_divergence = abs(plus_di - minus_di) > 20
        
        return {
            "bullish": is_bullish and adx_val > strong_trend,
            "bearish": not is_bullish and adx_val > strong_trend,
            "value": round(adx_val, 2),
            "strength": strength,
            "signal_type": signal_type,
            "confidence": min(adx_val, 100),
            "trend": trend,
            "reversal_signal": di_divergence and adx_val > strong_trend,
            "divergence": di_divergence,
            "supporting_signals": [
                f"ADX: {adx_val:.2f}",
                f"+DI: {plus_di:.2f}",
                f"-DI: {minus_di:.2f}",
                f"Trend: {trend}"
            ],
            "raw_values": {
                "adx": adx_val,
                "plus_di": plus_di,
                "minus_di": minus_di,
                "di_divergence": di_divergence,
                "trend_strength": trend,
                "strong_trend_threshold": strong_trend,
                "very_strong_threshold": very_strong_trend
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
        strong_trend = self.config['strong_trend']
        very_strong_trend = self.config['very_strong_trend']
        
        return f"""// ADX Indicator
[plus_di, minus_di, adx_value] = ta.dmi({period}, {period})
adx_strong = adx_value > {strong_trend}
adx_very_strong = adx_value > {very_strong_trend}
adx_bullish = plus_di > minus_di and adx_strong
adx_bearish = minus_di > plus_di and adx_strong"""
