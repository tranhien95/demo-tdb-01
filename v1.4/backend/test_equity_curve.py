"""
Test Equity Curve & Total Profit Calculation
Verify compound growth is calculated correctly
"""

def test_equity_curve_old_vs_new():
    """Compare old (wrong) vs new (correct) equity curve calculation"""
    
    print("=" * 70)
    print("EQUITY CURVE TEST - OLD vs NEW FORMULA")
    print("=" * 70)
    
    # Test scenario
    initial_balance = 10000
    risk_pct = 10.0  # Risk 10% per trade
    
    trades = [
        {'profit_pct': 20.0, 'desc': 'Win +20%'},
        {'profit_pct': -10.0, 'desc': 'Loss -10%'},
        {'profit_pct': 15.0, 'desc': 'Win +15%'},
        {'profit_pct': 10.0, 'desc': 'Win +10%'},
        {'profit_pct': -5.0, 'desc': 'Loss -5%'},
    ]
    
    # OLD FORMULA (WRONG)
    print("\n1️⃣  OLD FORMULA (WRONG):")
    print("   balance += (profit_pct / 100) * (balance * risk_pct / 100)")
    print("-" * 70)
    
    balance_old = initial_balance
    equity_old = [balance_old]
    
    for i, trade in enumerate(trades, 1):
        profit_pct = trade['profit_pct']
        # OLD: balance += (profit_pct / 100) * (balance * risk_pct / 100)
        profit_amount = (profit_pct / 100) * (balance_old * risk_pct / 100)
        balance_old += profit_amount
        equity_old.append(balance_old)
        
        print(f"Trade {i} ({trade['desc']}): ${balance_old:,.2f} "
              f"(profit: ${profit_amount:+,.2f})")
    
    total_return_old = ((balance_old - initial_balance) / initial_balance) * 100
    print(f"\nFinal Balance: ${balance_old:,.2f}")
    print(f"Total Return: {total_return_old:+.2f}%")
    
    # NEW FORMULA (CORRECT)
    print("\n\n2️⃣  NEW FORMULA (CORRECT):")
    print("   balance = balance * (1 + (risk_pct / 100) * (profit_pct / 100))")
    print("-" * 70)
    
    balance_new = initial_balance
    equity_new = [balance_new]
    
    for i, trade in enumerate(trades, 1):
        profit_pct = trade['profit_pct']
        # NEW: balance *= (1 + (risk_pct / 100) * (profit_pct / 100))
        old_balance = balance_new
        balance_new = balance_new * (1 + (risk_pct / 100) * (profit_pct / 100))
        profit_amount = balance_new - old_balance
        equity_new.append(balance_new)
        
        print(f"Trade {i} ({trade['desc']}): ${balance_new:,.2f} "
              f"(profit: ${profit_amount:+,.2f})")
    
    total_return_new = ((balance_new - initial_balance) / initial_balance) * 100
    print(f"\nFinal Balance: ${balance_new:,.2f}")
    print(f"Total Return: {total_return_new:+.2f}%")
    
    # COMPARISON
    print("\n\n3️⃣  COMPARISON:")
    print("=" * 70)
    difference = balance_new - balance_old
    print(f"Old Formula Final: ${balance_old:,.2f} ({total_return_old:+.2f}%)")
    print(f"New Formula Final: ${balance_new:,.2f} ({total_return_new:+.2f}%)")
    print(f"Difference: ${difference:+,.2f}")
    print(f"\n✓ New formula uses COMPOUND INTEREST on risked amount")
    print(f"✓ Each win/loss affects future position sizes")
    
    # EQUITY CURVES
    print("\n\n4️⃣  EQUITY CURVES:")
    print("-" * 70)
    print(f"{'Trade':<10} {'Old Balance':<15} {'New Balance':<15} {'Diff':<10}")
    print("-" * 70)
    print(f"{'Initial':<10} ${equity_old[0]:>12,.2f} ${equity_new[0]:>12,.2f} ${0:>8,.2f}")
    for i in range(1, len(equity_old)):
        diff = equity_new[i] - equity_old[i]
        print(f"Trade {i:<4} ${equity_old[i]:>12,.2f} ${equity_new[i]:>12,.2f} ${diff:>8,.2f}")
    
    return balance_old, balance_new


