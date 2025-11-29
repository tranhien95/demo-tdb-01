"""
Volume MA - Volume Moving Average
Compares current volume to average
"""

from typing import List, Dict
from .base import BaseIndicator


class VolumeMaIndicator(BaseIndicator):
    """Volume Moving Average with customizable settings"""
    
    def default_config(self) -> Dict:
        return {
            'period': 20,
            'volume_multiplier': 1.2,
            'description': 'Volume Moving Average'
        }
    
    def calculate(self, data: List[Dict], index: int, **kwargs) -> Dict:
        period = kwargs.get('period', self.config['period'])
        multiplier = kwargs.get('volume_multiplier', self.config['volume_multiplier'])
        
        if index < period:
            return {"bullish": False, "bearish": False, "value": 0, "strength": 0}
        
        vol_ma = sum(d["volume"] for d in data[index - period + 1:index + 1]) / period
        
        return {
            "bullish": data[index]["volume"] > vol_ma * multiplier,
            "bearish": data[index]["volume"] < vol_ma / multiplier,
            "value": vol_ma,
            "strength": abs(data[index]["volume"] - vol_ma) / vol_ma * 100
        }
    
    def get_pine_script(self) -> str:
        period = self.config['period']
        return f"""// Volume MA
vol_ma = ta.sma(volume, {period})
vol_bullish = volume > vol_ma * {self.config['volume_multiplier']}
vol_bearish = volume < vol_ma / {self.config['volume_multiplier']}"""
