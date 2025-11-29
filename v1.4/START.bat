@echo off
echo ========================================
echo   Combo Optimizer v1.4 - Startup
echo ========================================
echo.

echo Checking dependencies...
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed!
    echo Please install Python 3.8+ from https://www.python.org/
    pause
    exit /b 1
)

REM Check if Node.js is installed
node --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Node.js is not installed!
    echo Please install Node.js 18+ from https://nodejs.org/
    pause
    exit /b 1
)

echo [OK] Python and Node.js are installed
echo.

REM Start Backend
echo Starting Backend (Port 4000)...
cd backend
start "Combo Optimizer Backend" cmd /k "python main.py"
cd ..

REM Wait a bit for backend to start
timeout /t 3 /nobreak >nul

REM Check if pnpm is installed
pnpm --version >nul 2>&1
if errorlevel 1 (
    echo [WARNING] pnpm is not installed. Installing now...
    npm install -g pnpm
)

REM Start Frontend
echo Starting Frontend (Port 3000)...
cd frontend

REM Check if node_modules exists
if not exist "node_modules\" (
    echo Installing frontend dependencies...
    pnpm install
)

start "Combo Optimizer Frontend" cmd /k "pnpm dev"
cd ..

echo.
echo ========================================
echo   Combo Optimizer v1.4 is Running!
echo ========================================
echo Backend:  http://localhost:4000
echo Frontend: http://localhost:3000
echo.
echo Press any key to open browser...
pause >nul

REM Open browser
start http://localhost:3000

echo.
echo To stop the servers, close both terminal windows.
pause
