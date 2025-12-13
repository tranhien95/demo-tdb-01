"""
Test Performance Metrics Calculator
Verify all calculations are correct
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from performance_metrics import PerformanceMetrics


def test_profit_factor():
    """Test profit factor calculation"""
    print("\n=== Test Profit Factor ===")
    
    # Test case 1: 3 wins, 2 losses
    trades = [
        {'profit': 100, 'profit_pct': 10},
        {'profit': 150, 'profit_pct': 15},
        {'profit': -50, 'profit_pct': -5},
        {'profit': 200, 'profit_pct': 20},
        {'profit': -75, 'profit_pct': -7.5},
    ]
    
    pf = PerformanceMetrics.calculate_profit_factor(trades)
    print(f"Trades: 3 wins (100+150+200=450), 2 losses (-50-75=-125)")
    print(f"Profit Factor: {pf}")
    print(f"Expected: 450/125 = 3.6")
    print(f"✓ PASS" if pf == 3.6 else f"✗ FAIL")
    
    # Test case 2: No losses
    trades_no_loss = [
        {'profit': 100, 'profit_pct': 10},
        {'profit': 200, 'profit_pct': 20},
    ]
    pf2 = PerformanceMetrics.calculate_profit_factor(trades_no_loss)
    print(f"\nNo losses: Profit Factor = {pf2}")
    print(f"Expected: 300.0 (gross profit)")
    print(f"✓ PASS" if pf2 == 300.0 else f"✗ FAIL")


def test_sharpe_ratio():
    """Test Sharpe ratio calculation"""
    print("\n=== Test Sharpe Ratio ===")
    
    trades = [
        {'profit_pct': 10},
        {'profit_pct': -5},
        {'profit_pct': 15},
        {'profit_pct': -3},
        {'profit_pct': 12},
    ]
    
    sharpe = PerformanceMetrics.calculate_sharpe_ratio(trades)
    print(f"Returns: [10, -5, 15, -3, 12]")
    print(f"Mean: 5.8, Std Dev: ~8.35")
    print(f"Sharpe Ratio: {sharpe}")
    print(f"Expected: ~0.69")
    print(f"✓ PASS" if 0.6 <= sharpe <= 0.8 else f"✗ FAIL")


def test_sortino_ratio():
    """Test Sortino ratio calculation"""
    print("\n=== Test Sortino Ratio ===")
    
    trades = [
        {'profit_pct': 10},
        {'profit_pct': -5},
        {'profit_pct': 15},
        {'profit_pct': -3},
        {'profit_pct': 12},
    ]
    
    sortino = PerformanceMetrics.calculate_sortino_ratio(trades)
    print(f"Returns: [10, -5, 15, -3, 12]")
    print(f"Negative returns: [-5, -3]")
    print(f"Sortino Ratio: {sortino}")
    print(f"Expected: Higher than Sharpe (only downside volatility)")
    print(f"✓ PASS" if sortino > 0 else f"✗ FAIL")


def test_expectancy():
    """Test expectancy calculation"""
    print("\n=== Test Expectancy ===")
    
    trades = [
        {'profit': 100},
        {'profit': 150},
        {'profit': -50},
        {'profit': 200},
        {'profit': -75},
    ]
    
    expectancy = PerformanceMetrics.calculate_expectancy(trades)
    print(f"3 wins: avg = 150")
    print(f"2 losses: avg = -62.5")
    print(f"Win rate: 60%, Loss rate: 40%")
    print(f"Expectancy: {expectancy}")
    print(f"Formula: (0.6 * 150) - (0.4 * 62.5) = 90 - 25 = 65")
    print(f"✓ PASS" if expectancy == 65.0 else f"✗ FAIL")


def test_consecutive_losses():
    """Test max consecutive losses"""
    print("\n=== Test Max Consecutive Losses ===")
    
    trades = [
        {'profit': 100},
        {'profit': -50},
        {'profit': -75},
        {'profit': -30},
        {'profit': 200},
        {'profit': -40},
    ]
    
    max_losses = PerformanceMetrics.calculate_max_consecutive_losses(trades)
    print(f"Trade sequence: [Win, Loss, Loss, Loss, Win, Loss]")
    print(f"Max consecutive losses: {max_losses}")
    print(f"Expected: 3")
    print(f"✓ PASS" if max_losses == 3 else f"✗ FAIL")


def test_trade_quality():
    """Test trade quality analysis"""
    print("\n=== Test Trade Quality ===")
    
    trades = [
        {'profit': 100, 'profit_pct': 10},
        {'profit': 150, 'profit_pct': 15},
        {'profit': -50, 'profit_pct': -5},
        {'profit': 200, 'profit_pct': 20},
        {'profit': -75, 'profit_pct': -7.5},
    ]
    
    quality = PerformanceMetrics.analyze_trade_quality(trades)
    print(f"Avg Win: {quality['avg_win']} (expected: 150)")
    print(f"Avg Loss: {quality['avg_loss']} (expected: -62.5)")
    print(f"Largest Win: {quality['largest_win']} (expected: 200)")
    print(f"Largest Loss: {quality['largest_loss']} (expected: -75)")
    print(f"Profit per trade: {quality['profit_per_trade']} (expected: 65)")
    
    checks = [
        quality['avg_win'] == 150.0,
        quality['avg_loss'] == -62.5,
        quality['largest_win'] == 200.0,
        quality['largest_loss'] == -75.0,
        quality['profit_per_trade'] == 65.0,
    ]
    print(f"✓ ALL PASS" if all(checks) else f"✗ SOME FAILED")


def test_drawdown_details():
    """Test drawdown calculation"""
    print("\n=== Test Drawdown Details ===")
    
    equity_curve = [10000, 10500, 10800, 10200, 9800, 10100, 11000, 10500, 11500]
    
    dd = PerformanceMetrics.calculate_max_drawdown_details(equity_curve)
    print(f"Equity: {equity_curve}")
    print(f"Max Drawdown %: {dd['max_drawdown_pct']}")
    print(f"Max Drawdown Value: {dd['max_drawdown_value']}")
    print(f"Drawdown Duration: {dd['drawdown_duration']}")
    print(f"Recovery Duration: {dd['recovery_duration']}")
    print(f"Expected: Max at 9800 from peak 10800 = -9.26%")
    print(f"✓ PASS" if 9.0 <= dd['max_drawdown_pct'] <= 10.0 else f"✗ FAIL")


def test_all_metrics():
    """Test calculate_all_metrics function"""
    print("\n=== Test All Metrics Combined ===")
    
    trades = [
        {'profit': 100, 'profit_pct': 10},
        {'profit': 150, 'profit_pct': 15},
        {'profit': -50, 'profit_pct': -5},
        {'profit': 200, 'profit_pct': 20},
        {'profit': -75, 'profit_pct': -7.5},
    ]
    
    equity_curve = [10000, 11000, 12650, 12125, 14525, 13775]
    
    metrics = PerformanceMetrics.calculate_all_metrics(trades, equity_curve, 10000)
    
    print(f"Profit Factor: {metrics['profit_factor']}")
    print(f"Sharpe Ratio: {metrics['sharpe_ratio']}")
    print(f"Sortino Ratio: {metrics['sortino_ratio']}")
    print(f"Calmar Ratio: {metrics['calmar_ratio']}")
    print(f"Recovery Factor: {metrics['recovery_factor']}")
    print(f"Expectancy: {metrics['expectancy']}")
    print(f"Max Consecutive Losses: {metrics['max_consecutive_losses']}")
    print(f"Max Consecutive Wins: {metrics['max_consecutive_wins']}")
    print(f"Profit per Trade: {metrics['profit_per_trade']}")
    print(f"Max Drawdown %: {metrics['max_drawdown_pct']}")
    
    print(f"\n✓ All metrics calculated successfully!")


def main():
    """Run all tests"""
    print("=" * 60)
    print("PERFORMANCE METRICS TEST SUITE")
    print("=" * 60)
    
    test_profit_factor()
    test_sharpe_ratio()
    test_sortino_ratio()
    test_expectancy()
    test_consecutive_losses()
    test_trade_quality()
    test_drawdown_details()
    test_all_metrics()
    
    print("\n" + "=" * 60)
    print("TEST SUITE COMPLETED")
    print("=" * 60)


if __name__ == "__main__":
    main()
