"""
Indicator Config Variants
Predefined configuration variants for testing multiple parameter sets
"""

from typing import List, Dict, Any

# Config variants for each indicator
INDICATOR_CONFIG_VARIANTS: Dict[str, List[Dict[str, Any]]] = {
    'RSI': [
        {'period': 14, 'overbought': 70, 'oversold': 30, 'name': 'RSI(14,70,30)'},
        {'period': 14, 'overbought': 75, 'oversold': 25, 'name': 'RSI(14,75,25)'},
        {'period': 14, 'overbought': 80, 'oversold': 20, 'name': 'RSI(14,80,20)'},
        {'period': 21, 'overbought': 70, 'oversold': 30, 'name': 'RSI(21,70,30)'},
        {'period': 9, 'overbought': 70, 'oversold': 30, 'name': 'RSI(9,70,30)'},
    ],
    
    'MACD': [
        {'fast_period': 12, 'slow_period': 26, 'signal_period': 9, 'name': 'MACD(12,26,9)'},
        {'fast_period': 8, 'slow_period': 21, 'signal_period': 5, 'name': 'MACD(8,21,5)'},
        {'fast_period': 12, 'slow_period': 26, 'signal_period': 12, 'name': 'MACD(12,26,12)'},
        {'fast_period': 19, 'slow_period': 39, 'signal_period': 9, 'name': 'MACD(19,39,9)'},
    ],
    
    'Stochastic': [
        {'period': 14, 'k_period': 3, 'd_period': 3, 'overbought': 80, 'oversold': 20, 'name': 'Stoch(14,3,3,80,20)'},
        {'period': 14, 'k_period': 5, 'd_period': 3, 'overbought': 80, 'oversold': 20, 'name': 'Stoch(14,5,3,80,20)'},
        {'period': 21, 'k_period': 3, 'd_period': 3, 'overbought': 80, 'oversold': 20, 'name': 'Stoch(21,3,3,80,20)'},
        {'period': 14, 'k_period': 3, 'd_period': 3, 'overbought': 75, 'oversold': 25, 'name': 'Stoch(14,3,3,75,25)'},
    ],
    
    'Bollinger_Bands': [
        {'period': 20, 'std_dev': 2, 'name': 'BB(20,2)'},
        {'period': 20, 'std_dev': 2.5, 'name': 'BB(20,2.5)'},
        {'period': 20, 'std_dev': 1.5, 'name': 'BB(20,1.5)'},
        {'period': 15, 'std_dev': 2, 'name': 'BB(15,2)'},
        {'period': 25, 'std_dev': 2, 'name': 'BB(25,2)'},
    ],
    
    'ATR': [
        {'period': 14, 'threshold': 0.5, 'name': 'ATR(14,0.5)'},
        {'period': 14, 'threshold': 1.0, 'name': 'ATR(14,1.0)'},
        {'period': 21, 'threshold': 0.5, 'name': 'ATR(21,0.5)'},
        {'period': 10, 'threshold': 0.5, 'name': 'ATR(10,0.5)'},
    ],
    
    'CCI': [
        {'period': 20, 'name': 'CCI(20)'},
        {'period': 14, 'name': 'CCI(14)'},
        {'period': 30, 'name': 'CCI(30)'},
    ],
    
    'ADX': [
        {'period': 14, 'name': 'ADX(14)'},
        {'period': 21, 'name': 'ADX(21)'},
        {'period': 10, 'name': 'ADX(10)'},
    ],
    
    'SuperTrend': [
        {'period': 10, 'multiplier': 3.0, 'name': 'SuperTrend(10,3.0)'},
        {'period': 10, 'multiplier': 2.5, 'name': 'SuperTrend(10,2.5)'},
        {'period': 14, 'multiplier': 3.0, 'name': 'SuperTrend(14,3.0)'},
        {'period': 7, 'multiplier': 3.0, 'name': 'SuperTrend(7,3.0)'},
    ],
    
    'Donchian': [
        {'period': 20, 'name': 'Donchian(20)'},
        {'period': 14, 'name': 'Donchian(14)'},
        {'period': 30, 'name': 'Donchian(30)'},
    ],
    
    'MFI': [
        {'period': 14, 'name': 'MFI(14)'},
        {'period': 21, 'name': 'MFI(21)'},
        {'period': 9, 'name': 'MFI(9)'},
    ],
    
    'ROC': [
        {'period': 12, 'name': 'ROC(12)'},
        {'period': 14, 'name': 'ROC(14)'},
        {'period': 10, 'name': 'ROC(10)'},
    ],
    
    'Momentum': [
        {'period': 10, 'name': 'Momentum(10)'},
        {'period': 14, 'name': 'Momentum(14)'},
        {'period': 20, 'name': 'Momentum(20)'},
    ],
    
    'SMA': [
        {'period': 20, 'name': 'SMA(20)'},
        {'period': 50, 'name': 'SMA(50)'},
        {'period': 100, 'name': 'SMA(100)'},
        {'period': 200, 'name': 'SMA(200)'},
    ],
    
    'Williams_R': [
        {'period': 14, 'overbought': -20, 'oversold': -80, 'name': 'Williams_R(14,-20,-80)'},
        {'period': 14, 'overbought': -10, 'oversold': -90, 'name': 'Williams_R(14,-10,-90)'},
        {'period': 21, 'overbought': -20, 'oversold': -80, 'name': 'Williams_R(21,-20,-80)'},
        {'period': 9, 'overbought': -20, 'oversold': -80, 'name': 'Williams_R(9,-20,-80)'},
    ],
    
    'Parabolic_SAR': [
        {'af_start': 0.02, 'af_increment': 0.02, 'af_max': 0.2, 'name': 'Parabolic_SAR(0.02,0.02,0.2)'},
        {'af_start': 0.02, 'af_increment': 0.02, 'af_max': 0.1, 'name': 'Parabolic_SAR(0.02,0.02,0.1)'},
        {'af_start': 0.01, 'af_increment': 0.01, 'af_max': 0.2, 'name': 'Parabolic_SAR(0.01,0.01,0.2)'},
        {'af_start': 0.02, 'af_increment': 0.02, 'af_max': 0.3, 'name': 'Parabolic_SAR(0.02,0.02,0.3)'},
    ],
    
    'Aroon': [
        {'period': 14, 'aroon_up_threshold': 70, 'aroon_down_threshold': 70, 'name': 'Aroon(14,70,70)'},
        {'period': 14, 'aroon_up_threshold': 80, 'aroon_down_threshold': 80, 'name': 'Aroon(14,80,80)'},
        {'period': 21, 'aroon_up_threshold': 70, 'aroon_down_threshold': 70, 'name': 'Aroon(21,70,70)'},
        {'period': 10, 'aroon_up_threshold': 70, 'aroon_down_threshold': 70, 'name': 'Aroon(10,70,70)'},
    ],
}

