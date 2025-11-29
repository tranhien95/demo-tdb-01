"""
OBV - On Balance Volume
Cumulative volume indicator
"""

from typing import List, Dict
from .base import BaseIndicator


class OBVIndicator(BaseIndicator):
    """On Balance Volume with customizable settings"""
    
    def default_config(self) -> Dict:
        return {
            'description': 'On Balance Volume - Cumulative volume indicator'
        }
    
    def calculate(self, data: List[Dict], index: int, **kwargs) -> Dict:
        obv_val = 0
        for i in range(1, index + 1):
            if data[i]["close"] > data[i - 1]["close"]:
                obv_val += data[i]["volume"]
            elif data[i]["close"] < data[i - 1]["close"]:
                obv_val -= data[i]["volume"]
        
        prev_obv = 0
        if index > 1:
            for i in range(1, index):
                if data[i]["close"] > data[i - 1]["close"]:
                    prev_obv += data[i]["volume"]
                elif data[i]["close"] < data[i - 1]["close"]:
                    prev_obv -= data[i]["volume"]
        
        return {
            "bullish": obv_val > prev_obv,
            "bearish": obv_val < prev_obv,
            "value": obv_val,
            "strength": 50
        }
    
    def get_pine_script(self) -> str:
        return """// OBV Indicator
obv_value = ta.obv
obv_bullish = obv_value > obv_value[1]
obv_bearish = obv_value < obv_value[1]"""
