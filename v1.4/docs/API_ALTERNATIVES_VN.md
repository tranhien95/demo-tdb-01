# 📊 API Alternatives cho Chứng Khoán Việt Nam

Ngoài `vnstock`, có một số API/thư viện khác để lấy dữ liệu chứng khoán VN:

## 1. 🐍 **stockvip** (Python Library)

### Ưu điểm:
- ✅ Miễn phí, không cần API key
- ✅ Hỗ trợ nhiều loại dữ liệu (cổ phiếu, chỉ số, chứng quyền, phái sinh)
- ✅ Dễ sử dụng với Python

### Cài đặt:
```bash
pip install stockvip
```

### Sử dụng:
```python
from stockvip import StockVIP

client = StockVIP()
# Lấy dữ liệu lịch sử
df = client.get_historical_data('VCB', '2024-01-01', '2024-12-31', 'D')
```

### Tài liệu:
- PyPI: https://pypi.org/project/stockvip/
- GitHub: Tìm "stockvip python" trên GitHub

---

## 2. 🌐 **ckvn.info API** (REST API)

### Ưu điểm:
- ✅ Dữ liệu real-time và lịch sử
- ✅ Hỗ trợ HOSE, HNX
- ✅ API RESTful dễ tích hợp

### Nhược điểm:
- ❌ Cần API Key (có thể mất phí)
- ❌ Cần đăng ký tài khoản

### Endpoints:
```
GET https://api.ckvn.info/v1/stocks/{symbol}/ohlcv
GET https://api.ckvn.info/v1/stocks/list
```

### Tài liệu:
- Website: https://ckvn.info/data
- Cần đăng ký để lấy API Key

---

## 3. 🏦 **BSC API** (Công ty Chứng khoán BIDV)

### Ưu điểm:
- ✅ API chính thức từ công ty chứng khoán
- ✅ Hỗ trợ đặt lệnh, quản lý tài khoản
- ✅ Dữ liệu real-time

### Nhược điểm:
- ❌ Cần tài khoản giao dịch tại BSC
- ❌ Cần API Key
- ❌ Có thể có phí

### Tài liệu:
- Website: https://vh2.com.vn/api-lay-du-lieu-chung-khoan-1672504220
- Liên hệ BSC để lấy API Key

---

## 4. 📈 **TCBS API** (Techcombank Securities)

### Ưu điểm:
- ✅ API từ công ty chứng khoán lớn
- ✅ Dữ liệu đầy đủ

### Nhược điểm:
- ❌ Cần tài khoản TCBS
- ❌ Cần API Key

### Tài liệu:
- Liên hệ TCBS để biết thêm

---

## 5. 🔄 **SSI API** (Saigon Securities)

### Ưu điểm:
- ✅ API từ công ty chứng khoán lớn
- ✅ Hỗ trợ giao dịch

### Nhược điểm:
- ❌ Cần tài khoản SSI
- ❌ Cần API Key

### Tài liệu:
- Liên hệ SSI để biết thêm

---

## 6. 📊 **VNDirect API**

### Ưu điểm:
- ✅ API từ công ty chứng khoán
- ✅ Dữ liệu real-time

### Nhược điểm:
- ❌ Cần tài khoản VNDirect
- ❌ Cần API Key

### Tài liệu:
- Liên hệ VNDirect để biết thêm

---

## 7. 📈 **DNSE / Web Scraping**

### Ưu điểm:
- ✅ Miễn phí (nếu scrape từ public websites)
- ✅ Không cần API key
- ✅ Có thể lấy từ nhiều nguồn

### Nhược điểm:
- ❌ Có thể vi phạm ToS của website
- ❌ Dễ bị block nếu scrape quá nhiều
- ❌ Cần maintain khi website thay đổi structure
- ❌ Không ổn định bằng API chính thức

### Nguồn có thể scrape:
- cafef.vn
- vndirect.com.vn
- dnse.com.vn (nếu có)
- vcbs.com.vn
- etc.

### Tài liệu:
- Cần implement web scraping logic cho từng website

---

## 8. 💹 **yfinance (Yahoo Finance)**

### Ưu điểm:
- ✅ Miễn phí
- ✅ Dễ sử dụng
- ✅ Hỗ trợ một số mã VN (với .VN suffix)

### Nhược điểm:
- ❌ Không hỗ trợ đầy đủ mã VN
- ❌ Có thể không có data real-time
- ❌ Rate limits

### Cài đặt:
```bash
pip install yfinance
```

### Sử dụng:
```python
import yfinance as yf

ticker = yf.Ticker('VCB.VN')
df = ticker.history(period='1y', interval='1d')
```

### Tài liệu:
- PyPI: https://pypi.org/project/yfinance/
- GitHub: https://github.com/ranaroussi/yfinance

---

## 🎯 **Khuyến nghị:**

### Cho Development/Testing:
1. **vnstock** (đã có) - Miễn phí, dễ dùng ✅
2. **stockvip** - Alternative miễn phí
3. **yfinance** - Hỗ trợ một số mã VN (với .VN suffix)
4. **Web Scraping** - Từ cafef, vndirect, etc. (cần implement)

### Cho Production:
1. **ckvn.info** - Nếu cần API key và sẵn sàng trả phí
2. **BSC/TCBS/SSI/VNDirect** - Nếu đã có tài khoản giao dịch

---

## 🔧 **Implementation trong Project:**

### Hiện tại:
- ✅ `vnstock` - Đã implement đầy đủ
- ⚠️ `stockvip` - Đã tạo fetcher nhưng chưa implement đầy đủ (cần tài liệu)
- ⚠️ `dnse/yfinance` - Đã tạo fetcher, hỗ trợ yfinance (một số mã VN)

### Có thể thêm:
- `ckvn.info` - Cần API key
- `BSC/TCBS/SSI/VNDirect` - Cần tài khoản và API key
- `Web Scraping` - Từ cafef, vndirect, dnse, etc. (cần implement)

---

## 📝 **Ghi chú:**

1. **Giờ giao dịch VN**: 9:00 - 15:00 (giờ VN)
   - Ngoài giờ giao dịch, một số API có thể không trả về data

2. **Rate Limits**: Một số API có giới hạn số request/giờ

3. **Phí**: Một số API miễn phí, một số có phí (cần kiểm tra)

4. **Fallback**: Project đã có fallback data để UI vẫn hoạt động khi API lỗi

---

## 🚀 **Next Steps:**

1. **Test stockvip**: Cài đặt và test xem có hoạt động không
   ```bash
   pip install stockvip
   python -c "from stockvip import StockVIP; print('OK')"
   ```

2. **Implement stockvip fetcher**: Hoàn thiện `backend/stockvip_fetcher.py`

3. **Thêm API endpoints**: Tạo endpoints cho stockvip tương tự vnstock

4. **UI Integration**: Thêm option chọn data source (vnstock vs stockvip)

