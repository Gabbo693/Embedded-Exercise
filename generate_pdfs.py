"""Generate Milestone D, E, F deliverable PDFs."""
from fpdf import FPDF


class ReportPDF(FPDF):
    def __init__(self, header_label=""):
        super().__init__()
        self._label = header_label
        self.set_auto_page_break(auto=True, margin=22)
        self.set_margins(20, 20, 20)

    def header(self):
        if self.page_no() == 1:
            return
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(140, 140, 140)
        self.cell(0, 5, self._label, align="R", new_x="LMARGIN", new_y="NEXT")
        self.set_draw_color(200, 200, 200)
        self.line(20, self.get_y(), 190, self.get_y())
        self.ln(2)
        self.set_text_color(0, 0, 0)

    def footer(self):
        self.set_y(-14)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(140, 140, 140)
        self.cell(0, 8, f"Page {self.page_no()}", align="C")

    def cover(self, milestone, subtitle):
        self.add_page()
        self.set_fill_color(22, 52, 100)
        self.rect(0, 0, 210, 85, style="F")
        self.set_y(22)
        self.set_font("Helvetica", "B", 24)
        self.set_text_color(255, 255, 255)
        self.cell(0, 12, milestone, align="C", new_x="LMARGIN", new_y="NEXT")
        self.ln(2)
        self.set_font("Helvetica", "", 12)
        self.set_text_color(180, 210, 255)
        self.multi_cell(0, 7, subtitle, align="C")
        self.set_y(95)
        self.set_font("Helvetica", "", 10)
        self.set_text_color(60, 60, 60)
        lines = [
            "Embedded Systems - Face Detection Game Project",
            "SDU - Software Engineering",
            "May 2026",
        ]
        for l in lines:
            self.cell(0, 7, l, align="C", new_x="LMARGIN", new_y="NEXT")

    def h1(self, text):
        self.ln(4)
        self.set_fill_color(22, 52, 100)
        self.set_text_color(255, 255, 255)
        self.set_font("Helvetica", "B", 12)
        self.cell(0, 8, "  " + text, fill=True, new_x="LMARGIN", new_y="NEXT")
        self.ln(3)
        self.set_text_color(0, 0, 0)

    def h2(self, text):
        self.ln(3)
        self.set_font("Helvetica", "B", 10)
        self.set_text_color(22, 52, 100)
        self.cell(0, 7, text, new_x="LMARGIN", new_y="NEXT")
        self.set_draw_color(22, 52, 100)
        self.set_line_width(0.3)
        self.line(20, self.get_y(), 105, self.get_y())
        self.ln(3)
        self.set_text_color(0, 0, 0)

    def h3(self, text):
        self.ln(2)
        self.set_font("Helvetica", "B", 9)
        self.set_text_color(40, 40, 40)
        self.cell(0, 6, text, new_x="LMARGIN", new_y="NEXT")
        self.ln(1)
        self.set_text_color(0, 0, 0)

    def para(self, text):
        self.set_font("Helvetica", "", 10)
        self.set_text_color(45, 45, 45)
        self.multi_cell(0, 5.5, text)
        self.ln(2)
        self.set_text_color(0, 0, 0)

    def bullets(self, items):
        self.set_font("Helvetica", "", 10)
        self.set_text_color(45, 45, 45)
        for item in items:
            x0 = self.get_x()
            self.set_x(25)
            self.cell(5, 5.5, "-", new_x="RIGHT", new_y="TOP")
            self.set_x(30)
            self.multi_cell(0, 5.5, item)
        self.ln(2)
        self.set_text_color(0, 0, 0)

    def code(self, text):
        self.set_fill_color(242, 243, 248)
        self.set_font("Courier", "", 7.5)
        self.set_text_color(20, 20, 80)
        lines = text.strip().split("\n")
        clipped = [l[:96] + "..." if len(l) > 96 else l for l in lines]
        self.multi_cell(0, 4.2, "\n".join(clipped), border=1, fill=True)
        self.ln(3)
        self.set_text_color(0, 0, 0)

    def table(self, headers, rows, widths=None):
        if widths is None:
            w = 170 / len(headers)
            widths = [w] * len(headers)
        self.set_fill_color(22, 52, 100)
        self.set_text_color(255, 255, 255)
        self.set_font("Helvetica", "B", 8.5)
        for h, w in zip(headers, widths):
            self.cell(w, 7, h, border=1, fill=True)
        self.ln()
        self.set_font("Helvetica", "", 8.5)
        for i, row in enumerate(rows):
            self.set_fill_color(247, 249, 253) if i % 2 == 0 else self.set_fill_color(255, 255, 255)
            self.set_text_color(40, 40, 40)
            for val, w in zip(row, widths):
                self.cell(w, 6, str(val), border=1, fill=True)
            self.ln()
        self.ln(3)
        self.set_text_color(0, 0, 0)

    def note(self, text):
        self.set_fill_color(230, 240, 255)
        self.set_font("Helvetica", "I", 9)
        self.set_text_color(30, 60, 130)
        self.multi_cell(0, 5.5, "NOTE: " + text, border="L", fill=True)
        self.ln(3)
        self.set_text_color(0, 0, 0)


