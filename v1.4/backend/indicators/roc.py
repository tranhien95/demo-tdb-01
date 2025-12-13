"""
ROC - Rate of Change
Measures price momentum as percentage change with momentum strength analysis
"""

from typing import List, Dict
from .base import BaseIndicator


class ROCIndicator(BaseIndicator):
    """Rate of Change with comprehensive momentum analysis"""
    
    def default_config(self) -> Dict:
        return {
            'period': 12,
            'strong_up': 5.0,
            'strong_down': -5.0,
            'description': 'Rate of Change - Price momentum'
        }
    
    def calculate(self, data: List[Dict], index: int, **kwargs) -> Dict:
        period = kwargs.get('period', self.config['period'])
        strong_up = kwargs.get('strong_up', self.config['strong_up'])
        strong_down = kwargs.get('strong_down', self.config['strong_down'])
        
        if index < period:
            return self._empty_result()
        
        prev_close = data[index - period]["close"]
        if prev_close == 0:
            return self._empty_result()
        
        roc_val = ((data[index]["close"] - prev_close) / prev_close) * 100
        
        # Determine signal type based on ROC magnitude
        if roc_val > strong_up:
            signal_type = "STRONG_BUY"
            strength = min(abs(roc_val) * 10, 100)
            is_bullish = True
        elif roc_val > 0:
            signal_type = "BUY"
            strength = min(roc_val * 5, 75)
            is_bullish = True
        elif roc_val < strong_down:
            signal_type = "STRONG_SELL"
            strength = min(abs(roc_val) * 10, 100)
            is_bullish = False
        elif roc_val < 0:
            signal_type = "SELL"
            strength = min(abs(roc_val) * 5, 75)
            is_bullish = False
        else:
            signal_type = "NEUTRAL"
            strength = 0
            is_bullish = False
        
        # Momentum acceleration check
        momentum_accel = False
        if index >= period + 1:
            prev_roc = ((data[index - 1]["close"] - data[index - period - 1]["close"]) / data[index - period - 1]["close"]) * 100
            momentum_accel = (roc_val > prev_roc and roc_val > 0) or (roc_val < prev_roc and roc_val < 0)
        
        return {
            "bullish": is_bullish,
            "bearish": not is_bullish,
            "value": round(roc_val, 2),
            "strength": strength,
            "signal_type": signal_type,
            "confidence": min(abs(roc_val), 100),
            "trend": "UPTREND" if roc_val > 0 else "DOWNTREND",
            "reversal_signal": (roc_val > strong_up or roc_val < strong_down),
            "divergence": momentum_accel,  # Acceleration = divergence potential
            "supporting_signals": [
                f"ROC: {roc_val:.2f}%",
                f"Momentum: {'Strong' if abs(roc_val) > 5 else 'Weak'}",
                f"Acceleration: {'Yes' if momentum_accel else 'No'}"
            ],
            "raw_values": {
                "roc": roc_val,
                "current_close": data[index]["close"],
                "past_close": prev_close,
                "momentum_accel": momentum_accel,
                "strong_up_threshold": strong_up,
                "strong_down_threshold": strong_down
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
        period = self.config['period']
        strong_up = self.config['strong_up']
        strong_down = self.config['strong_down']
        
        return f"""// ROC Indicator
roc_value = ta.roc(close, {period})
roc_bullish = roc_value > {strong_up}
roc_bearish = roc_value < {strong_down}
roc_neutral = roc_value >= {strong_down} and roc_value <= {strong_up}"""
