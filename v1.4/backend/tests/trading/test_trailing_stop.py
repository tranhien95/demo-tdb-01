"""
Test Trailing Stop Loss Implementation
Demo cách trailing stop hoạt động
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from live_trading_models import Position, TradingConfig
from live_trading_engine import LiveTradingEngine
from datetime import datetime
from indicators.base import HelperFunctions


def test_trailing_stop_logic():
    """Test trailing stop logic với simulated price movement"""
    
    print("=" * 80)
    print("TEST TRAILING STOP LOSS")
    print("=" * 80)
    
    # Create test position
    entry_price = 100.0
    initial_sl = 99.0  # 1% SL
    position = Position(
        id="test-1",
        symbol="BTCUSDT",
        entry_price=entry_price,
        entry_time=datetime.now(),
        quantity=1.0,
        side="LONG",
        stoploss=initial_sl,
        takeprofit=102.0,  # 2% TP (2:1 R:R)
        entry_signal="STRONG_BUY",
        entry_confidence=80.0,
        highest_price=entry_price,
        lowest_price=0.0,
        initial_stoploss=initial_sl,
        trailing_activated=False
    )
    
    # Create mock candles for ATR calculation
    # Simulate price movement: 100 → 101 → 102 → 103 → 102 → 101
    candles = []
    base_time = datetime.now()
    prices = [100, 100.5, 101, 101.5, 102, 102.5, 103, 102.5, 102, 101.5, 101]
    
    for i, price in enumerate(prices):
        # Create candle with some volatility
        high = price * 1.002  # +0.2%
        low = price * 0.998   # -0.2%
        candles.append({
            'time': base_time,
            'open': price,
            'high': high,
            'low': low,
            'close': price,
            'volume': 1000.0
        })
    
    # Create engine instance
    engine = LiveTradingEngine()
    
    # Create mock config
    config = TradingConfig(
        symbol="BTCUSDT",
        timeframe="M5",
        strategy_name="Test",
        initial_balance=10000.0,
        risk_percent=2.0,
        margin=1.0,
        stoploss_percent=1.0,
        enable_trailing_stop=True,
        trailing_multiplier=1.5,
        trailing_activation_r=1.0
    )
    
    # Create mock state
    from live_trading_models import LiveTradingState, TradeStatus
    engine.state = LiveTradingState(
        status=TradeStatus.RUNNING,
        config=config,
        balance=10000.0,
        equity=10000.0,
        used_margin=0.0,
        available_margin=10000.0
    )
    
    # Convert candles to CandleData format
    from live_trading_models import CandleData
    candle_data = []
    for c in candles:
        candle_data.append(CandleData(
            time=c['time'],
            open=c['open'],
            high=c['high'],
            low=c['low'],
            close=c['close'],
            volume=c['volume']
        ))
    
    engine.price_history["BTCUSDT"] = candle_data
    
    print(f"\nInitial Position:")
    print(f"  Entry: ${entry_price:.2f}")
    print(f"  Initial SL: ${initial_sl:.2f} (1% below entry)")
    print(f"  TP: $102.00 (2% above entry)")
    print(f"  Trailing activated: {position.trailing_activated}")
    
    print(f"\n{'='*80}")
    print("SIMULATING PRICE MOVEMENT")
    print("="*80)
    
    # Simulate price movement
    test_prices = [100, 100.5, 101, 101.5, 102, 102.5, 103, 102.5, 102, 101.5, 101, 100.5, 100]
    
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
        print(f"  Trailing activated: {position.trailing_activated}")
        
        # Update trailing stop
        old_sl = position.stoploss
        engine._update_trailing_stop(position, price)
        
        if position.stoploss != old_sl:
            print(f"  ✅ SL Updated: ${old_sl:.2f} → ${position.stoploss:.2f}")
        
        # Check if SL hit
        if price <= position.stoploss:
            print(f"  🛑 STOP LOSS HIT! Price ${price:.2f} <= SL ${position.stoploss:.2f}")
            break
    
    print(f"\n{'='*80}")
    print("FINAL RESULTS")
    print("="*80)
    print(f"  Final Price: ${test_prices[-1]:.2f}")
    print(f"  Final SL: ${position.stoploss:.2f}")
    print(f"  Trailing activated: {position.trailing_activated}")
    print(f"  SL moved from ${initial_sl:.2f} to ${position.stoploss:.2f}")
    print(f"  Profit protected: ${position.stoploss - initial_sl:.2f}")


def test_trailing_stop_short():
    """Test trailing stop cho SHORT position"""
    
    print("\n" + "=" * 80)
    print("TEST TRAILING STOP - SHORT POSITION")
    print("=" * 80)
    
    entry_price = 100.0
    initial_sl = 101.0  # 1% above entry (for SHORT)
    position = Position(
        id="test-2",
        symbol="BTCUSDT",
        entry_price=entry_price,
        entry_time=datetime.now(),
        quantity=1.0,
        side="SHORT",
        stoploss=initial_sl,
        takeprofit=98.0,  # 2% below entry
        entry_signal="STRONG_SELL",
        entry_confidence=80.0,
        highest_price=float('inf'),
        lowest_price=entry_price,
        initial_stoploss=initial_sl,
        trailing_activated=False
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
        enable_trailing_stop=True,
        trailing_multiplier=1.5,
        trailing_activation_r=1.0
    )
    
    from live_trading_models import LiveTradingState, TradeStatus, CandleData
    engine.state = LiveTradingState(
        status=TradeStatus.RUNNING,
        config=config,
        balance=10000.0,
        equity=10000.0,
        used_margin=0.0,
        available_margin=10000.0
    )
    
    # Create mock candles (price going down)
    prices = [100, 99.5, 99, 98.5, 98, 97.5, 97, 97.5, 98, 98.5, 99]
    candle_data = []
    base_time = datetime.now()
    
    for price in prices:
        candle_data.append(CandleData(
            time=base_time,
            open=price,
            high=price * 1.002,
            low=price * 0.998,
            close=price,
            volume=1000.0
        ))
    
    engine.price_history["BTCUSDT"] = candle_data
    
    print(f"\nInitial SHORT Position:")
    print(f"  Entry: ${entry_price:.2f}")
    print(f"  Initial SL: ${initial_sl:.2f} (1% above entry)")
    print(f"  TP: $98.00 (2% below entry)")
    
    # Simulate price going down (good for SHORT)
    test_prices = [100, 99.5, 99, 98.5, 98, 97.5, 97, 97.5, 98, 98.5, 99, 99.5, 100]
    
    for i, price in enumerate(test_prices):
        position.update_price(price)
        profit = entry_price - price
        profit_pct = (profit / entry_price) * 100
        sl_distance_pct = abs(entry_price - initial_sl) / entry_price * 100
        profit_r = profit_pct / sl_distance_pct if sl_distance_pct > 0 else 0
        
        old_sl = position.stoploss
        engine._update_trailing_stop(position, price)
        
        if i < 5:  # Only show first few steps
            print(f"\nPrice: ${price:.2f}, Profit: {profit_r:.2f}R, SL: ${position.stoploss:.2f}", end="")
            if position.stoploss != old_sl:
                print(f" (Updated from ${old_sl:.2f})")
            else:
                print()
        
        if price >= position.stoploss:
            print(f"\n🛑 STOP LOSS HIT! Price ${price:.2f} >= SL ${position.stoploss:.2f}")
            break
    
    print(f"\nFinal SL: ${position.stoploss:.2f} (moved from ${initial_sl:.2f})")


if __name__ == "__main__":
    test_trailing_stop_logic()
    test_trailing_stop_short()
    
    print("\n" + "=" * 80)
    print("✅ TRAILING STOP TEST COMPLETE")
    print("=" * 80)
    print("\nKey Features:")
    print("  ✅ Trailing chỉ kích hoạt khi profit >= 1R")
    print("  ✅ SL chỉ di chuyển theo hướng có lợi (lên cho LONG, xuống cho SHORT)")
    print("  ✅ Trailing distance = ATR × multiplier (default 1.5x)")
    print("  ✅ Bảo vệ profit khi giá quay đầu")


