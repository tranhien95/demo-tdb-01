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
            return {"bullish": False, "bearish": False, "value": 0, "strength": 0, "signal_type": "NEUTRAL", "confidence": 0, "trend": "NEUTRAL", "reversal_signal": False, "divergence": False, "supporting_signals": [], "raw_values": {}}
        
        medians = [(d["high"] + d["low"]) / 2 for d in data[:index + 1]]
        fast_ma = sum(medians[index - fast + 1:index + 1]) / fast if index >= fast - 1 else 0
        slow_ma = sum(medians[index - slow + 1:index + 1]) / slow if index >= slow - 1 else 0
        
        ao_val = fast_ma - slow_ma
        prev_ao = 0
        if index > slow:
            prev_fast = sum(medians[index - fast:index]) / fast
            prev_slow = sum(medians[index - slow:index]) / slow
            prev_ao = prev_fast - prev_slow
        
        # Detect zero line crossing
        ao_zero_cross = (prev_ao <= 0 and ao_val > 0) or (prev_ao >= 0 and ao_val < 0)
        
        # AO color (green if positive and increasing, red if negative and decreasing)
        ao_color = "green" if ao_val > 0 else ("red" if ao_val < 0 else "gray")
        
        # Momentum acceleration
        ao_accel = 0
        if index > slow + 1:
            prev_prev_ao = 0
            if index > slow + 1:
                ppf = sum(medians[index - 1 - fast:index - 1]) / fast
                pps = sum(medians[index - 1 - slow:index - 1]) / slow
                prev_prev_ao = ppf - pps
            ao_accel = prev_ao - prev_prev_ao
        
        # Twin peaks pattern (potential reversal)
        twin_peak = False
        if index >= slow + 2:
            if (prev_ao < 0 and ao_val < 0 and abs(prev_ao - ao_val) < abs(prev_ao) * 0.2):
                twin_peak = True
        
        # Determine signal
        is_bullish = ao_val > 0 and ao_val > prev_ao
        strength = min(abs(ao_val) * 10, 100)
        
        if abs(ao_val) > 0.01:
            signal_type = "STRONG_BUY" if (is_bullish and ao_accel > 0) else ("BUY" if is_bullish else ("STRONG_SELL" if (not is_bullish and ao_accel < 0) else "SELL"))
        else:
            signal_type = "NEUTRAL"
        
        trend = "BULLISH" if ao_val > 0 else ("BEARISH" if ao_val < 0 else "NEUTRAL")
        
        return {
            "bullish": is_bullish,
            "bearish": not is_bullish,
            "value": ao_val,
            "strength": strength,
            "signal_type": signal_type,
            "confidence": strength,
            "trend": trend,
            "reversal_signal": ao_zero_cross or twin_peak,
            "divergence": twin_peak,
            "supporting_signals": [
                f"AO: {ao_val:+.6f}",
                f"Trend: {trend}",
                f"Zero line: {'Above' if ao_val > 0 else 'Below'}",
                f"Momentum: {'Accelerating' if ao_accel > 0 else 'Decelerating'}",
                f"Pattern: {'Twin peaks detected!' if twin_peak else 'No twin peaks'}"
            ],
            "raw_values": {
                "ao": ao_val,
                "ao_color": ao_color,
                "above_zero": ao_val > 0,
                "momentum_accel": ao_accel,
                "twin_peak_detected": twin_peak,
                "ao_slope": ao_val - prev_ao
            }
        }
    
    def get_pine_script(self) -> str:
        fast = self.config['fast_period']
        slow = self.config['slow_period']
        return f"""// Awesome Oscillator
ao_value = ta.sma(hl2, {fast}) - ta.sma(hl2, {slow})
ao_bullish = ao_value > 0 and ao_value > ao_value[1]
ao_bearish = ao_value < 0 and ao_value < ao_value[1]"""
