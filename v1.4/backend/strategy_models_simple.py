"""
Strategy Models - Simple Version (No Pydantic)
Data models for custom strategy building
"""

from typing import List, Dict, Optional, Any
from dataclasses import dataclass, field, asdict
from datetime import datetime
import uuid


@dataclass
class IndicatorConfig:
    """Configuration for a single indicator instance"""
    type: str
    config: Dict[str, Any] = field(default_factory=dict)
    weight: float = 1.0
    enabled: bool = True
    id: Optional[str] = None
    
    def __post_init__(self):
        if self.id is None:
            self.id = str(uuid.uuid4())[:8]
    
    def dict(self):
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data):
        return cls(**{k: v for k, v in data.items() if k in ['type', 'config', 'weight', 'enabled', 'id']})


@dataclass
class SignalLogic:
    """Signal confirmation logic"""
    threshold_percent: float = 70.0
    # Position switching controls
    min_holding_candles: int = 3  # Minimum candles to hold position before allowing switch
    switch_confirmation_candles: int = 2  # Candles needed to confirm switch signal
    allow_position_switch: bool = True  # Enable/disable position switching
    
    def dict(self):
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data):
        return cls(**{k: v for k, v in data.items() if k in ['threshold_percent', 'min_holding_candles', 'switch_confirmation_candles', 'allow_position_switch']})


@dataclass
class FilterConfig:
    """Trading filters configuration"""
    enable_adx: bool = False
    adx_threshold: float = 25.0
    enable_volume: bool = False
    volume_threshold: float = 1.5
    enable_ma_filter: bool = False
    ma_period: int = 50
    enable_atr_filter: bool = False
    min_atr: float = 0.0005
    enable_trend_filter: bool = False
    trend_ma: int = 200
    
    def dict(self):
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data):
        return cls(**{k: v for k, v in data.items() if k in [f for f in cls.__dataclass_fields__]})


@dataclass
class RiskManagement:
    """Risk management parameters"""
    risk_percent: float = 10.0
    reward_ratio: float = 1.0
    stop_loss_percent: float = 5.0
    capital: float = 10000.0
    margin: Optional[float] = None
    
    def dict(self):
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data):
        return cls(**{k: v for k, v in data.items() if k in ['risk_percent', 'reward_ratio', 'stop_loss_percent', 'capital', 'margin']})


@dataclass
class Strategy:
    """Custom trading strategy"""
    name: str
    indicators: List[IndicatorConfig] = field(default_factory=list)
    signal_logic: SignalLogic = field(default_factory=SignalLogic)
    filters: FilterConfig = field(default_factory=FilterConfig)
    risk: RiskManagement = field(default_factory=RiskManagement)
    description: str = ""
    created_at: Optional[str] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()
        
        # Convert dicts to objects if needed
        if isinstance(self.indicators, list) and self.indicators and isinstance(self.indicators[0], dict):
            self.indicators = [IndicatorConfig.from_dict(ind) for ind in self.indicators]
        
        if isinstance(self.signal_logic, dict):
            self.signal_logic = SignalLogic.from_dict(self.signal_logic)
        
        if isinstance(self.filters, dict):
            self.filters = FilterConfig.from_dict(self.filters)
        
        if isinstance(self.risk, dict):
            self.risk = RiskManagement.from_dict(self.risk)
    
    def dict(self):
        return {
            'name': self.name,
            'indicators': [ind.dict() for ind in self.indicators],
            'signal_logic': self.signal_logic.dict(),
            'filters': self.filters.dict(),
            'risk': self.risk.dict(),
            'description': self.description,
            'created_at': self.created_at
        }
    
    @classmethod
    def from_dict(cls, data):
        """Create Strategy from dict, handling both 'risk' and 'risk_management' keys"""
        indicators = [IndicatorConfig.from_dict(ind) for ind in data.get('indicators', [])]
        signal_logic = SignalLogic.from_dict(data.get('signal_logic', {}))
        filters = FilterConfig.from_dict(data.get('filters', {}))
        
        # Handle both 'risk' and 'risk_management' keys
        risk_data = data.get('risk') or data.get('risk_management', {})
        risk = RiskManagement.from_dict(risk_data)
        
        return cls(
            name=data.get('name', 'Unnamed'),
            indicators=indicators,
            signal_logic=signal_logic,
            filters=filters,
            risk=risk,
            description=data.get('description', ''),
            created_at=data.get('created_at')
        )


@dataclass
class SignalDetail:
    """Detail about a single indicator signal"""
    indicator_type: str
    indicator_id: str
    bullish: bool
    bearish: bool
    value: float
    weight: float
    contribution_percent: float
    enabled: bool = True
    
    def dict(self):
        return asdict(self)


@dataclass
class BacktestTrade:
    """A single trade execution"""
    entry_index: int
    entry_price: float
    entry_time: str
    direction: str
    size: float
    exit_index: int
    exit_price: float
    exit_time: str
    profit_loss: float
    profit_loss_percent: float
    bars_held: int
    
    def dict(self):
        return asdict(self)


@dataclass
class BacktestResult:
    """Backtest result summary"""
    status: str
    total_candles: int
    signals_found: int
    trades_executed: int
    winning_trades: int
    losing_trades: int
    win_rate: float
    profit_factor: float
    total_profit: float
    total_profit_percent: float
    max_drawdown: float
    sharpe_ratio: float
    trades: List[BacktestTrade] = field(default_factory=list)
    error: Optional[str] = None
    
    def dict(self):
        return {
            'status': self.status,
            'total_candles': self.total_candles,
            'signals_found': self.signals_found,
            'trades_executed': self.trades_executed,
            'winning_trades': self.winning_trades,
            'losing_trades': self.losing_trades,
            'win_rate': self.win_rate,
            'profit_factor': self.profit_factor,
            'total_profit': self.total_profit,
            'total_profit_percent': self.total_profit_percent,
            'max_drawdown': self.max_drawdown,
            'sharpe_ratio': self.sharpe_ratio,
            'trades': [t.dict() for t in self.trades],
            'error': self.error
        }


# Backward compatibility
class BacktestRequest:
    def __init__(self, strategy: dict, ohlcv_data: list):
        self.strategy = Strategy.from_dict(strategy)
        self.ohlcv_data = ohlcv_data
    
    def dict(self):
        return {
            'strategy': self.strategy.dict(),
            'ohlcv_data': self.ohlcv_data
        }


class StrategyListItem:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)
    
    def dict(self):
        return self.__dict__
