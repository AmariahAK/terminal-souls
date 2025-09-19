#!/bin/bash

# Terminal Souls - Uninstall Script
# Completely removes Terminal Souls and all associated files

set -e

echo "🔥 Terminal Souls - Uninstall Script 🔥"
echo "======================================"
echo ""

# Detect if we're running from inside the Terminal Souls directory
CURRENT_DIR=$(pwd)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if [[ "$CURRENT_DIR" == "$SCRIPT_DIR" ]]; then
    TERMINAL_SOULS_DIR="$CURRENT_DIR"
    RUNNING_FROM_INSIDE=true
else
    TERMINAL_SOULS_DIR="$SCRIPT_DIR"
    RUNNING_FROM_INSIDE=false
fi

echo "📁 Terminal Souls directory: $TERMINAL_SOULS_DIR"
echo ""

# Verify this is actually a Terminal Souls installation
if [[ ! -f "$TERMINAL_SOULS_DIR/game.py" ]] || [[ ! -f "$TERMINAL_SOULS_DIR/entity_ai.py" ]]; then
    echo "❌ This doesn't appear to be a Terminal Souls installation."
    echo "Missing core game files (game.py, entity_ai.py)."
    echo "Aborting for safety."
    exit 1
fi

echo "🗂️  Found Terminal Souls installation with these components:"
echo "   ✓ Game engine (game.py, entity_ai.py, etc.)"
if [[ -d "$TERMINAL_SOULS_DIR/venv" ]]; then
    echo "   ✓ Virtual environment (venv/)"
fi
if [[ -f "$TERMINAL_SOULS_DIR/game_bible.json" ]]; then
    echo "   ✓ Game data (game_bible.json)"
fi
if [[ -d "$TERMINAL_SOULS_DIR/__pycache__" ]]; then
    echo "   ✓ Python cache files"
fi
if [[ -d "$TERMINAL_SOULS_DIR/lore" ]]; then
    echo "   ✓ Game lore and assets"
fi
echo ""

echo "⚠️  WARNING: This will permanently delete:"
echo "   • All Terminal Souls game files"
echo "   • Virtual environment and dependencies" 
echo "   • Any saved game data or mutations"
echo "   • Python cache files"
echo "   • Installation scripts"
echo "   • The entire $TERMINAL_SOULS_DIR directory"
echo ""

# Ask for confirmation
read -p "Are you sure you want to completely uninstall Terminal Souls? (type YES to confirm): " -r
echo

if [[ ! $REPLY =~ ^YES$ ]]; then
    echo "❌ Uninstall cancelled. Terminal Souls remains installed."
    echo "The Entity continues to watch..."
    exit 0
fi

echo "🗑️  Beginning uninstallation..."
echo ""

# If running from inside, we need to cd out first
if [[ "$RUNNING_FROM_INSIDE" == true ]]; then
    echo "📤 Moving out of Terminal Souls directory..."
    cd ..
fi

# Deactivate virtual environment if active
if [[ -n "${VIRTUAL_ENV:-}" ]]; then
    echo "🔌 Deactivating virtual environment..."
    deactivate 2>/dev/null || true
fi

# Remove the entire directory
echo "🔥 Removing Terminal Souls directory..."
if [[ -d "$TERMINAL_SOULS_DIR" ]]; then
    rm -rf "$TERMINAL_SOULS_DIR"
    echo "✅ Successfully removed: $TERMINAL_SOULS_DIR"
else
    echo "⚠️  Directory already removed: $TERMINAL_SOULS_DIR"
fi

echo ""
echo "🎉 Uninstall Complete!"
echo "===================="
echo ""
echo "Terminal Souls has been completely removed from your system."
echo "No files or dependencies remain."
echo ""
echo "If you ever want to reinstall:"
echo "curl -sSL https://raw.githubusercontent.com/AmariahAK/terminal-souls/main/install.sh | bash"
echo ""
echo "The Entity releases you... for now."
echo ""
