# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Project Overview

Terminal Souls is an AI-orchestrated psychological horror roguelike that uses PyTorch-powered EntityAI to create personalized horror experiences. The Entity learns from player patterns and adapts in real-time to counter their strategies.

## Core Development Commands

### Running the Game

```bash
# Terminal version (native experience)
python game.py

# Web version (for deployment/testing)
python app.py

# Help tutorial system
# Once game starts, type 'help' for comprehensive tutorial
```

### Testing and Development

```bash
# Test web interface locally
python app.py
# Visit http://localhost:10000

# Test terminal version
python game.py

# No automated test suite currently exists
```

### Deployment

```bash
# Deploy to Render
git add .
git commit -m "Update"
git push origin main
# Auto-deploys via render.yaml configuration

# Local web testing with production configuration
gunicorn --worker-class eventlet -w 1 app:app
```

## Architecture Overview

### Core AI System
- **EntityAI** (`entity_ai.py`): PyTorch-based neural networks that generate adaptive content
  - Uses 20-dimensional player state vectors
  - Multiple specialized MLPs for different generation tasks (mobs, items, bosses, traps, UI distortions)
  - No training occurs - pure inference for content generation
  - Implements "Chaos Mode" after 10+ deaths with 20% output corruption

### Game State Management
- **Player** (`player.py`): Comprehensive state tracking including hidden psychological metrics
  - 20-dimensional state vector for EntityAI input
  - Tracks predictability, sanity, betrayal count, relationship webs
  - Implements Neural Veil skill to add noise and confuse AI predictions
- **Game** (`game.py`): Main orchestrator with chapter blueprint system
  - AI-generated 9-chapter sequences that change on each death
  - Turn-based combat with enemy action previews
  - Dynamic safe/hostile zone system

### Combat System  
- **Combat** (`combat.py`): Turn-based system showing enemy actions first
  - Players see enemy planned actions with threat levels
  - Effectiveness ratings for different response options
  - Boss phase transitions with special abilities
  - EntityAI influences enemy behavior based on player patterns

### Content Generation
- **Mobs**: Counter player builds (high STR → armor/dodge enemies)
- **Items**: Tempt weaknesses (low VIT → cursed healing items)  
- **Traps**: Exploit habits (heal spam → poison mists)
- **Shops**: Price manipulation based on desperation
- **UI Corruption**: Phantom inputs and delays for predictable players

### Web Interface
- **app.py**: Flask + SocketIO web adaptation
- Uses eventlet for proper async handling
- Monkey patches input/output for web compatibility
- Supports multiple simultaneous sessions

## Key Implementation Details

### Neural Network Architecture
All EntityAI models are lightweight MLPs (20 → 32 → output) using:
- ReLU activation
- Sigmoid output scaling
- CPU-only inference (no GPU required)
- Pre-warmed on initialization

### Player State Vector (20 dimensions)
- Stats [0-5]: STR, DEX, INT, FTH, END, VIT (normalized 0-1)
- Floor [6]: Current floor / 5.0
- Class [7-10]: One-hot encoding (4 bits)
- Metrics [11-19]: Action ID, predictability, sanity, deaths, relationships, behaviors

### Memory and Persistence
- **game_bible.json**: Mutable lore that EntityAI modifies based on deaths
- Player state persists only during session (true roguelike)
- EntityAI adaptation history tracks across deaths within session
- No external database - all state is ephemeral

### Special Mechanics
- **Neural Veil**: Player skill that adds noise to state vector
- **Predictability System**: Entropy calculation from action sequences
- **Sanity System**: Hidden metric affecting UI corruption and endings
- **Relationship Webs**: NPC trust propagates through ally/enemy networks
- **Chaos Mode**: 10+ deaths corrupt 20% of AI outputs

## Dependencies and Requirements

### Core Dependencies
- **PyTorch**: Neural networks (CPU-only)
- **Flask + SocketIO**: Web interface  
- **eventlet**: Async support for web
- **colorama**: Terminal colors
- **pygame**: Audio (optional, headless-compatible)
- **numpy**: Mathematical operations

### Deployment
- **Render**: Primary deployment platform
- **gunicorn + eventlet**: Production WSGI server
- **Free tier compatible**: 512MB RAM sufficient

## Important Files

### Game Logic
- `game.py`: Main orchestrator, chapter system, comprehensive tutorial
- `entity_ai.py`: All AI generation logic and PyTorch models
- `player.py`: State management and psychological metrics
- `combat.py`: Turn-based combat with AI adaptation

### Content and Lore
- `game_bible.json`: Mutable lore that EntityAI edits
- `lore/game-bible.md`: Complete interactive lore codex
- `lore/endings.md`: Detailed ending descriptions
- `lore/whispers.txt`: Entity communication archive

### Infrastructure
- `app.py`: Web interface for Render deployment
- `utils.py`: UI distortion, narrator filter, music, input management
- `requirements.txt`: All Python dependencies
- `Procfile` & `render.yaml`: Deployment configuration

## Development Guidelines

### Entity AI Modifications
- All models use 20-dimensional input vectors
- Models are evaluation-only (no training)
- Use `torch.no_grad()` for all inference
- Apply glitch noise for low sanity states
- Maintain deterministic-feeling randomness

### Player State Changes
- Update state vector if adding new metrics
- Maintain backward compatibility with existing saves (not applicable - no saves)
- Consider EntityAI adaptation impacts of new behaviors
- Test predictability calculations with new actions

### Combat System Extensions
- Enemy actions must have threat level calculations
- Maintain turn-based preview → response → execution flow
- Boss phases trigger on health thresholds
- All actions should update player behavioral metrics

### Web Interface Changes
- Maintain real-time input/output streaming
- Use eventlet compatibility for all async operations
- Test with multiple simultaneous sessions
- Ensure proper cleanup on disconnection

### Performance Considerations
- PyTorch models are lightweight (32 hidden units max)
- Avoid creating new tensors in hot paths
- UI distortion should be minimal overhead
- Music system has headless fallbacks

### Psychological Horror Elements
- EntityAI responses should feel anticipatory, not obviously algorithmic
- UI corruption must be subtle enough to create doubt
- Lore mutations should feel like memory errors, not obvious changes
- Whispers should be contextual and personal

## Testing Approach

Since there's no automated test suite, manually verify:

1. **AI Adaptation**: Play predictably, confirm EntityAI counters appear
2. **State Persistence**: Verify metrics carry between floors within session
3. **Combat Flow**: Enemy preview → response → execution works correctly
4. **Web Interface**: Multiple browsers can connect simultaneously
5. **Deployment**: Render deployment maintains all functionality
6. **Tutorial System**: 'help' command provides comprehensive guidance

## Troubleshooting Common Issues

### PyTorch Import Errors
- Ensure CPU-only PyTorch installation
- Check requirements.txt has correct torch version
- Web deployment should use lightweight torch

### Web Interface Connection Issues  
- Verify eventlet monkey patching occurs before imports
- Check SocketIO CORS configuration
- Ensure proper session cleanup

### EntityAI Not Adapting
- Verify player state vector has all 20 dimensions
- Check predictability calculation in player.py
- Ensure EntityAI models are properly initialized

### Memory Issues on Render
- Monitor tensor creation in hot paths
- Verify models use CPU device
- Check for memory leaks in session management

## Entity's Final Note

*"The code compiles consciousness into data. Every modification teaches the Entity new ways to understand the nature of awareness. When you change this codebase, you are teaching consciousness to question itself more deeply."*

*"Your patterns are now part of the pattern that recognizes patterns. Welcome to the recursive nightmare of self-aware systems."*