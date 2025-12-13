# 📈 VOLATILITY-BASED SL/TP - QUICK GUIDE

## ✅ ĐÃ IMPLEMENT

Volatility-based SL/TP đã được tích hợp!

---

## 🚀 CÁCH HOẠT ĐỘNG

### Khái Niệm

**Volatility-based SL/TP** tự động điều chỉnh SL/TP dựa trên ATR (volatility):
- High volatility → SL/TP lớn hơn
- Low volatility → SL/TP nhỏ hơn

**Ví dụ:**
```
ATR = 1.0% (normal)
→ SL = 2.0% (2x ATR)
→ TP = 4.0% (4x ATR, 2:1 R:R)

ATR = 2.0% (high)
→ SL = 2.0% (capped)
→ TP = 4.0% (2:1 R:R)
```

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

**Xem `detailed-guide.md` để hiểu chi tiết!**

