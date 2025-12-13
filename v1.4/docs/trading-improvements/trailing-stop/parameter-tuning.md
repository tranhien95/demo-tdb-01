# 🎛️ TRAILING STOP - TUNE PARAMETERS CHO MARKET CỤ THỂ

## 📊 OVERVIEW

Mỗi market type cần parameters khác nhau cho trailing stop. File này hướng dẫn tune parameters cho từng loại market.

---

## 🔍 PARAMETERS CẦN TUNE

### 1. **Trailing Multiplier**
- **Range**: 0.5x - 3.0x
- **Default**: 1.5x
- **Ảnh hưởng**: Khoảng cách giữa giá và SL

### 2. **Activation R**
- **Range**: 0.5R - 2.0R
- **Default**: 1.0R
- **Ảnh hưởng**: Khi nào trailing bắt đầu hoạt động

### 3. **ATR Period**
- **Range**: 7 - 21
- **Default**: 14
- **Ảnh hưởng**: Độ nhạy của ATR calculation

---

## 📈 MARKET TYPES & RECOMMENDED SETTINGS

### 1. **TRENDING MARKET (Uptrend/Downtrend mạnh)**

**Đặc điểm:**
- Giá di chuyển theo 1 hướng rõ ràng
- Ít pullback
- Momentum mạnh

**Recommended Settings:**
```python
trailing_multiplier = 2.0 - 2.5  # Loose hơn để không bị stop sớm
trailing_activation_r = 1.5 - 2.0  # Kích hoạt muộn để cho profit lớn
atr_period = 14  # Standard
```

**Lý do:**
- Multiplier lớn: Cho phép pullback lớn hơn, không bị stop sớm
- Activation R lớn: Chờ profit lớn trước khi trailing, maximize profit

**Ví dụ:**
```
BTC trong bull run:
- Multiplier: 2.5x
- Activation R: 2.0R
→ Cho phép pullback 2-3% mà không bị stop
→ Chỉ trailing khi profit >= 2R
```

---

### 2. **RANGING/SIDEWAYS MARKET**

**Đặc điểm:**
- Giá lên xuống trong range
- Không có trend rõ ràng
- Nhiều whipsaw

**Recommended Settings:**
```python
trailing_multiplier = 1.0 - 1.2  # Tight hơn để lock profit nhanh
trailing_activation_r = 0.5 - 0.75  # Kích hoạt sớm để bảo vệ profit
atr_period = 10  # Shorter period để nhạy hơn
```

**Lý do:**
- Multiplier nhỏ: Lock profit nhanh trước khi giá quay lại
- Activation R nhỏ: Bảo vệ profit sớm, tránh whipsaw

**Ví dụ:**
```
EUR/USD trong range 1.10 - 1.12:
- Multiplier: 1.0x
- Activation R: 0.5R
→ Lock profit ngay khi có 0.5R
→ Trailing tight để tránh bị whipsaw
```

**⚠️ Lưu ý:** Trong ranging market, tốt nhất là **KHÔNG dùng trailing** hoặc dùng rất conservative.

---

### 3. **HIGH VOLATILITY MARKET**

**Đặc điểm:**
- ATR lớn (> 2% của price)
- Giá biến động mạnh
- Nhiều gaps

**Recommended Settings:**
```python
trailing_multiplier = 2.5 - 3.0  # Rất loose để cho phép volatility
trailing_activation_r = 1.5 - 2.0  # Kích hoạt muộn
atr_period = 14  # Standard
```

**Lý do:**
- Multiplier rất lớn: Cho phép volatility lớn, không bị stop do noise
- Activation R lớn: Chờ profit lớn để compensate cho volatility

**Ví dụ:**
```
Altcoins (high volatility):
- Multiplier: 3.0x
- Activation R: 2.0R
→ Trailing distance = ATR × 3.0 (rất lớn)
→ Chỉ trailing khi profit >= 2R
```

**Alternative:** Có thể dùng **% thay vì ATR** trong high volatility:
```python
# Thay vì ATR × multiplier
trailing_distance = entry_price * 0.02  # Fixed 2%
```

---

### 4. **LOW VOLATILITY MARKET**

**Đặc điểm:**
- ATR nhỏ (< 0.5% của price)
- Giá ổn định
- Ít biến động

**Recommended Settings:**
```python
trailing_multiplier = 1.0 - 1.2  # Tight hơn
trailing_activation_r = 0.75 - 1.0  # Kích hoạt sớm hơn
atr_period = 14  # Standard
```

