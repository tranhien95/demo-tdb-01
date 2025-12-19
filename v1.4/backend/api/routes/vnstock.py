"""
Vietnam Stock Market API Routes
Endpoints for fetching data from Vietnam stock market (HOSE, HNX, UPCOM)
"""

from fastapi import APIRouter, Request
from datetime import datetime
from vnstock_fetcher import get_vnstock_fetcher
from api.models import BinanceRequest  # Reuse same model structure
from api.exceptions import (
    ValidationException,
    NotFoundException,
    ExternalServiceException
)
from api.decorators import handle_exceptions
from utils.logger import get_logger
import json

logger = get_logger(__name__)

router = APIRouter(prefix="/api/vnstock", tags=["vnstock"])


@router.get("/symbols")
@handle_exceptions
async def get_vnstock_symbols():
    """Get list of popular Vietnam stock symbols"""
    try:
        fetcher = get_vnstock_fetcher()
        symbols = fetcher.get_available_symbols()
        return {
            'status': 'success',
            'symbols': symbols,
            'count': len(symbols)
        }
    except ImportError as e:
        raise ExternalServiceException("VNStock", f"vnstock library not installed: {str(e)}")
    except Exception as e:
        raise ExternalServiceException("VNStock", f"Failed to fetch symbols: {str(e)}")


@router.get("/timeframes")
@handle_exceptions
async def get_vnstock_timeframes():
    """Get list of available timeframes"""
    try:
        fetcher = get_vnstock_fetcher()
        timeframes = fetcher.get_timeframes()
        return {
            'status': 'success',
            'timeframes': timeframes
        }
    except ImportError as e:
        raise ExternalServiceException("VNStock", f"vnstock library not installed: {str(e)}")
    except Exception as e:
        raise ExternalServiceException("VNStock", f"Failed to fetch timeframes: {str(e)}")


@router.post("/fetch")
@handle_exceptions
async def fetch_vnstock_data(request: BinanceRequest):  # Reuse BinanceRequest model
    """Fetch OHLCV data from Vietnam stock market
    
    Can use either:
    - limit: Number of candles to fetch (50-10000)
    - start_date and end_date: Date range (format: 'YYYY-MM-DD' or 'YYYY-MM-DD HH:MM:SS')
    """
    # Debug: print request details
    print(f"[API Route] Received VNStockRequest: symbol={request.symbol}, timeframe={request.timeframe}")
    print(f"[API Route] limit={request.limit}, start_date={request.start_date}, end_date={request.end_date}")
    
    logger.info(f"Received request: symbol={request.symbol}, timeframe={request.timeframe}, limit={request.limit}, start_date={request.start_date}, end_date={request.end_date}")
    
    # Validate input
    if not request.symbol or not request.timeframe:
        raise ValidationException("Symbol and timeframe are required")
    
    # Validate: must have either limit OR date range
    has_limit = request.limit is not None
    has_date_range = request.start_date is not None and request.end_date is not None
    
    if not has_limit and not has_date_range:
        raise ValidationException("Either 'limit' or both 'start_date' and 'end_date' must be provided")
    
    if has_limit and (request.limit < 50 or request.limit > 10000):
        raise ValidationException("Limit must be between 50 and 10000")
    
    if has_date_range:
        # Validate that start_date is before end_date
        try:
            from datetime import datetime
            start_dt = datetime.strptime(request.start_date.split()[0], '%Y-%m-%d')
            end_dt = datetime.strptime(request.end_date.split()[0], '%Y-%m-%d')
            if start_dt >= end_dt:
                raise ValidationException("start_date must be before end_date")
        except ValueError as e:
            raise ValidationException(f"Invalid date format: {str(e)}")
    
    try:
        fetcher = get_vnstock_fetcher()
        
        # Validate symbol
        if not fetcher.validate_symbol(request.symbol):
            raise ValidationException(f"Invalid symbol: {request.symbol}")
        
        # Fetch data - pass start_date and end_date if provided
        fetch_kwargs = {
            'symbol': request.symbol.upper(),  # Uppercase for Vietnam stocks
            'timeframe': request.timeframe,
        }
        
        # Only pass limit if provided (not None)
        if request.limit is not None:
            fetch_kwargs['limit'] = request.limit
        
        # Pass start_date and end_date if provided
        if request.start_date:
            fetch_kwargs['start_date'] = request.start_date
        if request.end_date:
            fetch_kwargs['end_date'] = request.end_date
        
        ohlcv_data = fetcher.fetch_ohlcv(**fetch_kwargs)
        
        if not ohlcv_data:
            raise NotFoundException("OHLCV data", request.symbol)
        
        return {
            'status': 'success',
            'symbol': request.symbol,
            'timeframe': request.timeframe,
            'count': len(ohlcv_data),
            'ohlcv_data': ohlcv_data,
            'fetched_at': datetime.now().isoformat(),
            'start_date': request.start_date,
            'end_date': request.end_date
        }
    
    except ImportError as e:
        raise ExternalServiceException("VNStock", f"vnstock library not installed: {str(e)}")
    except (ValidationException, NotFoundException):
        raise
    except ValueError as e:
        raise ValidationException(str(e))
    except Exception as e:
        raise ExternalServiceException("VNStock", f"Failed to fetch data: {str(e)}")


@router.get("/symbol-info/{symbol}")
@handle_exceptions
async def get_symbol_info(symbol: str):
    """Get symbol information"""
    if not symbol:
        raise ValidationException("Symbol is required")
    
    try:
        fetcher = get_vnstock_fetcher()
        info = fetcher.get_symbol_info(symbol.upper())
        
        if not info:
            raise NotFoundException("Symbol", symbol)
        
        return {
            'status': 'success',
            'data': info
        }
    except ImportError as e:
        raise ExternalServiceException("VNStock", f"vnstock library not installed: {str(e)}")
    except (ValidationException, NotFoundException):
        raise
    except Exception as e:
        raise ExternalServiceException("VNStock", f"Failed to get symbol info: {str(e)}")

