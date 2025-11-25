# ⚡ QUICK START (5 minutes)

## Step 1: Start Backend
```bash
cd d:\Trade\Demo1\v1.3
python run_backend.py
```

## Step 2: Open UI
```
file:///d:/Trade/Demo1/v1.3/combo-optimizer-v2.html
```

## Step 3: Test
1. Upload CSV (OANDA_XAUUSD_15.csv)
2. Click "Run Optimization"
3. See **+6.00% profit** in results ✅

---

## 📊 Problem Solved

| Metric | Before | After | Improvement |
|--------|--------|-------|------------|
| Indicator | RSI+MACD (0.4% agreement) | EMA_12+EMA_26 (100% agreement) | ✅ |
| Stop Loss | 2.0% | 0.75% | ✅ |
| RR Ratio | 4.0:1 | 2.0:1 | ✅ |
| **Profit** | **-2.36%** | **+6.00%** | **+8.36%** |
| Win Rate | 33% | 60% | +27% |
| Trades | 3 | 10 | +7 |

---

## 💡 Why It Works

1. **EMA Pair** - 100% agreement (no conflicting signals)
2. **RR 2:1** - Matches 60% win rate (positive expectancy)
3. **SL 0.75%** - Optimal balance (not too tight/loose)
4. **No Filters** - EMA is already high confidence

---

## 🆘 Troubleshooting

**Backend error?**
→ Check: `netstat -ano | Select-String ":8000"`
→ Fix: Restart backend, check port 8000 is free

**Wrong profit?**
→ Verify: CSV has 100+ candles
→ Check: All parameters match defaults (RR=2.0, SL=0.75%)
→ Try: Test with sample OANDA file

**Want to understand more?**
→ Read: README.md (complete guide)
→ See: test_correlated_pairs.py (verification)

---

**Status**: ✅ Production Ready | **Version**: 1.3.1
