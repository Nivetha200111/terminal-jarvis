@echo off
echo Starting Terminal Jarvis...
echo.
echo Setting up environment...
call .venv\Scripts\activate.bat
echo.
echo Launching desktop application...
python launch_desktop.py
echo.
echo Terminal Jarvis has closed.
pause
