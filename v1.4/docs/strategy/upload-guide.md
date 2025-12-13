# 📤 Strategy Upload Guide

## Overview

The Live Trading Dashboard now supports uploading custom strategies via JSON. You can either:

1. **Select from saved strategies** - dropdown list
2. **Paste JSON strategy** - custom strategy in JSON format

---

## Option 1: Use Saved Strategies

In the **Live Trading Dashboard**:

1. Select strategy from **Strategy** dropdown
2. The dropdown auto-loads all saved strategies from `/backend/saved_strategies/`

**Available strategies:**
- MACD_Strategy
- RSI_Strategy
- Combined_Indicators
- (Any others you've saved)

---

## Option 2: Upload Custom Strategy JSON

### Step 1: Prepare Your Strategy JSON

Create a JSON file with this structure:

```json
{
  "name": "my-custom-strategy",
  "description": "My custom trading strategy",
  "indicators": [
    {
      "name": "rsi",
      "params": {
        "period": 14,
        "overbought": 70,
        "oversold": 30
      }
    },
    {
      "name": "macd",
      "params": {
        "fast_period": 12,
        "slow_period": 26,
        "signal_period": 9
      }
    }
  ],
  "entry_signals": {
    "long": {
      "condition": "rsi < 30 AND macd_histogram > 0",
      "confidence": 75
    },
    "short": {
      "condition": "rsi > 70 AND macd_histogram < 0",
      "confidence": 75
    }
  },
  "exit_signals": {
    "tp_percent": 2,
    "sl_percent": 1.5
  },
  "risk_management": {
    "max_positions": 1,
    "position_size_percent": 2
  },
  "enabled": true
}
```

### Step 2: Copy Strategy JSON

In the **Live Trading Dashboard**:

1. Scroll to **"Or Paste Strategy JSON"** field
2. Paste your JSON into the textarea
3. Click **"Upload Strategy JSON"** button

### Step 3: Confirm Upload

You'll see: ✅ Loaded: my-custom-strategy

The strategy is now selected and ready to use!

---

## Strategy JSON Fields

| Field | Type | Description |
|-------|------|-------------|
| `name` | string | Strategy identifier (required) |
| `description` | string | Human-readable description |
| `indicators` | array | List of indicators to use |
| `entry_signals` | object | Long/short entry conditions |
| `exit_signals` | object | TP/SL percentages |
| `risk_management` | object | Position sizing rules |
| `enabled` | boolean | Enable/disable strategy |

### Indicators Supported

- **rsi** - Relative Strength Index
- **macd** - MACD
- **ema** - Exponential Moving Average
- **bollinger** - Bollinger Bands
- **atr** - Average True Range
- **stochastic** - Stochastic Oscillator
- **roc** - Rate of Change
- **adx** - Average Directional Index
- **cci** - Commodity Channel Index
- **obv** - On Balance Volume
- [+18 more indicators available]

---

## Example Strategies

### Strategy 1: Simple RSI

```json
{
  "name": "RSI-Only",
  "indicators": [
    {"name": "rsi", "params": {"period": 14}}
  ],
  "entry_signals": {
    "long": {"condition": "rsi < 30", "confidence": 60},
    "short": {"condition": "rsi > 70", "confidence": 60}
  },
  "exit_signals": {"tp_percent": 2, "sl_percent": 1.5},
  "risk_management": {"max_positions": 1, "position_size_percent": 2},
  "enabled": true
}
```

### Strategy 2: MACD + EMA

```json
{
  "name": "MACD-EMA",
  "indicators": [
    {"name": "macd", "params": {"fast_period": 12, "slow_period": 26, "signal_period": 9}},
    {"name": "ema", "params": {"period": 50}}
  ],
  "entry_signals": {
    "long": {
      "condition": "macd_histogram > 0 AND price > ema_50",
      "confidence": 70
    }
  },
  "exit_signals": {"tp_percent": 3, "sl_percent": 2},
  "risk_management": {"max_positions": 2, "position_size_percent": 1},
  "enabled": true
}
```

---

## Troubleshooting

### ❌ "Invalid JSON or error uploading"

- Check JSON syntax (use JSONLint.com)
- Ensure `name` field exists
- Verify all quotes are double quotes (not single)

### ❌ Strategy dropdown empty after upload

- Backend may not be running
- Check browser console for errors
- Restart backend: `python main.py`

### ❌ Upload appears to work but strategy not selectable

- Try selecting it from the dropdown
- If not there, check `/backend/saved_strategies/` folder
- May need to reload the page

---

## Using Uploaded Strategy

Once uploaded:

1. ✅ Strategy appears in dropdown
2. ✅ Automatically selected in form
3. ✅ Ready to use in Live Trading
4. ✅ Saved to `/backend/saved_strategies/`

Click **"▶️ START TRADING"** to begin!

---

## API Details

**Endpoint:** `POST /api/strategy/upload`

**Request:**
```json
{
  "name": "my-strategy",
  "indicators": [...],
  ...
}
```

**Response:**
```json
{
  "status": "success",
  "strategy_name": "my-strategy",
  "message": "Strategy \"my-strategy\" uploaded"
}
```

---

## File Locations

```
v1.4/
├── backend/
│   ├── main.py              (FastAPI server)
│   └── saved_strategies/    (Stored strategies)
│       ├── MACD_Strategy.json
│       ├── RSI_Strategy.json
│       └── my-custom-strategy.json  ← Your uploaded strategy
└── frontend/
    └── LiveTradingDashboard.tsx    (Dashboard component)
```

---

## Tips

💡 **Start Simple** - Begin with 1-2 indicators, then add more

💡 **Test Conditions** - Condition syntax: `indicator comparison value`

💡 **Confidence Scores** - 50-100 range (higher = more confident entries)

💡 **Risk Limits** - Keep position_size_percent ≤ 2% for safety

💡 **Paper Trade First** - All trades are simulated (no real money)

---

## Next Steps

1. ✅ Prepare your strategy JSON
2. ✅ Copy & paste into Dashboard
3. ✅ Click "Upload Strategy JSON"
4. ✅ Verify it loads successfully
5. ✅ Configure other settings (balance, risk, etc.)
6. ✅ Click "START TRADING"

**Ready to trade!** 🚀

---

*Last updated: December 9, 2025*
