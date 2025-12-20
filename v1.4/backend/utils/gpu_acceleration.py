"""
GPU Acceleration Module
Provides GPU acceleration for indicator calculations and backtesting
Falls back to CPU if GPU is not available
"""

import os
from typing import Optional, Tuple
import numpy as np

# Try to import GPU libraries
GPU_AVAILABLE = False
GPU_LIBRARY = None
gpu_array = None
gpu_device = None

try:
    import cupy as cp
    # Check if CUDA is available
    if cp.cuda.is_available():
        GPU_AVAILABLE = True
        GPU_LIBRARY = 'cupy'
        gpu_array = cp.array
        gpu_device = cp.cuda.Device
        print("✅ GPU acceleration enabled (cuPy)")
    else:
        print("⚠️ cuPy installed but no CUDA devices found")
except ImportError:
    pass

# Fallback to NumPy if no GPU
if not GPU_AVAILABLE:
    try:
        import numpy as cp  # Use numpy as fallback
        gpu_array = np.array
        print("ℹ️ Using CPU (NumPy) - no GPU acceleration")
    except ImportError:
        raise ImportError("Neither cuPy nor NumPy available")


class GPUAccelerator:
    """GPU acceleration wrapper with CPU fallback"""
    
    def __init__(self):
        self.gpu_available = GPU_AVAILABLE
        self.gpu_library = GPU_LIBRARY
        self.use_gpu = GPU_AVAILABLE and os.getenv('USE_GPU', 'true').lower() == 'true'
        
        if self.use_gpu and GPU_AVAILABLE:
            try:
                self.device = cp.cuda.Device(0)
                self.device.use()
                mempool = cp.get_default_memory_pool()
                pinned_mempool = cp.get_default_pinned_memory_pool()
                print(f"✅ GPU Device: {cp.cuda.Device(0).compute_capability}")
                print(f"✅ GPU Memory: {cp.cuda.Device(0).mem_info[1] / 1024**3:.2f} GB")
            except Exception as e:
                print(f"⚠️ GPU initialization failed: {e}. Falling back to CPU.")
                self.use_gpu = False
    
    def to_gpu(self, array: np.ndarray) -> any:
        """Convert numpy array to GPU array"""
        if self.use_gpu and GPU_AVAILABLE:
            return cp.asarray(array)
        return array
    
    def to_cpu(self, array: any) -> np.ndarray:
        """Convert GPU array back to numpy array"""
        if self.use_gpu and GPU_AVAILABLE:
            return cp.asnumpy(array)
        return np.asarray(array)
    
    def array(self, *args, **kwargs) -> any:
        """Create array (GPU or CPU)"""
        if self.use_gpu and GPU_AVAILABLE:
            return cp.array(*args, **kwargs)
        return np.array(*args, **kwargs)
    
    def zeros(self, shape, dtype=np.float32):
        """Create zeros array"""
        if self.use_gpu and GPU_AVAILABLE:
            return cp.zeros(shape, dtype=dtype)
        return np.zeros(shape, dtype=dtype)
    
    def ones(self, shape, dtype=np.float32):
        """Create ones array"""
        if self.use_gpu and GPU_AVAILABLE:
            return cp.ones(shape, dtype=dtype)
        return np.ones(shape, dtype=dtype)
    
    def sum(self, array, axis=None):
        """Sum array"""
        if self.use_gpu and GPU_AVAILABLE:
            return cp.sum(array, axis=axis)
        return np.sum(array, axis=axis)
    
    def mean(self, array, axis=None):
        """Mean of array"""
        if self.use_gpu and GPU_AVAILABLE:
            return cp.mean(array, axis=axis)
        return np.mean(array, axis=axis)
    
    def max(self, array, axis=None):
        """Max of array"""
        if self.use_gpu and GPU_AVAILABLE:
            return cp.max(array, axis=axis)
        return np.max(array, axis=axis)
    
    def min(self, array, axis=None):
        """Min of array"""
        if self.use_gpu and GPU_AVAILABLE:
            return cp.min(array, axis=axis)
        return np.min(array, axis=axis)
    
    def std(self, array, axis=None):
        """Standard deviation"""
        if self.use_gpu and GPU_AVAILABLE:
            return cp.std(array, axis=axis)
        return np.std(array, axis=axis)
    
    def roll(self, array, shift, axis=None):
        """Roll array"""
        if self.use_gpu and GPU_AVAILABLE:
            return cp.roll(array, shift, axis=axis)
        return np.roll(array, shift, axis=axis)
    
    def where(self, condition, x, y):
        """Where condition"""
        if self.use_gpu and GPU_AVAILABLE:
            return cp.where(condition, x, y)
        return np.where(condition, x, y)
    
    def concatenate(self, arrays, axis=0):
        """Concatenate arrays"""
        if self.use_gpu and GPU_AVAILABLE:
            return cp.concatenate(arrays, axis=axis)
        return np.concatenate(arrays, axis=axis)
    
    def synchronize(self):
        """Synchronize GPU operations"""
        if self.use_gpu and GPU_AVAILABLE:
            cp.cuda.Stream.null.synchronize()


