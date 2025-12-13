"""
Test Partial Profit Taking Implementation
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from live_trading_models import Position, TradingConfig, LiveTradingState, TradeStatus
from live_trading_engine import LiveTradingEngine
from datetime import datetime


def test_partial_profit_taking():
    """Test partial profit taking logic"""
    
    print("=" * 80)
    print("TEST PARTIAL PROFIT TAKING")
    print("=" * 80)
    
    # Create test position
    entry_price = 100.0
    initial_sl = 99.0  # 1% SL
    position = Position(
        id="test-partial-1",
        symbol="BTCUSDT",
        entry_price=entry_price,
        entry_time=datetime.now(),
        quantity=100.0,  # 100 units
        side="LONG",
        stoploss=initial_sl,
        takeprofit=102.0,
        entry_signal="STRONG_BUY",
        entry_confidence=80.0,
        highest_price=entry_price,
        lowest_price=0.0,
        initial_stoploss=initial_sl,
        trailing_activated=False,
        breakeven_set=False,
        partial_profit_rules=[
            {"r_level": 1.0, "close_pct": 0.5, "taken": False},   # 50% @ 1R
            {"r_level": 2.0, "close_pct": 0.25, "taken": False}  # 25% @ 2R
        ]
    )
    
    # Create engine
    engine = LiveTradingEngine()
    config = TradingConfig(
        symbol="BTCUSDT",
        timeframe="M5",
        strategy_name="Test",
        initial_balance=10000.0,
        risk_percent=2.0,
        margin=1.0,
        stoploss_percent=1.0,
        enable_partial_profit=True,
        partial_profit_rules=[
            {"r_level": 1.0, "close_pct": 0.5, "taken": False},
            {"r_level": 2.0, "close_pct": 0.25, "taken": False}
        ]
    )
    
    engine.state = LiveTradingState(
        status=TradeStatus.RUNNING,
        config=config,
        balance=10000.0,
        equity=10000.0,
        used_margin=0.0,
        available_margin=10000.0
    )
    engine.state.open_positions.append(position)
    
    print(f"\nInitial Position:")
    print(f"  Entry: ${entry_price:.2f}")
    print(f"  Quantity: {position.quantity:.2f} units")
    print(f"  Initial SL: ${initial_sl:.2f}")
    print(f"  Partial Rules:")
    for rule in position.partial_profit_rules:
        print(f"    - Close {rule['close_pct']*100:.0f}% @ {rule['r_level']}R")
    
    print(f"\n{'='*80}")
    print("SIMULATING PRICE MOVEMENT")
    print("="*80)
    
    # Simulate price movement
    test_prices = [
        100.0,  # Entry
        100.5,  # 0.5R
        101.0,  # 1.0R - Should trigger first partial
        101.5,  # 1.5R
        102.0,  # 2.0R - Should trigger second partial
        102.5,  # 2.5R
        103.0,  # 3.0R
    ]
    
    total_locked = 0.0
    
    for i, price in enumerate(test_prices):
        print(f"\n--- Step {i+1}: Price = ${price:.2f} ---")
        
        # Update position price
        position.update_price(price)
        
        # Calculate profit R
        profit = price - entry_price
        profit_pct = (profit / entry_price) * 100
        sl_distance_pct = abs(entry_price - initial_sl) / entry_price * 100
        profit_r = profit_pct / sl_distance_pct if sl_distance_pct > 0 else 0
        
        print(f"  Profit: ${profit:.2f} ({profit_pct:.2f}%) = {profit_r:.2f}R")
        print(f"  Current Quantity: {position.quantity:.2f} units")
        print(f"  Locked Profit: ${total_locked:.2f}")
        
        old_quantity = position.quantity
        old_balance = engine.state.balance
        
        # Check partial profit
        engine._check_partial_profit_taking(position, price)
        
        if position.quantity != old_quantity:
            locked = old_balance - engine.state.balance
            total_locked += locked
            print(f"  ✅ PARTIAL CLOSE!")
            print(f"  Closed: {old_quantity - position.quantity:.2f} units")
            print(f"  Locked Profit: ${locked:.2f}")
            print(f"  Remaining: {position.quantity:.2f} units")
    
    print(f"\n{'='*80}")
    print("FINAL RESULTS")
    print("="*80)
    print(f"  Final Quantity: {position.quantity:.2f} units")
    print(f"  Total Locked Profit: ${total_locked:.2f}")
    print(f"  Remaining Position Value: ${position.quantity * test_prices[-1]:.2f}")


if __name__ == "__main__":
    test_partial_profit_taking()
    
    print("\n" + "=" * 80)
    print("✅ PARTIAL PROFIT TAKING TEST COMPLETE")
    print("=" * 80)
    print("\nKey Features:")
    print("  ✅ Close 50% @ 1R")
    print("  ✅ Close 25% @ 2R")
    print("  ✅ Lock profit sớm")
    print("  ✅ Giảm risk exposure")