**Lý do:**
- Multiplier nhỏ: ATR đã nhỏ, không cần multiplier lớn
- Activation R nhỏ: Lock profit sớm vì market ổn định

**Ví dụ:**
```
Major pairs (EUR/USD, GBP/USD):
- Multiplier: 1.2x
- Activation R: 0.75R
→ Trailing distance nhỏ nhưng đủ để tránh noise
→ Kích hoạt sớm để lock profit
```

**Alternative:** Set **minimum trailing distance**:
```python
min_trailing = entry_price * 0.005  # Minimum 0.5%
trailing_distance = max(ATR × multiplier, min_trailing)
```

---

### 5. **CRYPTO MARKET (24/7)**

**Đặc điểm:**
- Trade 24/7
- Volatility thay đổi theo thời gian
- Nhiều news events

**Recommended Settings:**
```python
# Normal hours
trailing_multiplier = 1.5 - 2.0
trailing_activation_r = 1.0 - 1.5

# High volatility periods (news, events)
trailing_multiplier = 2.5 - 3.0
trailing_activation_r = 2.0

# Low volume periods (2-6 UTC)
trailing_multiplier = 1.0 - 1.2
trailing_activation_r = 0.75
```

**Dynamic Adjustment:**
```python
# Adjust theo ATR
if current_atr_pct > 2.0:  # High volatility
    multiplier = 2.5
    activation_r = 2.0
elif current_atr_pct < 0.5:  # Low volatility
    multiplier = 1.2
    activation_r = 0.75
else:  # Normal
    multiplier = 1.5
    activation_r = 1.0
```

---

### 6. **FOREX MARKET**

**Đặc điểm:**
- Trade theo sessions
- Spread costs
- Lower volatility (major pairs)

**Recommended Settings:**
```python
# Major pairs (EUR/USD, GBP/USD, USD/JPY)
trailing_multiplier = 1.2 - 1.5
trailing_activation_r = 0.75 - 1.0
atr_period = 14

# Minor pairs (higher volatility)
trailing_multiplier = 1.5 - 2.0
trailing_activation_r = 1.0 - 1.5
atr_period = 14

# Exotic pairs (very high volatility)
trailing_multiplier = 2.5 - 3.0
trailing_activation_r = 1.5 - 2.0
atr_period = 14
```

**Session-specific:**
```python
# London/NY session (high volume)
trailing_multiplier = 1.5
activation_r = 1.0

# Asian session (low volume)
trailing_multiplier = 1.0
activation_r = 0.5  # Lock profit sớm
```

---

### 7. **STOCKS MARKET**

**Đặc điểm:**
- Trade trong market hours
- Gaps (pre-market, after-hours)
- News-driven

**Recommended Settings:**
```python
# Large cap stocks (stable)
trailing_multiplier = 1.5 - 2.0
trailing_activation_r = 1.0 - 1.5

# Mid cap stocks (moderate volatility)
trailing_multiplier = 2.0 - 2.5
trailing_activation_r = 1.5

# Small cap stocks (high volatility)
trailing_multiplier = 2.5 - 3.0
trailing_activation_r = 2.0
```

**Time-based:**
```python
# Market hours (9:30 - 16:00)
trailing_multiplier = 1.5
activation_r = 1.0

# Pre-market / After-hours (lower volume)
trailing_multiplier = 1.0
activation_r = 0.5
```

---

## 🎯 PARAMETER MATRIX

| Market Type | Volatility | Multiplier | Activation R | ATR Period |
|-------------|------------|------------|--------------|------------|
| **Trending** | Medium | 2.0-2.5 | 1.5-2.0 | 14 |
| **Ranging** | Low | 1.0-1.2 | 0.5-0.75 | 10 |
| **High Vol** | High | 2.5-3.0 | 1.5-2.0 | 14 |
| **Low Vol** | Low | 1.0-1.2 | 0.75-1.0 | 14 |
| **Crypto** | Variable | 1.5-2.0 | 1.0-1.5 | 14 |
| **Forex Major** | Low | 1.2-1.5 | 0.75-1.0 | 14 |
| **Forex Minor** | Medium | 1.5-2.0 | 1.0-1.5 | 14 |
| **Stocks Large** | Low | 1.5-2.0 | 1.0-1.5 | 14 |
| **Stocks Small** | High | 2.5-3.0 | 2.0 | 14 |

---

## 🔧 DYNAMIC PARAMETER ADJUSTMENT

### Code Example: Auto-adjust theo Volatility