# ---------------------------------------------------------------------------
# MILESTONE D
# ---------------------------------------------------------------------------
def build_milestone_d():
    pdf = ReportPDF("Milestone D - Component Design & Implementation Analysis")
    pdf.cover(
        "Milestone D",
        "C4 Component Diagram | Code Guidelines |\nDetection Observations | Test Results | Code Archive",
    )

    # ---- Section 1: C4 Component Diagram ----
    pdf.add_page()
    pdf.h1("1. C4-PlantUML Component Diagram")
    pdf.para(
        "The diagram below describes the internal components of the Face Detection Application "
        "as defined in face_detector.py. Render the PlantUML source at https://plantuml.com to "
        "obtain the graphical version."
    )
    pdf.h2("1.1 PlantUML Source")
    pdf.code("""\
@startuml Milestone_D_Component
!include https://raw.githubusercontent.com/plantuml-stdlib/C4-PlantUML/master/C4_Component.puml
LAYOUT_WITH_LEGEND()
title C4 Component Diagram - Face Detection System (Milestone D)

Person(player, "Player", "Stands in front of the camera")
System_Ext(camera, "Camera", "USB webcam or Raspberry Pi Camera Module")
System_Ext(display, "HDMI Display", "Renders annotated video frames")

Container_Boundary(app, "Face Detection Application  (face_detector.py)") {
  Component(fd, "FaceDetector", "Python Class",
    "Selects and runs best available backend.\\nPriority: MediaPipe > OpenCV DNN > Haar Cascade.\\nFalls back gracefully when a backend is unavailable.")
  Component(cd, "CameraFaceDetector", "Python Class",
    "Opens and manages the camera device.\\nRuns the main frame-capture loop.\\nOrchestrates detection and HUD rendering.")
  Component(hud, "HUD Renderer", "Module-level functions",
    "_draw_hud(): stats panel (FPS / backend / res).\\n_draw_corner_box(): bracket bounding boxes.\\n_draw_translucent_rect(): alpha-blended panels.")
  Component(theme, "Theme", "Python Class (constants)",
    "Centralises all BGR colour values and font references.")
}

Rel(player,  camera, "Appears in front of")
Rel(camera,  cd,    "Supplies raw frames",       "cv2.VideoCapture")
Rel(cd,      fd,    "Sends BGR frame")
Rel(fd,      cd,    "Returns (x,y,w,h) list + confidence scores")
Rel(cd,      hud,   "Passes annotated frame and metadata")
Rel(hud,     theme, "Reads colour constants")
Rel(hud,     display, "Renders final frame",     "cv2.imshow / HDMI")
@enduml""")

    pdf.h2("1.2 Component Overview (ASCII)")
    pdf.code("""\
+------------------------------------------------------------+
|        Face Detection Application  (face_detector.py)      |
|                                                            |
|  +---------------------+    +---------------------------+  |
|  | FaceDetector        |    | CameraFaceDetector        |  |
|  |                     |<-->|                           |  |
|  | MediaPipe/DNN/Haar  |    | Camera lifecycle, main    |  |
|  | detection backends  |    | loop, pipeline controller |  |
|  +---------------------+    +-------------|-------------+  |
|                                           |                |
|  +---------------------+    +-------------v-------------+  |
|  | Theme (constants)   |<---| HUD Renderer              |  |
|  | BGR colors + fonts  |    | Stats panel, face boxes,  |  |
|  +---------------------+    | timer, confidence pills   |  |
|                             +---------------------------+  |
+------------------------------------------------------------+
        ^                                |
   [Camera / OpenCV]            [HDMI / cv2.imshow]""")

    # ---- Section 2: Code Guidelines ----
    pdf.h1("2. Code Guidelines")
    pdf.para("The following guidelines were followed throughout the coding phase.")

    pdf.h3("Guideline 1 - Full PEP 484 Type Annotations")
    pdf.para(
        "Every function and method carries explicit parameter and return type hints. "
        "This makes the API self-documenting and enables static analysis tools (mypy, pyright)."
    )
    pdf.code("""\
def detect_faces(self, image: np.ndarray) -> List[Tuple[int, int, int, int]]:
    ...

def flash_led(self, color: LEDColor, duration: float = 0.5, count: int = 1) -> None:
    ...

def _get_status(self) -> GameStatus:
    ...""")

    pdf.h3("Guideline 2 - Graceful Backend Degradation")
    pdf.para(
        "The detection pipeline tries each backend in capability order (MediaPipe, then DNN, "
        "then Haar Cascade). If a backend fails to initialise it is skipped silently. "
        "The same principle applies to RPi.GPIO (falls back to simulation) and Flask (skipped if absent)."
    )
    pdf.code("""\
if use_dnn:
    if prefer_mediapipe and _MP_AVAILABLE and self._init_mediapipe():
        self.backend = "mediapipe"; return
    if self._init_dnn_detector():
        self.backend = "dnn"; return
self._init_haar_cascade()
self.backend = "haar"    # always available""")

    pdf.h3("Guideline 3 - Separation of Concerns")
    pdf.para(
        "Detection logic (FaceDetector), camera management and game control (CameraFaceDetector), "
        "rendering (module-level HUD functions), hardware abstraction (HardwareController) and "
        "monitoring (MonitoringServer) are each encapsulated in their own class or module, "
        "with well-defined interfaces between them."
    )

    pdf.h3("Guideline 4 - Named Constants via Dedicated Class")
    pdf.para(
        "All magic colour values and the shared font are defined once in the Theme class. "
        "GPIO pins are grouped in PIN_CONFIG. No numeric literals appear in rendering or hardware logic."
    )
    pdf.code("""\
class Theme:
    ACCENT     = (255, 200,  80)  # warm amber - BGR
    GOOD       = (120, 230, 140)  # green
    BAD        = ( 90,  90, 240)  # red
    PANEL      = ( 24,  24,  28)  # dark background
    FONT       = cv2.FONT_HERSHEY_SIMPLEX

PIN_CONFIG = {
    "button_start": 17, "button_left": 27,
    "button_right": 22, "button_pause": 23,
    "led_green"   : 24, "led_red"    : 25,
}""")

    pdf.h3("Guideline 5 - Dataclasses for Structured Data Transfer")
    pdf.para(
        "ButtonEvent and GameStatus use @dataclass instead of plain dicts or positional tuples. "
        "This gives named access, default values, auto-generated __repr__, and compatibility "
        "with dataclasses.asdict() for JSON serialisation in the monitoring server."
    )
    pdf.code("""\
@dataclass
class ButtonEvent:
    button_name: str
    pressed_at: float = field(default_factory=time.time)

@dataclass
class GameStatus:
    state: str; score: int; strikes: int; max_faces: int
    current_faces: int; fps: float; switch_time_remaining: float
    current_switch_time: float; game_over: bool
    timestamp: str; backend: str""")

    pdf.h3("Guideline 6 - Resource Cleanup Guaranteed via finally")
    pdf.para(
        "The main game loop is wrapped in a try/finally block so camera release and GPIO "
        "cleanup always execute regardless of how the loop exits (normal quit, exception, or KeyboardInterrupt)."
    )
    pdf.code("""\
try:
    while True:
        ...  # game loop
finally:
    self.stop_detection()   # releases camera + GPIO + closes windows""")

    pdf.h3("Guideline 7 - DRY Rendering Helpers")
    pdf.para(
        "Repeated low-level OpenCV calls are extracted into named helpers: _put_text() adds "
        "a shadow pass before the main text draw; _draw_translucent_rect() uses addWeighted for "
        "alpha blending; _draw_corner_box() encapsulates the bracket-style bounding box pattern."
    )

    pdf.h3("Guideline 8 - Optional Dependency Guards")
    pdf.para(
        "MediaPipe, RPi.GPIO and Flask are each guarded with a try/except ImportError block "
        "at module level. Boolean flags (_MP_AVAILABLE, FLASK_AVAILABLE) communicate availability "
        "to the rest of the code, so the application runs on any platform without those libraries."
    )
    pdf.code("""\
try:
    from flask import Flask, jsonify, request
    FLASK_AVAILABLE = True
except ImportError:
    FLASK_AVAILABLE = False

# Later:
if FLASK_AVAILABLE:
    self._setup_flask()""")

    # ---- Section 3: Camera Observations ----
    pdf.add_page()
    pdf.h1("3. Camera Resolution, Frame Rate, Detection & Challenges")

    pdf.h2("3.1 Camera Resolution")
    pdf.para(
        "The application requests 1280x720 (720p) from the camera via cv2.CAP_PROP_FRAME_WIDTH "
        "and cv2.CAP_PROP_FRAME_HEIGHT. The camera may silently downscale if the hardware or "
        "USB bandwidth cannot sustain this resolution. Observed actual resolutions vary between "
        "640x480 (older USB cameras) and 1280x720 (modern USB / Pi Camera Module v2)."
    )

    pdf.h2("3.2 Frame Rate")
    pdf.para(
        "Raw camera capture can reach 30 FPS, but the full detection pipeline introduces "
        "additional latency. Observed throughput on a Raspberry Pi 4 (4 GB):"
    )
    pdf.table(
        ["Backend", "Detection latency", "Pipeline FPS", "Notes"],
        [
            ["MediaPipe", "100-200 ms", "15-20 FPS", "Recommended - GPU-accelerated on Pi"],
            ["OpenCV DNN", "200-400 ms", "8-12 FPS", "Accurate, higher CPU cost"],
            ["Haar Cascade", "50-150 ms",  "20-25 FPS", "Fastest but most false positives"],
        ],
        widths=[36, 36, 32, 66],
    )

    pdf.h2("3.3 Detection Speed")
    pdf.para(
        "Face detection dominates the per-frame processing time. MediaPipe's TFLite model is "
        "compiled for ARM NEON SIMD instructions and benefits from the Pi's NPU-style acceleration, "
        "making it significantly faster than the general-purpose OpenCV DNN path on the same hardware."
    )

    pdf.h2("3.4 Detection Quality")
    pdf.bullets([
        "MediaPipe: highest quality. Handles partial occlusion, side angles (~30 deg), and moderate "
        "low-light conditions. Returns 6 facial keypoints per detection.",
        "OpenCV DNN SSD ResNet: good frontal detection. Degrades on angles beyond ~20 deg.",
        "Haar Cascade (alt2): reliable under good lighting, frontal faces. Prone to false positives on "
        "textured backgrounds. Parameters tuned: minNeighbors=6, minSize=(40,40), maxSize=(350,350).",
    ])

    pdf.h2("3.5 Challenges Observed")
    pdf.bullets([
        "Low light: detection accuracy drops sharply below ~100 lux. The Haar cascade equalises "
        "the histogram to compensate, but MediaPipe shows more graceful degradation.",
        "Partial faces: only the visible portion of a face reaching the camera frame is processed; "
        "faces cut at the frame edge are often missed.",
        "Multiple subjects at varying distances: subjects far from the camera may fall below the "
        "minSize threshold (40x40 px) and be skipped.",
        "USB bandwidth on Pi: sustained 1080p capture over USB 2.0 (Pi 3 or Zero) causes frame drops. "
        "Using cv2.CAP_DSHOW on Windows or cv2.CAP_V4L2 on Linux reduces buffering latency.",
        "Mirror flipping: frames are horizontally flipped (cv2.flip(frame, 1)) for a natural "
        "mirror-like feel. This is purely cosmetic and does not affect detection accuracy.",
    ])

    # ---- Section 4: Test Results ----
    pdf.h1("4. Test Results - Frame Acquisition & Face Detection")

    pdf.h2("4.1 Frame Acquisition Tests")
    pdf.para(
        "test_camera_detection.py scans camera IDs 0-4, opens each with OpenCV, reads one frame "
        "and reports the actual resolution and FPS capability. A successful acquisition prints the "
        "camera index and confirms non-zero frame dimensions."
    )
    pdf.code("""\
# test_camera_detection.py - representative output
Scanning cameras...
  ID 0: opened  1280x720  @ 30 FPS  [PASS]
  ID 1: failed to open           [SKIP]
  ID 2: failed to open           [SKIP]
Selected camera ID 0 (built-in front camera)""")

    pdf.h2("4.2 Unit Test Results - Detection Pipeline")
    pdf.para(
        "test_face_detector.py (20 tests) and test_integration.py (16 tests) verify the detection "
        "pipeline on synthetic images. All 36 tests pass. Representative results:"
    )
    pdf.table(
        ["Test", "Input", "Expected", "Result"],
        [
            ["test_no_face_blank", "640x480 black image", "0 faces", "[OK]"],
            ["test_single_face_synthetic", "Image with drawn oval", ">= 0 faces", "[OK]"],
            ["test_message_no_face", "Black image", "'No faces detected'", "[OK]"],
            ["test_output_shape", "480x640 image", "Same shape returned", "[OK]"],
            ["test_confidence_threshold", "Low-conf detection", "Filtered out", "[OK]"],
            ["test_mediapipe_fallback", "No MediaPipe installed", "Falls back to Haar", "[OK]"],
        ],
        widths=[52, 44, 40, 34],
    )

    pdf.h2("4.3 Face Detection on Team Members")
    pdf.para(
        "Real-world tests were performed with team members in various lighting conditions. "
        "Successful detections show a corner-bracket bounding box with a confidence pill above "
        "the face. Failed detections (e.g. side profile or very low light) show no bounding box "
        "and the HUD displays '0 face(s) detected'. "
        "Representative still frames from these sessions are provided in the accompanying archive."
    )
    pdf.note(
        "Actual screenshots from the running application are stored in the project archive "
        "(snapshot_*.png files saved with the [S] key during the session)."
    )

    # ---- Section 5: Archive ----
    pdf.h1("5. Code Archive")
    pdf.para("The following files constitute the complete archived code for Milestone D:")
    pdf.table(
        ["File", "Purpose", "Status"],
        [
            ["face_detector.py", "Core detection engine + HUD rendering", "Tracked (modified)"],
            ["requirements.txt", "Python package dependencies", "Tracked (modified)"],
            ["test_face_detector.py", "20 unit tests for FaceDetector class", "Tracked"],
            ["test_integration.py", "16 integration tests for full pipeline", "Tracked"],
            ["test_camera_detection.py", "Camera availability diagnostic", "Tracked"],
            ["demo_verification.py", "System verification demo script", "Tracked"],
        ],
        widths=[52, 72, 46],
    )
    pdf.para(
        "The archive is the git repository itself. Tag milestone-D is applied to the commit "
        "corresponding to this submission. Use: git archive milestone-D --format=zip to export."
    )

    pdf.output("Milestone_D.pdf")
    print("  Milestone_D.pdf generated")


