# Embedded Face Detection Game - System Architecture

## Overview

This is a Raspberry Pi-based real-time face detection game with hardware button input, LED feedback, and HTTP monitoring. The system follows a professional embedded architecture with proper state management, threading, and timing constraints.

## System Layers

```
┌─────────────────────────────────────────────────────┐
│        Display Layer (HDMI Output)                   │
│  - Game HUD with score/strikes/timer                 │
│  - Countdown sequence                                │
│  - Face detection overlay                            │
└──────────────────────┬──────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────┐
│   Face Detection Layer (face_detector.py)            │
│  - CameraFaceDetector class                          │
│  - OpenCV/MediaPipe backends                         │
│  - Game state machine (IDLE/START/RUNNING/PAUSED/END)│
│  - Scoring & strike tracking                         │
│  - Dynamic difficulty scaling                        │
└──────────────────────┬──────────────────────────────┘
                       │
    ┌──────────────────┼──────────────────┐
    │                  │                  │
┌───▼───────┐  ┌──────▼──────┐  ┌───────▼──────┐
│ Hardware  │  │ Monitoring  │  │ Camera       │
│ Control   │  │ Server      │  │ Input        │
│ (GPIO)    │  │ (Flask)     │  │ (OpenCV)     │
└───┬───────┘  └──────┬──────┘  └───────┬──────┘
    │                  │                  │
    └──────────────────┼──────────────────┘
                       │
          ┌────────────┴────────────┐
          │                         │
    ┌─────▼──────┐          ┌──────▼──────┐
    │   Buttons  │          │    LEDs     │
    │  (GPIO in) │          │  (GPIO out) │
    └────────────┘          └─────────────┘
```

## Threading Model

```
Main Thread (Game Loop)
├─ Frame capture from camera
├─ Face detection
├─ Game logic (scoring, strikes, timing)
├─ HDMI display rendering
└─ Keyboard input (for testing)

Background Threads
├─ Button Thread 1: Start button monitoring (GPIO 17)
├─ Button Thread 2: Pause button monitoring (GPIO 23)
├─ Button Thread 3: Left button monitoring (GPIO 27)
├─ Button Thread 4: Right button monitoring (GPIO 22)
└─ HTTP Thread: Flask web server for monitoring

Thread Safety
├─ Game state: Protected by class-level atomicity (no locks needed for simple vars)
├─ Callbacks: Non-blocking, set state flags for main loop
└─ LED/Button: HardwareController handles synchronization
```

## State Machine

```
                    ┌─────────────┐
                    │    IDLE     │
                    │ Waiting for  │
                    │  Start cmd   │
                    └──────┬──────┘
                           │
                    [START] │ press or ENTER
                           │
                    ┌──────▼──────┐
                    │   START     │
                    │ Initialize  │
                    │    game     │
                    └──────┬──────┘
                           │ (instant)
                    ┌──────▼────────┐
         ┌──────────►   RUNNING     ◄─────────────┐
         │          │ Game logic:   │              │
         │          │ - Face detect │  [PAUSE]     │
         │          │ - Timer check │  press SPACE │
         │          │ - LED flash   │              │
         │   [RESUME]└──────┬───────┘              │
         │          SPACE   │              ┌───────▼──────┐
         │                  │              │   PAUSED     │
         │                  │              │ State frozen │
         │                  └──────────────►  Timer halt  │
         │                 (elapsed time  └──────────────┘
         │                  recorded)      
         │                  │
         │         [Strikes ≥ 3]
         │                  │
         │           ┌──────▼──────┐
         └───────────┤     END     │
           (resume)  │ Game Over   │
                     │ Show score  │
                     │ 3x red LED  │
                     └──────┬──────┘
                            │
                     [START] │ press or ENTER
                            │
                           reset to IDLE
```

## Button Input Flow

```
Hardware Button Press (GPIO)
        ↓
HardwareController._button_monitor_thread()
        ↓
Debounce check (50ms)
        ↓
Invoke registered callback
        ↓
CameraFaceDetector._on_button_XXX()
        ↓
Update game state (non-blocking)
        ↓
Main game loop detects state change
        ↓
Game logic updates accordingly
```

## Game Loop Timing

```
While Running:
├─ Read frame from camera       ~33ms @ 30 FPS
├─ Detect faces                 ~100-300ms
├─ Render HUD                   ~5-10ms
├─ Check timing constraints     <1ms
├─ Update LED feedback          ~200ms (async)
├─ Check keyboard input         <1ms (wait 1ms)
├─ Display on HDMI              ~16ms @ 60 Hz
└─ Total cycle                  ~50-100ms (10-20 FPS output)

Timing Constraints Handled:
├─ Game state frozen when paused (no time accumulation)
├─ Face detection result checked against time threshold
├─ LED flash happens in background thread
├─ HTTP requests don't block main loop
└─ Button presses processed within ~50-100ms
```

## Data Structures

### Game State
```python
class CameraFaceDetector:
    # State Management
    state: GameState              # IDLE, START, RUNNING, PAUSED, END
    paused: bool                  # Pause flag
    game_over: bool               # Game ended
    
    # Scoring
    score: int                    # Current score
    strikes: int                  # Strike count (0-3)
    max_faces: int                # Target face count (1-5)
    current_faces: int            # Detected face count
    
    # Timing
    switch_start_time: float      # Timestamp when round started
    pause_start_time: float       # Timestamp when paused
    paused_time_accumulated: float # Total paused duration
    base_switch_time: float       # Initial 3.0 seconds
    
    # Hardware
    hardware: HardwareController  # GPIO/button/LED control
    monitoring: MonitoringServer  # HTTP API server
```

