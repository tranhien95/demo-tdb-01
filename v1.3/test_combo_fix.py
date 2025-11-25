#!/usr/bin/env python3
"""
Quick test to verify that different combos produce different results
"""

import csv
import sys
from backend import BacktestEngine

# Load data
ohlcv_data = []
with open('OANDA_XAUUSD_15.csv', 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        try:
            ohlcv_data.append({
                'time': row.get('Date', row.get('time', '')),
                'open': float(row.get('Open', row.get('open', 0))),
                'high': float(row.get('High', row.get('high', 0))),
                'low': float(row.get('Low', row.get('low', 0))),
                'close': float(row.get('Close', row.get('close', 0))),
                'volume': float(row.get('Volume', row.get('volume', 0)))
            })
        except (ValueError, KeyError):
            continue

print(f"Loaded {len(ohlcv_data)} candles")

# Test parameters
filters = {}
params = {
    'threshold': 70,
    'risk_pct': 10,
    'rr_ratio': 2.0,
    'sl_pct': 0.75,
    'min_signal_ratio': 70,
    'candle_confirmation': 2
}

# Test different combos
test_combos = [
    ['RSI', 'MACD'],
    ['RSI', 'MACD', 'Stochastic'],
    ['EMA_50', 'EMA_200'],
    ['Stochastic', 'BB_Upper'],
    ['ADX', 'CCI', 'MFI']
]

print("\n" + "="*80)
print("Testing different indicator combinations:")
print("="*80)

for combo in test_combos:
    result = BacktestEngine.backtest_combo(
        combo, ohlcv_data,
        params['threshold'],
        params['risk_pct'],
        params['rr_ratio'],
        params['sl_pct'],
        filters,
        params['min_signal_ratio'],
        params['candle_confirmation']
    )
    
    print(f"\nCombo: {'+'.join(combo)}")
    print(f"  Trades: {result['trades']}")
    print(f"  Win Rate: {result['win_rate']}%")
    print(f"  Profit: {result['profit_pct']}%")
    print(f"  Sharpe: {result['sharpe']}")

print("\n✅ Test complete! Results should be DIFFERENT for each combo.")
