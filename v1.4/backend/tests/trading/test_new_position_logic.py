"""
Test New Position Sizing: Risk 10% of INITIAL capital
"""

def test_new_logic():
    print("=" * 80)
    print("NEW POSITION SIZING LOGIC TEST")
    print("=" * 80)
    
    initial_capital = 10000
    risk_pct = 10  # 10% of INITIAL capital
    sl_pct = 0.75  # SL distance
    
    print(f"\nSetup:")
    print(f"  Initial Capital: ${initial_capital:,.2f}")
    print(f"  Risk %: {risk_pct}% (of INITIAL capital)")
    print(f"  SL Distance: {sl_pct}%")
    
    # Calculate position size
    risk_amount = initial_capital * (risk_pct / 100)
    position_size = risk_amount / (sl_pct / 100)
    
    print(f"\nPosition Sizing:")
    print(f"  Risk Amount: ${initial_capital:,.2f} × {risk_pct}% = ${risk_amount:,.2f}")
    print(f"  Position Size: ${risk_amount:,.2f} / {sl_pct}% = ${position_size:,.2f}")
    print(f"  Leverage: {position_size / initial_capital:.1f}x")
    
    # Scenario 1: Hit SL
    print(f"\n{'='*80}")
    print("SCENARIO 1: HIT SL (-0.75%)")
    print("="*80)
    
    balance = initial_capital
    profit_pct_sl = -0.75
    actual_loss = position_size * (profit_pct_sl / 100)
    new_balance_sl = balance + actual_loss
    
    print(f"  Entry: Balance = ${balance:,.2f}")
    print(f"  Price loss: {profit_pct_sl}%")
    print(f"  Actual loss: ${position_size:,.2f} × {profit_pct_sl}% = ${actual_loss:,.2f}")
    print(f"  New balance: ${new_balance_sl:,.2f}")
    print(f"  Loss % of capital: {(actual_loss / initial_capital) * 100:.2f}%")
    print(f"  ✅ Loss = ${-actual_loss:.2f} = 10% initial capital")
    
    # Scenario 2: Hit TP (RR 2:1)
    print(f"\n{'='*80}")
    print("SCENARIO 2: HIT TP (+1.5% với RR 2:1)")
    print("="*80)
    
    balance = initial_capital
    profit_pct_tp = 1.5
    actual_gain = position_size * (profit_pct_tp / 100)
    new_balance_tp = balance + actual_gain
    
    print(f"  Entry: Balance = ${balance:,.2f}")
    print(f"  Price gain: {profit_pct_tp}%")
    print(f"  Actual gain: ${position_size:,.2f} × {profit_pct_tp}% = ${actual_gain:,.2f}")
    print(f"  New balance: ${new_balance_tp:,.2f}")
    print(f"  Gain % of capital: {(actual_gain / initial_capital) * 100:.2f}%")
    print(f"  ✅ Gain = ${actual_gain:.2f} = 20% initial capital (RR 2:1)")
    
    # Scenario 3: Multiple trades
    print(f"\n{'='*80}")
    print("SCENARIO 3: MULTIPLE TRADES (balance thay đổi, risk KHÔNG đổi)")
    print("="*80)
    
    balance = initial_capital
    trades = [
        ('Win TP', 1.5),
        ('Loss SL', -0.75),
        ('Win TP', 1.5),
        ('Win TP', 1.5),
    ]
    
    print(f"\nInitial: ${balance:,.2f}\n")
    
    for i, (desc, profit_pct) in enumerate(trades, 1):
        # Position size ALWAYS based on initial capital
        risk_amount = initial_capital * (risk_pct / 100)
        position_size = risk_amount / (sl_pct / 100)
        
        actual_profit = position_size * (profit_pct / 100)
        balance += actual_profit
        
        print(f"Trade {i} ({desc}):")
        print(f"  Position: ${position_size:,.2f} (always same!)")
        print(f"  Profit: ${actual_profit:+,.2f} ({(actual_profit/initial_capital)*100:+.1f}% of initial)")
        print(f"  Balance: ${balance:,.2f}")
        print()
    
    total_return = ((balance - initial_capital) / initial_capital) * 100
    print(f"Final Balance: ${balance:,.2f}")
    print(f"Total Return: {total_return:+.2f}%")
    
    print(f"\n💡 KEY POINTS:")
    print(f"  ✅ Position size FIXED = ${position_size:,.2f} (không thay đổi)")
    print(f"  ✅ Risk mỗi trade = 10% initial capital = ${risk_amount:,.2f}")
    print(f"  ✅ Balance tăng/giảm nhưng position size không đổi")
    print(f"  ⚠️  Leverage ~{position_size/initial_capital:.1f}x (cần margin/leverage)")


if __name__ == "__main__":
    test_new_logic()
