# Dependencies Upgrade - Pydantic v2 Migration

## ✅ Completed Changes

### 1. Updated `requirements.txt`
- ❌ Removed: `flask==3.0.0`, `flask-cors==4.0.0` (not used)
- ✅ Updated: `pydantic==1.10.13` → `pydantic==2.5.0`
- ✅ Kept: `fastapi==0.104.1`, `uvicorn[standard]==0.24.0`
- ✅ Added: `uvicorn[standard]` for better performance

### 2. Code Changes for Pydantic v2 Compatibility

#### Changed `.dict()` → `.model_dump()`
- ✅ `backend/strategy_storage.py` - `strategy.dict()` → `strategy.model_dump()`
- ✅ `backend/main.py` - `d.dict()` → `d.model_dump()` (OHLCV models)
- ✅ `backend/main.py` - `result.dict()` → `result.model_dump()` (PineScriptExport)
- ✅ `backend/strategy_engine.py` - `s.dict()` → `s.model_dump()` (SignalDetail)

#### Updated Config Class
- ✅ `backend/strategy_models.py` - Changed `class Config` → `model_config = ConfigDict()`
- ✅ Added `from pydantic import ConfigDict`

### 3. Files Modified
1. `backend/requirements.txt` - Updated dependencies
2. `backend/strategy_models.py` - Pydantic v2 syntax
3. `backend/strategy_storage.py` - `.model_dump()` method
4. `backend/main.py` - `.model_dump()` method (3 places)
5. `backend/strategy_engine.py` - `.model_dump()` method (2 places)

## 📋 Pydantic v2 Breaking Changes Addressed

### ✅ Fixed:
1. **`.dict()` → `.model_dump()`** - All instances updated
2. **`class Config` → `model_config = ConfigDict()`** - Updated in BacktestResult
3. **Import changes** - Added `ConfigDict` import

### ⚠️ Not Changed (Compatible):
- `Field(...)` syntax - Still works in v2
- `BaseModel` inheritance - No changes needed
- Validation - Same behavior

## 🧪 Testing Required

After upgrading, test these endpoints:
1. ✅ `/api/strategy/save` - Strategy saving
2. ✅ `/api/strategy/load` - Strategy loading
3. ✅ `/api/strategy/backtest` - Backtest execution
4. ✅ `/api/strategy/preview` - Signal preview
5. ✅ `/optimize-stream` - Optimization streaming
6. ✅ `/api/strategy/export-pine` - Pine Script export

## 🚀 Installation

```bash
cd backend
pip install -r requirements.txt --upgrade
```

## ⚠️ Potential Issues

### If you see errors:
1. **`AttributeError: 'X' object has no attribute 'model_dump'`**
   - Check if object is Pydantic model or dataclass
   - Dataclass models (strategy_models_simple.py) still use `.dict()`

2. **`ValidationError` changes**
   - Pydantic v2 has different error format
   - FastAPI handles this automatically

3. **`Config` class errors**
   - Make sure all `class Config` changed to `model_config = ConfigDict()`

## 📝 Notes

- `strategy_models_simple.py` uses dataclasses, not Pydantic
- Those models still use `.dict()` method (custom implementation)
- No changes needed for dataclass models

## ✅ Verification

Run these commands to verify:
```bash
# Check Pydantic version
python -c "import pydantic; print(pydantic.__version__)"
# Should output: 2.5.0

# Test imports
python -c "from strategy_models import Strategy; print('OK')"
# Should output: OK

# Test model_dump
python -c "from strategy_models import Strategy; s = Strategy(name='Test', indicators=[]); print(s.model_dump())"
# Should output dict without errors
```

---

**Upgrade Date:** 2025-12-11  
**Status:** ✅ Complete

