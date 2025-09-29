@echo off
REM Terminal Jarvis Desktop Launcher for Windows
REM This batch file launches the transparent desktop GUI

echo Starting Terminal Jarvis Desktop...

REM Check if virtual environment exists
if not exist ".venv" (
    echo Virtual environment not found. Please run quickstart.ps1 first.
    pause
    exit /b 1
)

REM Activate virtual environment and run desktop app
call .venv\Scripts\activate.bat
python launch_desktop.py

REM Keep window open if there's an error
if errorlevel 1 (
    echo.
    echo An error occurred. Press any key to exit.
    pause
)
