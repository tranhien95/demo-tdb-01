"""
Indicators Routes
Endpoints for indicator management
"""

from fastapi import APIRouter
from indicators import indicator_manager
from api.decorators import handle_exceptions
from utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/api/indicators", tags=["indicators"])


@router.get("/list")
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

