# Embedded Face Detection Game - Quick Start Guide

## Installation

### On Raspberry Pi

```bash
# Clone or download the project
cd ~/Embedded-Exercise

# Install dependencies
pip install -r requirements.txt

# Verify GPIO support
python -c "import RPi.GPIO; print('GPIO OK')"

# Verify camera
python test_camera_detection.py
```

### On Testing Machine (Non-Pi)

```bash
# Install without RPi.GPIO (will use simulated mode)
pip install opencv-python mediapipe Flask pytest

# Run tests
python -m pytest test_game_mechanics.py -v

# Test with keyboard input only
python face_detector.py
```

## Hardware Wiring

### Buttons (Connect to GPIO with Pull-up Resistors)

```
GPIO 17 (Pin 11)  ← Start Button     → GND
GPIO 27 (Pin 13)  ← Left Button      → GND
GPIO 22 (Pin 15)  ← Right Button     → GND
GPIO 23 (Pin 16)  ← Pause Button     → GND
```

### LEDs (With 330Ω Current Limiting Resistor)

```
GPIO 24 (Pin 18)  → Resistor → Green LED → GND
GPIO 25 (Pin 22)  → Resistor → Red LED   → GND
```

### Camera

```
Camera CSI Ribbon  → Pi Camera Connector
   OR
USB Camera         → USB Port
```

## Starting the Game

### Direct Launch

```bash
python face_detector.py
```

**Output**:
```
✓ Connected to built-in front camera (ID 0)
✓ Detection backend: mediapipe
  Hotkeys:  [START]=press or ENTER  [PAUSE]=SPACE  [LEFT/RIGHT]=A/D  Q=quit
  HTTP API: http://localhost:5000/game/status

```

### With Specific Settings

```python
# Modify main() in face_detector.py
detector = CameraFaceDetector(
    camera_id=0,              # Or 1 for external USB camera
    use_dnn=True,             # Use high-accuracy backend
    use_hardware=True,        # Enable GPIO (auto-detect)
    enable_monitoring=True,   # Enable HTTP API
    min_detection_confidence=0.6
)
```

## Keyboard Controls (For Testing)

| Key | Action |
|-----|--------|
| **ENTER** | Start/Restart game |
| **SPACE** | Pause/Resume |
| **A** | Decrease max faces |
| **D** | Increase max faces |
| **Q** | Quit |
| **R** | Restart game |
| **F** | Toggle fullscreen |
| **S** | Save screenshot |

## Hardware Buttons (GPIO)

| Button | GPIO | Action |
|--------|------|--------|
| Start | 17 | Start/Restart game (or press ENTER) |
| Pause | 23 | Pause/Resume (or press SPACE) |
| Left | 27 | Decrease max faces (or press A) |
| Right | 22 | Increase max faces (or press D) |

## Game Rules

### Objective
Detect the specified number of faces within the time limit.

### Gameplay
1. **Start**: Press Start button → game begins
2. **Each Round**: 
   - Timer counts down (starts at 3.0 seconds)
   - Show your face(s) to the camera
   - System detects faces
3. **Success**: Correct number detected → +1 score, timer resets
4. **Failure**: Incorrect number → +1 strike, timer resets
5. **Game Over**: 3 strikes → game ends, final score displayed

### Difficulty
- **Score 0**: 3.0 seconds per round (easiest)
- **Score 5**: 2.5 seconds per round
- **Score 10**: 2.0 seconds per round
- **Score 25+**: 0.5 seconds per round (hardest)

### Max Faces Target
- Default: 2 faces required
- Adjustable: 1-5 faces using Left/Right buttons
- Round succeeds when detected faces = max faces target

## LED Feedback

| Event | LED Signal | Meaning |
|-------|-----------|---------|
| Round Win | 🟢 Flash | Face count correct! |
| Strike | 🔴 Flash | Wrong face count |
| Game Start | 🟢 Flash (2x) | Game started |
| Game Over | 🔴 Flash (3x) | Game ended |

## Monitoring via HTTP

### Check Game Status
```bash
curl http://localhost:5000/game/status
```

**Response**:
```json
{
  "state": "running",
  "score": 5,
  "strikes": 1,
  "max_faces": 2,
  "current_faces": 1,
  "fps": 28.5,
  "switch_time_remaining": 1.23,
  "current_switch_time": 2.5,
  "game_over": false,
  "timestamp": 1704067200.123,
  "backend": "mediapipe"
}
```

### Start Game Remotely
```bash
curl -X POST http://localhost:5000/game/start
```

### Pause/Resume
```bash
curl -X POST http://localhost:5000/game/pause
```

