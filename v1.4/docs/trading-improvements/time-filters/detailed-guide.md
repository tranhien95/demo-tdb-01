# 📚 TIME-BASED FILTERS - GIẢI THÍCH CHI TIẾT

## 🎯 KHÁI NIỆM

Time-based Filters tránh trade trong giờ ít thanh khoản để:
- Tránh slippage cao
- Tránh false signals do low volume
- Tăng fill rate

---

## 🔍 CÁCH HOẠT ĐỘNG

### Crypto Market:
- **Avoid**: 2-6h UTC (low volume)
- **Trade**: All other hours

### Forex Market:
- **Avoid**: Asian session (0-6h UTC, low volatility)
- **Avoid**: Weekend
- **Trade**: London/NY sessions

### Stock Market:
- **Avoid**: Pre-market, after-hours
- **Avoid**: Weekend
- **Trade**: Market hours (9:30-16:00)

---

## ⚙️ CONFIGURATION

```python
enable_time_filter: bool = True
market_type: str = "crypto"  # "crypto", "forex", "stock"
```

---

## 📊 VÍ DỤ

| Market | Time | Tradeable? |
|--------|------|------------|
| Crypto | 2-6h UTC | ❌ No |
| Crypto | Other hours | ✅ Yes |
| Forex | Asian session | ❌ No |
| Forex | London/NY | ✅ Yes |
| Stock | Market hours | ✅ Yes |
| Stock | Pre-market | ❌ No |

---

## 🎯 LỢI ÍCH

- ✅ Tránh slippage cao
- ✅ Tránh false signals
- ✅ Tăng fill rate

---

**Xem code implementation trong `trading_improvements.py`**

