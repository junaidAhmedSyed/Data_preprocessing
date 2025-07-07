#!/bin/bash

# Snowflake Table Statistics Dashboard - Quick Start Script

echo "❄️ Starting Snowflake Table Statistics Dashboard..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8+ first."
    exit 1
fi

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip is not installed. Please install pip first."
    exit 1
fi

# Install requirements if they don't exist
if [ ! -f "requirements.txt" ]; then
    echo "❌ requirements.txt not found. Make sure you're in the correct directory."
    exit 1
fi

echo "📦 Installing/updating dependencies..."
pip3 install -r requirements.txt

# Create .streamlit directory if it doesn't exist
if [ ! -d ".streamlit" ]; then
    mkdir .streamlit
    echo "📁 Created .streamlit directory"
fi

# Check for secrets file
if [ ! -f ".streamlit/secrets.toml" ]; then
    echo "⚠️  No secrets.toml found. You can either:"
    echo "   1. Copy config_example.toml to .streamlit/secrets.toml and fill in your credentials"
    echo "   2. Enter credentials manually in the app"
    echo ""
fi

# Start the Streamlit app
echo "🚀 Starting the application..."
echo "📱 The app will open in your default browser"
echo "🛑 Press Ctrl+C to stop the application"
echo ""

streamlit run snowflake_stats_app.py