### Hardware Events
```python
@dataclass
class ButtonEvent:
    button_name: str              # "start", "pause", "left", "right"
    pressed_at: float             # Timestamp of press
```

### Status for Monitoring
```python
@dataclass
class GameStatus:
    state: str                    # Current state value
    score: int                    # Current score
    strikes: int                  # Current strikes (0-3)
    max_faces: int                # Max face target
    current_faces: int            # Current detected faces
    fps: float                    # Frames per second
    switch_time_remaining: float  # Time left in current round
    current_switch_time: float    # Total time for current round
    game_over: bool               # Game ended flag
    timestamp: str                # Current timestamp
    backend: str                  # Detection backend name
```

## LED Feedback Signals

```
Event                          LED Pattern
────────────────────────────────────────────────
Game Start                     🟢 Green flash (2x)
Face Detected (Correct)        🟢 Green flash (1x)
No Face (Strike)               🔴 Red flash (1x)
Game Over (3 Strikes)          🔴 Red flash (3x)
Button Press (Feedback)        🟢 or 🔴 flash
```

## HTTP Monitoring API

```
Endpoint               Method  Purpose
──────────────────────────────────────────────────
/health               GET     Server health check
/game/status          GET     Get full game state
/game/start           POST    Start/restart game
/game/pause           POST    Pause/resume game
/game/max-faces       POST    Adjust max face count
/metrics              GET     Get performance metrics

Example Usage:
  GET /game/status
  Response: {state, score, strikes, fps, ...}
  
  POST /game/pause
  Response: {message: "Game paused/resumed"}
  
  POST /game/max-faces
  Body: {value: 3} or {direction: "up"}
  Response: {message: "Max faces adjusted to 3"}
```

## Performance Characteristics

| Metric | Value | Notes |
|--------|-------|-------|
| Frame Rate | 10-20 FPS display | Full pipeline latency |
| Face Detection | 0.3-0.5s | OpenCV/MediaPipe |
| Button Response | <100ms | Hardware thread + debounce |
| LED Flash | 0.2-0.5s | Configurable duration |
| HTTP Latency | ~50-100ms | Local network |
| Memory Usage | ~100-150 MB | OpenCV + Python runtime |
| CPU Usage | ~40-60% | Single core, Raspberry Pi 4 |

## Configuration

### GPIO Pin Mapping (Raspberry Pi BCM)
```python
PIN_CONFIG = {
    "button_start": 17,      # Press to start game
    "button_left": 27,       # Decrease max faces
    "button_right": 22,      # Increase max faces
    "button_pause": 23,      # Pause/resume
    "led_green": 24,         # Success feedback
    "led_red": 25,           # Error feedback
}
```

### Game Parameters
```python
base_switch_time = 3.0          # Initial 3 seconds per round
min_switch_time = 0.5           # Minimum 0.5 seconds
score_difficulty = 0.1          # Reduces time by 0.1s per score
max_strikes = 3                 # Game ends at 3 strikes
max_faces_limit = (1, 5)        # Face count range
http_port = 5000                # Monitoring API port
button_debounce = 50            # milliseconds
```

## Error Handling

```
GPIO Not Available
├─ Detected at startup
├─ Falls back to simulated mode
├─ Keyboard input enabled for testing
└─ HTTP API still available

Camera Not Available
├─ Raises RuntimeError at startup
├─ Provides debug output
└─ User must fix camera connection

HTTP Port Conflict
├─ Flask prints error message
├─ Game continues without monitoring
└─ Use different port if needed
```

## Deployment Checklist

- [ ] Raspberry Pi with Python 3.8+
- [ ] GPIO pins configured correctly (BCM numbering)
- [ ] Buttons wired with pull-up resistors (or use GPIO.PUD_UP)
- [ ] LEDs with current-limiting resistors (330Ω recommended)
- [ ] Camera module or USB webcam
- [ ] Python dependencies: `pip install -r requirements.txt`
- [ ] Test GPIO: `python -c "import RPi.GPIO as GPIO; print('OK')"`
- [ ] Test camera: `python test_camera_detection.py`
- [ ] Run game: `python face_detector.py`

## Debugging

```bash
# Test GPIO availability
python -c "from hardware_controller import HardwareController; h = HardwareController(use_real_gpio=True); print('GPIO ready')"

# Test HTTP API
curl http://localhost:5000/health
curl http://localhost:5000/game/status

# Enable verbose output
# Modify logging in face_detector.py:
import logging
logging.basicConfig(level=logging.DEBUG)

# Monitor button presses (in test)
python -c "
from hardware_controller import HardwareController
h = HardwareController()
h.register_button_callback('button_start', lambda e: print(f'Start pressed at {e.pressed_at}'))
import time; time.sleep(10)  # Wait for presses
"

# Simulate button press (for testing)
python -c "
from face_detector import CameraFaceDetector
detector = CameraFaceDetector(use_hardware=False)
detector.hardware.simulate_button_press('button_start')
"
```

## Future Enhancements

1. **Countdown Display**: LED sequence for 3-2-1 countdown
2. **Max Faces Validation**: Success only if `detected == max_faces`
3. **Score Multiplier**: Bonus points for fast detections
4. **Difficulty Modes**: Easy/Normal/Hard presets
5. **Leaderboard**: Save high scores to HTTP server
6. **Audio Feedback**: Buzzer/speaker for feedback
7. **Network Streaming**: Stream camera to HTTP endpoint
8. **Configuration UI**: Web dashboard for settings
