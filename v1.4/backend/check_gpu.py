#!/usr/bin/env python3
"""
GPU Check Script
Kiểm tra xem hệ thống có hỗ trợ GPU acceleration không
"""

import sys
import os

print("=" * 60)
print("GPU Acceleration Check")
print("=" * 60)

# Check NumPy
try:
    import numpy as np
    print(f"[OK] NumPy: {np.__version__} (CPU fallback available)")
except ImportError:
    print("[ERROR] NumPy: NOT INSTALLED")
    print("   Install: pip install numpy")
    sys.exit(1)

# Check CUDA/cuPy
print("\n[CHECK] Checking for GPU libraries...")

try:
    import cupy as cp
    print(f"[OK] cuPy: Installed (version: {cp.__version__})")
    
    # Check CUDA availability
    if cp.cuda.is_available():
        device_count = cp.cuda.runtime.getDeviceCount()
        print(f"[OK] CUDA: Available")
        print(f"[OK] GPU Devices: {device_count}")
        
        for i in range(device_count):
            device = cp.cuda.Device(i)
            device.use()
            mem_info = device.mem_info
            props = device.attributes
            
            print(f"\n[GPU {i}]:")
            print(f"   Name: {cp.cuda.runtime.getDeviceProperties(i)['name'].decode()}")
            print(f"   Compute Capability: {device.compute_capability}")
            print(f"   Total Memory: {mem_info[1] / 1024**3:.2f} GB")
            print(f"   Free Memory: {mem_info[0] / 1024**3:.2f} GB")
            print(f"   Used Memory: {(mem_info[1] - mem_info[0]) / 1024**3:.2f} GB")
        
        print("\n[OK] GPU acceleration is READY!")
        print("   Backend will automatically use GPU for calculations")
        
    else:
        print("[WARNING] CUDA: Not available (no GPU devices found)")
        print("   Backend will use CPU (NumPy)")
        
except ImportError:
    print("[WARNING] cuPy: NOT INSTALLED")
    print("   Backend will use CPU (NumPy)")
    print("\n[INFO] To enable GPU acceleration:")
    print("   1. Check CUDA version: nvidia-smi")
    print("   2. Install cuPy:")
    print("      - CUDA 12.x: pip install cupy-cuda12x")
    print("      - CUDA 11.x: pip install cupy-cuda11x")
    print("      - CUDA 10.x: pip install cupy-cuda10x")

# Check environment variable
print("\n[CONFIG]:")
use_gpu_env = os.getenv('USE_GPU', 'not set')
print(f"   USE_GPU environment variable: {use_gpu_env}")
if use_gpu_env.lower() == 'false':
    print("   [WARNING] GPU is disabled by USE_GPU=false")
    print("   Backend will use CPU even if GPU is available")

print("\n" + "=" * 60)
print("[OK] Check complete!")
print("=" * 60)