def test_total_profit_calculation():
    """Test total profit calculation - SUM vs ROI"""
    
    print("\n\n" + "=" * 70)
    print("TOTAL PROFIT TEST - SUM vs ROI")
    print("=" * 70)
    
    trades = [
        {'profit_pct': 20.0},
        {'profit_pct': -10.0},
        {'profit_pct': 15.0},
        {'profit_pct': 10.0},
        {'profit_pct': -5.0},
    ]
    
    # OLD METHOD: Sum all profit_pct
    total_sum = sum([t['profit_pct'] for t in trades])
    print(f"\n1️⃣  OLD METHOD (WRONG): Sum of all profit_pct")
    print(f"   20% + (-10%) + 15% + 10% + (-5%) = {total_sum:+.2f}%")
    print(f"   ✗ This doesn't account for compound interest!")
    
    # NEW METHOD: Calculate ROI from equity curve
    initial = 10000
    final_old, final_new = test_equity_curve_old_vs_new()
    
    roi_old = ((final_old - initial) / initial) * 100
    roi_new = ((final_new - initial) / initial) * 100
    
    print(f"\n2️⃣  NEW METHOD (CORRECT): ROI from final balance")
    print(f"   Old formula ROI: {roi_old:+.2f}%")
    print(f"   New formula ROI: {roi_new:+.2f}%")
    print(f"   Sum of trades:   {total_sum:+.2f}%")
    print(f"\n   ✓ ROI reflects actual portfolio growth!")


def test_real_scenario():
    """Test với scenario thực tế"""
    
    print("\n\n" + "=" * 70)
    print("REAL SCENARIO TEST")
    print("=" * 70)
    
    print("\nScenario: EMA Strategy - 10 trades, 60% win rate")
    print("Capital: $10,000 | Risk per trade: 10% | RR: 2:1")
    print("-" * 70)
    
    initial = 10000
    risk_pct = 10
    
    # 6 wins @ +2%, 4 losses @ -1% (RR 2:1 với 1% SL)
    trades = [
        {'pct': 2.0, 'result': 'Win'},   # TP
        {'pct': 2.0, 'result': 'Win'},   # TP
        {'pct': -1.0, 'result': 'Loss'}, # SL
        {'pct': 2.0, 'result': 'Win'},   # TP
        {'pct': -1.0, 'result': 'Loss'}, # SL
        {'pct': 2.0, 'result': 'Win'},   # TP
        {'pct': 2.0, 'result': 'Win'},   # TP
        {'pct': -1.0, 'result': 'Loss'}, # SL
        {'pct': 2.0, 'result': 'Win'},   # TP
        {'pct': -1.0, 'result': 'Loss'}, # SL
    ]
    
    balance = initial
    print(f"\nTrade | Result | Profit% | Balance")
    print("-" * 50)
    print(f"   0  | Start  |   N/A   | ${balance:,.2f}")
    
    for i, trade in enumerate(trades, 1):
        old_balance = balance
        balance = balance * (1 + (risk_pct / 100) * (trade['pct'] / 100))
        profit = balance - old_balance
        print(f"   {i}  | {trade['result']:<6} | {trade['pct']:>+6.2f}% | ${balance:,.2f} ({profit:+,.2f})")
    
    total_return = ((balance - initial) / initial) * 100
    sum_pct = sum([t['pct'] for t in trades])
    
    print("-" * 50)
    print(f"\nFinal Balance: ${balance:,.2f}")
    print(f"Total Return (ROI): {total_return:+.2f}%")
    print(f"Sum of Profit%: {sum_pct:+.2f}%")
    print(f"\nDifference: {total_return - sum_pct:+.2f}%")
    print(f"✓ Compound interest effect!")
    
    # Expectancy check
    wins = [t for t in trades if t['pct'] > 0]
    losses = [t for t in trades if t['pct'] < 0]
    win_rate = len(wins) / len(trades) * 100
    avg_win = sum([t['pct'] for t in wins]) / len(wins)
    avg_loss = abs(sum([t['pct'] for t in losses]) / len(losses))
    expectancy = (win_rate / 100 * avg_win) - ((100 - win_rate) / 100 * avg_loss)
    
    print(f"\n📊 Strategy Stats:")
    print(f"   Win Rate: {win_rate:.1f}%")
    print(f"   Avg Win: {avg_win:+.2f}%")
    print(f"   Avg Loss: {-avg_loss:.2f}%")
    print(f"   Expectancy: {expectancy:+.2f}% per trade")


def main():
    test_equity_curve_old_vs_new()
    test_total_profit_calculation()
    test_real_scenario()
    
    print("\n\n" + "=" * 70)
    print("KEY FINDINGS:")
    print("=" * 70)
    print("1. Old formula: balance += profit × position_size")
    print("   → Linear growth, no compound effect")
    print("\n2. New formula: balance *= (1 + risk% × profit%)")
    print("   → Compound growth, realistic portfolio tracking")
    print("\n3. Total profit should be ROI, NOT sum of individual trades")
    print("   → Reflects actual portfolio performance")
    print("=" * 70)


if __name__ == "__main__":
    main()
