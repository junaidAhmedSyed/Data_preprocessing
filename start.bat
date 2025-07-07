@echo off
REM Snowflake Table Statistics Dashboard - Quick Start Script for Windows

echo ❄️ Starting Snowflake Table Statistics Dashboard...

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed. Please install Python 3.8+ first.
    pause
    exit /b 1
)

REM Check if pip is installed
pip --version >nul 2>&1
if errorlevel 1 (
    echo ❌ pip is not installed. Please install pip first.
    pause
    exit /b 1
)

REM Check if requirements.txt exists
if not exist requirements.txt (
    echo ❌ requirements.txt not found. Make sure you're in the correct directory.
    pause
    exit /b 1
)

echo 📦 Installing/updating dependencies...
pip install -r requirements.txt

REM Create .streamlit directory if it doesn't exist
if not exist .streamlit mkdir .streamlit && echo 📁 Created .streamlit directory

REM Check for secrets file
if not exist .streamlit\secrets.toml (
    echo ⚠️ No secrets.toml found. You can either:
    echo    1. Copy config_example.toml to .streamlit\secrets.toml and fill in your credentials
    echo    2. Enter credentials manually in the app
    echo.
)

REM Start the Streamlit app
echo 🚀 Starting the application...
echo 📱 The app will open in your default browser
echo 🛑 Press Ctrl+C to stop the application
echo.

streamlit run snowflake_stats_app.py