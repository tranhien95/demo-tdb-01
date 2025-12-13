"""
Live Trading Routes
Endpoints for live trading simulation
"""

from fastapi import APIRouter
from api.models import LiveTradingStartRequest
from live_trading_engine import get_live_trading_engine
from live_trading_models import TradingConfig
from api.exceptions import (
    ValidationException,
    InternalServerException
)
from api.decorators import handle_exceptions
from utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/api/live-trading", tags=["live-trading"])


@router.post("/start")
@handle_exceptions
async def start_live_trading(request: LiveTradingStartRequest):
    """Start live trading session"""
    engine = get_live_trading_engine()
    
    config = TradingConfig(
        symbol=request.symbol,
        timeframe=request.timeframe,
        strategy_name=request.strategy_name,
        initial_balance=request.initial_balance,
        risk_percent=request.risk_percent,
        margin=request.margin,
        stoploss_percent=request.stoploss_percent,
        reversal_strength_threshold=request.reversal_strength_threshold,
        max_positions=request.max_positions,
    )
    
    success = engine.initialize(config)
    if not success:
        raise ValidationException("Failed to initialize trading engine")
    
    state_dict = engine.get_state()
    return {"status": "started", "state": state_dict}


@router.get("/status")
@handle_exceptions
async def get_live_trading_status():
    """Get current trading status"""
    engine = get_live_trading_engine()
    state = engine.get_state()
    if not state:
        return {"status": "not_started"}
    return {"status": "running", "state": state}


@router.post("/update")
@handle_exceptions
async def update_live_trading():
    """Update trading (fetch latest data, check signals, execute trades)"""
    engine = get_live_trading_engine()
    result = engine.update()
    return {"status": "success", "result": result, "state": engine.get_state()}


@router.post("/stop")
@handle_exceptions
async def stop_live_trading():
    """Stop live trading"""
    engine = get_live_trading_engine()
    engine.stop()
    return {"status": "stopped", "state": engine.get_state()}


@router.post("/pause")
@handle_exceptions
async def pause_live_trading():
    """Pause live trading"""
    engine = get_live_trading_engine()
    engine.pause()
    return {"status": "paused", "state": engine.get_state()}


@router.post("/resume")
@handle_exceptions
async def resume_live_trading():
    """Resume live trading"""
    engine = get_live_trading_engine()
    engine.resume()
    return {"status": "resumed", "state": engine.get_state()}


@router.post("/close-all")
@handle_exceptions
async def close_all_live_positions():
    """Close all open positions"""
    engine = get_live_trading_engine()
    state = engine.get_state()
    
    if not state or not state.get("open_positions"):
        return {"status": "no_positions", "state": state}
    
    # Get current price (last closed price)
    current_price = state.get("state", {}).get("open_positions", [{}])[0].get("current_price", 0)
    if current_price == 0:
        raise ValidationException("Cannot determine current price")
    
    engine.close_all_positions(current_price)
    return {"status": "all_closed", "state": engine.get_state()}

