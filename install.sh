#!/bin/bash

# Terminal Souls - Local Installation Script
# This script sets up Terminal Souls on your local machine

set -e  # Exit on error

echo "🔥 Terminal Souls - Local Setup Script 🔥"
echo "==========================================="
echo ""

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    echo "Please install Python 3.8 or higher and try again."
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
echo "✅ Python $PYTHON_VERSION detected"

# Check Python version is 3.8+
python3 -c 'import sys; assert sys.version_info >= (3, 8), "Python 3.8+ required"' || {
    echo "❌ Python 3.8 or higher is required. You have Python $PYTHON_VERSION"
    exit 1
}

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
else
    echo "📦 Virtual environment already exists"
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "📚 Installing dependencies..."
pip install -r requirements.txt

# Create lore directory structure if it doesn't exist
echo "📁 Setting up game assets..."
mkdir -p lore/music

# Check if PyTorch is properly installed
echo "🧠 Testing PyTorch installation..."
python3 -c "import torch; print('✅ PyTorch installed successfully - version:', torch.__version__)" || {
    echo "❌ PyTorch installation failed. Trying to reinstall..."
    pip install --upgrade torch torchvision
}

# Test game can import without errors
echo "🎮 Testing game imports..."
python3 -c "from game import Game; print('✅ Game imports successfully')" || {
    echo "❌ Game import test failed. Check the logs above for errors."
    exit 1
}

echo ""
echo "🎉 Installation Complete!"
echo "======================="
echo ""
echo "To start playing Terminal Souls:"
echo "1. Activate the virtual environment: source venv/bin/activate"
echo "2. Run the game: python3 game.py"
echo ""
echo "Or use the direct launcher: ./play.sh"
echo ""
echo "For help during the game, type 'help' at the startup prompt."
echo ""
echo "📋 Other commands:"
echo "• Uninstall completely: ./uninstall.sh"
echo "• Reinstall dependencies: ./install.sh"
echo ""
echo "🔥 The Entity awaits your descent... 🔥"
