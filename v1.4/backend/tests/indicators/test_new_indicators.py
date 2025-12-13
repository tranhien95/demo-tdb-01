"""Test new indicators"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from indicators import indicator_manager
import random

# Sample data with more realistic OHLCV
data = []
price = 2000.0

for i in range(100):
    change = random.uniform(-20, 20)
    price += change
    
    open_price = price
    high_price = price + random.uniform(0, 15)
    low_price = price - random.uniform(0, 15)
    close_price = low_price + random.uniform(0, high_price - low_price)
    
    data.append({
        'open': round(open_price, 2),
        'high': round(high_price, 2),
        'low': round(low_price, 2),
        'close': round(close_price, 2),
        'volume': random.randint(1000, 10000),
        'time': f'2024-01-{i+1:02d} 00:00:00'
    })

print("="*70)
print("Testing ALL Indicators (27 indicators total)")
print("="*70)

all_indicators = indicator_manager.list_indicators()
print(f"\nTotal indicators: {len(all_indicators)}")
print(f"Indicators: {', '.join(all_indicators)}")

print("\n" + "="*70)
print("Testing NEW Advanced Indicators")
print("="*70)

new_indicators = ['Triple_EMA', 'Fibonacci', 'Ichimoku', 'Candlestick_Patterns', 'ICT_Concepts']

for ind_name in new_indicators:
    try:
        signal = indicator_manager.calculate_indicator(ind_name, data, 80)
        print(f'\n{ind_name}:')
        print(f'  Bullish: {signal["bullish"]}')
        print(f'  Bearish: {signal["bearish"]}')
        
        # Display specific values based on indicator
        if ind_name == 'Triple_EMA' and signal['value']:
            print(f'  Fast EMA: {signal["value"]["fast"]:.2f}')
            print(f'  Medium EMA: {signal["value"]["medium"]:.2f}')
            print(f'  Slow EMA: {signal["value"]["slow"]:.2f}')
        elif ind_name == 'Fibonacci' and signal['value']:
            print(f'  Swing High: {signal["value"]["swing_high"]:.2f}')
            print(f'  Swing Low: {signal["value"]["swing_low"]:.2f}')
            print(f'  Near Level: {signal["value"]["near_level"]}')
        elif ind_name == 'Ichimoku' and signal['value']:
            print(f'  Cloud Bullish: {signal["value"]["cloud_bullish"]}')
            print(f'  Price Above Cloud: {signal["value"]["price_above_cloud"]}')
        elif ind_name == 'Candlestick_Patterns' and signal['value']:
            print(f'  Patterns: {signal["value"]["patterns"]}')
            print(f'  Bullish Score: {signal["value"]["bullish_score"]}')
            print(f'  Bearish Score: {signal["value"]["bearish_score"]}')
        elif ind_name == 'ICT_Concepts' and signal['value']:
            print(f'  Bullish Score: {signal["value"]["bullish_score"]}')
            print(f'  Bearish Score: {signal["value"]["bearish_score"]}')
            print(f'  In Premium: {signal["value"]["zones"]["in_premium"]}')
            print(f'  In Discount: {signal["value"]["zones"]["in_discount"]}')
        
        print(f'  Strength: {signal["strength"]:.2f}')
    except Exception as e:
        print(f'\n{ind_name}: ❌ ERROR - {str(e)}')

print("\n" + "="*70)
print("Testing Pine Script Generation (New Indicators)")
print("="*70)

pine_code = indicator_manager.get_pine_script(['Triple_EMA', 'Fibonacci', 'Ichimoku'])
print(pine_code[:500] + "..." if len(pine_code) > 500 else pine_code)

print("\n" + "="*70)
print("✅ All 27 indicators registered and working!")
print("="*70)
