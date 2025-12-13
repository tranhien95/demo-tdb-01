# Hướng Dẫn Risk Management

## 📋 Các Trường Trong Risk Management Form

### 1. **Initial Capital ($)**
- **Mô tả**: Vốn ban đầu để backtest/live trading
- **Giá trị hiện tại**: $1,000
- **Giá trị hợp lý**: $1,000 - $100,000 (tùy mục đích)
- **Lưu ý**: Đây là số tiền giả định để tính toán, không ảnh hưởng đến kết quả % (nhưng ảnh hưởng đến số tiền thực tế)

### 2. **Risk per Trade (%)** ⚠️
- **Mô tả**: % vốn rủi ro cho mỗi trade
- **Giá trị hiện tại**: 50% ⚠️ **QUÁ CAO!**
- **Giá trị hợp lý**: 
  - **Conservative**: 1-2%
  - **Moderate**: 2-5%
  - **Aggressive**: 5-10%
  - **Cực kỳ nguy hiểm**: >10%
- **Ví dụ với 50%**:
  - Vốn: $1,000
  - Risk per trade: $500 (50% của $1,000)
  - Nếu thua 2 trades liên tiếp: Mất $1,000 → **Phá sản!**
  - Nếu thua 1 trade: Còn $500 → Mất 50% vốn

### 3. **Reward Ratio**
- **Mô tả**: Tỷ lệ Reward/Risk (Take Profit / Stop Loss)
- **Giá trị hiện tại**: 1.0 (1:1)
- **Giá trị hợp lý**: 
  - **Conservative**: 1.5-2.0 (cần win rate >50%)
  - **Moderate**: 2.0-3.0 (cần win rate >40%)
  - **Aggressive**: 3.0+ (cần win rate >30%)
- **Ví dụ với Reward Ratio = 1.0**:
  - Stop Loss: -3%
  - Take Profit: +3%
  - Cần win rate >50% để có lời

### 4. **Stop Loss (%)**
- **Mô tả**: % giá giảm (LONG) hoặc tăng (SHORT) để đóng lệnh thua lỗ
- **Giá trị hiện tại**: 3%
- **Giá trị hợp lý**: 
  - **Scalping**: 0.5-1%
  - **Day Trading**: 1-2%
  - **Swing Trading**: 2-5%
  - **Position Trading**: 5-10%

## ⚠️ CẢNH BÁO: Risk per Trade 50% Là CỰC KỲ NGUY HIỂM!

### Tại Sao Nguy Hiểm?

1. **Rủi Ro Phá Sản Cao**:
   ```
   Vốn ban đầu: $1,000
   Risk per trade: 50% = $500
   
   Trade 1: Thua → Còn $500
   Trade 2: Thua → Còn $0 (Phá sản!)
   ```

2. **Không Có Cơ Hội Phục Hồi**:
   - Với 50% risk, chỉ cần 2 trades thua là mất hết vốn
   - Không có cơ hội học hỏi và điều chỉnh

3. **Tâm Lý Căng Thẳng**:
   - Mỗi trade có thể mất 50% vốn
   - Áp lực tâm lý cực kỳ cao
   - Dễ đưa ra quyết định sai

4. **Không Phù Hợp Với Thực Tế**:
   - Không có trader chuyên nghiệp nào risk 50% per trade
   - Thường chỉ dùng trong gambling, không phải trading

## 📊 So Sánh Risk Levels

| Risk % | Trades Thua Để Phá Sản | Mức Độ Rủi Ro | Khuyến Nghị |
|--------|------------------------|---------------|-------------|
| 1%     | 100 trades             | Rất thấp      | ✅ Conservative |
| 2%     | 50 trades              | Thấp          | ✅ Recommended |
| 5%     | 20 trades              | Trung bình    | ⚠️ Moderate |
| 10%    | 10 trades              | Cao           | ⚠️ Aggressive |
| 20%    | 5 trades               | Rất cao       | ❌ Nguy hiểm |
| 50%    | 2 trades               | Cực kỳ cao    | ❌ **PHÁ SẢN** |

## 💡 Giá Trị Khuyến Nghị

### **Cho Người Mới Bắt Đầu**:
```json
{
  "risk_management": {
    "capital": 1000,
    "risk_percent": 1.0,      // 1% - An toàn
    "reward_ratio": 2.0,       // 1:2 - Cần win rate >40%
    "stop_loss_percent": 2.0   // 2% SL
  }
}
```

### **Cho Trader Có Kinh Nghiệm**:
```json
{
  "risk_management": {
    "capital": 10000,
    "risk_percent": 2.0,       // 2% - Cân bằng
    "reward_ratio": 2.5,       // 1:2.5 - Cần win rate >35%
    "stop_loss_percent": 3.0   // 3% SL
  }
}
```

### **Cho Trader Aggressive** (Không Khuyến Nghị):
```json
{
  "risk_management": {
    "capital": 5000,
    "risk_percent": 5.0,       // 5% - Cao
    "reward_ratio": 3.0,       // 1:3 - Cần win rate >30%
    "stop_loss_percent": 2.5   // 2.5% SL
  }
}
```

## 🎯 Công Thức Tính Position Size

Với các giá trị hiện tại:
- Capital: $1,000
- Risk per Trade: 50% = $500
- Stop Loss: 3%

**Position Size = Risk Amount / Stop Loss %**
- Position Size = $500 / 3% = $16,666.67

**Vấn đề**: Position size ($16,666) lớn hơn vốn ($1,000) → Cần margin/leverage rất cao → Rủi ro cực kỳ lớn!

## 🔧 Khuyến Nghị Sửa Đổi

### **Option 1: Conservative (Khuyến Nghị)**
```
Initial Capital: $1,000
Risk per Trade: 1-2%
Reward Ratio: 2.0
Stop Loss: 2%
```

### **Option 2: Moderate**
```
Initial Capital: $1,000
Risk per Trade: 2-5%
Reward Ratio: 2.0
Stop Loss: 3%
```

### **Option 3: Nếu Muốn Test Aggressive** (Chỉ cho backtest, không dùng live)
```
Initial Capital: $1,000
Risk per Trade: 10% (vẫn cao nhưng chấp nhận được cho test)
Reward Ratio: 2.0
Stop Loss: 3%
```

## 🛡️ Best Practices

1. **Không bao giờ risk >10% per trade**
2. **Risk 1-2% cho người mới, 2-5% cho có kinh nghiệm**
3. **Đảm bảo Reward Ratio >= 2.0 để có edge**
4. **Test strategy với risk thấp trước, tăng dần nếu hiệu quả**
5. **Luôn có stop loss, không bao giờ trade không có SL**

## 📈 Tính Toán Số Trades Có Thể Thua

Với Risk per Trade = R%:
- Số trades thua tối đa để phá sản = 100 / R

Ví dụ:
- Risk 1% → Có thể thua 100 trades
- Risk 2% → Có thể thua 50 trades
- Risk 5% → Có thể thua 20 trades
- Risk 50% → **Chỉ có thể thua 2 trades** ⚠️

## ⚠️ Kết Luận

**Risk per Trade 50% là CỰC KỲ NGUY HIỂM và không nên sử dụng!**

Khuyến nghị:
- Giảm xuống **1-2%** cho an toàn
- Hoặc tối đa **5%** nếu muốn aggressive
- **Không bao giờ** dùng >10% cho live trading

