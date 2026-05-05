# How to Play — Face Detection Game

## Objective

Show the required number of faces to the camera before the timer runs out. Each successful round scores a point. Miss three rounds and the game ends.

---

## Game Loop

Each round gives you a time window to present the target number of faces to the camera.

- **Timer expires with target met** → +1 score, timer resets, window shrinks
- **Timer expires with target not met** → +1 strike
- **3 strikes** → game over

---

## Difficulty Scaling

The time window shrinks as your score increases:

```
time_limit = 3.0 - (score × 0.1)   minimum: 0.5 seconds
```

| Score | Time limit |
|-------|-----------|
| 0     | 3.0 s     |
| 5     | 2.5 s     |
| 10    | 2.0 s     |
| 25+   | 0.5 s     |

---

## Face Target

The **"SHOW X FACES"** prompt at the top of the screen tells you how many faces must be visible simultaneously to count as a successful round.

- The prompt turns **green** when the current face count meets or exceeds the target
- The right-side panel shows `current / target` under **FACES**
- Adjust the target at any time with **A** (decrease) or **D** (increase), range 1–5

---

## HUD Layout

```
┌─────────────────────────────────────────────────────┐
│ FACE DETECTION / LIVE              BACKEND  MediaPipe │  ← title bar
├──────────────┬──────[ SHOW 2 FACES ]────┬────────────┤
│ STATS        │                          │ GAME       │
│ FPS   30.0   │                          │ SCORE      │
│ FACES  1     │                          │ 0003       │
│ CONF  94%    │                          │ STRIKES    │
│ RES 1280x720 │                          │ 1/3        │
│              │                          │ FACES      │
│              │                          │ 1/2        │
├──────────────┴──────────────────────────┴────────────┤
│              [████████████░░░░░░] 1.8s               │  ← timer bar
│ [Q] quit  [F] fullscreen  [S] snapshot  [SPACE] pause│
└─────────────────────────────────────────────────────┘
```

**Timer bar colours**

| Colour | Remaining |
|--------|-----------|
| Green  | > 30 %    |
| Amber  | 10–30 %   |
| Red    | < 10 %    |

---

## States

```
IDLE ──[ENTER/R]──► RUNNING ◄──[SPACE]──► PAUSED
                       │
                  (3 strikes)
                       │
                      END ──[ENTER/R]──► RUNNING
```

- **IDLE** — live camera shown, waiting to start
- **RUNNING** — game active, timer counting down
- **PAUSED** — timer frozen, score and strikes preserved
- **END** — game over screen with final score

---

## Controls

### Keyboard

| Key | Action |
|-----|--------|
| `ENTER` | Start game (from IDLE or END) |
| `SPACE` | Pause / resume |
| `R` | Restart from any state |
| `A` | Decrease face target (min 1) |
| `D` | Increase face target (max 5) |
| `F` | Toggle fullscreen |
| `S` | Save screenshot |
| `Q` / `ESC` | Quit |

### Hardware Buttons (Raspberry Pi)

| Button | GPIO (BCM) | Action |
|--------|-----------|--------|
| Start  | 17        | Start / restart |
| Pause  | 23        | Pause / resume |
| Left   | 27        | Decrease face target |
| Right  | 22        | Increase face target |

### LED Feedback

| Event | LED |
|-------|-----|
| Game start | Green × 2 flashes |
| Point scored | Green × 1 flash |
| Strike | Red × 1 flash |
| Game over | Red × 3 flashes |

---

## HTTP Monitoring API

When running with `enable_monitoring=True` (default), a REST API is available at `http://localhost:5000`.

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET  | `/health` | Health check |
| GET  | `/game/status` | Full game state snapshot |
| POST | `/game/start` | Start / restart game |
| POST | `/game/pause` | Pause / resume |
| POST | `/game/max-faces` | Set face target (`{"value": 2}` or `{"direction": "up"}`) |
| GET  | `/metrics` | FPS, face count, score |

---

## Launch Options

```python
# Default (hardware + monitoring enabled)
detector = CameraFaceDetector()

# Keyboard-only testing (no GPIO, no Flask)
detector = CameraFaceDetector(use_hardware=False, enable_monitoring=False)

# Specific camera
detector = CameraFaceDetector(camera_id=1)

# Auto-detect first working camera
detector = CameraFaceDetector(auto_detect=True)
```
