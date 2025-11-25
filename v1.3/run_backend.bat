@echo off
title Combo Optimizer - Backend Server
cls
cd /d "D:\Trade\Demo1\v1.3"
echo Starting Backend Server on http://localhost:8000
echo Press CTRL+C to stop
echo.
python.exe -m uvicorn backend:app --host 0.0.0.0 --port 8000 --reload
pause
