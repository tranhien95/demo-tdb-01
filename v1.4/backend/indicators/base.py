"""
Base Indicator Class
All indicators inherit from this base class
"""

from typing import List, Dict, Optional
from abc import ABC, abstractmethod


class BaseIndicator(ABC):
    """Abstract base class for all indicators"""
    
    def __init__(self):
        self.config = self.default_config()
    
    @abstractmethod
    def default_config(self) -> Dict:
        """Return default configuration for the indicator"""
        pass
    
    @abstractmethod
    def calculate(self, data: List[Dict], index: int, **kwargs) -> Dict:
        """
        Calculate indicator value and signals
        
        Returns:
            Dict with comprehensive indicator data:
            - bullish: bool (basic bullish signal)
            - bearish: bool (basic bearish signal)
            - value: float (main indicator value)
            - strength: float (0-100, signal strength)
            - signal_type: str (STRONG_BUY, BUY, NEUTRAL, SELL, STRONG_SELL)
            - confidence: float (0-100, confidence level)
            - trend: str (UPTREND, DOWNTREND, SIDEWAYS)
            - reversal_signal: bool (potential reversal detected)
            - divergence: bool (bullish/bearish divergence detected)
            - supporting_signals: list (additional signals)
            - raw_values: dict (all calculated values)
        """
        pass
    
    @abstractmethod
    def get_pine_script(self) -> str:
        """Return Pine Script code for the indicator"""
        pass
    
    def _validate_input(self, data: List[Dict], index: int) -> bool:
        """
        Validate input data before calculation
        
        Args:
            data: List of OHLCV dictionaries
            index: Current index to calculate
            
        Returns:
            True if input is valid, False otherwise
        """
        if not data or len(data) == 0:
            return False
        
        if index < 0 or index >= len(data):
            return False
        
        required_keys = ['open', 'high', 'low', 'close', 'volume']
        if not all(key in data[index] for key in required_keys):
            return False
        
        # Check for None/invalid values
        for key in ['high', 'low', 'close']:
            value = data[index].get(key)
            if value is None or (isinstance(value, (int, float)) and value <= 0):
                return False
        
        # Check high >= low
        if data[index]['high'] < data[index]['low']:
            return False
        
        # Check close is within high/low range
        if not (data[index]['low'] <= data[index]['close'] <= data[index]['high']):
            return False
        
        return True
    
    def calculate_safe(self, data: List[Dict], index: int, **kwargs) -> Dict:
        """
        Safe wrapper for calculate with validation and error handling
        
        Args:
            data: List of OHLCV dictionaries
            index: Current index to calculate
            **kwargs: Indicator-specific parameters
            
        Returns:
            Dict with indicator data or empty result on error
        """
        try:
            if not self._validate_input(data, index):
                return self._empty_result()
            
            return self.calculate(data, index, **kwargs)
        except Exception as e:
            from utils.logger import get_logger
            logger = get_logger(self.__class__.__name__)
            logger.error(f"Error in {self.__class__.__name__}.calculate(): {e}", exc_info=True)
            return self._empty_result()
    
    def _empty_result(self) -> Dict:
        """
        Return standard empty result
        
        Returns:
            Dict with default empty values
        """
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
    
    def get_name(self) -> str:
        """Return indicator name"""
        return self.__class__.__name__.replace('Indicator', '')
    
    def update_config(self, config: Dict):
        """Update indicator configuration"""
        self.config.update(config)


class HelperFunctions:
    """Helper functions for indicator calculations"""
    
    @staticmethod
    def sma(data: List[float], period: int) -> List[Optional[float]]:
        """Simple Moving Average"""
        sma = []
        for i in range(len(data)):
            if i < period - 1:
                sma.append(None)
            else:
                avg = sum(data[i - period + 1:i + 1]) / period
                sma.append(avg)
        return sma

    @staticmethod
    def ema(data: List[float], period: int) -> List[Optional[float]]:
        """Exponential Moving Average"""
        ema = []
        multiplier = 2 / (period + 1)
        
        for i in range(len(data)):
            if i < period - 1:
                ema.append(None)
            elif i == period - 1:
                ema.append(sum(data[:period]) / period)
            else:
                prev_ema = ema[i - 1]
                new_ema = data[i] * multiplier + prev_ema * (1 - multiplier)
                ema.append(new_ema)
        
        return ema
    
    @staticmethod
    def atr(data: List[Dict], index: int, period: int = 14) -> float:
        """Average True Range"""
        if index < period:
            return 0
        
        tr_sum = 0
        for i in range(index - period + 1, index + 1):
            prev_close = data[i - 1]["close"] if i > 0 else data[i]["close"]
            tr = max(
                data[i]["high"] - data[i]["low"],
                abs(data[i]["high"] - prev_close),
                abs(data[i]["low"] - prev_close)
            )
            tr_sum += tr
        
        return tr_sum / period
