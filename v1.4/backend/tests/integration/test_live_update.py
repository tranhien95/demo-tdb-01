import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from live_trading_engine import get_live_trading_engine
from live_trading_models import TradingConfig

try:
    engine = get_live_trading_engine()
    print('[OK] Engine created')
    
    config = TradingConfig(
        symbol='BTCUSDT',
        timeframe='M5',
        strategy_name='RSI_Strategy',
        initial_balance=1000,
        risk_percent=2,
        margin=1.0,
        stoploss_percent=2.0,
        reversal_strength_threshold=70,
        max_positions=1
    )
    
    result = engine.initialize(config)
    print(f'[OK] Engine initialized: {result}')
    
    if result:
        # Test update
        for i in range(3):
            state = engine.update()
            print(f'Update {i+1}:')
            print(f'  Status: {state.get("status", "unknown")}')
            print(f'  Balance: {state.get("balance")}')
            print(f'  Equity: {state.get("equity")}')
            open_pos = state.get("open_positions", [])
            if isinstance(open_pos, list):
                print(f'  Open positions: {len(open_pos)}')
            else:
                print(f'  Open positions: {open_pos}')
    
except Exception as e:
    print(f'[ERROR] {e}')
    import traceback
    traceback.print_exc()
