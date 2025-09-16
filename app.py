#!/usr/bin/env python3
"""
Terminal Souls Web Interface for Render deployment
"""

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
from game import Game

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'terminal-souls-secret-key')
socketio = SocketIO(app, cors_allowed_origins="*")

# Store active game sessions
active_games = {}

class WebGameInterface:
    """Interface to run Terminal Souls in web environment"""
    
    def __init__(self, session_id):
        self.session_id = session_id
        self.game = Game()
        self.input_queue = queue.Queue()
        self.output_buffer = []
        self.waiting_for_input = False
        
    def capture_print(self, text):
        """Capture print output for web display"""
        self.output_buffer.append(text)
        
    def send_output(self):
        """Send captured output to web client"""
        if self.output_buffer:
            output = '\n'.join(self.output_buffer)
            self.output_buffer = []
            socketio.emit('game_output', {'text': output}, room=self.session_id)
    
    def get_input(self, prompt=""):
        """Get input from web client"""
        self.waiting_for_input = True
        socketio.emit('request_input', {'prompt': prompt}, room=self.session_id)
        
        # Wait for input from client
        try:
            user_input = self.input_queue.get(timeout=60)  # 60 second timeout
            self.waiting_for_input = False
            return user_input
        except queue.Empty:
            self.waiting_for_input = False
            return ""
    
    def run_game(self):
        """Run the game with web interface"""
        # Monkey patch input and print for web
        original_input = __builtins__['input']
        original_print = __builtins__['print']
        
        def web_input(prompt=""):
            self.send_output()  # Send any pending output first
            return self.get_input(prompt)
        
        def web_print(*args, **kwargs):
            output = StringIO()
            print(*args, file=output, **kwargs)
            self.capture_print(output.getvalue().strip())
        
        try:
            __builtins__['input'] = web_input
            __builtins__['print'] = web_print
            
            # Run the game
            self.game.run()
            
        finally:
            # Restore original functions
            __builtins__['input'] = original_input
            __builtins__['print'] = original_print
            
            # Send final output
            self.send_output()
            socketio.emit('game_ended', room=self.session_id)

@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')

@socketio.on('start_game')
def handle_start_game():
    """Start a new game session"""
    session_id = str(uuid.uuid4())
    session['game_id'] = session_id
    
    # Create new game interface
    game_interface = WebGameInterface(session_id)
    active_games[session_id] = game_interface
    
    # Start game in background thread
    def run_game_thread():
        try:
            game_interface.run_game()
        except Exception as e:
            socketio.emit('game_error', {'error': str(e)}, room=session_id)
        finally:
            # Clean up session
            if session_id in active_games:
                del active_games[session_id]
    
    thread = threading.Thread(target=run_game_thread)
    thread.daemon = True
    thread.start()
    
    emit('game_started', {'session_id': session_id})

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

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    socketio.run(app, host='0.0.0.0', port=port, debug=False)
