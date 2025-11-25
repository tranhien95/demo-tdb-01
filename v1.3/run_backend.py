#!/usr/bin/env python3
"""
Simple runner for backend that won't shut down
"""
import sys
import os
from pathlib import Path

# Add current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

if __name__ == "__main__":
    try:
        print("[Backend] Importing modules...")
        import uvicorn
        from backend import app
        
        print("[Backend] Starting Combo Optimizer v1.3 Backend...")
        print("[Backend] Available at http://0.0.0.0:8000")
        print("[Backend] Press CTRL+C to stop")
        
        # Keep the server running
        uvicorn.run(
            app, 
            host="0.0.0.0", 
            port=8000, 
            log_level="info",
            access_log=True
        )
    except KeyboardInterrupt:
        print("\n[Backend] Shutting down...")
        sys.exit(0)
    except Exception as e:
        print(f"[Backend] STARTUP ERROR: {e}")
        import traceback
        traceback.print_exc()
        print("[Backend] Keeping process alive for debugging...")
        import time
        while True:
            time.sleep(1)
