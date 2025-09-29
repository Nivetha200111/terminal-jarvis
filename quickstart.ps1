# Terminal Jarvis Quick Start Script for Windows PowerShell
# This script sets up the environment and provides instructions for getting started

Write-Host "Terminal Jarvis - Local LLM Setup" -ForegroundColor Cyan
Write-Host "=================================" -ForegroundColor Cyan
Write-Host ""

# Check if Python is installed
$pythonCheck = Get-Command python -ErrorAction SilentlyContinue
if ($pythonCheck) {
    $pythonVersion = python --version 2>&1
    Write-Host "[OK] Python found: $pythonVersion" -ForegroundColor Green
} else {
    Write-Host "[ERROR] Python not found. Please install Python 3.8+ from https://python.org" -ForegroundColor Red
    exit 1
}

# Create virtual environment if it doesn't exist
if (-not (Test-Path ".venv")) {
    Write-Host "Creating virtual environment..." -ForegroundColor Yellow
    python -m venv .venv
}

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& .\.venv\Scripts\Activate.ps1

# Install dependencies
Write-Host "Installing dependencies..." -ForegroundColor Yellow
pip install --upgrade pip
pip install -r requirements.txt

Write-Host ""
Write-Host "[SUCCESS] Setup complete!" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "1. Download a GGUF model from Hugging Face (e.g., TheBloke/Llama-2-7B-GGUF)"
Write-Host ""
Write-Host "Choose your interface:" -ForegroundColor Yellow
Write-Host "  Desktop GUI: python launch_desktop.py (or double-click launch_desktop.bat)"
Write-Host "  Terminal CLI: python -m jarvis --model path\to\your\model.gguf"
Write-Host "  Demo Mode:    python demo.py (no model required)"
Write-Host ""
Write-Host "For help: python -m jarvis --help" -ForegroundColor Yellow