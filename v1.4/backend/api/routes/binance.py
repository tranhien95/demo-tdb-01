"""
Binance API Routes
Endpoints for fetching data from Binance
"""

from fastapi import APIRouter
from datetime import datetime
from binance_fetcher import get_binance_fetcher
from api.models import BinanceRequest
from api.exceptions import (
    ValidationException,
    NotFoundException,
    ExternalServiceException
)
from api.decorators import handle_exceptions
from utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/api/binance", tags=["binance"])


@router.get("/symbols")
@handle_exceptions
async def get_binance_symbols():
    """Get list of popular symbols from Binance"""
    try:
        fetcher = get_binance_fetcher()
        symbols = fetcher.get_available_symbols()
        return {
            'status': 'success',
            'symbols': symbols,
            'count': len(symbols)
        }
    except Exception as e:
        raise ExternalServiceException("Binance", f"Failed to fetch symbols: {str(e)}")


@router.get("/timeframes")
@handle_exceptions
async def get_binance_timeframes():
    """Get list of available timeframes"""
    try:
        fetcher = get_binance_fetcher()
        timeframes = fetcher.get_timeframes()
        return {
            'status': 'success',
            'timeframes': timeframes
        }
    except Exception as e:
        raise ExternalServiceException("Binance", f"Failed to fetch timeframes: {str(e)}")


@router.post("/fetch")
@handle_exceptions
async def fetch_binance_data(request: BinanceRequest):
    """Fetch OHLCV data from Binance"""
    # Validate input
    if not request.symbol or not request.timeframe:
        raise ValidationException("Symbol and timeframe are required")
    
    if request.limit < 50 or request.limit > 10000:
        raise ValidationException("Limit must be between 50 and 10000")
    
    try:
        fetcher = get_binance_fetcher()
        
        # Validate symbol
        if not fetcher.validate_symbol(request.symbol):
            raise ValidationException(f"Invalid symbol: {request.symbol}")
        
        # Fetch data
        ohlcv_data = fetcher.fetch_ohlcv(
            request.symbol,
            request.timeframe,
            request.limit
        )
        
        if not ohlcv_data:
            raise NotFoundException("OHLCV data", request.symbol)
        
        return {
            'status': 'success',
            'symbol': request.symbol,
            'timeframe': request.timeframe,
            'count': len(ohlcv_data),
            'ohlcv_data': ohlcv_data,
            'fetched_at': datetime.now().isoformat()
        }
    
    except (ValidationException, NotFoundException):
        raise
    except Exception as e:
        raise ExternalServiceException("Binance", f"Failed to fetch data: {str(e)}")


@router.get("/symbol-info/{symbol}")
@handle_exceptions
async def get_symbol_info(symbol: str):
    """Get symbol information"""
    if not symbol:
        raise ValidationException("Symbol is required")
    
    try:
        fetcher = get_binance_fetcher()
        info = fetcher.get_symbol_info(symbol)
        
        if not info:
            raise NotFoundException("Symbol", symbol)
        
        return {
            'status': 'success',
            'data': info
        }
    except (ValidationException, NotFoundException):
        raise
    except Exception as e:
        raise ExternalServiceException("Binance", f"Failed to get symbol info: {str(e)}")

