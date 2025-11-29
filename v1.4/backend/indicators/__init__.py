"""
Indicators Module
Modular indicator system - Each indicator = 1 file with own config
"""

from .base import BaseIndicator, HelperFunctions

# Core Indicators (each in separate file)
from .rsi import RSIIndicator
from .macd import MACDIndicator
from .stochastic import StochasticIndicator
from .bollinger import BollingerBandsIndicator
from .adx import ADXIndicator

# EMA Indicators
from .ema import EMAIndicator, EMA50Indicator, EMA200Indicator, EMA12Indicator, EMA26Indicator

# Momentum Indicators (each in separate file)
from .cci import CCIIndicator
from .mfi import MFIIndicator
from .roc import ROCIndicator
from .vroc import VROCIndicator
from .rvi import RVIIndicator
from .awesome_oscillator import AwesomeOscillatorIndicator
from .momentum import MomentumIndicator

# Volatility Indicators (each in separate file)
from .atr import ATRIndicator
from .donchian import DonchianIndicator
from .supertrend import SuperTrendIndicator

# Volume Indicators (each in separate file)
from .volume_ma import VolumeMaIndicator
from .obv import OBVIndicator

# Support/Resistance (each in separate file)
from .pivot_points import PivotPointsIndicator

# Advanced Pattern & Concept Indicators
from .triple_ema import TripleEMAIndicator
from .fibonacci import FibonacciIndicator
from .ichimoku import IchimokuIndicator
from .candlestick_patterns import CandlestickPatternsIndicator
from .ict_concepts import ICTConceptsIndicator

# Registry of all available indicators (27 indicators)
INDICATOR_REGISTRY = {
    # Momentum Oscillators
    'RSI': RSIIndicator,
    'MACD': MACDIndicator,
    'Stochastic': StochasticIndicator,
    'CCI': CCIIndicator,
    'MFI': MFIIndicator,
    'ROC': ROCIndicator,
    'VROC': VROCIndicator,
    'RVI': RVIIndicator,
    'Awesome_Oscillator': AwesomeOscillatorIndicator,
    'Momentum': MomentumIndicator,
    
    # Trend Indicators
    'EMA_50': EMA50Indicator,
    'EMA_200': EMA200Indicator,
    'EMA_12': EMA12Indicator,
    'EMA_26': EMA26Indicator,
    'ADX': ADXIndicator,
    'SuperTrend': SuperTrendIndicator,
    
    # Volatility Indicators
    'Bollinger_Bands': BollingerBandsIndicator,
    'ATR': ATRIndicator,
    'Donchian': DonchianIndicator,
    
    # Volume Indicators
    'Volume_MA': VolumeMaIndicator,
    'OBV': OBVIndicator,
    
    # Support/Resistance
    'Pivot_Points': PivotPointsIndicator,
    
    # Advanced Pattern & Concept Indicators
    'Triple_EMA': TripleEMAIndicator,
    'Fibonacci': FibonacciIndicator,
    'Ichimoku': IchimokuIndicator,
    'Candlestick_Patterns': CandlestickPatternsIndicator,
    'ICT_Concepts': ICTConceptsIndicator,
}


class IndicatorManager:
    """Manage and calculate all indicators"""
    
    def __init__(self):
        self.indicators = {}
        self._initialize_indicators()
    
    def _initialize_indicators(self):
        """Initialize all registered indicators"""
        for name, indicator_class in INDICATOR_REGISTRY.items():
            self.indicators[name] = indicator_class()
    
    def get_indicator(self, name: str) -> BaseIndicator:
        """Get indicator instance by name"""
        return self.indicators.get(name)
    
    def calculate_indicator(self, name: str, data: list, index: int, **kwargs) -> dict:
        """Calculate specific indicator"""
        indicator = self.get_indicator(name)
        if indicator:
            return indicator.calculate(data, index, **kwargs)
        return {"bullish": False, "bearish": False, "value": 0, "strength": 0}
    
    def get_all_signals(self, data: list, index: int) -> dict:
        """Get signals from all indicators"""
        signals = {}
        for name, indicator in self.indicators.items():
            signals[name] = indicator.calculate(data, index)
        return signals
    
    def get_pine_script(self, indicator_names: list) -> str:
        """Generate Pine Script code for selected indicators"""
        code = "// ======================== INDICATORS ========================\n"
        for name in indicator_names:
            indicator = self.get_indicator(name)
            if indicator:
                code += indicator.get_pine_script() + "\n\n"
            else:
                code += f"// {name} indicator not found\n\n"
        return code
    
    def list_indicators(self) -> list:
        """List all available indicators"""
        return list(self.indicators.keys())
    
    def get_indicator_config(self, name: str) -> dict:
        """Get indicator configuration"""
        indicator = self.get_indicator(name)
        if indicator:
            return indicator.config
        return {}
    
    def update_indicator_config(self, name: str, config: dict):
        """Update indicator configuration"""
        indicator = self.get_indicator(name)
        if indicator:
            indicator.update_config(config)


# Global indicator manager instance
indicator_manager = IndicatorManager()


# Convenience functions for backward compatibility
def get_all_signals(data: list, index: int) -> dict:
    """Get all indicator signals (backward compatible)"""
    return indicator_manager.get_all_signals(data, index)


def get_pine_script_code(indicators: list) -> str:
    """Generate Pine Script code (backward compatible)"""
    return indicator_manager.get_pine_script(indicators)


__all__ = [
    'BaseIndicator',
    'HelperFunctions',
    'IndicatorManager',
    'indicator_manager',
    'get_all_signals',
    'get_pine_script_code',
    'INDICATOR_REGISTRY',
    # Individual indicators
    'RSIIndicator',
    'MACDIndicator',
    'EMAIndicator',
    'EMA50Indicator',
    'EMA200Indicator',
    'EMA12Indicator',
    'EMA26Indicator',
    'StochasticIndicator',
    'BollingerBandsIndicator',
    'ADXIndicator',
    'TripleEMAIndicator',
    'FibonacciIndicator',
    'IchimokuIndicator',
    'CandlestickPatternsIndicator',
    'ICTConceptsIndicator',
]
