# Test Suite

Cấu trúc test suite cho Combo Optimizer v1.4

## 📁 Cấu Trúc

```
tests/
├── indicators/          # Test cho indicators
│   ├── test_indicators.py
│   ├── test_new_indicators.py
│   ├── test_custom_indicators.py
│   └── test_individual_configs.py
│
├── trading/             # Test cho trading features
│   ├── test_trailing_stop.py
│   ├── test_breakeven_stop.py
│   ├── test_partial_profit.py
│   ├── test_dynamic_position_sizing.py
│   ├── test_position_sizing.py
│   └── test_new_position_logic.py
│
├── integration/         # Test integration
│   ├── test_live_trading.py
│   ├── test_live_update.py
│   ├── test_binance_fetcher.py
│   └── test_user_scenario.py
│
└── performance/         # Test performance metrics
    ├── test_performance_metrics.py
    ├── test_equity_curve.py
    └── test_real_equity.py
```

## 🚀 Cách Chạy Tests

### Chạy tất cả tests trong một thư mục:
```bash
cd backend/tests/indicators
python test_indicators.py
```

### Chạy từ root directory:
```bash
cd backend
python -m tests.indicators.test_indicators
```

### Chạy một test cụ thể:
```bash
cd backend
python tests/trading/test_trailing_stop.py
```

## 📝 Ghi Chú

- Tất cả file test đã được cấu hình để import từ `backend/` directory
- Mỗi thư mục có `__init__.py` để setup path
- Tests có thể chạy độc lập hoặc như một module

## ✅ Test Categories

### Indicators Tests
- Test tất cả indicators hoạt động đúng
- Test config cho từng indicator
- Test custom indicators

### Trading Tests
- Trailing stop loss
- Breakeven stop
- Partial profit taking
- Dynamic position sizing
- Position sizing logic

### Integration Tests
- Live trading engine
- Binance fetcher
- User scenarios

### Performance Tests
- Performance metrics calculation
- Equity curve
- Real strategy testing

