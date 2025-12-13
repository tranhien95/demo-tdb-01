"""
Test custom indicators from examples.py
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from indicators import indicator_manager, INDICATOR_REGISTRY
from indicators.examples import CustomRSI_EMAIndicator, TrendFollowingIndicator

# Đăng ký custom indicators
INDICATOR_REGISTRY['Custom_RSI_EMA'] = CustomRSI_EMAIndicator
INDICATOR_REGISTRY['Trend_Following'] = TrendFollowingIndicator

# Re-initialize manager
indicator_manager._initialize_indicators()

print("="*60)
print("Custom Indicators Test")
print("="*60)
print("\nAvailable indicators:", len(indicator_manager.list_indicators()))
print("Custom indicators: Custom_RSI_EMA, Trend_Following")

# Sample data
data = []
for i in range(100):
    data.append({
        'open': 100 + i * 0.1,
        'high': 105 + i * 0.1,
        'low': 95 + i * 0.1,
        'close': 102 + i * 0.1,
        'volume': 1000 + i * 10
    })

print("\n" + "="*60)
print("Testing Custom_RSI_EMA Indicator")
print("="*60)

# Calculate signal
signal = indicator_manager.calculate_indicator('Custom_RSI_EMA', data, 50)
print(f"\nBullish: {signal['bullish']}")
print(f"Bearish: {signal['bearish']}")
print(f"Strength: {signal['strength']:.2f}")
print(f"Metadata: {signal.get('metadata', {})}")

# Get config
config = indicator_manager.get_indicator_config('Custom_RSI_EMA')
print(f"\nCurrent Config:")
for key, value in config.items():
    print(f"  {key}: {value}")

# Get Pine Script
pine_code = indicator_manager.get_pine_script(['Custom_RSI_EMA'])
print("\nPine Script Code:")
print(pine_code)

print("\n" + "="*60)
print("Testing Trend_Following Indicator")
print("="*60)

signal2 = indicator_manager.calculate_indicator('Trend_Following', data, 50)
print(f"\nBullish: {signal2['bullish']}")
print(f"Bearish: {signal2['bearish']}")
print(f"Strength: {signal2['strength']:.2f}")
print(f"Metadata: {signal2.get('metadata', {})}")

config2 = indicator_manager.get_indicator_config('Trend_Following')
print(f"\nCurrent Config:")
for key, value in config2.items():
    print(f"  {key}: {value}")

print("\n" + "="*60)
print("Test completed successfully!")
print("="*60)
