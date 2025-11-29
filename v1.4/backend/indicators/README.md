# Indicators Module - Architecture Guide

## Cấu trúc thư mục

```
backend/
├── indicators/
│   ├── __init__.py                  # Registry & Manager (22 indicators)
│   ├── base.py                      # Base class & Helper functions
│   ├── rsi.py                       # RSI Indicator
│   ├── macd.py                      # MACD Indicator
│   ├── ema.py                       # EMA Indicators (50, 200, 12, 26)
│   ├── stochastic.py                # Stochastic Oscillator
│   ├── bollinger.py                 # Bollinger Bands
│   ├── adx.py                       # ADX Indicator
│   ├── additional.py                # CCI, MFI, Volume_MA, SuperTrend, OBV
│   ├── momentum_indicators.py       # ROC, VROC, RVI, Awesome, Momentum
│   ├── volatility_indicators.py     # ATR, Donchian
│   ├── pivot_indicators.py          # Pivot Points
│   ├── examples.py                  # Custom indicator examples
│   └── README.md                    # This file
├── main.py                          # FastAPI server
└── indicators.py                    # (deprecated - can be removed)
```

## Cách hoạt động

### 1. Base Class (`base.py`)

Mỗi indicator kế thừa từ `BaseIndicator` và phải implement 3 methods:

```python
class BaseIndicator(ABC):
    @abstractmethod
    def default_config(self) -> Dict:
        """Cấu hình mặc định"""
        pass
    
    @abstractmethod
    def calculate(self, data: List[Dict], index: int, **kwargs) -> Dict:
        """Tính toán giá trị và tín hiệu"""
        pass
    
    @abstractmethod
    def get_pine_script(self) -> str:
        """Generate Pine Script code"""
        pass
```

### 2. Tạo Indicator mới

**Ví dụ: Tạo CCI Indicator**

Tạo file `indicators/cci.py`:

```python
"""
CCI - Commodity Channel Index
Measures deviation from average price
"""

from typing import List, Dict
from .base import BaseIndicator


class CCIIndicator(BaseIndicator):
    """CCI Indicator with customizable settings"""
    
    def default_config(self) -> Dict:
        return {
            'period': 20,
            'overbought': 100,
            'oversold': -100,
            'description': 'Commodity Channel Index'
        }
    
    def calculate(self, data: List[Dict], index: int, **kwargs) -> Dict:
        """Calculate CCI value and signals"""
        period = kwargs.get('period', self.config['period'])
        oversold = kwargs.get('oversold', self.config['oversold'])
        overbought = kwargs.get('overbought', self.config['overbought'])
        
        if index < period:
            return {"bullish": False, "bearish": False, "value": 0, "strength": 0}
        
        tp_list = [(d["high"] + d["low"] + d["close"]) / 3 
                   for d in data[index - period + 1:index + 1]]
        sma_tp = sum(tp_list) / period
        tp = (data[index]["high"] + data[index]["low"] + data[index]["close"]) / 3
        
        mad = sum(abs(tp - sma_tp) for tp in tp_list) / period
        cci_val = (tp - sma_tp) / (0.015 * mad) if mad > 0 else 0
        
        return {
            "bullish": cci_val < oversold,
            "bearish": cci_val > overbought,
            "value": cci_val,
            "strength": abs(cci_val) / 200 * 100
        }
    
    def get_pine_script(self) -> str:
        """Generate Pine Script code"""
        period = self.config['period']
        oversold = self.config['oversold']
        overbought = self.config['overbought']
        
        return f"""// CCI Indicator
cci_value = ta.cci(close, {period})
cci_bullish = cci_value < {oversold}
cci_bearish = cci_value > {overbought}"""
```

### 3. Đăng ký Indicator

Thêm vào `indicators/__init__.py`:

```python
from .cci import CCIIndicator

INDICATOR_REGISTRY = {
    'RSI': RSIIndicator,
    'MACD': MACDIndicator,
    'CCI': CCIIndicator,  # ← Thêm dòng này
    # ... other indicators
}
```

### 4. Cấu hình Indicator

Mỗi indicator có config riêng, có thể thay đổi runtime:

```python
# Lấy indicator manager
from indicators import indicator_manager

# Xem config hiện tại
config = indicator_manager.get_indicator_config('RSI')
print(config)  # {'period': 14, 'overbought': 70, 'oversold': 30}

# Thay đổi config
indicator_manager.update_indicator_config('RSI', {
    'period': 21,
    'overbought': 75,
    'oversold': 25
})

# Sử dụng với custom config
signal = indicator_manager.calculate_indicator(
    'RSI', 
    data, 
    index, 
    period=10,  # Override config
    oversold=20
)
```

## Lợi ích của kiến trúc mới

