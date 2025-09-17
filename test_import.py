#!/usr/bin/env python3
"""
Test script to debug import and initialization issues
"""

import os
import sys

def test_imports():
    """Test all major imports to identify issues"""
    
    print("Testing imports...")
    
    try:
        print("1. Testing eventlet...")
        import eventlet
        eventlet.monkey_patch()
        print("   ✓ eventlet imported and patched")
    except Exception as e:
        print(f"   ✗ eventlet failed: {e}")
        return False
    
    try:
        print("2. Testing warnings suppression...")
        import warnings
        warnings.filterwarnings("ignore", category=FutureWarning, module="torch")
        print("   ✓ warnings configured")
    except Exception as e:
        print(f"   ✗ warnings failed: {e}")
    
    try:
        print("3. Testing Flask...")
        from flask import Flask
        print("   ✓ Flask imported")
    except Exception as e:
        print(f"   ✗ Flask failed: {e}")
        return False
    
    try:
        print("4. Testing Flask-SocketIO...")
        from flask_socketio import SocketIO
        print("   ✓ Flask-SocketIO imported")
    except Exception as e:
        print(f"   ✗ Flask-SocketIO failed: {e}")
        return False
    
    try:
        print("5. Testing PyTorch...")
        import torch
        print(f"   ✓ PyTorch imported (version: {torch.__version__})")
        print(f"   ✓ PyTorch device: {torch.device('cpu')}")
    except Exception as e:
        print(f"   ✗ PyTorch failed: {e}")
        return False
    
    try:
        print("6. Testing game imports...")
        from game import Game
        print("   ✓ Game class imported")
    except Exception as e:
        print(f"   ✗ Game import failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    try:
        print("7. Testing game initialization...")
        game = Game()
        print("   ✓ Game instance created")
    except Exception as e:
        print(f"   ✗ Game initialization failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    try:
        print("8. Testing EntityAI...")
        from entity_ai import EntityAI
        entity_ai = EntityAI()
        print("   ✓ EntityAI created")
    except Exception as e:
        print(f"   ✗ EntityAI failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print("\n✓ All imports successful!")
    return True

def test_basic_app():
    """Test basic Flask app creation"""
    try:
        print("\nTesting Flask app creation...")
        from flask import Flask
        from flask_socketio import SocketIO
        
        app = Flask(__name__)
        app.config['SECRET_KEY'] = 'test-key'
        
        socketio = SocketIO(app, 
                           cors_allowed_origins="*",
                           async_mode='eventlet',
                           ping_timeout=60,
                           ping_interval=25)
        
        print("✓ Flask app and SocketIO created successfully")
        return True
    except Exception as e:
        print(f"✗ App creation failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=== Terminal Souls Import Test ===")
    print(f"Python version: {sys.version}")
    print(f"Working directory: {os.getcwd()}")
    print()
    
    # Test imports
    imports_ok = test_imports()
    
    # Test app creation
    app_ok = test_basic_app()
    
    if imports_ok and app_ok:
        print("\n🎉 All tests passed! The app should work.")
    else:
        print("\n❌ Some tests failed. Check the errors above.")
        sys.exit(1)