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
from indicators import indicator_manager, get_pine_script_code
from utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(tags=["optimization"])


@router.post("/optimize-stream")
async def optimize_stream(request: Request):
    """Run optimization with streaming progress updates"""
    try:
        body = await request.json()
        logger.debug(f"Optimization request received with keys: {list(body.keys())}")
        
        # Print to console for debugging (always visible)
        min_combo = body.get('minComboSize', body.get('min_combo_size', 'NOT PROVIDED'))
        max_combo = body.get('maxComboSize', body.get('max_combo_size', 'NOT PROVIDED'))
        print(f"[OPTIMIZATION] Received - minComboSize: {min_combo}, maxComboSize: {max_combo}")
        logger.info(f"Received params - minComboSize: {min_combo}, maxComboSize: {max_combo}")
        
        try:
            params = OptimizationParams(**body)
            print(f"[OPTIMIZATION] Parsed - min_combo_size: {params.min_combo_size}, max_combo_size: {params.max_combo_size}")
            logger.info(f"Parsed params - min_combo_size: {params.min_combo_size}, max_combo_size: {params.max_combo_size}")
        except ValidationError as ve:
            print(f"[OPTIMIZATION] Validation Error: {ve}")
            logger.error(f"Validation error: {ve}")
            raise ValidationException(f"Invalid optimization parameters: {str(ve)}")
        except Exception as pe:
            print(f"[OPTIMIZATION] Parse Error: {pe}")
            logger.error(f"Parse error: {pe}", exc_info=True)
            raise ValidationException(f"Failed to parse request: {str(pe)}")
    except ValidationException:
        raise
    except Exception as e:
        print(f"[OPTIMIZATION] Unexpected Error: {e}")
        logger.error(f"Unexpected error: {e}", exc_info=True)
        raise ValidationException(f"Failed to parse request: {str(e)}")
    
    async def progress_generator():
        try:
            data = [d.model_dump() for d in params.ohlcv_data]
            
            # Use same indicator list as Strategy Builder (from indicator_manager)
            indicators = indicator_manager.list_indicators()
            
            combos = []
            print(f"[OPTIMIZATION] Generating combos from size {params.min_combo_size} to {params.max_combo_size}")
            for size in range(params.min_combo_size, params.max_combo_size + 1):
                size_combos = list(combinations(indicators, size))
                combos.extend([list(combo) for combo in size_combos])
                print(f"[OPTIMIZATION] Generated {len(size_combos)} combos of size {size}")
                logger.info(f"Generated {len(size_combos)} combos of size {size}")
            
            if params.max_combos > 0:
                combos = combos[:params.max_combos]
            total_combos = len(combos)
            print(f"[OPTIMIZATION] Total combos to test: {total_combos} (size range: {params.min_combo_size} to {params.max_combo_size})")
            logger.info(f"Total combos to test: {total_combos} (size range: {params.min_combo_size} to {params.max_combo_size})")
            
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
                    params.candle_confirmation,
                    params.enable_trailing_stop,
                    params.trailing_activation_r,
                    params.trailing_multiplier,
                    params.enable_partial_tp_close,
                    params.tp_close_pct
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
    """Generate Pine Script code from indicator list (full strategy with signal logic)"""
    if not indicators:
        raise ValidationException("Indicators list cannot be empty")
    
    from strategy_models import Strategy, IndicatorConfig, SignalLogic, FilterConfig, RiskManagement
    from pine_script_generator import pine_script_generator
    
    # Create a temporary strategy from indicators
    indicator_configs = [
        IndicatorConfig(
            type=ind,
            config={},
            weight=1.0,
            enabled=True
        )
        for ind in indicators
    ]
    
    strategy = Strategy(
        name="Optimized Combo",
        description=f"Auto-generated from combo: {' + '.join(indicators)}",
        indicators=indicator_configs,
        signal_logic=SignalLogic(threshold_percent=70),
        filters=FilterConfig(),
        risk_management=RiskManagement(
            risk_percent=10.0,
            reward_ratio=1.0,
            stop_loss_percent=5.0,
            capital=1000
        )
    )
    
    # Generate full strategy code
    try:
        result = pine_script_generator.generate(strategy)
        
        logger.info(f"Generated full strategy code for {len(indicators)} indicators, code length: {len(result.code)}")
        
        return {
            'status': 'success',
            'code': result.code,
            'indicators': indicators,
            'strategy_name': result.strategy_name
        }
    except Exception as e:
        logger.error(f"Error generating Pine Script: {str(e)}", exc_info=True)
        raise InternalServerException(f"Failed to generate Pine Script: {str(e)}")