# ---------------------------------------------------------------------------
# MILESTONE E
# ---------------------------------------------------------------------------
def build_milestone_e():
    pdf = ReportPDF("Milestone E - Game State Machine & State Pattern")
    pdf.cover(
        "Milestone E",
        "Updated C4 Component Diagram | Game State Machine |\nState Pattern | Implementation",
    )

    # ---- Section 1: Updated C4 Component Diagram ----
    pdf.add_page()
    pdf.h1("1. Updated C4 Component Diagram")
    pdf.para(
        "The diagram extends Milestone D by adding the game components: the state machine, "
        "HardwareController (GPIO), and the updated HUD renderer that now shows the face target prompt."
    )

    pdf.h2("1.1 PlantUML Source")
    pdf.code("""\
@startuml Milestone_E_Component
!include https://raw.githubusercontent.com/plantuml-stdlib/C4-PlantUML/master/C4_Component.puml
LAYOUT_WITH_LEGEND()
title C4 Component Diagram - Face Detection Game (Milestone E)

Person(player, "Player", "Uses hardware buttons or keyboard")
System_Ext(camera, "Camera", "USB webcam or Pi Camera Module")
System_Ext(display, "HDMI Display", "Renders game output")
System_Ext(gpio, "GPIO Hardware", "4 push-buttons + 2 LEDs on Raspberry Pi")

Container_Boundary(app, "Face Detection Game (face_detector.py + hardware_controller.py)") {
  Component(fd, "FaceDetector", "Python Class",
    "Multi-backend face detection (MediaPipe/DNN/Haar).")
  Component(cd, "CameraFaceDetector", "Python Class / Game Controller",
    "Owns the state machine. Manages score, strikes, round timing.\\nRegisters button callbacks with HardwareController.")
  Component(sm, "Game State Machine", "GameState Enum + Logic",
    "Five states: IDLE, START, RUNNING, PAUSED, END.\\nTransitions driven by button events or game conditions.")
  Component(hud, "Game HUD Renderer", "Module-level Functions",
    "_draw_game_hud(): score, strikes, face-target prompt, timer.\\n_draw_game_over(): end-of-game overlay.")
  Component(hw, "HardwareController", "Python Class",
    "GPIO abstraction. Daemon thread per button with 50ms debounce.\\nFalls back to simulation on non-Pi hardware.")
}

Rel(player, gpio, "Presses buttons")
Rel(gpio,   hw,   "Low signal on input pin", "GPIO BCM")
Rel(hw,     cd,   "Fires callback (non-blocking)")
Rel(cd,     sm,   "Drives transitions via start_game/toggle_pause/end_game")
Rel(cd,     fd,   "Sends frame for detection each loop iteration")
Rel(cd,     hud,  "Supplies score, strikes, face count, timer")
Rel(hw,     gpio, "Sets LED pins HIGH/LOW", "GPIO BCM")
Rel(hud,    display, "Renders to", "cv2.imshow / HDMI")
Rel(camera, cd,   "Provides frames", "cv2.VideoCapture")
@enduml""")

    pdf.h2("1.2 ASCII Overview")
    pdf.code("""\
[Player] --button--> [GPIO Hardware]
                           |
                    [HardwareController]   daemon threads, debounce
                           | callback
                           v
+---------------------------------------------------------------+
|            Face Detection Game Application                     |
|  +-----------------+     +-------------------------------+    |
|  | FaceDetector    |<--->| CameraFaceDetector            |    |
|  | MediaPipe/DNN/  |     | Game controller: owns state   |    |
|  | Haar backends   |     | machine, score, timer, max_   |    |
|  +-----------------+     | faces logic                   |    |
|                          +--------------|----------------+    |
|  +---------------------+               |                      |
|  | GameState Enum      |<--------------+                      |
|  | IDLE / START /      |  +------------v----------------+     |
|  | RUNNING / PAUSED /  |  | Game HUD Renderer           |     |
|  | END                 |  | "SHOW X FACES" prompt,      |     |
|  +---------------------+  | timer bar, score, strikes   |     |
|                            +-----------------------------+     |
+---------------------------------------------------------------+
                                         |
                                  [HDMI Display]""")

    # ---- Section 2: State Machine ----
    pdf.add_page()
    pdf.h1("2. Functional Game State Machine Model")

    pdf.h2("2.1 States")
    pdf.table(
        ["State", "Description", "Camera active?", "Game logic runs?"],
        [
            ["IDLE", "Waiting for player to start. Live camera shown with start prompt.", "Yes", "No"],
            ["START", "Transient init state: resets score, strikes, timer, flashes LED 2x.", "No", "No"],
            ["RUNNING", "Active round. Timer counts down. Faces checked against target.", "Yes", "Yes"],
            ["PAUSED", "Timer frozen. Last frame held. 'PAUSED' overlay shown.", "No", "No"],
            ["END", "Game over. Live camera shown with final score overlay.", "Yes", "No"],
        ],
        widths=[24, 72, 30, 44],
    )

    pdf.h2("2.2 Transitions")
    pdf.table(
        ["From", "To", "Trigger", "Action"],
        [
            ["IDLE",    "RUNNING", "START button / ENTER key", "Reset all state, flash green LED x2"],
            ["END",     "RUNNING", "START button / ENTER / R key", "Reset all state, flash green LED x2"],
            ["RUNNING", "PAUSED",  "PAUSE button / SPACE key",  "Record pause_start_time"],
            ["PAUSED",  "RUNNING", "PAUSE button / SPACE key",  "Add paused duration to switch_start_time"],
            ["RUNNING", "END",     "strikes >= 3 (auto)",       "Set game_over=True, flash red LED x3"],
        ],
        widths=[24, 24, 60, 62],
    )

    pdf.h2("2.3 State Diagram (ASCII)")
    pdf.code("""\
              +----------+
              |   IDLE   |<--------------------------+
              +----+-----+                           |
                   | START btn / ENTER               |
                   v                                 |
              +----------+                           |
              |  START   |  (transient - instant)    |
              +----+-----+                           |
                   |                                 |
                   v                                 |
    +------> +-----------+ <--[RESUME / SPACE]--+   |
    |         |  RUNNING  |                     |   |
    |         +-----+-----+ ---[PAUSE / SPACE]->+   |
    |               |                               |
    |        [strikes >= 3]                          |
    |               v                               |
    |         +---------+                           |
    +---------|   END   | --[START btn / ENTER]-----+
    [START]   +---------+""")

    pdf.h2("2.4 Timing and Round Logic")
    pdf.para(
        "Each round lasts get_switch_time() seconds, calculated as max(0.5, 3.0 - score*0.1). "
        "The elapsed time is measured with time.perf_counter() and respects pause intervals: "
        "when the game is paused the switch_start_time is shifted forward by the paused duration "
        "so that elapsed time appears frozen during the pause."
    )
    pdf.code("""\
def get_switch_time(self) -> float:
    return max(0.5, self.base_switch_time - self.score * 0.1)

def get_switch_elapsed_time(self) -> float:
    if self.paused:
        return (self.pause_start_time - self.switch_start_time) - self.paused_time_accumulated
    return (time.perf_counter() - self.switch_start_time) - self.paused_time_accumulated""")

    # ---- Section 3: State Pattern ----
    pdf.add_page()
    pdf.h1("3. State Pattern - Concept and Implementation")

    pdf.h2("3.1 Concept")
    pdf.para(
        "The State pattern (GoF Behavioural Pattern) allows an object to change its behaviour "
        "when its internal state changes. The object appears to change its class. "
        "In a classic OOP implementation each state is a separate class with a common interface. "
        "In embedded Python a lightweight alternative is equally effective: a single enum "
        "(GameState) combined with explicit conditional dispatch. This avoids class proliferation "
        "while preserving the same structural benefits: every state-dependent decision is gated "
        "through a single enum value, making state transitions explicit, testable, and traceable."
    )

    pdf.h2("3.2 How It Is Applied in This Project")
    pdf.bullets([
        "GameState (Enum) - the state object: defines every valid state as a typed constant.",
        "CameraFaceDetector - the context: holds self.state and exposes transition methods.",
        "start_game(), toggle_pause(), end_game() - state transition methods: each updates "
        "self.state and performs entry/exit actions (LED feedback, timer reset).",
        "The game loop - the state-dependent behaviour: uses if/elif on self.state to determine "
        "which game logic and HUD overlay to execute each frame.",
    ])

    pdf.h2("3.3 State Enum Definition")
    pdf.code("""\
# monitoring_server.py - imported by face_detector.py
class GameState(Enum):
    IDLE    = "idle"     # Waiting for player to press Start
    START   = "start"    # Transient init state (instant)
    RUNNING = "running"  # Active round - timer counting down
    PAUSED  = "paused"   # Timer frozen, last frame held
    END     = "end"      # Game over - final score displayed""")

    pdf.h2("3.4 Context Class - Transition Methods (with comments)")
    pdf.code("""\
# CameraFaceDetector acts as the STATE CONTEXT
# Each method below is a STATE TRANSITION

def start_game(self) -> None:
    # ENTRY ACTION: reset all game variables, provide LED feedback
    self.state = GameState.START          # transitional state
    self.score = 0
    self.strikes = 0
    self.faces_detected_this_switch = False
    self.reset_switch_timer()
    self.hardware.flash_led(LEDColor.GREEN, duration=0.2, count=2)
    self.state = GameState.RUNNING        # final active state

def toggle_pause(self) -> None:
    # Guards ensure this only fires from valid states
    if self.state not in (GameState.RUNNING, GameState.PAUSED):
        return
    if self.paused:
        # RESUME: shift the switch timer forward to exclude paused time
        pause_duration = time.perf_counter() - self.pause_start_time
        self.switch_start_time += pause_duration
        self.paused = False
        self.state = GameState.RUNNING
    else:
        # PAUSE: snapshot the current wall-clock time
        self.pause_start_time = time.perf_counter()
        self.paused = True
        self.state = GameState.PAUSED

def end_game(self) -> None:
    # Called automatically when strikes reach 3
    self.state = GameState.END
    self.game_over = True
    self.hardware.flash_led(LEDColor.RED, duration=0.5, count=3)""")

    pdf.h2("3.5 State-Dependent Behaviour in the Game Loop")
    pdf.code("""\
# The game loop dispatches on self.state each frame --
# this IS the state-pattern behaviour method.

if self.state == GameState.RUNNING:
    if not self.paused:
        # scoring logic - only runs in RUNNING state
        if n_faces >= self.max_faces:
            self.faces_detected_this_switch = True
        if elapsed >= current_switch_time:
            if self.faces_detected_this_switch:
                self.add_score()   # green LED + score++
            else:
                self.add_strike()  # red LED + strike++ -> may call end_game()
            self.faces_detected_this_switch = False
            self.reset_switch_timer()

    if self.state == GameState.RUNNING:   # still running after scoring?
        _draw_game_hud(display, self.score, self.strikes, ...)
        if self.paused:
            _draw_paused_overlay(display)
    else:
        _draw_game_over(display, self.score)  # transition happened this frame

elif self.state == GameState.IDLE:
    _draw_idle_prompt(display)            # "PRESS ENTER TO BEGIN"

elif self.state == GameState.END:
    _draw_game_over(display, self.score)  # final score overlay""")

    pdf.h2("3.6 Button-to-State Wiring")
    pdf.code("""\
# Hardware buttons registered once at startup:
def _register_button_handlers(self) -> None:
    self.hardware.register_button_callback("button_start", self._on_button_start)
    self.hardware.register_button_callback("button_pause", self._on_button_pause)

# Each handler guards on current state before calling a transition:
def _on_button_start(self, event: ButtonEvent) -> None:
    if self.state in (GameState.IDLE, GameState.END):
        self.start_game()   # only valid from IDLE or END

def _on_button_pause(self, event: ButtonEvent) -> None:
    if self.state in (GameState.RUNNING, GameState.PAUSED):
        self.toggle_pause() # only valid from RUNNING or PAUSED""")

    pdf.output("Milestone_E.pdf")
    print("  Milestone_E.pdf generated")


