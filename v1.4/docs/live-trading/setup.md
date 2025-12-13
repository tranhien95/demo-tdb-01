# 🚀 Phase 1 - Live Trading MVP Setup Guide

## ✅ What's Implemented

### Backend (Python):
1. **live_trading_models.py** - Data models for trading
   - `TradingConfig` - Configuration settings
   - `Position` - Open position tracking
   - `ClosedTrade` - Historical trades
   - `LiveTradingState` - Overall state

2. **live_trading_engine.py** - Core trading logic
   - Initialize trading session
   - Fetch live Binance data
   - Calculate signals from strategy
   - Auto-execute entries based on signals
   - Auto-exit on TP/SL hit or reversal signal
   - Track P&L and metrics
   - Persist state to JSON

3. **main.py** - REST API endpoints
   - `POST /api/live-trading/start` - Start trading
   - `GET /api/live-trading/status` - Get status
   - `POST /api/live-trading/update` - Update (fetch data, check signals, execute)
   - `POST /api/live-trading/pause` - Pause
   - `POST /api/live-trading/resume` - Resume
   - `POST /api/live-trading/stop` - Stop
   - `POST /api/live-trading/close-all` - Close all positions

### Frontend (React):
1. **LiveTradingDashboard.tsx** - Complete trading UI
   - Configuration panel (symbol, timeframe, strategy, settings)
   - Account statistics (balance, equity, P&L)
   - Performance metrics (win rate, profit factor, drawdown)
   - Open positions panel with real-time P&L
   - Trade history table
   - Control buttons (start, pause, resume, stop, close-all)

## 🔧 How It Works

### Entry Logic:
1. Fetch latest 200 candles from Binance
2. Run selected strategy through all 27 indicators
3. Calculate signal (STRONG_BUY, BUY, NEUTRAL, SELL, STRONG_SELL)
4. **Entry:** If signal >= STRONG_BUY and confidence >= 65%
   - Position size = (balance × risk%) / (entry_price × SL%)
   - SL = entry_price ± SL% (configurable, default 2%)
   - TP = entry_price ± (SL% × 2) for 2:1 risk/reward

### Exit Logic (Auto-Close):
1. **TP Hit:** When price reaches TP level → CLOSE with profit
2. **SL Hit:** When price hits SL level → CLOSE with loss
3. **Reversal Signal:** When strong opposite signal appears with confidence >= reversal_threshold%
   - LONG + STRONG_SELL → Close
   - SHORT + STRONG_BUY → Close

### State Tracking:
- Real-time position P&L calculation
- Cumulative account balance
- Equity = balance + open positions P&L
- Metrics: win_rate, profit_factor, max_drawdown, daily_pnl
- All data persisted to `backend/trading_data/` as JSON

## 📋 Configuration Options

```python
symbol: str              # BTCUSDT, ETHUSDT, etc.
timeframe: str          # M1, M5, M15, H1, H4, D
strategy_name: str      # Select from saved strategies
initial_balance: float  # Starting capital (USDT)
risk_percent: float     # % of balance per trade (1-5% recommended)
margin: float           # Leverage (1.0 = no leverage, 2.0 = 2x)
stoploss_percent: float # Fixed SL % (1-3% recommended)
reversal_strength_threshold: float  # Reversal signal strength (50-80%)
max_positions: int      # Max concurrent positions
```

## 🚀 Quick Start

### Step 1: Ensure Backend is Running
```bash
cd d:\Trade\Demo1\v1.4\backend
python main.py
# Should see: Uvicorn running on http://0.0.0.0:4000
```

### Step 2: Ensure Frontend is Running
```bash
cd d:\Trade\Demo1\v1.4\frontend
npm run dev
# Should see: http://localhost:3001
```

### Step 3: Use Live Trading Dashboard

1. Click **"📊 Live Trading"** tab
2. **Configure:**
   - Symbol: BTCUSDT (or your choice)
   - Timeframe: M5
   - Strategy: Select a saved strategy
   - Initial Balance: 1000 USDT
   - Risk %: 2% per trade
   - Margin: 1.0 (no leverage)
   - SL %: 2.0%
   - Reversal Strength: 70%

3. Click **"▶️ START TRADING"**
   - System will fetch live Binance data
   - Run indicators every 5 seconds
   - Auto-enter when STRONG_BUY appears
   - Auto-exit on TP/SL/Reversal

