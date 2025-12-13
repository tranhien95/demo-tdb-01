"""
MFI - Money Flow Index
Volume-weighted RSI indicator with comprehensive volume analysis
"""

from typing import List, Dict
from .base import BaseIndicator


class MFIIndicator(BaseIndicator):
    """MFI Indicator with comprehensive volume analysis"""
    
    def default_config(self) -> Dict:
        return {
            'period': 14,
            'overbought': 80,
            'oversold': 20,
            'extreme_overbought': 90,
            'extreme_oversold': 10,
            'description': 'Money Flow Index - Volume-weighted RSI'
        }
    
    def calculate(self, data: List[Dict], index: int, **kwargs) -> Dict:
        period = kwargs.get('period', self.config['period'])
        oversold = kwargs.get('oversold', self.config['oversold'])
        overbought = kwargs.get('overbought', self.config['overbought'])
        extreme_oversold = kwargs.get('extreme_oversold', self.config['extreme_oversold'])
        extreme_overbought = kwargs.get('extreme_overbought', self.config['extreme_overbought'])
        
        if index < period:
            return self._empty_result()
        
        pos_flow, neg_flow = 0, 0
        for i in range(index - period + 1, index + 1):
            tp = (data[i]["high"] + data[i]["low"] + data[i]["close"]) / 3
            prev_tp = (data[i - 1]["high"] + data[i - 1]["low"] + data[i - 1]["close"]) / 3
            mf = tp * data[i]["volume"]
            
            if tp > prev_tp:
                pos_flow += mf
            else:
                neg_flow += mf
        
        ratio = pos_flow / neg_flow if neg_flow > 0 else 100
        mfi_val = 100 - (100 / (1 + ratio)) if neg_flow > 0 else 100
        
        # Determine signal type
        if mfi_val < extreme_oversold:
            signal_type = "STRONG_BUY"
            strength = 100
            is_bullish = True
        elif mfi_val < oversold:
            signal_type = "BUY"
            strength = 75
            is_bullish = True
        elif mfi_val > extreme_overbought:
            signal_type = "STRONG_SELL"
            strength = 100
            is_bullish = False
        elif mfi_val > overbought:
            signal_type = "SELL"
            strength = 75
            is_bullish = False
        else:
            signal_type = "NEUTRAL"
            strength = 50
            is_bullish = False
        
        # Volume confirmation
        avg_volume = sum(d["volume"] for d in data[max(0, index - 20):index + 1]) / min(21, index + 1)
        volume_confirmation = data[index]["volume"] > avg_volume * 1.2
        
        return {
            "bullish": is_bullish,
            "bearish": not is_bullish,
            "value": round(mfi_val, 2),
            "strength": strength if volume_confirmation else strength * 0.75,
            "signal_type": signal_type,
            "confidence": min(abs(mfi_val - 50), 50),
            "trend": "UPTREND" if mfi_val > 50 else "DOWNTREND",
            "reversal_signal": mfi_val < extreme_oversold or mfi_val > extreme_overbought,
            "divergence": False,
            "supporting_signals": [
                f"MFI: {mfi_val:.2f}",
                f"Positive Flow: {pos_flow:.0f}",
                f"Negative Flow: {neg_flow:.0f}",
                f"Volume: {'Above' if volume_confirmation else 'Below'} average"
            ],
            "raw_values": {
                "mfi": mfi_val,
                "positive_flow": pos_flow,
                "negative_flow": neg_flow,
                "flow_ratio": ratio,
                "volume": data[index]["volume"],
                "avg_volume": avg_volume,
                "volume_confirmation": volume_confirmation
            }
        }
    
    def _empty_result(self) -> Dict:
        """Return empty result"""
        return {
            "bullish": False,
            "bearish": False,
            "value": 50,
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
        overbought = self.config['overbought']
        oversold = self.config['oversold']
        
        return f"""// MFI - Money Flow Index
mfi_value = ta.mfi(close, {period})
mfi_bullish = mfi_value < {oversold}
mfi_bearish = mfi_value > {overbought}
mfi_neutral = mfi_value >= {oversold} and mfi_value <= {overbought}"""
        period = self.config['period']
        return f"""// MFI Indicator
mfi_value = ta.mfi(close, {period})
mfi_bullish = mfi_value < {self.config['oversold']}
mfi_bearish = mfi_value > {self.config['overbought']}"""
