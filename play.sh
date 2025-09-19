#!/bin/bash

# Terminal Souls - Game Launcher
# Activates virtual environment and starts the game

set -e

echo "🔥 Starting Terminal Souls..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Please run ./install.sh first."
    echo ""
    echo "Available commands:"
    echo "• Install: ./install.sh"
    echo "• Uninstall: ./uninstall.sh"
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

# Check if dependencies are installed
python3 -c "import torch, pygame, colorama, numpy" 2>/dev/null || {
    echo "❌ Dependencies missing. Running installation..."
    echo ""
    echo "If you're having persistent issues, try:"
    echo "• Complete reinstall: ./uninstall.sh && ./install.sh"
    echo ""
    ./install.sh
}

# Clear screen and start game
clear
python3 game.py
