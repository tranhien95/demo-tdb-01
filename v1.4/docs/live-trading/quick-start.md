# 🚀 LIVE TRADING MVP - QUICK START (3 Steps)

## ✅ What's New (Phase 1 Complete)

### New Files Created:
1. **backend/live_trading_models.py** - Data models
2. **backend/live_trading_engine.py** - Core trading engine
3. **frontend/src/components/LiveTradingDashboard.tsx** - UI dashboard
4. **LIVE_TRADING_SETUP.md** - Detailed documentation

### API Endpoints Added to main.py:
```
POST   /api/live-trading/start      - Start trading session
GET    /api/live-trading/status     - Get current status
POST   /api/live-trading/update     - Update (fetch, signals, trade)
POST   /api/live-trading/pause      - Pause trading
POST   /api/live-trading/resume     - Resume trading
POST   /api/live-trading/stop       - Stop trading
POST   /api/live-trading/close-all  - Close all positions
```

### Dependencies Updated:
```
fastapi==0.104.1
uvicorn==0.24.0
pydantic==1.10.13
```

---

## 🎯 How to Run (3 Steps)

### **Step 1: Start Backend**
```bash
cd d:\Trade\Demo1\v1.4\backend
python main.py
```

Should see:
```
INFO:     Uvicorn running on http://0.0.0.0:4000
```

### **Step 2: Start Frontend**
```bash
cd d:\Trade\Demo1\v1.4\frontend
npm run dev
```

Should see:
```
VITE v5.0.0 ready in... ms
➜  Local: http://localhost:5173
```

(Note: If you see port 5173 instead of 3001, that's fine - React will use that port)

### **Step 3: Open & Use Live Trading**

1. Go to `http://localhost:5173` (or whatever port frontend shows)
2. Click **"📊 Live Trading"** tab
3. **Configure:**
   - **Symbol:** BTCUSDT (or ETHUSDT, XAUUSD, etc.)
   - **Timeframe:** M5 (5-minute candles)
   - **Strategy:** Select a saved strategy (if none, create one in Strategy Builder first)
   - **Initial Balance:** 1000 (USDT)
   - **Risk %:** 2 (% of balance per trade)
   - **Margin:** 1.0 (no leverage)
   - **SL %:** 2.0 (stop loss %)
   - **Reversal Strength:** 70 (%)
4. Click **"▶️ START TRADING"**

---

## 📊 What Happens Automatically

✅ **Every 5 seconds:**
1. Fetches latest 200 candles from Binance
2. Runs 27 indicators
3. Calculates signal (STRONG_BUY → STRONG_SELL)
4. **Auto-enters** when signal = STRONG_BUY + confidence ≥ 65%
5. **Auto-exits** when:
   - Price hits Take Profit (TP)
   - Price hits Stop Loss (SL)
   - Opposite STRONG signal appears (reversal)
6. Updates P&L, balance, equity in real-time
7. Saves all trades to database

---

## 💡 Configuration Explained

| Setting | Example | What It Does |
|---------|---------|-------------|
| **Symbol** | BTCUSDT | Which crypto pair to trade |
| **Timeframe** | M5 | 5-minute candles (M1, M5, M15, H1, H4, D) |
| **Strategy** | MyStrat | Which saved strategy to use |
| **Initial Balance** | 1000 | Starting capital (USDT) |
| **Risk %** | 2 | % of balance risked per trade (1-5% safe) |
| **Margin** | 1.0 | Leverage (1=none, 2=2x, 5=5x) |
| **SL %** | 2.0 | Fixed stop loss % from entry |
| **Reversal %** | 70 | Confidence needed for reversal exit |

**Example Trade:**
- Entry: $50,000 (1 BTC at BTCUSDT)
- Risk 2% = $20 per trade
- SL 2% = $49,000
- TP 2% × 2 = $51,000 (2:1 reward:risk)
- Position size = $20 / (50000 × 2%) = 0.02 BTC

---

## 🎮 Dashboard Controls

**Start Trading:**
- Configure settings → Click **"▶️ START TRADING"**

**While Trading:**
- **⏸️ Pause** - Stop new entries, keep positions open
- **▶️ Resume** - Continue after pause
- **⏹️ Stop** - Stop everything, save state
- **Close All** - Manually close all positions

**Monitor:**
- **Account Stats** - Balance, Equity, Daily P&L, Win Rate
- **Performance** - Profit Factor, Max Drawdown, Margin Usage
- **Open Positions** - Real-time P&L for each position
- **Trade History** - Last 10 closed trades

---

## ⚙️ Advanced Settings

### Position Sizing Formula:
```
position_size = (balance × risk_percent) / (entry_price × sl_percent)
```

### Exit Signals:
1. **TP Hit** → Close with profit
2. **SL Hit** → Close with loss
3. **Reversal** → STRONG signal opposite direction
4. **Manual** → Close All button

### P&L Calculation:
```
LONG:  P&L = (exit_price - entry_price) × quantity
SHORT: P&L = (entry_price - exit_price) × quantity
```

---

## 🔧 Troubleshooting

| Problem | Solution |
|---------|----------|
| "Strategy not found" | Create/save a strategy in Strategy Builder first |
| No positions opening | Check if signal is STRONG_BUY, confidence ≥ 65% |
| Positions not closing | Check update every 5s is running, verify price |
| Connection error | Check Binance API status, try different symbol |
| Port already in use | Change port in main.py or kill process |

---

## 📈 Live Testing Tips

1. **Start small** - Use 1000 USDT, 2% risk
2. **Watch 1 hour** - Let it run, observe behavior
3. **Check P&L** - Look for consistent winning signals
4. **Monitor margin** - Make sure you don't run out
5. **Save state** - Auto-saves to `backend/trading_data/`

---

## 🔮 Next Phase (Phase 2 - Coming Soon)

- [ ] Real Binance Testnet integration
- [ ] Multiple concurrent strategies
- [ ] Advanced charting
- [ ] Email/Discord notifications
- [ ] Dynamic position sizing
- [ ] Trailing stop loss
- [ ] Risk management (max DD limit)
- [ ] Manual order override

---

## 📞 Support

**Error with backend?**
```bash
cd backend
python -m pip install --upgrade pydantic fastapi uvicorn
python main.py
```

**Error with frontend?**
```bash
cd frontend
npm install
npm run dev
```

**Detailed docs:**
See `LIVE_TRADING_SETUP.md` for full technical documentation

---

## ✨ Features You Have Now

✅ Paper trading (no real money)  
✅ Live Binance data (real prices)  
✅ 27 advanced indicators  
✅ Auto-entry & auto-exit  
✅ Real-time P&L tracking  
✅ Trade history logging  
✅ Performance metrics  
✅ Responsive dashboard  
✅ Saved strategies support  
✅ Configurable risk management  

---

**Ready to trade?** 🚀

**Go to Live Trading tab and click START!**
