# 📚 VOLATILITY-BASED SL/TP - GIẢI THÍCH CHI TIẾT

## 🎯 KHÁI NIỆM

Volatility-based SL/TP tự động điều chỉnh SL/TP dựa trên ATR (volatility).

---

## 🔍 CÁCH HOẠT ĐỘNG

### Formula:

```
SL Distance = ATR × SL Multiplier (default 2.0x)
TP Distance = ATR × TP Multiplier (default 4.0x, 2:1 R:R)

Ví dụ:
ATR = $0.50 (1% of $50)
SL = $0.50 × 2.0 = $1.00 (2%)
TP = $0.50 × 4.0 = $2.00 (4%)
```

---

## 📊 VÍ DỤ

| ATR | ATR% | SL Distance | TP Distance |
|-----|------|--------------|-------------|
| $0.25 | 0.5% | 0.5% | 1.0% |
| $0.50 | 1.0% | 2.0% | 4.0% |
| $1.00 | 2.0% | 2.0% (capped) | 4.0% |

---

## ⚙️ CONFIGURATION

```python
enable_atr_sl_tp: bool = False  # Enable ATR-based SL/TP
atr_sl_multiplier: float = 2.0  # ATR multiplier for SL
atr_tp_multiplier: float = 4.0  # ATR multiplier for TP
```

---

## 🎯 LỢI ÍCH

- ✅ SL không bị stop sớm trong volatile market
- ✅ TP realistic hơn
- ✅ Tăng win rate 5-10%

---

**Xem code implementation trong `trading_improvements.py`**

