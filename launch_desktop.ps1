# Terminal Jarvis Desktop Launcher for PowerShell
# This script launches the transparent desktop GUI

Write-Host "Starting Terminal Jarvis Desktop..." -ForegroundColor Cyan

# Check if virtual environment exists
if (-not (Test-Path ".venv")) {
    Write-Host "Virtual environment not found. Please run quickstart.ps1 first." -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& .\.venv\Scripts\Activate.ps1

# Run desktop app
Write-Host "Launching desktop application..." -ForegroundColor Green
python launch_desktop.py

# Check for errors
if ($LASTEXITCODE -ne 0) {
    Write-Host "An error occurred. Press Enter to exit." -ForegroundColor Red
    Read-Host
}
