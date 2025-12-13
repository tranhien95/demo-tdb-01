"""
Optimization Routes
Endpoints for strategy optimization
"""

from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse
from pydantic import ValidationError
import json
from itertools import combinations
from api.models import OptimizationParams
from api.backtest_engine import BacktestEngine
from api.exceptions import ValidationException, InternalServerException
from api.decorators import handle_exceptions
from indicators import get_pine_script_code
from utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(tags=["optimization"])


@router.post("/optimize-stream")
async def optimize_stream(request: Request):
    """Run optimization with streaming progress updates"""
    try:
        body = await request.json()
        logger.debug(f"Optimization request received with keys: {list(body.keys())}")
        
        params = OptimizationParams(**body)
    except ValidationError as e:
        raise ValidationException(f"Invalid optimization parameters: {str(e)}")
    except Exception as e:
        raise ValidationException(f"Failed to parse request: {str(e)}")
    
    async def progress_generator():
        try:
            data = [d.model_dump() for d in params.ohlcv_data]
            
            indicators = [
                'RSI', 'MACD', 'Stochastic', 'Bollinger_Bands',
                'Volume_MA', 'EMA_50', 'EMA_200', 'EMA_12', 'EMA_26',
                'ADX', 'CCI', 'MFI', 'ROC', 'VROC', 'RVI', 'Donchian',
                'Awesome_Oscillator', 'Momentum', 'ATR', 'Pivot_Points', 'OBV', 'SuperTrend'
            ]
            
            combos = []
            for size in range(params.min_combo_size, params.max_combo_size + 1):
                for combo in combinations(indicators, size):
                    combos.append(list(combo))
            
            if params.max_combos > 0:
                combos = combos[:params.max_combos]
            total_combos = len(combos)
            
            BacktestEngine._get_or_compute_signals(data)
            
            results = []
            for idx, combo in enumerate(combos):
                result = BacktestEngine.backtest_combo(
                    combo,
                    data,
                    params.threshold,
                    params.risk_percent,
                    params.rr_ratio,
                    params.sl_percent,
                    params.filters,
                    params.min_signal_ratio,
                    params.candle_confirmation
                )
                if result['trades'] > 0:
                    results.append(result)
                
                if (idx + 1) % 5 == 0 or idx == total_combos - 1:
                    progress = round(((idx + 1) / total_combos) * 100, 1)
                    yield f'data: {{"progress": {progress}, "tested": {idx + 1}, "with_trades": {len(results)}}}\n\n'
            
            results.sort(key=lambda x: x['profit_pct'], reverse=True)
            
            final_data = {
                'results': results[:100],
                'total_tested': total_combos,
                'total_with_trades': len(results),
                'progress': 100
            }
            yield f'data: {{"final": true, "data": {json.dumps(final_data)}}}\n\n'
        
        except Exception as e:
            logger.error(f"Error in optimization stream: {e}", exc_info=True)
            yield f'data: {{"error": "{str(e)}"}}\n\n'
    
    return StreamingResponse(progress_generator(), media_type="text/event-stream")


@router.post("/generate-pine-script")
@handle_exceptions
async def generate_pine_script(indicators: list[str]):
    """Generate Pine Script code from indicator list"""
    if not indicators:
        raise ValidationException("Indicators list cannot be empty")
    
    code = get_pine_script_code(indicators)
    return {
        'status': 'success',
        'code': code,
        'indicators': indicators
    }

