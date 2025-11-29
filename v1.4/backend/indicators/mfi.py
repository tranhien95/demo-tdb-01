"""
MFI - Money Flow Index
Volume-weighted RSI indicator
"""

from typing import List, Dict
from .base import BaseIndicator


class MFIIndicator(BaseIndicator):
    """MFI Indicator with customizable settings"""
    
    def default_config(self) -> Dict:
        return {
            'period': 14,
            'overbought': 80,
            'oversold': 20,
            'description': 'Money Flow Index - Volume-weighted RSI'
        }
    
    def calculate(self, data: List[Dict], index: int, **kwargs) -> Dict:
        period = kwargs.get('period', self.config['period'])
        oversold = kwargs.get('oversold', self.config['oversold'])
        overbought = kwargs.get('overbought', self.config['overbought'])
        
        if index < period:
            return {"bullish": False, "bearish": False, "value": 50, "strength": 0}
        
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
        mfi_val = 100 - (100 / (1 + ratio))
        
        return {
            "bullish": mfi_val < oversold,
            "bearish": mfi_val > overbought,
            "value": mfi_val,
            "strength": abs(50 - mfi_val) / 50 * 100
        }
    
    def get_pine_script(self) -> str:
        period = self.config['period']
        return f"""// MFI Indicator
mfi_value = ta.mfi(close, {period})
mfi_bullish = mfi_value < {self.config['oversold']}
mfi_bearish = mfi_value > {self.config['overbought']}"""
