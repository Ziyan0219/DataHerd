#!/bin/bash

# DataHerd Installation Script
# This script automates the complete installation process for DataHerd

set -e  # Exit on any error

echo "🐄 DataHerd - Intelligent Cattle Data Cleaning Agent"
echo "=" * 50
echo "Starting installation process..."

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.11+ first."
    exit 1
fi

# Check Python version
PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
REQUIRED_VERSION="3.11"

if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then
    echo "❌ Python $REQUIRED_VERSION or higher is required. Current version: $PYTHON_VERSION"
    exit 1
fi

echo "✅ Python $PYTHON_VERSION detected"

# Create virtual environment
echo "🔧 Creating virtual environment..."
if [ -d "dataherd_env" ]; then
    echo "⚠️  Virtual environment already exists. Removing old one..."
    rm -rf dataherd_env
fi

python3 -m venv dataherd_env
source dataherd_env/bin/activate

echo "✅ Virtual environment created and activated"

# Install Python dependencies
echo "🔧 Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo "✅ Python dependencies installed"

# Set up environment configuration
echo "🔧 Setting up environment configuration..."
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "✅ Environment configuration file created (.env)"
    echo "⚠️  Please edit .env file and set your OPENAI_API_KEY"
else
    echo "✅ Environment configuration file already exists"
fi

# Initialize database
echo "🔧 Initializing database..."
python -m db.init_db

echo "✅ Database initialized"

# Check if Node.js is available for frontend build
if command -v node &> /dev/null && command -v pnpm &> /dev/null; then
    echo "🔧 Building frontend..."
    cd dataherd-frontend
    pnpm install
    pnpm run build
    cd ..
    echo "✅ Frontend built successfully"
else
    echo "⚠️  Node.js or pnpm not found. Skipping frontend build."
    echo "   You can build the frontend later with:"
    echo "   cd dataherd-frontend && pnpm install && pnpm run build"
fi

echo ""
echo "🎉 Installation completed successfully!"
echo ""
echo "To start DataHerd:"
echo "1. Activate the virtual environment: source dataherd_env/bin/activate"
echo "2. Make sure to set your OPENAI_API_KEY in the .env file"
echo "3. Run: python start.py"
echo ""
echo "The application will be available at: http://localhost:9000"
echo "API documentation will be available at: http://localhost:9000/docs"
echo ""
echo "For more information, see README.md"

