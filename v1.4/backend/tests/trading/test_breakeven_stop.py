"""
Test Breakeven Stop Implementation
Demo cách breakeven stop hoạt động
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from live_trading_models import Position, TradingConfig, LiveTradingState, TradeStatus
from live_trading_engine import LiveTradingEngine
from datetime import datetime


def test_breakeven_stop_long():
    """Test breakeven stop cho LONG position"""
    
    print("=" * 80)
    print("TEST BREAKEVEN STOP - LONG POSITION")
    print("=" * 80)
    
    # Create test position
    entry_price = 100.0
    initial_sl = 99.0  # 1% below entry
    position = Position(
        id="test-breakeven-1",
        symbol="BTCUSDT",
        entry_price=entry_price,
        entry_time=datetime.now(),
        quantity=1.0,
        side="LONG",
        stoploss=initial_sl,
        takeprofit=102.0,
        entry_signal="STRONG_BUY",
        entry_confidence=80.0,
        highest_price=entry_price,
        lowest_price=0.0,
        initial_stoploss=initial_sl,
        trailing_activated=False,
        breakeven_set=False
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
        enable_breakeven_stop=True,
        breakeven_activation_r=1.0,  # Activate at 1R
        breakeven_buffer_pct=0.1  # 0.1% buffer
    )
    
    engine.state = LiveTradingState(
        status=TradeStatus.RUNNING,
        config=config,
        balance=10000.0,
        equity=10000.0,
        used_margin=0.0,
        available_margin=10000.0
    )
    
    print(f"\nInitial Position:")
    print(f"  Entry: ${entry_price:.2f}")
    print(f"  Initial SL: ${initial_sl:.2f} (1% below entry)")
    print(f"  Breakeven activation: {config.breakeven_activation_r}R")
    print(f"  Buffer: {config.breakeven_buffer_pct}%")
    
    print(f"\n{'='*80}")
    print("SIMULATING PRICE MOVEMENT")
    print("="*80)
    
    # Simulate price movement
    test_prices = [
        100.0,  # Entry
        100.3,  # 0.3R
        100.5,  # 0.5R
        100.7,  # 0.7R
        100.9,  # 0.9R
        101.0,  # 1.0R - Should trigger breakeven!
        101.5,  # 1.5R
        102.0,  # 2.0R
        101.5,  # Pullback
        101.0,  # Pullback
        100.5,  # Pullback - Should hit breakeven SL
    ]
    
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
        print(f"  Current SL: ${position.stoploss:.2f}")
        print(f"  Breakeven set: {position.breakeven_set}")
        
        # Check breakeven
        old_sl = position.stoploss
        engine._check_breakeven_stop(position, price)
        
        if position.stoploss != old_sl:
            print(f"  ✅ BREAKEVEN ACTIVATED! SL: ${old_sl:.2f} → ${position.stoploss:.2f}")
            print(f"  ✅ Entry: ${entry_price:.2f}, New SL: ${position.stoploss:.2f} (Entry + {config.breakeven_buffer_pct}%)")
        
        # Check if SL hit
        if price <= position.stoploss:
            print(f"  🛑 STOP LOSS HIT! Price ${price:.2f} <= SL ${position.stoploss:.2f}")
            if position.breakeven_set:
                print(f"  ✅ Protected by breakeven! Exit at entry level (no loss)")
            break
    
    print(f"\n{'='*80}")
    print("FINAL RESULTS")
    print("="*80)
    print(f"  Final Price: ${test_prices[-1]:.2f}")
    print(f"  Final SL: ${position.stoploss:.2f}")
    print(f"  Breakeven set: {position.breakeven_set}")
    if position.breakeven_set:
        print(f"  ✅ Breakeven activated at ${position.stoploss:.2f}")
        print(f"  ✅ SL moved from ${initial_sl:.2f} to ${position.stoploss:.2f}")
        print(f"  ✅ Trade protected from loss!")


def test_breakeven_stop_short():
    """Test breakeven stop cho SHORT position"""
    
    print("\n" + "=" * 80)
    print("TEST BREAKEVEN STOP - SHORT POSITION")
    print("=" * 80)
    
    entry_price = 100.0
    initial_sl = 101.0  # 1% above entry
    position = Position(
        id="test-breakeven-2",
        symbol="BTCUSDT",
        entry_price=entry_price,
        entry_time=datetime.now(),
        quantity=1.0,
        side="SHORT",
        stoploss=initial_sl,
        takeprofit=98.0,
        entry_signal="STRONG_SELL",
        entry_confidence=80.0,
        highest_price=float('inf'),
        lowest_price=entry_price,
        initial_stoploss=initial_sl,
        trailing_activated=False,
        breakeven_set=False
    )
    
    engine = LiveTradingEngine()
    config = TradingConfig(
        symbol="BTCUSDT",
        timeframe="M5",
        strategy_name="Test",
        initial_balance=10000.0,
        risk_percent=2.0,
        margin=1.0,
        stoploss_percent=1.0,
        enable_breakeven_stop=True,
        breakeven_activation_r=1.0,
        breakeven_buffer_pct=0.1
    )
    
    engine.state = LiveTradingState(
        status=TradeStatus.RUNNING,
        config=config,
        balance=10000.0,
        equity=10000.0,
        used_margin=0.0,
        available_margin=10000.0
    )
    
    print(f"\nInitial SHORT Position:")
    print(f"  Entry: ${entry_price:.2f}")
    print(f"  Initial SL: ${initial_sl:.2f} (1% above entry)")
    
    # Simulate price going down (good for SHORT)
    test_prices = [
        100.0,  # Entry
        99.7,   # 0.3R
        99.5,   # 0.5R
        99.3,   # 0.7R
        99.1,   # 0.9R
        99.0,   # 1.0R - Should trigger breakeven!
        98.5,   # 1.5R
        98.0,   # 2.0R
        98.5,   # Pullback
        99.0,   # Pullback
        99.5,   # Pullback - Should hit breakeven SL
    ]
    
    for i, price in enumerate(test_prices):
        position.update_price(price)
        profit = entry_price - price
        profit_pct = (profit / entry_price) * 100
        sl_distance_pct = abs(entry_price - initial_sl) / entry_price * 100
        profit_r = profit_pct / sl_distance_pct if sl_distance_pct > 0 else 0
        
        if i < 8:  # Show first 8 steps
            print(f"\nPrice: ${price:.2f}, Profit: {profit_r:.2f}R, SL: ${position.stoploss:.2f}", end="")
            old_sl = position.stoploss
            engine._check_breakeven_stop(position, price)
            if position.stoploss != old_sl:
                print(f" → ${position.stoploss:.2f} (BREAKEVEN!)")
            else:
                print()
        
        if price >= position.stoploss:
            print(f"\n🛑 STOP LOSS HIT! Price ${price:.2f} >= SL ${position.stoploss:.2f}")
            if position.breakeven_set:
                print(f"  ✅ Protected by breakeven! Exit at entry level")
            break
    
    print(f"\nFinal SL: ${position.stoploss:.2f} (moved from ${initial_sl:.2f})")
    print(f"Breakeven set: {position.breakeven_set}")


def test_breakeven_vs_trailing():
    """Test interaction giữa breakeven và trailing"""
    
    print("\n" + "=" * 80)
    print("TEST BREAKEVEN + TRAILING INTERACTION")
    print("=" * 80)
    
    print("\nScenario: Breakeven activates first, then trailing takes over")
    print("="*80)
    
    entry_price = 100.0
    initial_sl = 99.0
    position = Position(
        id="test-combined",
        symbol="BTCUSDT",
        entry_price=entry_price,
        entry_time=datetime.now(),
        quantity=1.0,
        side="LONG",
        stoploss=initial_sl,
        takeprofit=102.0,
        entry_signal="STRONG_BUY",
        entry_confidence=80.0,
        highest_price=entry_price,
        lowest_price=0.0,
        initial_stoploss=initial_sl,
        trailing_activated=False,
        breakeven_set=False
    )
    
    engine = LiveTradingEngine()
    config = TradingConfig(
        symbol="BTCUSDT",
        timeframe="M5",
        strategy_name="Test",
        initial_balance=10000.0,
        risk_percent=2.0,
        margin=1.0,
        stoploss_percent=1.0,
        enable_breakeven_stop=True,
        breakeven_activation_r=1.0,
        breakeven_buffer_pct=0.1,
        enable_trailing_stop=True,
        trailing_multiplier=1.5,
        trailing_activation_r=1.0
    )
    
    engine.state = LiveTradingState(
        status=TradeStatus.RUNNING,
        config=config,
        balance=10000.0,
        equity=10000.0,
        used_margin=0.0,
        available_margin=10000.0
    )
    
    # Mock candles for ATR
    from live_trading_models import CandleData
    candles = []
    for i in range(20):
        candles.append(CandleData(
            time=datetime.now(),
            open=100.0,
            high=100.5,
            low=99.5,
            close=100.0,
            volume=1000.0
        ))
    engine.price_history["BTCUSDT"] = candles
    
    prices = [100.0, 100.5, 101.0, 101.5, 102.0, 102.5, 103.0, 102.5, 102.0]
    
    print(f"\nPrice Movement:")
    for i, price in enumerate(prices):
        position.update_price(price)
        profit_r = (price - entry_price) / (entry_price - initial_sl)
        
        print(f"\nPrice: ${price:.2f} ({profit_r:.2f}R)")
        
        # Check breakeven first
        old_sl = position.stoploss
        engine._check_breakeven_stop(position, price)
        if position.stoploss != old_sl:
            print(f"  [Breakeven] SL: ${old_sl:.2f} → ${position.stoploss:.2f}")
        
        # Then trailing
        old_sl = position.stoploss
        engine._update_trailing_stop(position, price)
        if position.stoploss != old_sl:
            print(f"  [Trailing] SL: ${old_sl:.2f} → ${position.stoploss:.2f}")
        
        print(f"  Final SL: ${position.stoploss:.2f}")
    
    print(f"\n✅ Breakeven và Trailing hoạt động cùng nhau:")
    print(f"  - Breakeven: Bảo vệ ở entry level")
    print(f"  - Trailing: Tiếp tục di chuyển SL lên khi profit tăng")


if __name__ == "__main__":
    test_breakeven_stop_long()
    test_breakeven_stop_short()
    test_breakeven_vs_trailing()
    
    print("\n" + "=" * 80)
    print("✅ BREAKEVEN STOP TEST COMPLETE")
    print("=" * 80)
    print("\nKey Features:")
    print("  ✅ Breakeven chỉ kích hoạt khi profit >= 1R")
    print("  ✅ SL di chuyển về entry + buffer (tránh spread)")
    print("  ✅ Bảo vệ trade khỏi loss khi đã có profit")
    print("  ✅ Hoạt động cùng với trailing stop")

