# ⏰ TIME-BASED FILTERS - QUICK GUIDE

## ✅ ĐÃ IMPLEMENT

Time-based Filters đã được tích hợp!

---

## 🚀 CÁCH HOẠT ĐỘNG

### Khái Niệm

**Time-based Filters** tránh trade trong giờ ít thanh khoản:
- Crypto: Tránh 2-6h UTC
- Forex: Tránh Asian session
- Stock: Tránh pre-market/after-hours

---

## ⚙️ CONFIGURATION

```python
enable_time_filter: bool = True
market_type: str = "crypto"  # "crypto", "forex", "stock"
```

---

## 🎯 LỢI ÍCH

- ✅ Tránh slippage cao
- ✅ Tránh false signals do low volume
- ✅ Tăng fill rate

---

**Xem `detailed-guide.md` để hiểu chi tiết!**

