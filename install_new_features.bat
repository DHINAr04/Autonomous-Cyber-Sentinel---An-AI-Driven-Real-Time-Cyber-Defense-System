@echo off
echo.
echo ========================================
echo  Installing New Features
echo  Autonomous Cyber Sentinel
echo ========================================
echo.
cd /d "%~dp0"
call .venv\Scripts\activate.bat
echo Installing new dependencies...
echo This may take a few minutes...
echo.
python -m pip install matplotlib plotly pandas jinja2 reportlab pillow aiosmtplib
echo.
echo ========================================
echo  Installation Complete!
echo ========================================
echo.
echo New Features Added:
echo  - 6 Threat Intelligence Sources
echo  - Automated PDF Report Generation
echo  - Advanced Charts and Visualizations
echo  - Enhanced Dashboard
echo.
echo Restart your server to use new features:
echo  .\start_server.bat
echo.
pause
