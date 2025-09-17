#!/usr/bin/env python3
"""
Terminal Souls Web Interface for Render deployment
"""

# CRITICAL: eventlet.monkey_patch() MUST be called before any other imports
import eventlet
eventlet.monkey_patch()

# Suppress torch warnings that conflict with eventlet
import warnings
warnings.filterwarnings("ignore", category=FutureWarning, module="torch")

import os
import asyncio
from flask import Flask, render_template, request, jsonify, session
from flask_socketio import SocketIO, emit
import uuid
import threading
import queue
import sys
from io import StringIO
import contextlib

# Import the game
try:
    from game import Game
    print("[DEBUG] Successfully imported Game class")
except Exception as e:
    print(f"[ERROR] Failed to import Game: {e}")
    import traceback
    traceback.print_exc()
    raise

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'terminal-souls-secret-key')

# Configure for production
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 300

# Initialize SocketIO with proper configuration for Render
socketio = SocketIO(app, 
                   cors_allowed_origins="*",
                   logger=True,
                   engineio_logger=True,
                   async_mode='eventlet',
                   ping_timeout=60,
                   ping_interval=25)

# Store active game sessions
active_games = {}

class WebGameInterface:
    """Interface to run Terminal Souls in web environment"""
    
    def __init__(self, session_id, app_instance):
        try:
            print(f"[DEBUG] Initializing WebGameInterface for session {session_id}")
            self.session_id = session_id
            self.app = app_instance
            print(f"[DEBUG] Creating Game instance...")
            self.game = Game()
            print(f"[DEBUG] Game instance created successfully")
            self.input_queue = queue.Queue()
            self.output_buffer = []
            self.waiting_for_input = False
            print(f"[DEBUG] WebGameInterface initialization complete")
        except Exception as e:
            print(f"[ERROR] WebGameInterface initialization failed: {e}")
            import traceback
            traceback.print_exc()
            raise
        
    def capture_print(self, text):
        """Capture print output for web display"""
        self.output_buffer.append(text)
        
    def send_output(self):
        """Send captured output to web client"""
        if self.output_buffer:
            output = '\n'.join(self.output_buffer)
            self.output_buffer = []
            with self.app.app_context():
                socketio.emit('game_output', {'text': output}, room=self.session_id)
    
    def get_input(self, prompt=""):
        """Get input from web client"""
        self.waiting_for_input = True
        
        # Debug: Log input request
        print(f"[DEBUG] Emitting request_input with prompt: {prompt}")
        
        with self.app.app_context():
            socketio.emit('request_input', {'prompt': prompt}, room=self.session_id)
        
        # Wait for input from client
        try:
            print(f"[DEBUG] Waiting for input from queue...")
            user_input = self.input_queue.get(timeout=60)  # 60 second timeout
            self.waiting_for_input = False
            print(f"[DEBUG] Got input from queue: {user_input}")
            return user_input
        except queue.Empty:
            print(f"[DEBUG] Input timeout - no input received")
            self.waiting_for_input = False
            return ""
    
    def run_game(self):
        """Run the game with web interface"""
        import sys
        
        # Monkey patch input and print for web
        original_input = __builtins__['input']
        original_print = __builtins__['print']
        original_stdout = sys.stdout
        
        def web_input(prompt=""):
            # Send any pending output first
            self.send_output()  
            if prompt:
                self.capture_print(prompt)
                self.send_output()
            
            # Debug: Log that we're waiting for input
            print(f"[DEBUG] Waiting for input with prompt: {prompt}")
            
            result = self.get_input(prompt)
            # Clear processing state after receiving input
            with self.app.app_context():
                socketio.emit('clear_processing', room=self.session_id)
            
            # Debug: Log received input
            print(f"[DEBUG] Received input: {result}")
            return result
        
        def web_print(*args, **kwargs):
            # Capture the print output
            output = StringIO()
            print(*args, file=output, **kwargs)
            content = output.getvalue().rstrip('\n')
            if content:  # Only capture non-empty content
                self.capture_print(content)
                # Send output immediately for real-time display
                self.send_output()
        
        # Custom stdout to capture any direct writes
        class WebStdout:
            def __init__(self, interface):
                self.interface = interface
                
            def write(self, text):
                if text.strip():  # Only capture non-empty content
                    self.interface.capture_print(text.rstrip('\n'))
                    self.interface.send_output()
                return len(text)
                
            def flush(self):
                pass
        
        try:
            # Replace both print and stdout
            __builtins__['input'] = web_input
            __builtins__['print'] = web_print
            sys.stdout = WebStdout(self)
            
            # Send initial game output
            self.capture_print("🔥 The Entity stirs... Compiling your doom...")
            self.send_output()
            
            # Run the game
            self.game.run()
            
        finally:
            # Restore original functions
            __builtins__['input'] = original_input
            __builtins__['print'] = original_print
            sys.stdout = original_stdout
            
            # Send final output
            self.send_output()
            with self.app.app_context():
                socketio.emit('game_ended', room=self.session_id)

@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')

@socketio.on('start_game')
def handle_start_game():
    """Start a new game session"""
    try:
        print(f"[DEBUG] Received start_game request")
        session_id = str(uuid.uuid4())
        session['game_id'] = session_id
        
        print(f"[DEBUG] Creating game interface for session {session_id}")
        # Create new game interface
        game_interface = WebGameInterface(session_id, app)
        active_games[session_id] = game_interface
        
        print(f"[DEBUG] Starting game thread for session {session_id}")
        # Start game in background thread
        def run_game_thread():
            try:
                print(f"[DEBUG] Game thread started for session {session_id}")
                game_interface.run_game()
                print(f"[DEBUG] Game thread completed for session {session_id}")
            except Exception as e:
                print(f"[ERROR] Game thread error for session {session_id}: {e}")
                import traceback
                traceback.print_exc()
                try:
                    with app.app_context():
                        socketio.emit('game_error', {'error': f'Game initialization error: {str(e)}'}, room=session_id)
                except Exception as emit_error:
                    print(f"[ERROR] Failed to emit error: {emit_error}")
            finally:
                # Clean up session
                print(f"[DEBUG] Cleaning up session {session_id}")
                if session_id in active_games:
                    del active_games[session_id]
        
        thread = threading.Thread(target=run_game_thread)
        thread.daemon = True
        thread.start()
        
        print(f"[DEBUG] Emitting game_started for session {session_id}")
        emit('game_started', {'session_id': session_id})
        
    except Exception as e:
        print(f"[ERROR] Failed to start game: {e}")
        import traceback
        traceback.print_exc()
        emit('game_error', {'error': f'Failed to start game: {str(e)}'})

@socketio.on('send_input')
def handle_input(data):
    """Handle user input"""
    session_id = session.get('game_id')
    user_input = data.get('input', '')
    
    if session_id in active_games:
        game_interface = active_games[session_id]
        if game_interface.waiting_for_input:
            game_interface.input_queue.put(user_input)

@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    print(f"Client connected: {request.sid}")

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    session_id = session.get('game_id')
    if session_id in active_games:
        del active_games[session_id]
    print(f"Client disconnected: {request.sid}")

# Health check endpoint
@app.route('/health')
def health_check():
    return {'status': 'ok', 'message': 'Terminal Souls is running'}

# Serve static files properly
@app.route('/static/<path:filename>')
def serve_static(filename):
    return app.send_static_file(filename)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    print(f"[DEBUG] Starting server on port {port}")
    socketio.run(app, host='0.0.0.0', port=port, debug=False, allow_unsafe_werkzeug=True)
