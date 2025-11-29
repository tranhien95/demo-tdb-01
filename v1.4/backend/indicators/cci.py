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
            return {"bullish": False, "bearish": False, "value": 0, "strength": 0}
        
        tp_list = [(d["high"] + d["low"] + d["close"]) / 3 for d in data[index - period + 1:index + 1]]
        sma_tp = sum(tp_list) / period
        tp = (data[index]["high"] + data[index]["low"] + data[index]["close"]) / 3
        
        mad = sum(abs(tp - sma_tp) for tp in tp_list) / period
        cci_val = (tp - sma_tp) / (0.015 * mad) if mad > 0 else 0
        
        return {
            "bullish": cci_val < oversold,
            "bearish": cci_val > overbought,
            "value": cci_val,
            "strength": abs(cci_val) / 200 * 100
        }
    
    def get_pine_script(self) -> str:
        period = self.config['period']
        return f"""// CCI Indicator
cci_value = ta.cci(close, {period})
cci_bullish = cci_value < {self.config['oversold']}
cci_bearish = cci_value > {self.config['overbought']}"""