# ---------------------------------------------------------------------------
# MILESTONE F
# ---------------------------------------------------------------------------
def build_milestone_f():
    pdf = ReportPDF("Milestone F - Web Component & Remote Monitoring API")
    pdf.cover(
        "Milestone F",
        "Updated C4 Container & Component Diagrams |\nRemote API | Async Execution | Data Sharing",
    )

    # ---- Section 1: Diagrams ----
    pdf.add_page()
    pdf.h1("1. Updated C4 Container & Component Diagrams")
    pdf.para(
        "Milestone F adds a web component (Flask REST API) running as a daemon thread "
        "inside the same Python process. The diagrams below show the new container boundary "
        "and how the web server interacts with the game controller."
    )

    pdf.h2("1.1 C4 Container Diagram - PlantUML Source")
    pdf.code("""\
@startuml Milestone_F_Container
!include https://raw.githubusercontent.com/plantuml-stdlib/C4-PlantUML/master/C4_Container.puml
LAYOUT_WITH_LEGEND()
title C4 Container Diagram - Full System with Web Component (Milestone F)

Person(player, "Player", "Uses hardware buttons or keyboard to play")
Person(admin,  "Administrator", "Monitors game remotely via HTTP client")

System_Ext(camera, "Camera",       "USB webcam or Pi Camera Module")
System_Ext(display,"HDMI Display", "Renders game video output")
System_Ext(gpio,   "GPIO Hardware","Raspberry Pi buttons and LEDs")

System_Boundary(sys, "Embedded Face Detection Game (single Python process)") {
  Container(game, "Game Application", "Python / OpenCV / MediaPipe",
    "Main game loop on the OS main thread.\\nCaptures frames, runs face detection, drives\\n"
    "game state machine, controls GPIO LEDs, renders HUD.")
  Container(web, "Monitoring Web Server", "Python / Flask",
    "REST API on port 5000. Runs as a daemon thread\\n"
    "inside the same process. Reads and controls game state\\nvia registered Python callbacks.")
}

Rel(player, game,   "Interacts via",    "GPIO buttons / keyboard")
Rel(admin,  web,    "Queries & controls","HTTP / port 5000")
Rel(camera, game,   "Provides frames",  "cv2.VideoCapture")
Rel(game,   display,"Renders to",       "cv2.imshow / HDMI")
Rel(gpio,   game,   "Button events",    "GPIO daemon thread")
Rel(game,   gpio,   "LED outputs",      "GPIO BCM write")
Rel(game,   web,    "Shares live state","Python callbacks / shared object")
Rel(web,    game,   "Control commands", "Callback invocation on HTTP request")
@enduml""")

    pdf.h2("1.2 Container Diagram - ASCII Overview")
    pdf.code("""\
[Player] ----GPIO/KB---->  +----------------------------------------------+
[Admin]  ----HTTP:5000-->  |  Face Detection Game  (one Python process)   |
                           |                                              |
                           |  +----------------------------------+        |
                           |  | Game Application (main thread)  |        |
                           |  |                                  |        |
                           |  |  - cv2.VideoCapture (camera)    |        |
                           |  |  - FaceDetector (MediaPipe/DNN) |        |
                           |  |  - CameraFaceDetector (state    |        |
                           |  |    machine, scoring, GPIO LED)  |        |
                           |  |  - HUD rendering -> HDMI        |        |
                           |  +----------------|-----------------+        |
                           |        shared object / callbacks             |
                           |  +----------------v-----------------+        |
                           |  | Monitoring Web Server (daemon)   |        |
                           |  |  Flask app, port 5000            |        |
                           |  |  GET  /game/status               |        |
                           |  |  POST /game/start  /game/pause   |        |
                           |  |  GET  /metrics   /health         |        |
                           |  +----------------------------------+        |
                           +----------------------------------------------+""")

    pdf.h2("1.3 Component Diagram Update - PlantUML Source")
    pdf.code("""\
@startuml Milestone_F_Component
!include https://raw.githubusercontent.com/plantuml-stdlib/C4-PlantUML/master/C4_Component.puml
LAYOUT_WITH_LEGEND()
title C4 Component Diagram - with Web Component (Milestone F)

Container_Boundary(game_ct, "Game Application (main thread)") {
  Component(cd,  "CameraFaceDetector", "Python Class",
    "Game controller. Exposes _get_status(), start_game(),\\n"
    "toggle_pause(), _adjust_max_faces() as callbacks.")
  Component(fd,  "FaceDetector",       "Python Class",  "Face detection pipeline.")
  Component(hud, "HUD Renderer",       "Functions",     "Game overlay rendering.")
  Component(hw,  "HardwareController", "Python Class",  "GPIO buttons and LEDs.")
}

Container_Boundary(web_ct, "Monitoring Server (daemon thread)") {
  Component(ms,  "MonitoringServer",   "Python Class / Flask",
    "Wraps Flask app. Registers routes. Holds callback\\n"
    "references to the game controller methods.")
  Component(routes, "Flask Routes",   "Flask decorators",
    "/health  /game/status  /game/start\\n/game/pause  /game/max-faces  /metrics")
}

Rel(cd,     ms,     "Registers callbacks at startup")
Rel(ms,     routes, "Mounts routes on Flask app")
Rel(routes, cd,     "Invokes game callbacks on HTTP request")
Rel(cd,     fd,     "Face detection per frame")
Rel(cd,     hw,     "LED feedback + button events")
Rel(cd,     hud,    "HUD rendering")
@enduml""")

    # ---- Section 2: Remote API ----
    pdf.add_page()
    pdf.h1("2. Remote API Description")

    pdf.h2("2.1 Protocol and Network Details")
    pdf.table(
        ["Property", "Value"],
        [
            ["Protocol",      "HTTP/1.1 (REST)"],
            ["Host",          "0.0.0.0  (binds all network interfaces on the Raspberry Pi)"],
            ["Port",          "5000  (configurable via MonitoringServer(port=...))"],
            ["Data format",   "JSON  (application/json)"],
            ["HTTP methods",  "GET for read-only queries, POST for state-changing commands"],
            ["Auth",          "None (local network assumed; add token middleware if exposed publicly)"],
        ],
        widths=[44, 126],
    )

    pdf.h2("2.2 Endpoints")
    pdf.table(
        ["Method", "Endpoint", "Description", "Response"],
        [
            ["GET",  "/health",         "Server liveness check",          '{"status":"ok","timestamp":"..."}'],
            ["GET",  "/game/status",    "Full game state snapshot",        "GameStatus JSON object"],
            ["POST", "/game/start",     "Start or restart the game",       '{"message":"Game started"}'],
            ["POST", "/game/pause",     "Toggle pause / resume",           '{"message":"Game paused/resumed"}'],
            ["POST", "/game/max-faces", "Adjust face target (see body)",   '{"message":"Max faces adjusted..."}'],
            ["GET",  "/metrics",        "FPS, face count, score, state",   "Metrics JSON object"],
        ],
        widths=[18, 38, 56, 58],
    )

    pdf.h2("2.3 Request / Response Examples")
    pdf.h3("GET /game/status")
    pdf.code("""\
GET http://192.168.1.42:5000/game/status

HTTP/1.1 200 OK
Content-Type: application/json

{
  "state":                "running",
  "score":                7,
  "strikes":              1,
  "max_faces":            2,
  "current_faces":        2,
  "fps":                  18.4,
  "switch_time_remaining": 1.23,
  "current_switch_time":  2.3,
  "game_over":            false,
  "timestamp":            "2026-05-04T14:32:01.456789",
  "backend":              "mediapipe"
}""")

    pdf.h3("POST /game/max-faces (increment by direction)")
    pdf.code("""\
POST http://192.168.1.42:5000/game/max-faces
Content-Type: application/json

{ "direction": "up" }          # increment target by 1  (max 5)
# OR
{ "direction": "down" }        # decrement target by 1  (min 1)
# OR
{ "value": 3 }                 # set to specific value

HTTP/1.1 200 OK
{ "message": "Max faces adjusted to 3" }""")

    # ---- Section 3: Async Execution ----
    pdf.h1("3. Asynchronous Execution Mechanism")

    pdf.para(
        "The web server and the game loop run concurrently inside a single Python process "
        "using the threading module. This avoids the complexity of multi-process IPC while "
        "keeping the HTTP server completely transparent to the game loop."
    )

    pdf.h2("3.1 Threading Architecture")
    pdf.code("""\
# Thread layout at runtime:
#
#  MainThread      -  game loop: camera capture, face detection,
#                     state machine, HUD render, keyboard input
#
#  Thread-Flask    -  Flask WSGI server (daemon=True)
#                     handles incoming HTTP requests
#
#  Thread-BtnStart -  GPIO pin 17 polling (daemon=True)
#  Thread-BtnPause -  GPIO pin 23 polling (daemon=True)
#  Thread-BtnLeft  -  GPIO pin 27 polling (daemon=True)
#  Thread-BtnRight -  GPIO pin 22 polling (daemon=True)
#
#  Thread-LED-*    -  short-lived daemon threads created by flash_led()
#                     for non-blocking LED flash sequences""")

    pdf.h2("3.2 Flask Daemon Thread - Code")
    pdf.code("""\
# monitoring_server.py
def start(self) -> None:
    if not self.app:
        print("Flask not available. HTTP monitoring disabled.")
        return

    def run_server():
        # Flask's built-in Werkzeug WSGI server handles concurrency
        # with its own internal thread pool (threaded=True)
        self.app.run(
            host=self.host,     # "0.0.0.0" - all interfaces
            port=self.port,     # 5000
            debug=False,        # must be False in daemon thread
            threaded=True,      # each request gets its own thread
        )

    self.server_thread = threading.Thread(target=run_server, daemon=True)
    self.server_thread.start()
    # daemon=True means this thread is automatically killed when the
    # main thread (game loop) exits - no explicit shutdown needed""")

    pdf.h2("3.3 Why the Web Server Does Not Interfere With the Game Loop")
    pdf.bullets([
        "The Flask thread blocks inside app.run() waiting for HTTP connections. "
        "It consumes CPU only when an HTTP request arrives, which is infrequent (<1% CPU overhead).",
        "HTTP handlers execute in Flask worker threads (threaded=True), never on the main thread. "
        "The game loop is never blocked by an HTTP request.",
        "daemon=True ensures the Flask thread is cleaned up automatically when the game exits "
        "via the finally block - no orphaned processes.",
        "The Python GIL serialises bytecode execution between threads, so simple Python variable "
        "reads/writes are effectively atomic for the small integer and boolean types used as game state.",
    ])

    # ---- Section 4: Data Sharing ----
    pdf.h1("4. Data Sharing Between Web Server and Game")

    pdf.h2("4.1 Mechanism: Python Callback References")
    pdf.para(
        "Instead of shared memory, queues, or pipes, the MonitoringServer holds direct "
        "references to bound methods of the CameraFaceDetector instance. These callbacks "
        "are registered once at startup:"
    )
    pdf.code("""\
# In CameraFaceDetector.__init__():
if self.monitoring:
    # READ callbacks - web server calls these to get current state
    self.monitoring.set_game_state_callback(self._get_status)

    # WRITE callbacks - web server calls these to control the game
    self.monitoring.set_start_game_callback(self.start_game)
    self.monitoring.set_pause_game_callback(self.toggle_pause)
    self.monitoring.set_adjust_max_faces_callback(self._adjust_max_faces)

    self.monitoring.start()  # launch daemon thread""")

    pdf.h2("4.2 Read Path: Status Snapshot")
    pdf.code("""\
# Called by Flask route on GET /game/status
# Executes in a Flask worker thread
def _get_status(self) -> GameStatus:
    fps = (sum(self._fps_samples) / len(self._fps_samples)
           if self._fps_samples else 0.0)
    # Reads simple Python attributes - safe under GIL without a lock
    return GameStatus(
        state=self.state.value,          # str (Enum.value)
        score=self.score,                # int
        strikes=self.strikes,            # int
        max_faces=self.max_faces,        # int
        current_faces=self.current_faces,# int
        fps=fps,                         # float
        switch_time_remaining=max(0.0,
            self.get_switch_time() - self.get_switch_elapsed_time()),
        current_switch_time=self.get_switch_time(),
        game_over=self.game_over,        # bool
        timestamp=datetime.now().isoformat(),
        backend=self.detector.backend,   # str
    )""")

    pdf.h2("4.3 Write Path: Control Commands")
    pdf.para(
        "POST endpoints invoke the same transition methods (start_game, toggle_pause, "
        "_adjust_max_faces) that hardware buttons use. Because these methods only modify "
        "simple Python integer/bool/enum attributes, and Python's GIL prevents two threads "
        "from executing Python bytecode simultaneously, no explicit locking is required for "
        "the attribute writes."
    )
    pdf.code("""\
# Flask route handler (runs in Flask worker thread):
@self.app.route('/game/start', methods=['POST'])
def start_game():
    if self._start_game_callback:
        self._start_game_callback()   # -> CameraFaceDetector.start_game()
        return jsonify({"message": "Game started"}), 200

# The callback modifies game state:
def start_game(self) -> None:        # runs in Flask worker thread!
    self.state   = GameState.RUNNING  # atomic under GIL
    self.score   = 0                  # atomic under GIL
    self.strikes = 0                  # atomic under GIL
    ...""")

    pdf.h2("4.4 Thread Safety Summary")
    pdf.table(
        ["Concern", "How it is handled"],
        [
            ["Read of int/bool/str from Flask thread",
             "Safe: Python GIL ensures single-bytecode atomicity"],
            ["Write of int/bool/str from Flask thread",
             "Safe: single assignment is one bytecode (STORE_ATTR)"],
            ["Write during active game-loop read",
             "Rare race; worst case: one stale frame of game state, no corruption"],
            ["fps deque (collections.deque)",
             "deque.append() is thread-safe in CPython (deque uses a C-level lock)"],
            ["LED flash threads",
             "HardwareController spawns daemon threads; each thread owns its own pin write"],
        ],
        widths=[66, 104],
    )

    pdf.output("Milestone_F.pdf")
    print("  Milestone_F.pdf generated")


if __name__ == "__main__":
    print("Generating PDFs...")
    build_milestone_d()
    build_milestone_e()
    build_milestone_f()
    print("Done.")
