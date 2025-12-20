"""
Aroon Indicator
Measures trend strength and identifies trend changes
Consists of Aroon Up and Aroon Down (0-100)
"""

from typing import List, Dict
from .base import BaseIndicator


class AroonIndicator(BaseIndicator):
    """Aroon Indicator"""
    
    def default_config(self) -> Dict:
        return {
            'period': 14,
            'aroon_up_threshold': 70,
            'aroon_down_threshold': 70,
            'description': 'Aroon Indicator - Trend strength'
        }
    
    def calculate(self, data: List[Dict], index: int, **kwargs) -> Dict:
        """Calculate Aroon Indicator"""
        period = kwargs.get('period', self.config['period'])
        aroon_up_threshold = kwargs.get('aroon_up_threshold', self.config['aroon_up_threshold'])
        aroon_down_threshold = kwargs.get('aroon_down_threshold', self.config['aroon_down_threshold'])
        
        if index < period - 1:
            return self._empty_result()
        
        # Get period data
        period_data = data[index - period + 1:index + 1]
        
        # Find highest high and lowest low positions
        highest_high = max([d["high"] for d in period_data])
        lowest_low = min([d["low"] for d in period_data])
        
        # Find positions (periods ago) of highest high and lowest low
        highest_pos = period - 1
        lowest_pos = period - 1
        
        for i in range(len(period_data) - 1, -1, -1):
            if period_data[i]["high"] == highest_high:
                highest_pos = len(period_data) - 1 - i
                break
        
        for i in range(len(period_data) - 1, -1, -1):
            if period_data[i]["low"] == lowest_low:
                lowest_pos = len(period_data) - 1 - i
                break
        
        # Calculate Aroon Up and Aroon Down
        # Formula: Aroon = ((period - periods since highest/lowest) / period) * 100
        aroon_up = ((period - highest_pos) / period) * 100
        aroon_down = ((period - lowest_pos) / period) * 100
        
        # Calculate Aroon Oscillator (Aroon Up - Aroon Down)
        aroon_oscillator = aroon_up - aroon_down
        
        # Determine signal type
        if aroon_up > aroon_up_threshold and aroon_down < 50:
            signal_type = "STRONG_BUY"
            signal_strength = min(aroon_up, 100)
            is_bullish = True
        elif aroon_up > 50 and aroon_oscillator > 0:
            signal_type = "BUY"
            signal_strength = min(aroon_up * 0.75, 75)
            is_bullish = True
        elif aroon_down > aroon_down_threshold and aroon_up < 50:
            signal_type = "STRONG_SELL"
            signal_strength = min(aroon_down, 100)
            is_bullish = False
        elif aroon_down > 50 and aroon_oscillator < 0:
            signal_type = "SELL"
            signal_strength = min(aroon_down * 0.75, 75)
            is_bullish = False
        else:
            signal_type = "NEUTRAL"
            signal_strength = abs(aroon_oscillator) / 2
            is_bullish = False
        
        # Check for Aroon crossover (trend change signal)
        crossover = False
        if index >= period:
            prev_period_data = data[index - period:index]
            prev_highest = max([d["high"] for d in prev_period_data])
            prev_lowest = min([d["low"] for d in prev_period_data])
            
            prev_highest_pos = period - 1
            prev_lowest_pos = period - 1
            for i in range(len(prev_period_data) - 1, -1, -1):
                if prev_period_data[i]["high"] == prev_highest:
                    prev_highest_pos = len(prev_period_data) - 1 - i
                    break
            for i in range(len(prev_period_data) - 1, -1, -1):
                if prev_period_data[i]["low"] == prev_lowest:
                    prev_lowest_pos = len(prev_period_data) - 1 - i
                    break
            
            prev_aroon_up = ((period - prev_highest_pos) / period) * 100
            prev_aroon_down = ((period - prev_lowest_pos) / period) * 100
            prev_oscillator = prev_aroon_up - prev_aroon_down
            
            # Crossover when oscillator crosses zero
            crossover = (prev_oscillator < 0 and aroon_oscillator > 0) or (prev_oscillator > 0 and aroon_oscillator < 0)
        
        # Trend classification
        if aroon_up > aroon_down:
            trend = "UPTREND"
        elif aroon_down > aroon_up:
            trend = "DOWNTREND"
        else:
            trend = "SIDEWAYS"
        
        return {
            "bullish": is_bullish,
            "bearish": not is_bullish,
            "value": round(aroon_oscillator, 2),
            "strength": signal_strength,
            "signal_type": signal_type,
            "confidence": min(abs(aroon_oscillator), 100),
            "trend": trend,
            "reversal_signal": crossover,
            "divergence": False,
            "supporting_signals": [
                f"Aroon Up: {aroon_up:.1f}",
                f"Aroon Down: {aroon_down:.1f}",
                f"Oscillator: {aroon_oscillator:+.1f}",
                f"{'Strong uptrend' if aroon_up > aroon_up_threshold else 'Strong downtrend' if aroon_down > aroon_down_threshold else 'Sideways'}"
            ],
            "raw_values": {
                "aroon_up": aroon_up,
                "aroon_down": aroon_down,
                "aroon_oscillator": aroon_oscillator,
                "highest_pos": highest_pos,
                "lowest_pos": lowest_pos
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
        
        return f"""// Aroon Indicator
[aroon_up, aroon_down] = ta.aroon({period})
aroon_oscillator = aroon_up - aroon_down
aroon_bullish = aroon_up > aroon_down and aroon_up > 50
aroon_bearish = aroon_down > aroon_up and aroon_down > 50"""

