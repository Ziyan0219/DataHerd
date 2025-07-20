#!/bin/bash

# DataHerd Quick Start Script

echo "🐄 DataHerd - Intelligent Cattle Data Cleaning Agent"
echo "=================================================="

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed or not in PATH"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "🔧 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "🔧 Installing dependencies..."
pip install -r requirements.txt

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found, copying from .env.example"
    cp .env.example .env
    echo "📝 Please edit .env file with your configuration before running again"
    exit 1h
fi

# Start the application
echo "🚀 Starting DataHerd..."
python3 start.py "$@"

