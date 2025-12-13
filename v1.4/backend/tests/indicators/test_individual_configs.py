"""
Test individual indicator configs
Demonstrate that each indicator has its own configurable parameters
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from indicators import indicator_manager

print("="*70)
print("TESTING INDIVIDUAL INDICATOR CONFIGS")
print("="*70)

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

# Test RSI with different periods
print("\n1. RSI với periods khác nhau:")
print("-" * 70)

for period in [10, 14, 21]:
    signal = indicator_manager.calculate_indicator('RSI', data, 50, period=period)
    print(f"   RSI({period}): Value={signal['value']:.2f}, Bullish={signal['bullish']}, Bearish={signal['bearish']}")

# Test MACD with different settings
print("\n2. MACD với settings khác nhau:")
print("-" * 70)

configs = [
    {'fast_period': 12, 'slow_period': 26, 'signal_period': 9},
    {'fast_period': 5, 'slow_period': 35, 'signal_period': 5},
]

for config in configs:
    signal = indicator_manager.calculate_indicator('MACD', data, 50, **config)
    print(f"   MACD({config['fast_period']},{config['slow_period']},{config['signal_period']}): Value={signal['value']:.2f}")

# Test EMA with different periods
print("\n3. EMA với periods khác nhau:")
print("-" * 70)

# Update EMA_50 config to 100
indicator_manager.update_indicator_config('EMA_50', {'period': 100})
signal_50 = indicator_manager.calculate_indicator('EMA_50', data, 50)
print(f"   EMA_50 (changed to 100): Value={signal_50['value']:.2f}")

# Reset back
indicator_manager.update_indicator_config('EMA_50', {'period': 50})
signal_50_reset = indicator_manager.calculate_indicator('EMA_50', data, 50)
print(f"   EMA_50 (reset to 50): Value={signal_50_reset['value']:.2f}")

# Test CCI with different periods
print("\n4. CCI với periods khác nhau:")
print("-" * 70)

for period in [14, 20, 30]:
    signal = indicator_manager.calculate_indicator('CCI', data, 50, period=period)
    print(f"   CCI({period}): Value={signal['value']:.2f}")

# Test Volume_MA with different settings
print("\n5. Volume_MA với settings khác nhau:")
print("-" * 70)

for period, multiplier in [(10, 1.2), (20, 1.5), (30, 2.0)]:
    signal = indicator_manager.calculate_indicator(
        'Volume_MA', data, 50, 
        period=period, 
        volume_multiplier=multiplier
    )
    print(f"   Volume_MA(period={period}, mult={multiplier}): Bullish={signal['bullish']}")

# Test SuperTrend with different settings
print("\n6. SuperTrend với settings khác nhau:")
print("-" * 70)

for period, multiplier in [(7, 2.0), (10, 3.0), (14, 4.0)]:
    signal = indicator_manager.calculate_indicator(
        'SuperTrend', data, 50,
        period=period,
        multiplier=multiplier
    )
    print(f"   SuperTrend(period={period}, mult={multiplier}): Value={signal['value']:.2f}")

# Test ATR with different periods
print("\n7. ATR với periods khác nhau:")
print("-" * 70)

for period in [10, 14, 20]:
    signal = indicator_manager.calculate_indicator('ATR', data, 50, period=period)
    print(f"   ATR({period}): Value={signal['value']:.2f}")

# Test Donchian with different periods
print("\n8. Donchian với periods khác nhau:")
print("-" * 70)

for period in [10, 20, 50]:
    signal = indicator_manager.calculate_indicator('Donchian', data, 50, period=period)
    print(f"   Donchian({period}): Value={signal['value']:.2f}")

print("\n" + "="*70)
print("✅ MỖI INDICATOR CÓ CONFIG RIÊNG VÀ CÓ THỂ CUSTOMIZE!")
print("="*70)
print("\nLưu ý:")
print("  - Mỗi indicator nằm trong 1 file riêng biệt")
print("  - Config có thể thay đổi runtime")
print("  - Parameters có thể override khi calculate")
print("  - Mỗi indicator độc lập hoàn toàn")
