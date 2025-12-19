# TradingView Settings Fix - Critical for Matching Python Backtest

## ⚠️ Problem: TradingView Shows Only 7% Profit vs Python's 91%

**Root Cause:** TradingView's UI Settings are overriding the calculated `qty` in Pine Script code.

## ✅ Solution: Fix TradingView Settings

### Step 1: Open Strategy Settings
1. Click the **Settings button (⚙️)** on the TradingView chart
2. Or right-click on strategy name → "Settings"

### Step 2: Fix "Kích thước lệnh mặc định" (Default Order Size)
1. Go to **"Đặc tính" (Properties)** tab
2. Find **"Kích thước lệnh mặc định" (Default Order Size)**
3. **CHANGE VALUE FROM `1` TO `0`** (zero)
4. Or leave it empty/blank
5. Make sure Type is **"Fixed"** or **"Số lượng"** (not "Percentage")

### Step 3: Verify Settings Match Python Backtest

| Setting | Python Backtest | TradingView Should Be |
|---------|----------------|----------------------|
| Initial Capital | 1000 | 1000 |
| Default Order Size | Calculated (~0.6-0.7) | **0** (not 1!) |
| Commission | 0% | 0% |
| Slippage | 0 | 0 ticks |
| Pyramiding | 0 | 0 orders |

### Step 4: Verify Data Period
- Check that TradingView is using the **same date range** as Python backtest
- Example: Python uses Nov 15, 2025 - Dec 13, 2025
- TradingView must use the **exact same period**

## 🔍 How to Verify Settings are Correct

After running backtest, check the **trade list**:

### ❌ WRONG (Settings Override):
- "Cỡ lệnh" shows **"1 hợp đồng"** or **"1"**
- Profit is only **~7%** instead of **~91%**

### ✅ CORRECT (Using Calculated Qty):
- "Cỡ lệnh" shows **"0.62768"** or similar calculated value
- Profit matches Python backtest (**~91%**)

## 📊 Position Size Calculation

The Pine Script calculates position size based on risk:

```
risk_amount = initial_capital * risk_percent / 100
position_size = risk_amount / (sl_percent / 100)
qty = position_size / entry_price
```

**Example:**
- Initial Capital: $1,000
- Risk %: 10%
- SL %: 5%
- Entry Price: $3,186.34

**Calculation:**
- Risk Amount = $1,000 × 10% = $100
- Position Size = $100 ÷ 5% = **$2,000**
- Quantity = $2,000 ÷ $3,186.34 = **0.62768**

If Settings override to `1`, position size becomes only `1 × $3,186.34 = $3,186.34`, which is **much larger** than intended, leading to different risk and profit calculations.

## 🔧 Alternative: Force Qty in Code

If Settings still override, you can hardcode the qty calculation in Pine Script (not recommended, but works):

```pine
// Force qty calculation (bypasses Settings)
calculate_qty(entry_price) =>
    risk_amount = initial_capital * risk_percent / 100
    position_size = risk_amount / (sl_percent / 100)
    qty = position_size / entry_price
    math.max(qty, 0.0001)  // Ensure minimum qty > 0

// Use it explicitly
qty_long = calculate_qty(close)
strategy.entry("Long", strategy.long, qty=qty_long)
```

## 📝 Summary

1. **ALWAYS set Default Order Size = 0** in TradingView Settings
2. **Verify trade list shows calculated qty** (not "1 hợp đồng")
3. **Check data period matches** Python backtest
4. **Compare number of trades** - should be same between Python and TradingView

If profit still doesn't match after fixing Settings, check:
- Entry timing (do trades start at same time?)
- Number of trades (same count?)
- Position size in trade list (calculated qty or "1"?)

