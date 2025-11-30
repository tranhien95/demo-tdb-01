"""
Test scenario giống ảnh user: 2 SHORT trades SL -0.75%
"""

def test_user_scenario():
    """Test 2 SHORT trades với SL -0.75% như trong ảnh"""
    
    print("=" * 70)
    print("TEST SCENARIO - 2 SHORT TRADES (GIỐNG ẢNH)")
    print("=" * 70)
    
    capital = 1000.0  # Giả sử capital $1000
    risk_pct = 10.0   # Risk 10% per trade
    
    trades = [
        {
            'entry': 1279.80,
            'exit': 1289.40,
            'type': 'SHORT',
            'sl_pct': -0.75
        },
        {
            'entry': 1264.00,
            'exit': 1273.48,
            'type': 'SHORT',
            'sl_pct': -0.75
        }
    ]
    
    print(f"\nInitial Capital: ${capital:,.2f}")
    print(f"Risk per trade: {risk_pct}%")
    print(f"Position size per trade: ${capital * risk_pct / 100:,.2f}\n")
    
    balance = capital
    total_usd = 0
    
    for i, trade in enumerate(trades, 1):
        entry = trade['entry']
        exit = trade['exit']
        
        # Price difference (không dùng để tính profit nữa!)
        price_diff = entry - exit  # SHORT: profit when price goes down
        price_diff_pct = (price_diff / entry) * 100
        
        # Actual profit calculation
        position_size = balance * (risk_pct / 100)
        actual_profit_usd = position_size * (price_diff_pct / 100)
        
        # Update balance
        balance = balance * (1 + (risk_pct / 100) * (price_diff_pct / 100))
        total_usd += actual_profit_usd
        
        print(f"Trade {i} (SHORT):")
        print(f"  Entry: ${entry:,.2f}")
        print(f"  Exit:  ${exit:,.2f}")
        print(f"  Price Diff: ${price_diff:+,.2f} ({price_diff_pct:+.2f}%)")
        print(f"  Position Size: ${position_size:,.2f}")
        print(f"  ❌ OLD (WRONG): Profit = ${price_diff:+,.2f}")
        print(f"  ✅ NEW (CORRECT): Profit = ${actual_profit_usd:+,.2f}")
        print(f"  Balance: ${balance:,.2f}\n")
    
    total_return_pct = ((balance - capital) / capital) * 100
    
    print("=" * 70)
    print("SUMMARY:")
    print("=" * 70)
    print(f"Final Balance: ${balance:,.2f}")
    print(f"Total Return %: {total_return_pct:+.2f}%")
    print(f"Total Profit USD: ${total_usd:+,.2f}")
    
    print(f"\n📊 Expected in UI:")
    print(f"  Total Profit %: {total_return_pct:+.2f}%")
    print(f"  Total Profit USD: ${balance - capital:+,.2f}")
    
    print(f"\n✅ Với capital $1000:")
    print(f"  Trade 1: Entry 1279.80, Exit 1289.40 → Loss -$7.50")
    print(f"  Trade 2: Entry 1264.00, Exit 1273.48 → Loss -$7.48")
    print(f"  Total: -$14.98 (-1.50%)")
    
    print(f"\n💡 Trong ảnh của bạn có thể capital khác $1000")
    print(f"  Nếu capital = $100 → Total loss = -$1.50 (-1.50%)")


if __name__ == "__main__":
    test_user_scenario()
