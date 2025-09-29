# Terminal Jarvis Deployment Script for PowerShell
# This script creates a complete deployment package

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Terminal Jarvis Deployment Script" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if virtual environment exists
if (-not (Test-Path ".venv")) {
    Write-Host "Creating virtual environment..." -ForegroundColor Yellow
    python -m venv .venv
    if ($LASTEXITCODE -ne 0) {
        Write-Host "ERROR: Failed to create virtual environment" -ForegroundColor Red
        Read-Host "Press Enter to exit"
        exit 1
    }
}

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& .\.venv\Scripts\Activate.ps1
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Failed to activate virtual environment" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Install dependencies
Write-Host "Installing dependencies..." -ForegroundColor Yellow
pip install --upgrade pip
pip install -r requirements.txt
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Failed to install dependencies" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Run tests
Write-Host "Running system tests..." -ForegroundColor Yellow
python test_rag.py
if ($LASTEXITCODE -ne 0) {
    Write-Host "WARNING: Some tests failed, but continuing with deployment" -ForegroundColor Yellow
}

# Create deployment directory
Write-Host "Creating deployment package..." -ForegroundColor Yellow
if (Test-Path "deployment") {
    Remove-Item -Recurse -Force "deployment"
}
New-Item -ItemType Directory -Path "deployment" | Out-Null
New-Item -ItemType Directory -Path "deployment\jarvis" | Out-Null
New-Item -ItemType Directory -Path "deployment\models" | Out-Null
New-Item -ItemType Directory -Path "deployment\data" | Out-Null

# Copy files
Write-Host "Copying application files..." -ForegroundColor Yellow
Copy-Item -Recurse "jarvis" "deployment\jarvis\"
Copy-Item "requirements.txt" "deployment\"
Copy-Item "setup.py" "deployment\"
Copy-Item "README.md" "deployment\"
Copy-Item "launch_desktop.py" "deployment\"
Copy-Item "launch_desktop.bat" "deployment\"
Copy-Item "launch_desktop.ps1" "deployment\"
Copy-Item "demo.py" "deployment\"
Copy-Item "test_rag.py" "deployment\"
Copy-Item "test_demo.py" "deployment\"
Copy-Item "quickstart.ps1" "deployment\"

# Create launcher script
Write-Host "Creating launcher script..." -ForegroundColor Yellow
@"
@echo off
echo Starting Terminal Jarvis...
call .venv\Scripts\activate.bat
python launch_desktop.py
pause
"@ | Out-File -FilePath "deployment\start_jarvis.bat" -Encoding ASCII

# Create README for deployment
Write-Host "Creating deployment README..." -ForegroundColor Yellow
@"
# Terminal Jarvis - Deployment Package

This is a complete deployment package for Terminal Jarvis.

## Quick Start

1. Double-click start_jarvis.bat to launch the desktop app
2. Or run: python launch_desktop.py
3. Or run: python demo.py for the demo chooser

## Features

- Transparent desktop GUI with pip mode
- RAG system for document knowledge base
- Task automation (add to PATH, install packages, etc.)
- Local LLM with GGUF model support
- Terminal CLI interface

## Setup

1. Download a GGUF model and place it in the models\ folder
2. Run the application
3. Use the Knowledge Base menu to add documents
4. Ask questions and let Jarvis help with tasks!

## Examples

### Adding Python to PATH
"Add Python to my PATH" - Jarvis will automatically add Python to your system PATH

### Installing Packages
"Install numpy package" - Jarvis will install the package using pip

### Document Search
Upload documents to the knowledge base and ask questions about them

### System Tasks
"Show me system status" - Get CPU, memory, and disk usage information
"Run dir command" - Execute system commands
"@ | Out-File -FilePath "deployment\DEPLOYMENT_README.md" -Encoding UTF8

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "Deployment completed successfully!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "The deployment package is in the 'deployment' folder." -ForegroundColor Cyan
Write-Host "You can now distribute this folder to other users." -ForegroundColor Cyan
Write-Host ""
Write-Host "To run Terminal Jarvis:" -ForegroundColor Yellow
Write-Host "1. Navigate to the deployment folder" -ForegroundColor White
Write-Host "2. Double-click start_jarvis.bat" -ForegroundColor White
Write-Host ""
Write-Host "Or run: python launch_desktop.py" -ForegroundColor White
Write-Host ""
Read-Host "Press Enter to continue"
