"""
Awesome Oscillator
Bill Williams' momentum indicator
"""

from typing import List, Dict
from .base import BaseIndicator


class AwesomeOscillatorIndicator(BaseIndicator):
    """Awesome Oscillator with customizable settings"""
    
    def default_config(self) -> Dict:
        return {
            'fast_period': 5,
            'slow_period': 34,
            'description': 'Awesome Oscillator - Bill Williams'
        }
    
    def calculate(self, data: List[Dict], index: int, **kwargs) -> Dict:
        fast = kwargs.get('fast_period', self.config['fast_period'])
        slow = kwargs.get('slow_period', self.config['slow_period'])
        
        if index < slow:
            return {"bullish": False, "bearish": False, "value": 0, "strength": 0}
        
        medians = [(d["high"] + d["low"]) / 2 for d in data[:index + 1]]
        fast_ma = sum(medians[index - fast + 1:index + 1]) / fast if index >= fast - 1 else 0
        slow_ma = sum(medians[index - slow + 1:index + 1]) / slow if index >= slow - 1 else 0
        
        ao_val = fast_ma - slow_ma
        prev_ao = 0
        if index > slow:
            prev_fast = sum(medians[index - fast:index]) / fast
            prev_slow = sum(medians[index - slow:index]) / slow
            prev_ao = prev_fast - prev_slow
        
        return {
            "bullish": ao_val > 0 and ao_val > prev_ao,
            "bearish": ao_val < 0 and ao_val < prev_ao,
            "value": ao_val,
            "strength": abs(ao_val) * 10
        }
    
    def get_pine_script(self) -> str:
        fast = self.config['fast_period']
        slow = self.config['slow_period']
        return f"""// Awesome Oscillator
ao_value = ta.sma(hl2, {fast}) - ta.sma(hl2, {slow})
ao_bullish = ao_value > 0 and ao_value > ao_value[1]
ao_bearish = ao_value < 0 and ao_value < ao_value[1]"""
