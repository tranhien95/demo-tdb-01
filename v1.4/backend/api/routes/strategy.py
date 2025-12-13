"""
Strategy Routes
Endpoints for strategy management and backtesting
"""

from fastapi import APIRouter, Request
from pydantic import ValidationError
from indicators import indicator_manager
from strategy_models import Strategy, BacktestRequest
from strategy_engine import StrategyEngine
# Use database storage instead of JSON
from strategy_storage_db import strategy_storage
from pine_script_generator import pine_script_generator
from api.exceptions import (
    ValidationException,
    NotFoundException,
    InternalServerException
)
from api.decorators import handle_exceptions
from utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/api/strategy", tags=["strategy"])


@router.get("/indicators/list")
@handle_exceptions
async def list_indicators():
    """List all available indicators with their configs"""
    indicators = indicator_manager.list_indicators()
    result = []
    
    for ind_name in indicators:
        config = indicator_manager.get_indicator_config(ind_name)
        result.append({
            'type': ind_name,
            'description': config.get('description', ''),
            'default_config': config
        })
    
    return {'indicators': result}


@router.post("/validate")
@handle_exceptions
async def validate_strategy(strategy: Strategy):
    """Validate strategy configuration"""
    # Basic validation
    if not strategy.indicators:
        raise ValidationException("Strategy must have at least one indicator")
    
    enabled_count = sum(1 for ind in strategy.indicators if ind.enabled)
    if enabled_count == 0:
        raise ValidationException("Strategy must have at least one enabled indicator")
    
    # Check indicator types are valid
    available = indicator_manager.list_indicators()
    for ind in strategy.indicators:
        if ind.type not in available:
            raise ValidationException(f"Invalid indicator type: {ind.type}")
    
    return {'valid': True, 'message': 'Strategy is valid'}


@router.post("/preview")
@handle_exceptions
async def preview_strategy_signals(request: BacktestRequest):
    """Preview signal count without full backtest"""
    data = [d.model_dump() if hasattr(d, 'model_dump') else (d.dict() if hasattr(d, 'dict') else d) for d in request.ohlcv_data]
    strategy = request.strategy
    
    total_signals = 0
    long_signals = 0
    short_signals = 0
    
    # Quick loop to count signals
    for i in range(50, len(data)):
        direction, bull_pct, bear_pct, _ = StrategyEngine.calculate_signal(
            strategy, data, i
        )
        
        if direction:
            if StrategyEngine.apply_filters(strategy, data, i, direction):
                total_signals += 1
                if direction == 'LONG':
                    long_signals += 1
                else:
                    short_signals += 1
    
    return {
        'total_signals': total_signals,
        'long_signals': long_signals,
        'short_signals': short_signals,
        'total_candles': len(data) - 50
    }


@router.post("/backtest")
@handle_exceptions
async def backtest_strategy(request: BacktestRequest):
    """Run full backtest on custom strategy"""
    data = request.ohlcv_data
    strategy = request.strategy
    
    # Log backtest request
    logger.info(f"Backtest request received - Strategy: {strategy.name}")
    logger.debug(f"Backtest params - Risk: {strategy.risk_management.risk_percent}%, "
                f"RR: {strategy.risk_management.reward_ratio}:1, "
                f"SL: {strategy.risk_management.stop_loss_percent}%, "
                f"Capital: ${strategy.risk_management.capital:,.2f}, "
                f"Data points: {len(data)}")
    
    # Run backtest
    result = StrategyEngine.backtest_strategy(strategy, data)
    
    # Result is already a dict from the engine
    return result


@router.post("/save")
@handle_exceptions
async def save_strategy(strategy: Strategy):
    """Save strategy to disk"""
    success = strategy_storage.save_strategy(strategy)
    if not success:
        raise InternalServerException("Failed to save strategy")
    return {'status': 'success', 'message': f'Strategy "{strategy.name}" saved'}


@router.get("/list")
@handle_exceptions
async def list_strategies():
    """List all saved strategies"""
    strategies = strategy_storage.list_strategies()
    return {'strategies': [s.model_dump() for s in strategies]}


@router.post("/upload")
@handle_exceptions
async def upload_strategy(request: Request):
    """Upload strategy from JSON body"""
    data = await request.json()
    
    if 'name' not in data:
        raise ValidationException('Strategy name required')
    
    strategy_name = data['name']
    
    # Create strategy model and save using Strategy model
    try:
        strategy = Strategy(
            name=strategy_name,
            description=data.get('description', ''),
            indicators=data.get('indicators', []),
            signal_logic=data.get('signal_logic', {}),
            filters=data.get('filters', {}),
            risk_management=data.get('risk_management', {})
        )
    except ValidationError as e:
        raise ValidationException(f'Invalid strategy format: {str(e)}')
    
    success = strategy_storage.save_strategy(strategy)
    
    if not success:
        raise InternalServerException('Failed to save strategy')
    
    return {
        'status': 'success',
        'strategy_name': strategy_name,
        'message': f'Strategy "{strategy_name}" uploaded'
    }


@router.get("/load/{name}")
@handle_exceptions
async def load_strategy(name: str):
    """Load strategy by name"""
    if not name:
        raise ValidationException("Strategy name is required")
    
    strategy = strategy_storage.load_strategy(name)
    if not strategy:
        raise NotFoundException("Strategy", name)
    
    return strategy.model_dump()


@router.delete("/delete/{name}")
@handle_exceptions
async def delete_strategy(name: str):
    """Delete strategy by name"""
    if not name:
        raise ValidationException("Strategy name is required")
    
    success = strategy_storage.delete_strategy(name)
    if not success:
        raise NotFoundException("Strategy", name)
    
    return {'status': 'success', 'message': f'Strategy "{name}" deleted'}


@router.post("/export-pine")
@handle_exceptions
async def export_pine_script(strategy: Strategy):
    """Export strategy to Pine Script"""
    result = pine_script_generator.generate(strategy)
    return result.model_dump()

