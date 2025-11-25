@echo off
echo.
echo ========================================
echo  Autonomous Cyber Sentinel
echo ========================================
echo.
cd /d "%~dp0"
call .venv\Scripts\activate.bat
echo Starting server on http://localhost:8001
echo Press Ctrl+C to stop
echo.
python -m uvicorn sentinel.dashboard.app:app --host 0.0.0.0 --port 8001
pause