# Global GPU accelerator instance
gpu = GPUAccelerator()


def vectorized_rsi(closes: np.ndarray, period: int = 14, use_gpu: bool = True) -> np.ndarray:
    """
    Vectorized RSI calculation on GPU/CPU
    
    Args:
        closes: Array of closing prices
        period: RSI period
        use_gpu: Whether to use GPU
        
    Returns:
        Array of RSI values
    """
    if len(closes) < period + 1:
        return np.full(len(closes), 50.0)
    
    arr = gpu.to_gpu(closes.astype(np.float32)) if use_gpu else closes.astype(np.float32)
    
    # Calculate price changes
    deltas = arr[1:] - arr[:-1]
    
    # Separate gains and losses
    gains = gpu.where(deltas > 0, deltas, 0)
    losses = gpu.where(deltas < 0, -deltas, 0)
    
    # Calculate RSI using Wilder's smoothing
    rsi_values = gpu.zeros(len(closes))
    
    # First period: simple average
    first_gain = gpu.mean(gains[:period])
    first_loss = gpu.mean(losses[:period])
    
    if first_loss == 0:
        first_rs = 100
    else:
        first_rs = first_gain / first_loss
    rsi_values[period] = 100 - (100 / (1 + first_rs))
    
    # Subsequent periods: Wilder's smoothing
    for i in range(period + 1, len(closes)):
        avg_gain = (first_gain * (period - 1) + gains[i - 1]) / period
        avg_loss = (first_loss * (period - 1) + losses[i - 1]) / period if first_loss > 0 else 0.0001
        first_gain = avg_gain
        first_loss = avg_loss
        
        if avg_loss == 0:
            rs = 100
        else:
            rs = avg_gain / avg_loss
        rsi_values[i] = 100 - (100 / (1 + rs))
    
    result = gpu.to_cpu(rsi_values) if use_gpu else rsi_values
    return np.where(np.isnan(result), 50.0, result)


def vectorized_ema(closes: np.ndarray, period: int, use_gpu: bool = True) -> np.ndarray:
    """
    Vectorized EMA calculation on GPU/CPU
    
    Args:
        closes: Array of closing prices
        period: EMA period
        use_gpu: Whether to use GPU
        
    Returns:
        Array of EMA values
    """
    if len(closes) < period:
        return closes
    
    arr = gpu.to_gpu(closes.astype(np.float32)) if use_gpu else closes.astype(np.float32)
    
    multiplier = 2.0 / (period + 1)
    ema_values = gpu.zeros(len(closes))
    
    # Start with SMA
    ema_values[period - 1] = gpu.mean(arr[:period])
    
    # Calculate EMA for remaining values
    for i in range(period, len(closes)):
        ema_values[i] = (arr[i] * multiplier) + (ema_values[i - 1] * (1 - multiplier))
    
    result = gpu.to_cpu(ema_values) if use_gpu else ema_values
    return np.where(np.isnan(result), closes, result)


def vectorized_sma(closes: np.ndarray, period: int, use_gpu: bool = True) -> np.ndarray:
    """
    Vectorized SMA calculation on GPU/CPU using convolution
    
    Args:
        closes: Array of closing prices
        period: SMA period
        use_gpu: Whether to use GPU
        
    Returns:
        Array of SMA values
    """
    if len(closes) < period:
        return closes
    
    arr = gpu.to_gpu(closes.astype(np.float32)) if use_gpu else closes.astype(np.float32)
    
    # Use cumulative sum for efficient moving average
    cumsum = gpu.zeros(len(closes) + 1)
    cumsum[1:] = gpu.array([gpu.sum(arr[:i+1]) for i in range(len(arr))])
    
    # Calculate SMA
    sma_values = (cumsum[period:] - cumsum[:-period]) / period
    
    # Pad beginning with NaN
    padding = gpu.zeros(period - 1)
    result = gpu.concatenate([padding, sma_values])
    
    result_cpu = gpu.to_cpu(result) if use_gpu else result
    return np.where(np.isnan(result_cpu), closes[:len(result_cpu)], result_cpu)


def batch_backtest_combos(combos: list, data: list, params: dict, use_gpu: bool = True) -> list:
    """
    Batch backtest multiple combos in parallel on GPU
    
    Args:
        combos: List of combo configs to test
        data: OHLCV data
        params: Backtest parameters
        use_gpu: Whether to use GPU
        
    Returns:
        List of backtest results
    """
    # For now, this is a placeholder for future GPU parallelization
    # Current implementation still uses CPU loop
    # Future: Can use GPU streams or CUDA kernels for parallel backtesting
    
    results = []
    for combo in combos:
        # This would be parallelized on GPU in future implementation
        # For now, use existing CPU implementation
        pass
    
    return results

