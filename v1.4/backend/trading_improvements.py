"""
Trading Improvements Module
Các cải tiến cho trading engine để tăng performance
"""

from typing import List, Dict, Optional, Tuple
from datetime import datetime
from live_trading_models import Position, SignalWithConfidence
from indicators.base import HelperFunctions


class TradingImprovements:
    """Các cải tiến trading logic"""
    
    @staticmethod
    def update_trailing_stop(
        position: Position,
        current_price: float,
        atr: float,
        trailing_multiplier: float = 1.5
    ) -> bool:
        """
        Update trailing stop loss cho position
        
        Args:
            position: Position object
            current_price: Giá hiện tại
            atr: ATR value (Average True Range)
            trailing_multiplier: Multiplier cho trailing distance (default 1.5x ATR)
            
        Returns:
            True nếu trailing stop được update
        """
        if not position:
            return False
        
        # Tính profit theo R (risk units)
        entry = position.entry_price
        initial_sl_distance = abs(entry - position.stoploss)
        
        if position.side == "LONG":
            profit = current_price - entry
            profit_pct = (profit / entry) * 100
        else:  # SHORT
            profit = entry - current_price
            profit_pct = (profit / entry) * 100
        
        # Chỉ kích hoạt trailing khi profit >= 1R
        profit_r = profit_pct / (initial_sl_distance / entry * 100) if initial_sl_distance > 0 else 0
        
        if profit_r < 1.0:
            return False  # Chưa đạt 1R, chưa trailing
        
        # Tính trailing distance
        trailing_distance = atr * trailing_multiplier
        
        # Update trailing stop
        if position.side == "LONG":
            new_sl = current_price - trailing_distance
            # Chỉ di chuyển SL lên, không bao giờ xuống
            if new_sl > position.stoploss:
                position.stoploss = new_sl
                if not hasattr(position, 'trailing_activated'):
                    position.trailing_activated = False
                position.trailing_activated = True
                return True
        else:  # SHORT
            new_sl = current_price + trailing_distance
            # Chỉ di chuyển SL xuống, không bao giờ lên
            if new_sl < position.stoploss:
                position.stoploss = new_sl
                if not hasattr(position, 'trailing_activated'):
                    position.trailing_activated = False
                position.trailing_activated = True
                return True
        
        return False
    
    @staticmethod
    def check_breakeven_stop(
        position: Position,
        current_price: float,
        breakeven_r: float = 1.0,
        buffer_pct: float = 0.1
    ) -> bool:
        """
        Di chuyển SL về breakeven khi profit >= breakeven_r
        
        Args:
            position: Position object
            current_price: Giá hiện tại
            breakeven_r: Profit R để kích hoạt breakeven (default 1.0 = 1R)
            buffer_pct: Buffer % để tránh bị stop do spread (default 0.1%)
            
        Returns:
            True nếu breakeven được set
        """
        if not position:
            return False
        
        # Check nếu đã set breakeven rồi
        if hasattr(position, 'breakeven_set') and position.breakeven_set:
            return False
        
        entry = position.entry_price
        initial_sl_distance = abs(entry - position.stoploss)
        
        # Tính profit R
        if position.side == "LONG":
            profit = current_price - entry
            profit_pct = (profit / entry) * 100
        else:  # SHORT
            profit = entry - current_price
            profit_pct = (profit / entry) * 100
        
        profit_r = profit_pct / (initial_sl_distance / entry * 100) if initial_sl_distance > 0 else 0
        
        # Kích hoạt breakeven khi profit >= breakeven_r
        if profit_r >= breakeven_r:
            if position.side == "LONG":
                # Entry + buffer để tránh spread
                position.stoploss = entry * (1 + buffer_pct / 100)
            else:  # SHORT
                position.stoploss = entry * (1 - buffer_pct / 100)
            
            if not hasattr(position, 'breakeven_set'):
                position.breakeven_set = False
            position.breakeven_set = True
            return True
        
        return False
    
    @staticmethod
    def check_partial_profit_taking(
        position: Position,
        current_price: float,
        partial_rules: List[Dict] = None
    ) -> Optional[float]:
        """
        Check xem có nên partial profit taking không
        
        Args:
            position: Position object
            current_price: Giá hiện tại
            partial_rules: List các rules cho partial exit
                Format: [{"r_level": 1.0, "close_pct": 0.5, "taken": False}, ...]
                
        Returns:
            % position cần close (0.0 - 1.0), hoặc None nếu không close
        """
        if not position or not partial_rules:
            return None
        
        entry = position.entry_price
        initial_sl_distance = abs(entry - position.stoploss)
        
        # Tính profit R
        if position.side == "LONG":
            profit = current_price - entry
            profit_pct = (profit / entry) * 100
        else:  # SHORT
            profit = entry - current_price
            profit_pct = (profit / entry) * 100
        
        profit_r = profit_pct / (initial_sl_distance / entry * 100) if initial_sl_distance > 0 else 0
        
        # Check từng rule
        for rule in partial_rules:
            r_level = rule.get('r_level', 0)
            close_pct = rule.get('close_pct', 0)
            taken = rule.get('taken', False)
            
            if profit_r >= r_level and not taken:
                rule['taken'] = True  # Mark as taken
                return close_pct
        
        return None
    
    @staticmethod
    def calculate_dynamic_position_size(
        base_risk_pct: float,
        confidence: float,
        volatility_pct: float,
        max_multiplier: float = 2.0
    ) -> float:
        """
        Tính position size động dựa trên confidence và volatility
        
        Args:
            base_risk_pct: Risk % cơ bản (ví dụ: 2%)
            confidence: Confidence level (0-100)
            volatility_pct: Volatility % (ATR/price * 100)
            max_multiplier: Max multiplier cho position size
            
        Returns:
            Adjusted risk %
        """
        # Confidence multiplier
        if confidence < 70:
            conf_multiplier = 0.5  # Giảm 50% khi confidence thấp
        elif confidence < 80:
            conf_multiplier = 0.75
        elif confidence < 90:
            conf_multiplier = 1.0  # Base size
        elif confidence < 95:
            conf_multiplier = 1.5  # Tăng 50%
        else:
            conf_multiplier = 2.0  # Tăng 100% khi confidence rất cao
        
        # Volatility adjustment
        # Giảm size khi volatility cao
        if volatility_pct > 2.0:
            vol_multiplier = 0.5  # Giảm 50%
        elif volatility_pct > 1.5:
            vol_multiplier = 0.75
        elif volatility_pct < 0.3:
            vol_multiplier = 0.75  # Giảm khi quá calm (có thể false signal)
        else:
            vol_multiplier = 1.0  # Normal
        
        # Final size
        adjusted_risk = base_risk_pct * conf_multiplier * vol_multiplier
        
        # Cap at max_multiplier
        return min(adjusted_risk, base_risk_pct * max_multiplier)
    
    @staticmethod
    def check_multi_timeframe_trend(
        higher_tf_data: List[Dict],
        current_price: float
    ) -> str:
        """
        Check trend trên higher timeframe
        
        Args:
            higher_tf_data: OHLCV data từ higher timeframe
            current_price: Giá hiện tại
            
        Returns:
            "UPTREND", "DOWNTREND", hoặc "SIDEWAYS"
        """
        if len(higher_tf_data) < 200:
            return "SIDEWAYS"  # Không đủ data
        
        closes = [d['close'] for d in higher_tf_data]
        
        # Calculate EMAs
        ema_50 = HelperFunctions.ema(closes, 50)
        ema_200 = HelperFunctions.ema(closes, 200)
        
        if len(ema_50) == 0 or len(ema_200) == 0:
            return "SIDEWAYS"
        
        ema_50_val = ema_50[-1]
        ema_200_val = ema_200[-1]
        
        if ema_50_val is None or ema_200_val is None:
            return "SIDEWAYS"
        
        # Determine trend
        if current_price > ema_50_val > ema_200_val:
            return "UPTREND"
        elif current_price < ema_50_val < ema_200_val:
            return "DOWNTREND"
        else:
            return "SIDEWAYS"
    
    @staticmethod
    def calculate_atr_based_sl_tp(
        entry_price: float,
        atr: float,
        rr_ratio: float = 2.0
    ) -> Tuple[float, float]:
        """
        Tính SL/TP dựa trên ATR
        
        Args:
            entry_price: Entry price
            atr: ATR value
            rr_ratio: Risk/Reward ratio (default 2.0)
            
        Returns:
            (sl_distance_pct, tp_distance_pct) in %
        """
        atr_pct = (atr / entry_price) * 100
        
        # Base SL = 2x ATR
        sl_distance_pct = atr_pct * 2
        
        # Adjust based on volatility
        if atr_pct < 0.3:  # Very low volatility
            sl_distance_pct = 0.5  # Minimum 0.5%
        elif atr_pct > 1.5:  # High volatility
            sl_distance_pct = 2.0  # Maximum 2%
        
        # TP = SL * RR ratio
        tp_distance_pct = sl_distance_pct * rr_ratio
        
        return sl_distance_pct, tp_distance_pct
    
    @staticmethod
    def calculate_signal_quality_score(
        confidence: float,
        volume_ratio: float,
        trend_aligned: bool,
        volatility_optimal: bool,
        time_optimal: bool
    ) -> float:
        """
        Tính điểm chất lượng signal (0-100)
        
        Args:
            confidence: Signal confidence (0-100)
            volume_ratio: Current volume / Average volume
            trend_aligned: Signal có align với trend không
            volatility_optimal: Volatility có optimal không
            time_optimal: Time có optimal không
            
        Returns:
            Quality score (0-100)
        """
        score = 0.0
        
        # 1. Confidence (30 points)
        if confidence >= 90:
            score += 30
        elif confidence >= 80:
            score += 25
        elif confidence >= 70:
            score += 20
        elif confidence >= 60:
            score += 10
        
        # 2. Volume confirmation (20 points)
        if volume_ratio >= 1.5:
            score += 20
        elif volume_ratio >= 1.2:
            score += 15
        elif volume_ratio >= 1.0:
            score += 10
        
        # 3. Trend alignment (20 points)
        if trend_aligned:
            score += 20
        
        # 4. Volatility (15 points)
        if volatility_optimal:
            score += 15
        else:
            score += 5
        
        # 5. Time filter (15 points)
        if time_optimal:
            score += 15
        
        return min(score, 100.0)
    
    @staticmethod
    def is_tradeable_time(current_time: datetime, market_type: str = "crypto") -> bool:
        """
        Check xem thời gian hiện tại có tốt cho trading không
        
        Args:
            current_time: Current datetime
            market_type: "crypto", "forex", hoặc "stock"
            
        Returns:
            True nếu tradeable
        """
        hour = current_time.hour
        weekday = current_time.weekday()
        
        if market_type == "crypto":
            # Crypto: Tránh 2-6 UTC (low volume)
            if 2 <= hour <= 6:
                return False
            # Crypto trade 24/7
            return True
        
        elif market_type == "forex":
            # Forex: Tránh weekend
            if weekday >= 5:  # Saturday, Sunday
                return False
            # Tránh Asian session (low volatility)
            if 0 <= hour <= 6:
                return False
            return True
        
        elif market_type == "stock":
            # Stock: Chỉ trade trong market hours
            if weekday >= 5:  # Weekend
                return False
            # Market hours: 9:30 - 16:00 (adjust theo timezone)
            if hour < 9 or hour >= 16:
                return False
            return True
        
        return True


# Example usage trong live_trading_engine.py:
"""
# Trong method _check_exit_conditions:
from trading_improvements import TradingImprovements

# 1. Check breakeven
TradingImprovements.check_breakeven_stop(
    position, current_price, breakeven_r=1.0
)

# 2. Update trailing stop
atr = self._calculate_atr(symbol, 14)
TradingImprovements.update_trailing_stop(
    position, current_price, atr, trailing_multiplier=1.5
)

# 3. Check partial profit
partial_rules = [
    {"r_level": 1.0, "close_pct": 0.5, "taken": False},
    {"r_level": 2.0, "close_pct": 0.25, "taken": False}
]
close_pct = TradingImprovements.check_partial_profit_taking(
    position, current_price, partial_rules
)
if close_pct:
    self._close_partial(position, close_pct)
"""