# Indicators that don't need variants (use default only)
INDICATORS_WITHOUT_VARIANTS = [
    'SMA_50', 'SMA_200',  # Fixed periods
    'EMA_50', 'EMA_200', 'EMA_12', 'EMA_26',  # Fixed periods
    'Volume_MA', 'OBV',  # Simple indicators
    'Pivot_Points', 'Fibonacci', 'Ichimoku',  # Complex indicators with fixed logic
    'Candlestick_Patterns', 'ICT_Concepts',  # Pattern recognition
    'Triple_EMA', 'VROC', 'RVI', 'Awesome_Oscillator',  # Can add later if needed
]


def get_indicator_variants(indicator_name: str) -> List[Dict[str, Any]]:
    """
    Get all config variants for an indicator
    
    Returns:
        List of config dicts, each with a 'name' field for display
        If no variants, returns list with default config
    """
    if indicator_name in INDICATOR_CONFIG_VARIANTS:
        return INDICATOR_CONFIG_VARIANTS[indicator_name]
    else:
        # Return default config (will be handled by indicator's default_config)
        return [{'name': indicator_name, 'use_default': True}]


def generate_indicator_with_configs(indicator_name: str) -> List[Dict[str, Any]]:
    """
    Generate list of indicator configs to test
    
    Returns:
        List of dicts with format: {
            'indicator_name': str,
            'config': dict,
            'display_name': str  # e.g., "RSI(14,70,30)"
        }
    """
    variants = get_indicator_variants(indicator_name)
    result = []
    
    for variant in variants:
        if variant.get('use_default'):
            # Use default config
            result.append({
                'indicator_name': indicator_name,
                'config': {},
                'display_name': indicator_name
            })
        else:
            # Use variant config
            config = {k: v for k, v in variant.items() if k != 'name'}
            result.append({
                'indicator_name': indicator_name,
                'config': config,
                'display_name': variant.get('name', indicator_name)
            })
    
    return result

