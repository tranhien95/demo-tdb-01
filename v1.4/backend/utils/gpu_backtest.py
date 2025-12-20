"""
GPU-Accelerated Backtesting
Parallel backtesting of multiple indicator combinations on GPU
"""

import numpy as np
from typing import List, Dict, Any
from utils.gpu_acceleration import gpu, GPU_AVAILABLE


class GPUBacktestEngine:
    """GPU-accelerated backtesting engine"""
    
    def __init__(self):
        self.use_gpu = GPU_AVAILABLE and gpu.use_gpu
    
    def prepare_data_gpu(self, ohlcv_data: List[Dict]) -> Dict:
        """
        Prepare OHLCV data for GPU processing
        
        Returns:
            Dict with GPU arrays for OHLCV
        """
        closes = np.array([d['close'] for d in ohlcv_data], dtype=np.float32)
        opens = np.array([d['open'] for d in ohlcv_data], dtype=np.float32)
        highs = np.array([d['high'] for d in ohlcv_data], dtype=np.float32)
        lows = np.array([d['low'] for d in ohlcv_data], dtype=np.float32)
        volumes = np.array([d['volume'] for d in ohlcv_data], dtype=np.float32)
        
        if self.use_gpu:
            return {
                'close': gpu.to_gpu(closes),
                'open': gpu.to_gpu(opens),
                'high': gpu.to_gpu(highs),
                'low': gpu.to_gpu(lows),
                'volume': gpu.to_gpu(volumes),
                'length': len(ohlcv_data)
            }
        else:
            return {
                'close': closes,
                'open': opens,
                'high': highs,
                'low': lows,
                'volume': volumes,
                'length': len(ohlcv_data)
            }
    
    def batch_calculate_indicators(self, data_gpu: Dict, indicator_configs: List[Dict]) -> Dict:
        """
        Batch calculate multiple indicators on GPU
        
        Args:
            data_gpu: GPU-prepared OHLCV data
            indicator_configs: List of indicator configurations
            
        Returns:
            Dict with indicator signals for each combo
        """
        # This is a simplified version
        # In full implementation, would calculate all indicators in parallel on GPU
        
        results = {}
        closes = data_gpu['close']
        
        for config in indicator_configs:
            ind_name = config['indicator_name']
            ind_config = config.get('config', {})
            
            # Example: Calculate RSI on GPU if requested
            if ind_name == 'RSI' and 'period' in ind_config:
                period = ind_config['period']
                rsi_values = self._calculate_rsi_gpu(closes, period)
                results[ind_name] = rsi_values
        
        return results
    
    def _calculate_rsi_gpu(self, closes, period: int):
        """Calculate RSI on GPU"""
        from utils.gpu_acceleration import vectorized_rsi
        
        closes_cpu = gpu.to_cpu(closes) if self.use_gpu else closes
        rsi = vectorized_rsi(closes_cpu, period, use_gpu=self.use_gpu)
        
        if self.use_gpu:
            return gpu.to_gpu(rsi)
        return rsi
    
    def batch_backtest(self, combos: List[List[Dict]], data: List[Dict], 
                      params: Dict, batch_size: int = 100) -> List[Dict]:
        """
        Batch backtest multiple combos on GPU
        
        Args:
            combos: List of combo configs
            data: OHLCV data
            params: Backtest parameters
            batch_size: Number of combos to process in parallel
            
        Returns:
            List of backtest results
        """
        # Prepare data once
        data_gpu = self.prepare_data_gpu(data)
        
        results = []
        
        # Process in batches
        for i in range(0, len(combos), batch_size):
            batch = combos[i:i + batch_size]
            
            # For now, fallback to CPU backtesting
            # Future: Implement full GPU parallel backtesting
            for combo in batch:
                # Use existing CPU backtest logic
                # This will be replaced with GPU kernel in future
                pass
        
        return results

