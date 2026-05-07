"""
HTTP Monitoring Server
Provides REST API for game state observation and control
"""
print("Importing: threading")
import threading
print("Importing: json")
import json
print("Importing: Dict, Any")
from typing import Dict, Any
print("Importing: dataclass, asdict")
from dataclasses import dataclass, asdict
print("Importing: Enum")
from enum import Enum
print("Importing: datetime")
from datetime import datetime

try:
    print("Importing: Flask, jsonify, request")
    from flask import Flask, jsonify, request
    FLASK_AVAILABLE = True
except ImportError:
    FLASK_AVAILABLE = False


class GameState(Enum):
    """Game state enum"""
    IDLE = "idle"
    START = "start"
    RUNNING = "running"
    PAUSED = "paused"
    END = "end"


@dataclass
class GameStatus:
    """Current game status snapshot"""
    state: str
    score: int
    strikes: int
    max_faces: int
    current_faces: int
    fps: float
    switch_time_remaining: float
    current_switch_time: float
    game_over: bool
    timestamp: str
    backend: str


class MonitoringServer:
    """HTTP monitoring server for game state"""
    
    def __init__(self, port: int = 5000, host: str = "0.0.0.0"):
        self.port = port
        self.host = host
        self.app = None
        self.server_thread = None
        self._game_state_callback = None
        self._start_game_callback = None
        self._pause_game_callback = None
        self._adjust_max_faces_callback = None
        
        if FLASK_AVAILABLE:
            self._setup_flask()
    
    def _setup_flask(self) -> None:
        """Initialize Flask app with routes"""
        self.app = Flask(__name__)
        
        # Routes
        @self.app.route('/health', methods=['GET'])
        def health():
            """Health check endpoint"""
            return jsonify({"status": "ok", "timestamp": datetime.now().isoformat()}), 200
        
        @self.app.route('/game/status', methods=['GET'])
        def get_status():
            """Get current game status"""
            if self._game_state_callback:
                status = self._game_state_callback()
                if status:
                    return jsonify(asdict(status)), 200
            return jsonify({"error": "Game state unavailable"}), 503
        
        @self.app.route('/game/start', methods=['POST'])
        def start_game():
            """Start a new game"""
            if self._start_game_callback:
                self._start_game_callback()
                return jsonify({"message": "Game started"}), 200
            return jsonify({"error": "Game not available"}), 503
        
        @self.app.route('/game/pause', methods=['POST'])
        def pause_game():
            """Pause/resume game"""
            if self._pause_game_callback:
                self._pause_game_callback()
                return jsonify({"message": "Game paused/resumed"}), 200
            return jsonify({"error": "Game not available"}), 503
        
        @self.app.route('/game/max-faces', methods=['POST'])
        def adjust_max_faces():
            """Adjust maximum face count"""
            data = request.get_json() or {}
            new_max = data.get('value')
            direction = data.get('direction')  # 'up' or 'down'
            
            if self._adjust_max_faces_callback:
                self._adjust_max_faces_callback(new_max, direction)
                return jsonify({"message": f"Max faces adjusted to {new_max}"}), 200
            return jsonify({"error": "Game not available"}), 503
        
        @self.app.route('/metrics', methods=['GET'])
        def get_metrics():
            """Get performance metrics"""
            if self._game_state_callback:
                status = self._game_state_callback()
                if status:
                    return jsonify({
                        "fps": status.fps,
                        "current_faces": status.current_faces,
                        "game_state": status.state,
                        "score": status.score,
                        "timestamp": status.timestamp
                    }), 200
            return jsonify({"error": "Metrics unavailable"}), 503
    
    def set_game_state_callback(self, callback) -> None:
        """Set callback to get game state snapshot
        
        Args:
            callback: Function that returns GameStatus
        """
        self._game_state_callback = callback
    
    def set_start_game_callback(self, callback) -> None:
        """Set callback to start game
        
        Args:
            callback: Function to call when start is requested
        """
        self._start_game_callback = callback
    
    def set_pause_game_callback(self, callback) -> None:
        """Set callback to pause/resume game
        
        Args:
            callback: Function to call when pause is requested
        """
        self._pause_game_callback = callback
    
    def set_adjust_max_faces_callback(self, callback) -> None:
        """Set callback to adjust max face count
        
        Args:
            callback: Function(new_max, direction) to call
        """
        self._adjust_max_faces_callback = callback
    
    def start(self) -> None:
        """Start the HTTP server in a background thread"""
        if not self.app:
            print("⚠ Flask not available. HTTP monitoring disabled.")
            return
        
        def run_server():
            print(f"✓ HTTP monitoring server starting on {self.host}:{self.port}")
            self.app.run(host=self.host, port=self.port, debug=False, threaded=True)
        
        self.server_thread = threading.Thread(target=run_server, daemon=True)
        self.server_thread.start()
    
    def stop(self) -> None:
        """Stop the HTTP server"""
        print("Stopping HTTP monitoring server...")
        # Flask doesn't have a clean way to stop from outside, so we just let the thread exit