### Adjust Max Faces
```bash
# Increase by 1
curl -X POST http://localhost:5000/game/max-faces \
  -H "Content-Type: application/json" \
  -d '{"direction": "up"}'

# Set to specific value
curl -X POST http://localhost:5000/game/max-faces \
  -H "Content-Type: application/json" \
  -d '{"value": 3}'
```

## Troubleshooting

### GPIO Error: "No module named RPi.GPIO"

**On Pi**: Install RPi.GPIO
```bash
pip install RPi.GPIO
```

**On Testing Machine**: Ignore - will use simulated mode
```
⚠ GPIO not available: No module named 'RPi'
  Using simulated GPIO (keyboard fallback available)
```

### Camera Not Found

```bash
# Check available cameras
python test_camera_detection.py

# Try external camera (ID 1)
# Modify main():
detector = CameraFaceDetector(camera_id=1)
detector.start_detection()
```

### Buttons Not Working

1. **Verify GPIO pins**: 
   ```bash
   python -c "import RPi.GPIO as GPIO; GPIO.setmode(GPIO.BCM); GPIO.setup(17, GPIO.IN); print(GPIO.input(17))"
   ```

2. **Check wiring**: Ensure buttons are connected to correct GPIO pins

3. **Test with keyboard**: Use keyboard shortcuts instead

4. **Enable debug output**:
   ```python
   import logging
   logging.basicConfig(level=logging.DEBUG)
   ```

### Frame Rate Too Low

1. **Switch backends**:
   ```python
   detector = CameraFaceDetector(use_dnn=False)  # Use Haar Cascade
   ```

2. **Reduce resolution**:
   ```python
   # In start_detection():
   self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
   self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
   ```

3. **Check CPU usage**: `top` command

## Testing

### Run All Tests
```bash
python -m pytest -v
```

### Run Game Mechanics Tests Only
```bash
python -m pytest test_game_mechanics.py -v
```

### Test with Coverage Report
```bash
python -m pytest --cov=face_detector --cov=hardware_controller --cov=monitoring_server --cov-report=html
# Open htmlcov/index.html in browser
```

## Performance Optimization

### For Raspberry Pi 4
- Use MediaPipe backend (GPU acceleration)
- Resolution: 1280×720 @ 30 FPS typical
- CPU usage: 40-60% single core

### For Raspberry Pi 3
- Use Haar Cascade backend (faster)
- Resolution: 640×480 @ 15-20 FPS
- CPU usage: 70-80% single core

### Benchmarking
```bash
# Add to start_detection() to profile
import cProfile
cProfile.run('detector.start_detection()', sort='cumtime')
```

## Configuration Files

### Modify Game Parameters
Edit `face_detector.py`:
```python
self.base_switch_time = 3.0    # Initial round time (seconds)
self.max_faces = 2              # Default max face target
```

### Modify GPIO Pins
Edit `hardware_controller.py`:
```python
self.PIN_CONFIG = {
    "button_start": 17,   # Change GPIO pin numbers as needed
    "button_left": 27,
    "button_right": 22,
    "button_pause": 23,
    "led_green": 24,
    "led_red": 25,
}
```

### Change HTTP Port
```python
detector = CameraFaceDetector()
detector.monitoring = MonitoringServer(port=8000)  # Use port 8000
```

## Examples

### Simple Game
```python
from face_detector import CameraFaceDetector

game = CameraFaceDetector(
    camera_id=0,
    use_hardware=False,  # Keyboard only for testing
    enable_monitoring=False  # No HTTP API
)
game.start_detection()  # Start keyboard-based game
```

### Professional Deployment
```python
from face_detector import CameraFaceDetector

game = CameraFaceDetector(
    camera_id=0,
    use_dnn=True,        # High accuracy
    use_hardware=True,   # GPIO buttons & LEDs
    enable_monitoring=True  # HTTP monitoring
)
game.start_detection()  # Full production setup
```

### Simulated Testing
```python
from face_detector import CameraFaceDetector

game = CameraFaceDetector(
    camera_id=0,
    use_hardware=False,  # No GPIO
    enable_monitoring=False  # No network
)

# Simulate button presses
game.hardware.simulate_button_press('button_start')
game.hardware.flash_led(LEDColor.GREEN, duration=0.2, count=1)
```

## Support

For issues or questions:
1. Check [SYSTEM_ARCHITECTURE.md](SYSTEM_ARCHITECTURE.md) for detailed design
2. See [REQUIREMENTS_ALIGNMENT.md](REQUIREMENTS_ALIGNMENT.md) for specifications
3. Review test files for usage examples
4. Enable debug logging for troubleshooting

## Next Steps

- [ ] Wire up hardware buttons and LEDs
- [ ] Test GPIO connectivity
- [ ] Run game on Raspberry Pi
- [ ] Monitor via HTTP API
- [ ] Adjust difficulty parameters
- [ ] Deploy as systemd service