### 1. **Tách biệt rõ ràng**
- Mỗi indicator là 1 file độc lập
- Dễ tìm, đọc, sửa code
- Không ảnh hưởng indicators khác

### 2. **Config linh hoạt**
- Mỗi indicator có config riêng
- Có thể thay đổi runtime
- Override khi tính toán

### 3. **Dễ mở rộng**
- Thêm indicator mới: tạo file → đăng ký
- Không cần sửa code cũ
- Plugin-like architecture

### 4. **Pine Script tự động**
- Mỗi indicator tự generate Pine Script
- Sync với logic Python
- Dễ maintain

### 5. **Testing dễ dàng**
- Test từng indicator riêng lẻ
- Mock dependencies dễ dàng
- Unit test cụ thể

## Sử dụng trong Main.py

```python
from indicators import indicator_manager, get_all_signals

# Tính toán tất cả indicators
signals = get_all_signals(ohlcv_data, index)

# Tính toán 1 indicator cụ thể
rsi_signal = indicator_manager.calculate_indicator('RSI', data, index)

# Generate Pine Script
pine_code = indicator_manager.get_pine_script(['RSI', 'MACD', 'EMA_50'])

# List tất cả indicators
all_indicators = indicator_manager.list_indicators()
```

## Migration từ code cũ

File `indicators.py` cũ vẫn hoạt động nhưng deprecated. Các steps migrate:

1. ✅ Tạo folder `indicators/`
2. ✅ Tách các indicator sang files riêng
3. ✅ Tạo `IndicatorManager` trong `__init__.py`
4. ✅ Update `main.py` để dùng manager mới
5. 🔄 Thêm các indicators còn lại (CCI, MFI, ROC, etc.)
6. 🔄 Test đầy đủ
7. 🔄 Xóa `indicators.py` cũ

## Next Steps

### ✅ HOÀN THÀNH: Tất cả 22 indicators đã được thêm!
- ✅ CCI (Commodity Channel Index)
- ✅ MFI (Money Flow Index)
- ✅ ROC (Rate of Change)
- ✅ VROC (Volume ROC)
- ✅ RVI (Relative Vigor Index)
- ✅ Donchian Channel
- ✅ Awesome Oscillator
- ✅ Momentum
- ✅ ATR (Average True Range)
- ✅ Pivot Points
- ✅ OBV (On Balance Volume)
- ✅ SuperTrend
- ✅ Volume MA

### Enhancements (Optional):
- [ ] Thêm validation cho config
- [ ] Thêm indicator combinations
- [ ] Thêm performance metrics per indicator
- [ ] Web UI để config indicators
- [ ] Export/Import indicator configs
- [ ] Indicator backtesting riêng lẻ

## Example: Thêm custom indicator

```python
# indicators/custom_rsi_ema.py
"""
Custom RSI+EMA Combo Indicator
"""

from typing import List, Dict
from .base import BaseIndicator, HelperFunctions
from .rsi import RSIIndicator
from .ema import EMAIndicator


class CustomRSIEMAIndicator(BaseIndicator):
    """Combined RSI and EMA signal"""
    
    def __init__(self):
        super().__init__()
        self.rsi = RSIIndicator()
        self.ema = EMAIndicator()
    
    def default_config(self) -> Dict:
        return {
            'rsi_period': 14,
            'ema_period': 50,
            'weight_rsi': 0.6,
            'weight_ema': 0.4,
            'description': 'Combined RSI and EMA signals'
        }
    
    def calculate(self, data: List[Dict], index: int, **kwargs) -> Dict:
        # Tính RSI
        rsi_signal = self.rsi.calculate(
            data, index, 
            period=self.config['rsi_period']
        )
        
        # Tính EMA
        ema_signal = self.ema.calculate(
            data, index,
            period=self.config['ema_period']
        )
        
        # Kết hợp signals với trọng số
        w_rsi = self.config['weight_rsi']
        w_ema = self.config['weight_ema']
        
        combined_strength = (
            rsi_signal['strength'] * w_rsi + 
            ema_signal['strength'] * w_ema
        )
        
        return {
            "bullish": rsi_signal['bullish'] and ema_signal['bullish'],
            "bearish": rsi_signal['bearish'] and ema_signal['bearish'],
            "value": combined_strength,
            "strength": combined_strength
        }
    
    def get_pine_script(self) -> str:
        return f"""// Custom RSI+EMA Combo
{self.rsi.get_pine_script()}
{self.ema.get_pine_script()}
combo_bullish = rsi_bullish and ema{self.config['ema_period']}_bullish
combo_bearish = rsi_bearish and ema{self.config['ema_period']}_bearish"""
```

Đăng ký trong `__init__.py`:
```python
from .custom_rsi_ema import CustomRSIEMAIndicator

INDICATOR_REGISTRY = {
    # ...
    'Custom_RSI_EMA': CustomRSIEMAIndicator,
}
```
