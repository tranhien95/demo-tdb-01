"""
Test Equity Curve with Real Strategy
Verify portfolio growth calculation is correct
"""

import sys
sys.path.insert(0, 'C:/Data/PineScript/demo-tdb-01/v1.4/backend')

from strategy_models import Strategy, IndicatorConfig, RiskManagement, SignalLogic, FilterConfig
from strategy_engine import StrategyEngine
import csv


def load_sample_data():
    """Load sample OHLCV data"""
    data = []
    with open('C:/Data/PineScript/demo-tdb-01/v1.4/OANDA_XAUUSD_15.csv', 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            data.append({
                'time': row['time'],
                'open': float(row['open']),
                'high': float(row['high']),
                'low': float(row['low']),
                'close': float(row['close']),
                'volume': int(float(row['Volume']))  # Capital V
            })
    return data[:500]  # Use first 500 candles


def create_simple_strategy():
    """Create a simple EMA strategy"""
    return Strategy(
        name="Test EMA Strategy",
        description="Simple EMA 12/26 crossover",
        indicators=[
            IndicatorConfig(
                type="EMA_12",
                config={},
                weight=1.0,
                enabled=True,
                id="ema12"
            ),
            IndicatorConfig(
                type="EMA_26",
                config={},
                weight=1.0,
                enabled=True,
                id="ema26"
            ),
        ],
        signal_logic=SignalLogic(threshold_percent=70.0),
        filters=FilterConfig(),
        risk_management=RiskManagement(
            risk_percent=10.0,
            rr_ratio=2.0,
            sl_percent=0.75,
            candle_confirmation=2,
            capital=10000.0
        )
    )


def test_equity_curve_calculation():
    """Test equity curve with real backtest"""
    print("=" * 80)
    print("EQUITY CURVE TEST - REAL BACKTEST")
    print("=" * 80)
    
    # Load data
    print("\n📊 Loading data...")
    data = load_sample_data()
    print(f"   Loaded {len(data)} candles")
    
    # Create strategy
    print("\n🎯 Creating strategy...")
    strategy = create_simple_strategy()
    print(f"   Strategy: {strategy.name}")
    print(f"   Indicators: EMA_12, EMA_26")
    print(f"   Capital: ${strategy.risk_management.capital:,.2f}")
    print(f"   Risk per trade: {strategy.risk_management.risk_percent}%")
    
    # Run backtest
    print("\n🔄 Running backtest...")
    result = StrategyEngine.backtest_strategy(strategy, data)
    
    # Display results
    print("\n" + "=" * 80)
    print("RESULTS")
    print("=" * 80)
    
    print(f"\n📈 Trade Statistics:")
    print(f"   Total Trades: {result.total_trades}")
    print(f"   Wins: {result.winning_trades} ({result.win_rate:.2f}%)")
    print(f"   Losses: {result.losing_trades}")
    
    print(f"\n💰 Profit Metrics:")
    print(f"   Total Return: {result.profit_pct:+.2f}%")
    print(f"   Total Profit USD: ${result.total_profit_usd:+,.2f}")
    print(f"   Profit Factor: {result.profit_factor:.2f}")
    print(f"   Expectancy: {result.expectancy:.4f}")
    
    print(f"\n📊 Risk Metrics:")
    print(f"   Max Drawdown: {result.max_drawdown:.2f}%")
    print(f"   Sharpe Ratio: {result.sharpe_ratio:.2f}")
    print(f"   Sortino Ratio: {result.sortino_ratio:.2f}")
    print(f"   Calmar Ratio: {result.calmar_ratio:.2f}")
    
    print(f"\n🎲 Trade Quality:")
    print(f"   Avg Win: ${result.avg_win:+.4f} ({result.avg_win_pct:+.2f}%)")
    print(f"   Avg Loss: ${result.avg_loss:.4f} ({result.avg_loss_pct:.2f}%)")
    print(f"   Largest Win: ${result.largest_win:+.4f}")
    print(f"   Largest Loss: ${result.largest_loss:.4f}")
    print(f"   Profit per Trade: ${result.profit_per_trade:+.4f}")
    
    # Verify equity curve
    print("\n" + "=" * 80)
    print("EQUITY CURVE VERIFICATION")
    print("=" * 80)
    
    initial_capital = strategy.risk_management.capital
    final_balance = result.equity_curve[-1]
    
    print(f"\n💵 Portfolio Growth:")
    print(f"   Initial Capital: ${initial_capital:,.2f}")
    print(f"   Final Balance: ${final_balance:,.2f}")
    print(f"   Growth: ${final_balance - initial_capital:+,.2f}")
    
    # Calculate ROI
    calculated_roi = ((final_balance - initial_capital) / initial_capital) * 100
    reported_roi = result.profit_pct
    
    print(f"\n🎯 ROI Verification:")
    print(f"   Reported Total Return: {reported_roi:+.2f}%")
    print(f"   Calculated from Equity: {calculated_roi:+.2f}%")
    print(f"   Difference: {abs(reported_roi - calculated_roi):.6f}%")
    
    if abs(reported_roi - calculated_roi) < 0.01:
        print(f"   ✅ PASS - ROI matches equity curve!")
    else:
        print(f"   ❌ FAIL - ROI doesn't match equity curve!")
    
    # Verify total_profit_usd
    calculated_profit = final_balance - initial_capital
    reported_profit = result.total_profit_usd
    
    print(f"\n💰 USD Profit Verification:")
    print(f"   Reported Profit USD: ${reported_profit:+,.2f}")
    print(f"   Calculated from Equity: ${calculated_profit:+,.2f}")
    print(f"   Difference: ${abs(reported_profit - calculated_profit):.2f}")
    
    if abs(reported_profit - calculated_profit) < 0.01:
        print(f"   ✅ PASS - USD profit matches equity curve!")
    else:
        print(f"   ❌ FAIL - USD profit doesn't match equity curve!")
    
    # Show equity curve sample
    print(f"\n📈 Equity Curve (First 10 & Last 10 points):")
    print(f"   {'Index':<8} {'Balance':<15} {'Change':<12}")
    print(f"   {'-' * 35}")
    
    for i in range(min(10, len(result.equity_curve))):
        if i == 0:
            change = 0
        else:
            change = result.equity_curve[i] - result.equity_curve[i-1]
        print(f"   {i:<8} ${result.equity_curve[i]:>12,.2f} {change:>+10,.2f}")
    
    if len(result.equity_curve) > 20:
        print(f"   {'...':<8} {'...':<15} {'...':<12}")
        
        for i in range(len(result.equity_curve) - 10, len(result.equity_curve)):
            change = result.equity_curve[i] - result.equity_curve[i-1]
            print(f"   {i:<8} ${result.equity_curve[i]:>12,.2f} {change:>+10,.2f}")
    
    # Show sample trades
    if result.trades:
        print(f"\n🔍 Sample Trades (Last 5):")
        print(f"   {'Entry':<10} {'Exit':<10} {'Profit':<12} {'%':<8} {'Reason':<8}")
        print(f"   {'-' * 50}")
        
        for trade in result.trades[-5:]:
            print(f"   ${trade.entry:<9.2f} ${trade.exit:<9.2f} "
                  f"${trade.profit:>+10.4f} {trade.profit_pct:>+6.2f}% {trade.exit_reason:<8}")
    
    print("\n" + "=" * 80)
    
    return result


if __name__ == "__main__":
    result = test_equity_curve_calculation()
    
    print("\n✅ TEST COMPLETED")
    print("=" * 80)
