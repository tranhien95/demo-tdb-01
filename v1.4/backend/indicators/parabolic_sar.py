"""
Parabolic SAR (Stop and Reverse)
Trend-following indicator that provides entry and exit points
"""

from typing import List, Dict
from .base import BaseIndicator


class ParabolicSARIndicator(BaseIndicator):
    """Parabolic SAR Indicator"""
    
    def default_config(self) -> Dict:
        return {
            'af_start': 0.02,  # Acceleration Factor start
            'af_increment': 0.02,  # Acceleration Factor increment
            'af_max': 0.2,  # Acceleration Factor maximum
            'description': 'Parabolic SAR - Stop and Reverse'
        }
    
    def calculate(self, data: List[Dict], index: int, **kwargs) -> Dict:
        """Calculate Parabolic SAR"""
        af_start = kwargs.get('af_start', self.config['af_start'])
        af_increment = kwargs.get('af_increment', self.config['af_increment'])
        af_max = kwargs.get('af_max', self.config['af_max'])
        
        if index < 2:
            return self._empty_result()
        
        # Initialize SAR
        sar = None
        ep = None  # Extreme Point
        af = af_start  # Acceleration Factor
        trend = None  # 'UP' or 'DOWN'
        
        # Calculate SAR for all previous periods to get current value
        for i in range(1, index + 1):
            if i == 1:
                # Initial SAR
                sar = data[i - 1]["low"]
                ep = data[i - 1]["high"]
                trend = 'UP'
            else:
                prev_high = data[i - 1]["high"]
                prev_low = data[i - 1]["low"]
                current_high = data[i]["high"]
                current_low = data[i]["low"]
                
                if trend == 'UP':
                    # Update SAR
                    sar = sar + af * (ep - sar)
                    sar = min(sar, data[i - 1]["low"], data[i - 2]["low"] if i >= 2 else sar)
                    
                    # Check for reversal
                    if current_low < sar:
                        trend = 'DOWN'
                        sar = ep
                        ep = current_low
                        af = af_start
                    else:
                        # Update EP and AF
                        if current_high > ep:
                            ep = current_high
                            af = min(af + af_increment, af_max)
                else:  # trend == 'DOWN'
                    # Update SAR
                    sar = sar + af * (ep - sar)
                    sar = max(sar, data[i - 1]["high"], data[i - 2]["high"] if i >= 2 else sar)
                    
                    # Check for reversal
                    if current_high > sar:
                        trend = 'UP'
                        sar = ep
                        ep = current_high
                        af = af_start
                    else:
                        # Update EP and AF
                        if current_low < ep:
                            ep = current_low
                            af = min(af + af_increment, af_max)
        
        current_price = data[index]["close"]
        distance_percent = abs(current_price - sar) / sar * 100 if sar > 0 else 0
        
        # Determine signal type
        if trend == 'UP':
            if current_price > sar:
                signal_type = "BUY"
                signal_strength = min(distance_percent * 10, 100)
                is_bullish = True
            else:
                signal_type = "SELL"  # Reversal signal
                signal_strength = 100
                is_bullish = False
        else:  # trend == 'DOWN'
            if current_price < sar:
                signal_type = "SELL"
                signal_strength = min(distance_percent * 10, 100)
                is_bullish = False
            else:
                signal_type = "BUY"  # Reversal signal
                signal_strength = 100
                is_bullish = True
        
        # Check for reversal (SAR flip)
        reversal = False
        if index > 0:
            prev_trend = 'UP' if data[index - 1]["close"] > sar else 'DOWN'
            reversal = (trend != prev_trend) if prev_trend else False
        
        return {
            "bullish": is_bullish,
            "bearish": not is_bullish,
            "value": round(sar, 2),
            "strength": signal_strength,
            "signal_type": signal_type,
            "confidence": min(distance_percent * 20, 100),
            "trend": "UPTREND" if trend == 'UP' else "DOWNTREND",
            "reversal_signal": reversal,
            "divergence": False,
            "supporting_signals": [
                f"SAR: {sar:.2f}",
                f"Trend: {trend}",
                f"Price {'above' if current_price > sar else 'below'} SAR",
                f"AF: {af:.3f}"
            ],
            "raw_values": {
                "sar": sar,
                "extreme_point": ep,
                "acceleration_factor": af,
                "trend": trend,
                "distance_percent": distance_percent
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
        af_start = self.config['af_start']
        af_increment = self.config['af_increment']
        af_max = self.config['af_max']
        
        return f"""// Parabolic SAR Indicator
sar = ta.sar({af_start}, {af_increment}, {af_max})
sar_bullish = close > sar
sar_bearish = close < sar"""