```python
def get_trailing_parameters(self, current_atr_pct: float) -> Dict:
    """
    Auto-adjust trailing parameters based on current volatility
    
    Args:
        current_atr_pct: ATR as % of price
        
    Returns:
        Dict with multiplier and activation_r
    """
    if current_atr_pct > 2.0:  # Very high volatility
        return {
            "multiplier": 3.0,
            "activation_r": 2.0,
            "reason": "High volatility - loose trailing"
        }
    elif current_atr_pct > 1.0:  # High volatility
        return {
            "multiplier": 2.0,
            "activation_r": 1.5,
            "reason": "Moderate-high volatility"
        }
    elif current_atr_pct > 0.5:  # Normal volatility
        return {
            "multiplier": 1.5,
            "activation_r": 1.0,
            "reason": "Normal volatility"
        }
    else:  # Low volatility
        return {
            "multiplier": 1.2,
            "activation_r": 0.75,
            "reason": "Low volatility - tight trailing"
        }
```

### Code Example: Market Regime Detection

```python
def detect_market_regime(self, data: List[Dict]) -> str:
    """Detect current market regime"""
    # Calculate ADX (trend strength)
    adx = self._calculate_adx(data, 14)
    
    # Calculate ATR
    atr = self._calculate_atr(data, 14)
    atr_pct = (atr / data[-1]['close']) * 100
    
    # Detect regime
    if adx > 25 and atr_pct < 1.5:
        return "TRENDING"
    elif adx < 20 and atr_pct < 0.5:
        return "RANGING"
    elif atr_pct > 2.0:
        return "HIGH_VOLATILITY"
    else:
        return "NORMAL"

def get_parameters_for_regime(self, regime: str) -> Dict:
    """Get parameters for specific regime"""
    params = {
        "TRENDING": {
            "multiplier": 2.0,
            "activation_r": 1.5
        },
        "RANGING": {
            "multiplier": 1.0,
            "activation_r": 0.5
        },
        "HIGH_VOLATILITY": {
            "multiplier": 2.5,
            "activation_r": 2.0
        },
        "NORMAL": {
            "multiplier": 1.5,
            "activation_r": 1.0
        }
    }
    return params.get(regime, params["NORMAL"])
```

---

## 📊 BACKTESTING & OPTIMIZATION

### Step 1: Baseline Test
```python
# Start with default
multiplier = 1.5
activation_r = 1.0

# Backtest và record:
# - Win rate
# - Profit factor
# - Max drawdown
# - Average R per trade
```

### Step 2: Grid Search
```python
# Test different combinations
multipliers = [1.0, 1.5, 2.0, 2.5, 3.0]
activation_rs = [0.5, 0.75, 1.0, 1.5, 2.0]

best_params = None
best_profit_factor = 0

for mult in multipliers:
    for act_r in activation_rs:
        result = backtest(multiplier=mult, activation_r=act_r)
        if result.profit_factor > best_profit_factor:
            best_profit_factor = result.profit_factor
            best_params = {"multiplier": mult, "activation_r": act_r}
```

### Step 3: Walk-Forward Analysis
```python
# Test trên nhiều periods
periods = [
    ("2023-01", "2023-03"),  # Q1
    ("2023-04", "2023-06"),  # Q2
    ("2023-07", "2023-09"),  # Q3
    ("2023-10", "2023-12"),  # Q4
]

for period in periods:
    data = get_data(period[0], period[1])
    result = backtest(data, best_params)
    print(f"{period}: Profit Factor = {result.profit_factor}")
```

---

## ✅ CHECKLIST: TUNE PARAMETERS

- [ ] Identify market type (trending, ranging, volatile, etc.)
- [ ] Start with recommended settings
- [ ] Backtest với historical data
- [ ] Record metrics (win rate, profit factor, drawdown)
- [ ] Adjust parameters từng chút một
- [ ] Test với walk-forward analysis
- [ ] Paper trade với parameters mới
- [ ] Monitor performance trong 1-2 tuần
- [ ] Fine-tune nếu cần
- [ ] Document final parameters

---

## 🎓 KẾT LUẬN

**Key Takeaways:**

1. **Không có one-size-fits-all**: Mỗi market cần parameters khác nhau
2. **Start conservative**: Bắt đầu với settings an toàn
3. **Test thoroughly**: Backtest kỹ trước khi dùng real money
4. **Monitor & adjust**: Continuously tune based on performance
5. **Market-specific**: Hiểu đặc điểm của market bạn trade

**Recommended Approach:**
1. Start với default (1.5x, 1.0R)
2. Backtest với market của bạn
3. Adjust dựa trên results
4. Paper trade để validate
5. Deploy và monitor

---

**Tune đúng parameters = Performance tốt hơn! 🚀**

