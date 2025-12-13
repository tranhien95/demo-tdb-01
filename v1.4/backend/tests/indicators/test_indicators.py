"""Test script to verify indicators module"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from indicators import indicator_manager

print('Total indicators:', len(indicator_manager.list_indicators()))
print('\nIndicators:')
for ind in indicator_manager.list_indicators():
    config = indicator_manager.get_indicator_config(ind)
    desc = config.get('description', 'N/A')
    print(f'  - {ind}: {desc}')

print('\n' + '='*50)
print('Testing indicator calculations...')
print('='*50)

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

# Test a few indicators
test_indicators = ['RSI', 'MACD', 'EMA_50', 'Stochastic', 'Bollinger_Bands']

for ind_name in test_indicators:
    try:
        signal = indicator_manager.calculate_indicator(ind_name, data, 50)
        print(f'\n{ind_name}:')
        print(f'  Bullish: {signal["bullish"]}')
        print(f'  Bearish: {signal["bearish"]}')
        print(f'  Value: {signal["value"]:.2f}')
        print(f'  Strength: {signal["strength"]:.2f}')
    except Exception as e:
        print(f'\n{ind_name}: ERROR - {e}')

print('\n' + '='*50)
print('✅ All indicator tests completed!')
print('='*50)
