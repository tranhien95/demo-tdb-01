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
            Dict with keys: bullish, bearish, value, strength
        """
        pass
    
    @abstractmethod
    def get_pine_script(self) -> str:
        """Return Pine Script code for the indicator"""
        pass
    
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