4. **Monitor:**
   - Open Positions panel shows live P&L
   - Account stats show balance, equity, daily P&L
   - Performance metrics show win rate, profit factor
   - Recent trades table shows all closed trades

5. **Control:**
   - **Pause:** Stop new entries, keep open positions
   - **Resume:** Resume trading
   - **Stop:** Stop trading and save state
   - **Close All:** Manually close all positions

## 📊 Example Scenario

**Config:**
- Symbol: BTCUSDT
- Timeframe: M5
- Initial Balance: 1000 USDT
- Risk per Trade: 2% = $20
- SL: 2% = $200 loss max per trade
- Position Size = $20 / ($50000 × 0.02) = 0.02 BTC ≈ $1000

**Trade Execution:**
1. Signal: STRONG_BUY (confidence 85%)
2. Entry: $50,000 @ 0.02 BTC
3. SL: $49,000 (2% below)
4. TP: $51,000 (2% above = 2:1 RR)
5. If price hits $51,000 → **Close at +$200 profit**
6. If price hits $49,000 → **Close at -$200 loss**
7. If STRONG_SELL signal → **Close immediately**

## 🔄 Update Interval

- Default: Every 5 seconds
- Fetches latest candles
- Recalculates all indicators
- Checks exit conditions
- Checks entry conditions
- Updates P&L and metrics

To change interval, edit in LiveTradingDashboard.tsx:
```typescript
setInterval(() => {
  updateTrading();
}, 5000); // Change to 10000 for 10 seconds, etc.
```

## 💾 Data Persistence

All trading sessions are saved to:
```
backend/trading_data/SYMBOL_TIMESTAMP.json
```

Example: `backend/trading_data/BTCUSDT_2025-12-09T14_30_45.json`

Contains:
- Complete config
- All open/closed trades
- Account balance history
- Performance metrics
- Timestamps

## ⚠️ Important Notes

1. **Paper Trading Only:** No real money used, all simulated
2. **Market Hours:** Works 24/7 with crypto (Binance always open)
3. **Slippage:** Not simulated - assumes instant execution at signal price
4. **Fees:** Not deducted - real trading will have 0.1% fees per trade
5. **Margin:** If margin > 1.0, position size increases proportionally

## 🔮 Next Phase Features (Phase 2)

- [ ] Real Binance Testnet integration (actual orders)
- [ ] Trailing stop loss
- [ ] Dynamic position sizing (Kelly Criterion)
- [ ] Multiple symbol trading
- [ ] Webhooks for trade notifications
- [ ] Advanced charting with indicators
- [ ] Backtest comparison
- [ ] Risk management (daily loss limit, max DD)
- [ ] Manual order placement override
- [ ] Order modification (adjust SL/TP while open)

## 🐛 Troubleshooting

**Q: "Strategy not found" error**
- A: Make sure strategy is saved in Strategy Builder first
- Go to Strategy Builder tab → Create/configure strategy → Save

**Q: No positions opening**
- Check if signal is reaching STRONG_BUY threshold
- Check confidence is >= 65%
- Check max_positions hasn't been reached
- Check available margin is enough

**Q: Positions not closing on TP**
- Check if update interval is running (should update every 5s)
- Check if price actually reached TP level
- Check if reversal signal is strong enough (threshold %)

**Q: Connection errors to Binance**
- Check internet connection
- Check Binance API status (status.binance.com)
- Try different symbol (BTCUSDT usually most reliable)

## 📞 API Response Examples

### Start Trading Response:
```json
{
  "status": "started",
  "state": {
    "status": "running",
    "config": {...},
    "balance": 1000,
    "equity": 1000,
    "open_positions": [],
    "total_trades": 0,
    "win_rate": 0,
    "daily_pnl": 0
  }
}
```

### Update Response (with position):
```json
{
  "status": "success",
  "result": {
    "current_price": 50234.50,
    "open_positions": 1,
    "signal": "STRONG_BUY"
  },
  "state": {
    "balance": 1000,
    "equity": 1015.50,
    "open_positions": [{
      "id": "uuid",
      "side": "LONG",
      "entry_price": 50000,
      "current_price": 50234.50,
      "current_pnl": 234.50,
      "current_pnl_percent": 2.35
    }]
  }
}
```

---

**Ready to trade!** 🎯 Let me know if you need any modifications or have questions!
