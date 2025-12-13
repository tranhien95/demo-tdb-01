import json

# Trade data
trades_raw = [
    {"entry": 91303.56, "exit": 89934.01, "sl": 91988.34, "tp": 89934.01, "profit": 1999.995, "profit_pct": 1.5, "type": "SHORT"},
    {"entry": 86869.51, "exit": 86464.73, "sl": 86217.99, "tp": 88172.55, "profit": -621.2843, "profit_pct": -0.47, "type": "LONG"},
    {"entry": 86464.73, "exit": 85167.76, "sl": 87113.22, "tp": 85167.76, "profit": 1999.9985, "profit_pct": 1.5, "type": "SHORT"},
    {"entry": 85790.44, "exit": 86433.87, "sl": 86433.87, "tp": 84503.58, "profit": -1000.0026, "profit_pct": -0.75, "type": "SHORT"},
    {"entry": 88675.45, "exit": 90005.58, "sl": 88010.38, "tp": 90005.58, "profit": 1999.9973, "profit_pct": 1.5, "type": "LONG"},
]

position_size = 133333.33

print("=" * 100)
print("KIỂM TRA DỮ LIỆU - SL 5% & RR 1:1")
print("=" * 100)
print()

errors = []

for idx, trade in enumerate(trades_raw, 1):
    entry = trade['entry']
    exit_p = trade['exit']
    sl = trade['sl']
    tp = trade['tp']
    reported_profit = trade['profit']
    reported_profit_pct = trade['profit_pct']
    trade_type = trade['type']
    
    print(f"TRADE #{idx} ({trade_type})")
    print(f"  Entry: {entry:.2f}")
    print(f"  Exit:  {exit_p:.2f}")
    print(f"  SL:    {sl:.2f} | TP: {tp:.2f}")
    
    # 1. Kiểm tra SL distance
    sl_distance = abs(sl - entry) / entry * 100
    print(f"  SL distance: {sl_distance:.3f}% (expected: 5.000%)", end="")
    if abs(sl_distance - 5) > 0.05:
        print(f" ✗ SAI {abs(sl_distance - 5):.3f}%")
        errors.append(f"Trade {idx}: SL distance {sl_distance:.3f}% != 5%")
    else:
        print(" ✓")
    
    # 2. Kiểm tra TP distance
    tp_distance = abs(tp - entry) / entry * 100
    print(f"  TP distance: {tp_distance:.3f}% (expected: 5.000%)", end="")
    if abs(tp_distance - 5) > 0.05:
        print(f" ✗ SAI {abs(tp_distance - 5):.3f}%")
        errors.append(f"Trade {idx}: TP distance {tp_distance:.3f}% != 5%")
    else:
        print(" ✓")
    
    # 3. Kiểm tra profit tính toán
    if trade_type == "SHORT":
        calculated_profit = (entry - exit_p) * position_size / entry
        expected_profit_pct = (entry - exit_p) / entry * 100
    else:  # LONG
        calculated_profit = (exit_p - entry) * position_size / entry
        expected_profit_pct = (exit_p - entry) / entry * 100
    
    print(f"  Profit: ${reported_profit:.4f} | Calculated: ${calculated_profit:.4f}", end="")
    if abs(reported_profit - calculated_profit) > 10:
        print(f" ✗ SAI ${abs(reported_profit - calculated_profit):.2f}")
        errors.append(f"Trade {idx}: Profit mismatch ${reported_profit:.2f} vs ${calculated_profit:.2f}")
    else:
        print(" ✓")
    
    print(f"  Profit %: {reported_profit_pct:.4f}% | Expected: {expected_profit_pct:.4f}%", end="")
    if abs(reported_profit_pct - expected_profit_pct) > 0.05:
        print(f" ✗ SAI")
        errors.append(f"Trade {idx}: Profit % {reported_profit_pct}% != {expected_profit_pct:.4f}%")
    else:
        print(" ✓")
    
    print()

print()
print("=" * 100)
if errors:
    print(f"❌ PHÁT HIỆN {len(errors)} LỖI:")
    for error in errors:
        print(f"   • {error}")
else:
    print("✅ DỮ LIỆU CHÍNH XÁC")
print("=" * 100)
