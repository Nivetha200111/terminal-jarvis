@echo off
REM Terminal Jarvis Deployment Script for Windows
REM This script creates a complete deployment package

echo ========================================
echo Terminal Jarvis Deployment Script
echo ========================================
echo.

REM Check if virtual environment exists
if not exist ".venv" (
    echo Creating virtual environment...
    python -m venv .venv
    if errorlevel 1 (
        echo ERROR: Failed to create virtual environment
        pause
        exit /b 1
    )
)

REM Activate virtual environment
echo Activating virtual environment...
call .venv\Scripts\activate.bat
if errorlevel 1 (
    echo ERROR: Failed to activate virtual environment
    pause
    exit /b 1
)

REM Install dependencies
echo Installing dependencies...
pip install --upgrade pip
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

REM Run tests
echo Running system tests...
python test_rag.py
if errorlevel 1 (
    echo WARNING: Some tests failed, but continuing with deployment
)

REM Create deployment directory
echo Creating deployment package...
if exist "deployment" rmdir /s /q deployment
mkdir deployment
mkdir deployment\jarvis
mkdir deployment\models
mkdir deployment\data

REM Copy files
echo Copying application files...
xcopy /E /I jarvis deployment\jarvis\
copy requirements.txt deployment\
copy setup.py deployment\
copy README.md deployment\
copy launch_desktop.py deployment\
copy launch_desktop.bat deployment\
copy launch_desktop.ps1 deployment\
copy demo.py deployment\
copy test_rag.py deployment\
copy test_demo.py deployment\
copy quickstart.ps1 deployment\

REM Create launcher script
echo Creating launcher script...
echo @echo off > deployment\start_jarvis.bat
echo echo Starting Terminal Jarvis... >> deployment\start_jarvis.bat
echo call .venv\Scripts\activate.bat >> deployment\start_jarvis.bat
echo python launch_desktop.py >> deployment\start_jarvis.bat
echo pause >> deployment\start_jarvis.bat

REM Create README for deployment
echo Creating deployment README...
echo # Terminal Jarvis - Deployment Package > deployment\DEPLOYMENT_README.md
echo. >> deployment\DEPLOYMENT_README.md
echo This is a complete deployment package for Terminal Jarvis. >> deployment\DEPLOYMENT_README.md
echo. >> deployment\DEPLOYMENT_README.md
echo ## Quick Start >> deployment\DEPLOYMENT_README.md
echo. >> deployment\DEPLOYMENT_README.md
echo 1. Double-click start_jarvis.bat to launch the desktop app >> deployment\DEPLOYMENT_README.md
echo 2. Or run: python launch_desktop.py >> deployment\DEPLOYMENT_README.md
echo 3. Or run: python demo.py for the demo chooser >> deployment\DEPLOYMENT_README.md
echo. >> deployment\DEPLOYMENT_README.md
echo ## Features >> deployment\DEPLOYMENT_README.md
echo. >> deployment\DEPLOYMENT_README.md
echo - Transparent desktop GUI with pip mode >> deployment\DEPLOYMENT_README.md
echo - RAG system for document knowledge base >> deployment\DEPLOYMENT_README.md
echo - Task automation (add to PATH, install packages, etc.) >> deployment\DEPLOYMENT_README.md
echo - Local LLM with GGUF model support >> deployment\DEPLOYMENT_README.md
echo - Terminal CLI interface >> deployment\DEPLOYMENT_README.md
echo. >> deployment\DEPLOYMENT_README.md
echo ## Setup >> deployment\DEPLOYMENT_README.md
echo. >> deployment\DEPLOYMENT_README.md
echo 1. Download a GGUF model and place it in the models\ folder >> deployment\DEPLOYMENT_README.md
echo 2. Run the application >> deployment\DEPLOYMENT_README.md
echo 3. Use the Knowledge Base menu to add documents >> deployment\DEPLOYMENT_README.md
echo 4. Ask questions and let Jarvis help with tasks! >> deployment\DEPLOYMENT_README.md

echo.
echo ========================================
echo Deployment completed successfully!
echo ========================================
echo.
echo The deployment package is in the 'deployment' folder.
echo You can now distribute this folder to other users.
echo.
echo To run Terminal Jarvis:
echo 1. Navigate to the deployment folder
echo 2. Double-click start_jarvis.bat
echo.
echo Or run: python launch_desktop.py
echo.
pause
