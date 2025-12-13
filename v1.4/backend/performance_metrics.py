"""
Performance Metrics Calculator
Standardized calculations for trading strategy performance
"""

from typing import List, Dict, Optional
import math


class PerformanceMetrics:
    """Calculate standardized trading performance metrics"""
    
    @staticmethod
    def calculate_profit_factor(trades: List[Dict]) -> float:
        """
        Calculate Profit Factor = Gross Profit / Gross Loss
        
        Args:
            trades: List of completed trades with 'profit' field
            
        Returns:
            Profit factor (0 if no losses)
        """
        if not trades:
            return 0.0
        
        gross_profit = sum([t.get('profit', 0) for t in trades if t.get('profit', 0) > 0])
        gross_loss = abs(sum([t.get('profit', 0) for t in trades if t.get('profit', 0) < 0]))
        
        if gross_loss == 0:
            return gross_profit if gross_profit > 0 else 0.0
        
        return round(gross_profit / gross_loss, 2)
    
    @staticmethod
    def calculate_sharpe_ratio(trades: List[Dict], risk_free_rate: float = 0.0) -> float:
        """
        Calculate Sharpe Ratio = (Mean Return - Risk Free Rate) / Std Dev of Returns
        
        Args:
            trades: List of completed trades with 'profit_pct' field
            risk_free_rate: Annual risk-free rate (default 0%)
            
        Returns:
            Sharpe ratio (0 if no volatility)
        """
        if not trades or len(trades) < 2:
            return 0.0
        
        returns = [t.get('profit_pct', 0) for t in trades]
        
        # Calculate mean and std dev
        mean_return = sum(returns) / len(returns)
        variance = sum([(r - mean_return) ** 2 for r in returns]) / len(returns)
        std_dev = math.sqrt(variance)
        
        if std_dev == 0:
            return 0.0
        
        sharpe = (mean_return - risk_free_rate) / std_dev
        return round(sharpe, 2)
    
    @staticmethod
    def calculate_sortino_ratio(trades: List[Dict], risk_free_rate: float = 0.0) -> float:
        """
        Calculate Sortino Ratio = (Mean Return - Risk Free Rate) / Downside Deviation
        Only considers downside volatility (negative returns)
        
        Args:
            trades: List of completed trades with 'profit_pct' field
            risk_free_rate: Annual risk-free rate (default 0%)
            
        Returns:
            Sortino ratio
        """
        if not trades or len(trades) < 2:
            return 0.0
        
        returns = [t.get('profit_pct', 0) for t in trades]
        mean_return = sum(returns) / len(returns)
        
        # Only negative returns for downside deviation
        negative_returns = [r for r in returns if r < 0]
        
        if not negative_returns:
            return 0.0
        
        downside_variance = sum([r ** 2 for r in negative_returns]) / len(negative_returns)
        downside_dev = math.sqrt(downside_variance)
        
        if downside_dev == 0:
            return 0.0
        
        sortino = (mean_return - risk_free_rate) / downside_dev
        return round(sortino, 2)
    
    @staticmethod
    def calculate_calmar_ratio(total_return_pct: float, max_drawdown_pct: float) -> float:
        """
        Calculate Calmar Ratio = Total Return / Max Drawdown
        
        Args:
            total_return_pct: Total return percentage
            max_drawdown_pct: Maximum drawdown percentage
            
        Returns:
            Calmar ratio (higher is better)
        """
        if max_drawdown_pct == 0:
            return 0.0
        
        return round(total_return_pct / max_drawdown_pct, 2)
    
    @staticmethod
    def calculate_recovery_factor(net_profit: float, max_drawdown: float) -> float:
        """
        Calculate Recovery Factor = Net Profit / Max Drawdown
        
        Args:
            net_profit: Total net profit in currency
            max_drawdown: Maximum drawdown in currency
            
        Returns:
            Recovery factor (higher is better)
        """
        if max_drawdown == 0:
            return 0.0
        
        return round(net_profit / max_drawdown, 2)
    
    @staticmethod
    def calculate_expectancy(trades: List[Dict]) -> float:
        """
        Calculate Expectancy = (Win Rate × Avg Win) - (Loss Rate × Avg Loss)
        
        Args:
            trades: List of completed trades with 'profit' field
            
        Returns:
            Expected profit per trade
        """
        if not trades:
            return 0.0
        
        winning_trades = [t for t in trades if t.get('profit', 0) > 0]
        losing_trades = [t for t in trades if t.get('profit', 0) < 0]
        
        total_trades = len(trades)
        win_count = len(winning_trades)
        loss_count = len(losing_trades)
        
        if win_count == 0 and loss_count == 0:
            return 0.0
        
        win_rate = win_count / total_trades
        loss_rate = loss_count / total_trades
        
        avg_win = sum([t['profit'] for t in winning_trades]) / win_count if win_count > 0 else 0
        avg_loss = abs(sum([t['profit'] for t in losing_trades]) / loss_count) if loss_count > 0 else 0
        
        expectancy = (win_rate * avg_win) - (loss_rate * avg_loss)
        return round(expectancy, 4)
    
    @staticmethod
    def calculate_max_consecutive_losses(trades: List[Dict]) -> int:
        """
        Calculate maximum consecutive losing trades
        
        Args:
            trades: List of completed trades with 'profit' field
            
        Returns:
            Max consecutive losses
        """
        if not trades:
            return 0
        
        max_streak = 0
        current_streak = 0
        
        for trade in trades:
            if trade.get('profit', 0) < 0:
                current_streak += 1
                max_streak = max(max_streak, current_streak)
            else:
                current_streak = 0
        
        return max_streak
    
    @staticmethod
    def calculate_max_consecutive_wins(trades: List[Dict]) -> int:
        """
        Calculate maximum consecutive winning trades
        
        Args:
            trades: List of completed trades with 'profit' field
            
        Returns:
            Max consecutive wins
        """
        if not trades:
            return 0
        
        max_streak = 0
        current_streak = 0
        
        for trade in trades:
            if trade.get('profit', 0) > 0:
                current_streak += 1
                max_streak = max(max_streak, current_streak)
            else:
                current_streak = 0
        
        return max_streak
    
    @staticmethod
    def analyze_trade_quality(trades: List[Dict]) -> Dict:
        """
        Analyze trade quality metrics
        
        Args:
            trades: List of completed trades with 'profit' field
            
        Returns:
            Dict with quality metrics
        """
        if not trades:
            return {
                'avg_win': 0.0,
                'avg_loss': 0.0,
                'largest_win': 0.0,
                'largest_loss': 0.0,
                'avg_win_pct': 0.0,
                'avg_loss_pct': 0.0,
                'profit_per_trade': 0.0,
            }
        
        winning_trades = [t for t in trades if t.get('profit', 0) > 0]
        losing_trades = [t for t in trades if t.get('profit', 0) < 0]
        
        avg_win = sum([t['profit'] for t in winning_trades]) / len(winning_trades) if winning_trades else 0
        avg_loss = sum([t['profit'] for t in losing_trades]) / len(losing_trades) if losing_trades else 0
        
        avg_win_pct = sum([t.get('profit_pct', 0) for t in winning_trades]) / len(winning_trades) if winning_trades else 0
        avg_loss_pct = sum([t.get('profit_pct', 0) for t in losing_trades]) / len(losing_trades) if losing_trades else 0
        
        all_profits = [t.get('profit', 0) for t in trades]
        largest_win = max(all_profits) if all_profits else 0
        largest_loss = min(all_profits) if all_profits else 0
        
        total_profit = sum(all_profits)
        profit_per_trade = total_profit / len(trades) if trades else 0
        
        return {
            'avg_win': round(avg_win, 4),
            'avg_loss': round(avg_loss, 4),
            'largest_win': round(largest_win, 4),
            'largest_loss': round(largest_loss, 4),
            'avg_win_pct': round(avg_win_pct, 2),
            'avg_loss_pct': round(avg_loss_pct, 2),
            'profit_per_trade': round(profit_per_trade, 4),
        }
    
    @staticmethod
    def calculate_max_drawdown_details(equity_curve: List[float]) -> Dict:
        """
        Calculate detailed drawdown information
        
        Args:
            equity_curve: List of equity values over time
            
        Returns:
            Dict with drawdown details
        """
        if not equity_curve or len(equity_curve) < 2:
            return {
                'max_drawdown_pct': 0.0,
                'max_drawdown_value': 0.0,
                'drawdown_duration': 0,
                'recovery_duration': 0,
            }
        
        max_equity = equity_curve[0]
        max_drawdown_value = 0
        max_drawdown_pct = 0
        drawdown_start_idx = 0
        drawdown_end_idx = 0
        current_drawdown_start = 0
        
        for i, equity in enumerate(equity_curve):
            if equity > max_equity:
                max_equity = equity
                current_drawdown_start = i
            
            drawdown_value = max_equity - equity
            drawdown_pct = (drawdown_value / max_equity * 100) if max_equity > 0 else 0
            
            if drawdown_pct > max_drawdown_pct:
                max_drawdown_pct = drawdown_pct
                max_drawdown_value = drawdown_value
                drawdown_start_idx = current_drawdown_start
                drawdown_end_idx = i
        
        drawdown_duration = drawdown_end_idx - drawdown_start_idx
        
        # Find recovery duration
        recovery_duration = 0
        if drawdown_end_idx < len(equity_curve) - 1:
            recovery_equity = equity_curve[drawdown_end_idx]
            for i in range(drawdown_end_idx + 1, len(equity_curve)):
                if equity_curve[i] >= max_equity:
                    recovery_duration = i - drawdown_end_idx
                    break
        
        return {
            'max_drawdown_pct': round(max_drawdown_pct, 2),
            'max_drawdown_value': round(max_drawdown_value, 2),
            'drawdown_duration': drawdown_duration,
            'recovery_duration': recovery_duration,
        }
    
    @staticmethod
    def calculate_all_metrics(trades: List[Dict], equity_curve: List[float], 
                            initial_capital: float = 10000.0) -> Dict:
        """
        Calculate all performance metrics at once
        
        Args:
            trades: List of completed trades
            equity_curve: Equity curve data
            initial_capital: Starting capital
            
        Returns:
            Dict with all metrics
        """
        if not trades:
            return {
                'profit_factor': 0.0,
                'sharpe_ratio': 0.0,
                'sortino_ratio': 0.0,
                'calmar_ratio': 0.0,
                'recovery_factor': 0.0,
                'expectancy': 0.0,
                'max_consecutive_losses': 0,
                'max_consecutive_wins': 0,
                'profit_per_trade': 0.0,
                'avg_win': 0.0,
                'avg_loss': 0.0,
                'avg_win_pct': 0.0,
                'avg_loss_pct': 0.0,
                'largest_win': 0.0,
                'largest_loss': 0.0,
                'max_drawdown_pct': 0.0,
                'max_drawdown_value': 0.0,
                'drawdown_duration': 0,
                'recovery_duration': 0,
            }
        
        profit_factor = PerformanceMetrics.calculate_profit_factor(trades)
        sharpe = PerformanceMetrics.calculate_sharpe_ratio(trades)
        sortino = PerformanceMetrics.calculate_sortino_ratio(trades)
        expectancy = PerformanceMetrics.calculate_expectancy(trades)
        max_cons_losses = PerformanceMetrics.calculate_max_consecutive_losses(trades)
        max_cons_wins = PerformanceMetrics.calculate_max_consecutive_wins(trades)
        trade_quality = PerformanceMetrics.analyze_trade_quality(trades)
        
        # Calculate drawdown details
        dd_details = PerformanceMetrics.calculate_max_drawdown_details(equity_curve)
        
        # Calculate total return
        final_equity = equity_curve[-1] if equity_curve else initial_capital
        total_return_pct = ((final_equity - initial_capital) / initial_capital * 100)
        
        calmar = PerformanceMetrics.calculate_calmar_ratio(
            total_return_pct, 
            dd_details['max_drawdown_pct']
        )
        
        recovery = PerformanceMetrics.calculate_recovery_factor(
            final_equity - initial_capital,
            dd_details['max_drawdown_value']
        )
        
        return {
            'profit_factor': profit_factor,
            'sharpe_ratio': sharpe,
            'sortino_ratio': sortino,
            'calmar_ratio': calmar,
            'recovery_factor': recovery,
            'expectancy': expectancy,
            'max_consecutive_losses': max_cons_losses,
            'max_consecutive_wins': max_cons_wins,
            'profit_per_trade': trade_quality['profit_per_trade'],
            'avg_win': trade_quality['avg_win'],
            'avg_loss': trade_quality['avg_loss'],
            'avg_win_pct': trade_quality['avg_win_pct'],
            'avg_loss_pct': trade_quality['avg_loss_pct'],
            'largest_win': trade_quality['largest_win'],
            'largest_loss': trade_quality['largest_loss'],
            'max_drawdown_pct': dd_details['max_drawdown_pct'],
            'max_drawdown_value': dd_details['max_drawdown_value'],
            'drawdown_duration': dd_details['drawdown_duration'],
            'recovery_duration': dd_details['recovery_duration'],
        }
