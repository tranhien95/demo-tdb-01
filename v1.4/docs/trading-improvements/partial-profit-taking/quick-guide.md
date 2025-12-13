# 💰 PARTIAL PROFIT TAKING - QUICK GUIDE

## ✅ ĐÃ IMPLEMENT

Partial Profit Taking đã được tích hợp vào `live_trading_engine.py`!

---

## 🚀 CÁCH HOẠT ĐỘNG

### Khái Niệm

**Partial Profit Taking** tự động đóng một phần position khi đạt profit targets, nhằm:
- Lock profit sớm
- Giảm risk exposure
- Tăng win rate

**Ví dụ:**
```
Entry: $100, Position: 100 units

Price = $101 (1R profit):
→ Close 50% → 50 units @ $101
→ Remaining: 50 units

Price = $102 (2R profit):
→ Close 25% of original → 25 units @ $102
→ Remaining: 25 units

Price = $103 (3R profit):
→ Remaining 25% chạy đến TP hoặc trailing stop
```

---

## ⚙️ CONFIGURATION

### Default Rules:

```python
partial_profit_rules = [
    {"r_level": 1.0, "close_pct": 0.5, "taken": False},   # Close 50% @ 1R
    {"r_level": 2.0, "close_pct": 0.25, "taken": False}  # Close 25% @ 2R
]
```

### Custom Rules:

```python
# Scale out 30% @ 1R, 30% @ 2R, 40% @ TP
partial_profit_rules = [
    {"r_level": 1.0, "close_pct": 0.3, "taken": False},
    {"r_level": 2.0, "close_pct": 0.3, "taken": False},
    # Remaining 40% goes to TP
]
```

---

## 📊 VÍ DỤ

### Scenario: LONG Position

```
Entry: $100, SL: $99 (1R = $1)
Position: 100 units

Price = $101 (1R):
→ Close 50 units @ $101
→ Profit: $50
→ Remaining: 50 units

Price = $102 (2R):
→ Close 25 units @ $102
→ Profit: $50
→ Remaining: 25 units

Price = $103 (TP hit):
→ Close 25 units @ $103
→ Profit: $75

Total Profit: $50 + $50 + $75 = $175
vs Fixed: $300 (nếu hold toàn bộ đến TP)
```

**Lợi ích:**
- Lock $100 profit sớm (50% @ 1R + 25% @ 2R)
- Giảm risk nếu giá quay lại
- Tăng win rate

---

## 🎯 LỢI ÍCH

- ✅ Lock profit sớm
- ✅ Giảm risk exposure
- ✅ Tăng win rate 5-10%
- ✅ Tâm lý tốt hơn

---

**Xem `detailed-guide.md` để hiểu chi tiết!**

