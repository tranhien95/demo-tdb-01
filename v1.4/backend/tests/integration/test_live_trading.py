import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from live_trading_engine import get_live_trading_engine
from live_trading_models import TradingConfig

try:
    engine = get_live_trading_engine()
    print('✅ Engine created')
    
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
    print(f'✅ Engine initialized: {result}')
    
    if result:
        state = engine.get_state()
        print(f'✅ State: balance={state.get("balance")}, equity={state.get("equity")}')
    
except Exception as e:
    print(f'❌ Error: {e}')
    import traceback
    traceback.print_exc()
