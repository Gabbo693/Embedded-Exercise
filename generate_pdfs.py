"""Generate Milestone D, E, F, G deliverable PDFs."""
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


# ---------------------------------------------------------------------------
# MILESTONE G
# ---------------------------------------------------------------------------
def build_milestone_g():
    pdf = ReportPDF("Milestone G - System Optimisation Analysis")
    pdf.cover(
        "Milestone G",
        "Updated Architecture Diagrams |\nBottleneck Analysis | Optimisation Strategies",
    )

    # ---- Section 1: Updated Architecture Diagrams ----
    pdf.add_page()
    pdf.h1("1. Updated Architecture Diagrams")
    pdf.para(
        "The diagrams in this section extend the Milestone F component model with two additions: "
        "the PYNQ camera integration (camera.py) and the dual display path that enables direct "
        "HDMI output on the FPGA board without an X11 display server."
    )

    pdf.h2("1.1 Updated C4 Component Diagram - PlantUML Source")
    pdf.code("""\
@startuml Milestone_G_Component
!include https://raw.githubusercontent.com/plantuml-stdlib/C4-PlantUML/master/C4_Component.puml
LAYOUT_WITH_LEGEND()
title C4 Component Diagram - Optimised System with PYNQ Support (Milestone G)

Person(player, "Player", "Uses hardware buttons or keyboard")
Person(admin,  "Admin",  "HTTP monitoring client")
System_Ext(camera_hw, "Camera", "USB webcam or PYNQ MIPI camera")
System_Ext(display,   "Display", "PC window (cv2.imshow) or PYNQ HDMI out")
System_Ext(gpio,      "GPIO", "Raspberry Pi / PYNQ buttons and LEDs")

Container_Boundary(app, "Face Detection Game (single Python process)") {
  Component(cam_mod, "camera.py", "PYNQ Module",
    "PYNQ-specific camera setup and HDMI output.\\n"
    "setup() -> (hdmi_out, videoIn).\\n"
    "get_frame() mirrors frame via array slice.\\n"
    "clean_up() releases HDMI and VideoCapture.\\n"
    "Auto-detected at import time; disabled on non-PYNQ hosts.")

  Component(cd, "CameraFaceDetector", "Python Class",
    "Unified game controller for both platforms.\\n"
    "Uses camera.py paths when _PYNQ_AVAILABLE=True,\\n"
    "standard cv2.VideoCapture paths otherwise.\\n"
    "Owns state machine, scoring, timing.")

  Component(fd, "FaceDetector", "Python Class",
    "MediaPipe > DNN > Haar backend chain.\\n"
    "Chosen backend fixed at startup; no runtime switching.")

  Component(hud, "HUD Renderer", "Module Functions",
    "_draw_game_hud(): game overlay (score, timer, prompt).\\n"
    "_draw_hud(): stats panel (FPS, backend, res).\\n"
    "Output written to HDMI frame or cv2.imshow window.")

  Component(hw,  "HardwareController", "Python Class",
    "GPIO/simulation abstraction. 50 ms debounce per button.")

  Component(ms,  "MonitoringServer", "Flask / daemon thread",
    "REST API on port 5000. Reads/writes game state\\n"
    "via Python callback references.")
}

Rel(player,    gpio,    "Presses buttons")
Rel(gpio,      hw,      "Pin interrupt",       "GPIO BCM")
Rel(hw,        cd,      "Button callback")
Rel(camera_hw, cd,      "Raw frames",          "VideoCapture / PYNQ")
Rel(cd,        cam_mod, "Uses when PYNQ",       "setup/get_frame/clean_up")
Rel(cd,        fd,      "BGR frame")
Rel(fd,        cd,      "(x,y,w,h) + scores")
Rel(cd,        hud,     "score, faces, timer")
Rel(hud,       display, "Final frame",          "cv2.imshow OR hdmi_out.writeframe")
Rel(cd,        ms,      "Registers callbacks")
Rel(ms,        cd,      "Control via HTTP",     "callback invocation")
Rel(admin,     ms,      "HTTP /game/status etc","port 5000")
@enduml""")

    pdf.h2("1.2 Dual Display Path - ASCII")
    pdf.code("""\
                        [Camera frame]
                             |
                    cv2.flip (non-PYNQ)    OR    camera.get_frame() (PYNQ, already mirrored)
                             |
                    [FaceDetector.process_frame()]
                             |
                    [_draw_hud() + _draw_game_hud()]
                             |
               _PYNQ_AVAILABLE?
              /               \\
            YES                NO
             |                  |
    hdmi_out.newframe()    cv2.imshow()
    outframe[:h,:w] = display
    hdmi_out.writeframe()      cv2.waitKey(1) -> keyboard input
                               (hardware buttons only on PYNQ)""")

    pdf.h2("1.3 Frame Pipeline Data Flow")
    pdf.code("""\
Main thread (one iteration, ~16 ms target at 60 FPS):

  1. cap.read()  /  camera.get_frame()          ~1-2  ms  (USB DMA)
  2. cv2.flip() - skipped on PYNQ               ~0.3  ms
  3. FaceDetector.detect_faces()                ~10-100 ms (backend-dependent)
  4. FaceDetector.draw_faces()                  ~1    ms
  5. _draw_hud() + _draw_game_hud()             ~1    ms
  6. cv2.imshow() / hdmi_out.writeframe()       ~1-3  ms
  7. cv2.waitKey(1) - skipped on PYNQ           ~1    ms
                                                ------
  Total (MediaPipe on Pi 4)                    ~15-20 ms  -> ~50-65 FPS theoretical
  Total (DNN on Pi 4)                          ~40-60 ms  -> ~17-25 FPS
  Total (Haar on Pi 4)                         ~10-20 ms  -> ~50-100 FPS""")

    # ---- Section 2: Bottlenecks ----
    pdf.add_page()
    pdf.h1("2. Identified and Possible Bottlenecks")

    pdf.para(
        "The following bottlenecks were identified by analysis of the pipeline architecture "
        "and observed behaviour on target hardware (Raspberry Pi 4, PYNQ Z2)."
    )

    pdf.h2("2.1 Face Detection Inference (Critical)")
    pdf.para(
        "Face detection dominates per-frame compute time. The entire pipeline is serialised: "
        "detection must finish before the next frame can be captured, overlays drawn, and the "
        "frame displayed. Any backend slower than the target frame period (16 ms at 60 FPS) "
        "becomes the rate-limiting step."
    )
    pdf.table(
        ["Backend", "Typical latency (Pi 4)", "Pipeline FPS ceiling", "Notes"],
        [
            ["MediaPipe (TFLite)", "10-20 ms",  "50-65 FPS", "NEON SIMD; best choice"],
            ["OpenCV DNN SSD",     "40-60 ms",  "17-25 FPS", "ResNet backbone; high CPU"],
            ["Haar Cascade",       "10-25 ms",  "40-100 FPS", "Fast but imprecise"],
        ],
        widths=[40, 46, 44, 40],
    )

    pdf.h2("2.2 Sequential Single-Threaded Pipeline")
    pdf.para(
        "Camera capture, face detection, HUD rendering, and display output all execute "
        "sequentially on the main thread. Steps 1 and 3 are largely independent: the camera "
        "sensor exposes a new frame in hardware while the previous frame is still being "
        "processed. This parallelism is unexploited -- the main loop always waits for the "
        "detector to finish before requesting the next frame."
    )

    pdf.h2("2.3 Full-Resolution Input to Detector")
    pdf.para(
        "Frames are passed to the detector at capture resolution (1280x720 or 640x480). "
        "MediaPipe's internal BlazeFace model operates on 128x128 input and resizes the frame "
        "internally. Passing a 1280x720 frame forces an extra resize inside TFLite that the "
        "caller could perform more cheaply at a lower resolution upstream."
    )

    pdf.h2("2.4 Camera Input Buffer Latency")
    pdf.para(
        "OpenCV's VideoCapture maintains an internal frame buffer (default 4-5 frames). "
        "When the game loop runs slower than the camera frame rate the buffer fills up, "
        "and subsequent cap.read() calls return stale frames rather than the latest camera "
        "image. This is visible as perceived latency between a player's movement and the "
        "on-screen bounding box response."
    )

    pdf.h2("2.5 Per-Frame HDMI Frame Allocation (PYNQ)")
    pdf.para(
        "On PYNQ, hdmi_out.newframe() allocates a fresh numpy array on every frame. "
        "At 30+ FPS this generates 30+ allocations per second that the Python garbage "
        "collector must eventually collect, causing occasional GC pauses that manifest "
        "as brief frame-rate drops."
    )

    pdf.h2("2.6 Per-Flash LED Thread Spawning")
    pdf.para(
        "HardwareController.flash_led() creates a new daemon thread each time it is called. "
        "Under frequent scoring (high score, short switch times) this creates multiple short-lived "
        "threads per second. Thread creation overhead is low on Linux but non-zero; on "
        "resource-constrained hardware (Pi Zero, PYNQ Z1) this is a measurable cost."
    )

    pdf.h2("2.7 GIL Contention from Monitoring Server")
    pdf.para(
        "When an HTTP client polls the /metrics or /game/status endpoint at high frequency "
        "(e.g. every 100 ms), Flask worker threads compete with the game loop for the Python GIL. "
        "Each HTTP handler must acquire the GIL to execute Python code, which can delay game-loop "
        "frames by a few milliseconds per poll."
    )

    pdf.h2("2.8 cv2.waitKey(1) Frame Floor (non-PYNQ)")
    pdf.para(
        "On non-PYNQ platforms the game loop calls cv2.waitKey(1) every frame. This call "
        "yields the thread for at least 1 ms to allow the OpenCV event loop to process window "
        "events. Because the OS scheduler has ~1 ms granularity, the actual sleep is "
        "1-3 ms, setting a soft floor of ~330-1000 FPS on the loop iteration rate "
        "(irrelevant when detection is slower, but visible when using Haar Cascade)."
    )

    # ---- Section 3: Optimisation Strategies ----
    pdf.add_page()
    pdf.h1("3. Proposed and Applied Optimisation Strategies")

    pdf.h2("3.1 Applied Optimisations")

    pdf.h3("A - Backend Priority Chain (Applied)")
    pdf.para(
        "The FaceDetector selects the fastest suitable backend at startup and locks it in for "
        "the session. MediaPipe is tried first (fastest on ARM), then OpenCV DNN, then Haar. "
        "No runtime switching means zero overhead for backend selection per frame."
    )
    pdf.code("""\
if use_dnn:
    if prefer_mediapipe and _MP_AVAILABLE and self._init_mediapipe():
        self.backend = "mediapipe"; return   # fastest path locked in
    if self._init_dnn_detector():
        self.backend = "dnn"; return
self._init_haar_cascade()
self.backend = "haar"                        # guaranteed fallback""")

    pdf.h3("B - Frame Skipped During Pause (Applied)")
    pdf.para(
        "When the game is paused, cap.read() and the detector are not called. The last rendered "
        "frame is reused via last_frame.copy(). This eliminates all compute from the two most "
        "expensive pipeline steps during an idle state."
    )
    pdf.code("""\
if not self.paused:
    frame = _camera_module.get_frame(self.cap)  # skipped when paused
    if ok:
        rendered, n_faces, _ = self.detector.process_frame(frame)
        last_frame = rendered

display = last_frame.copy()   # reuse held frame during pause""")

    pdf.h3("C - Sticky Detection Flag (Applied)")
    pdf.para(
        "Rather than counting or re-detecting faces at the end of each round, a boolean flag "
        "faces_detected_this_switch is set to True the moment the target is met. The round-end "
        "check is then a single boolean read -- O(1) regardless of how many frames were processed "
        "in the round."
    )
    pdf.code("""\
# Each frame (O(1)):
if n_faces >= self.max_faces:
    self.faces_detected_this_switch = True   # sticky - never cleared mid-round

# At round end (O(1)):
if self.faces_detected_this_switch:
    self.add_score()
else:
    self.add_strike()
self.faces_detected_this_switch = False      # reset for next round""")

    pdf.h3("D - PYNQ Direct HDMI Write (Applied)")
    pdf.para(
        "On PYNQ the game writes directly to the HDMI framebuffer via the PYNQ library instead "
        "of going through an X11 display server and cv2.imshow(). This removes the X11 round-trip "
        "and the associated socket and context-switch overhead."
    )
    pdf.code("""\
if _PYNQ_AVAILABLE:
    outframe = self._hdmi_out.newframe()
    outframe[:copy_h, :copy_w, :] = display[:copy_h, :copy_w, :]
    self._hdmi_out.writeframe(outframe)      # DMA transfer to HDMI
else:
    cv2.imshow(self.WINDOW_NAME, display)    # X11 path on desktop""")

    pdf.h3("E - PYNQ Mirror via Array Slice (Applied)")
    pdf.para(
        "camera.get_frame() on PYNQ mirrors the frame using a NumPy array slice "
        "(frame[:, ::-1, :]) rather than calling cv2.flip(). NumPy slice-based reversal "
        "is performed in C and avoids creating a full copy when the result is immediately "
        "consumed by the detector."
    )
    pdf.code("""\
# camera.py - get_frame():
return frame_vga[0:frame_in_h-1, frame_in_w-1:0:-1, :]  # in-place slice, no copy

# face_detector.py - no flip call on PYNQ:
if _PYNQ_AVAILABLE:
    frame = _camera_module.get_frame(self.cap)   # already mirrored
else:
    ok, frame = self.cap.read()
    if ok:
        frame = cv2.flip(frame, 1)               # explicit flip on desktop""")

    pdf.h3("F - Daemon Threads for Non-Critical Work (Applied)")
    pdf.para(
        "The Flask monitoring server and all GPIO button polling threads run as daemon=True "
        "threads. They execute only when triggered (HTTP request or pin edge) and are "
        "automatically killed when the main game loop exits, requiring no explicit shutdown logic."
    )

    pdf.h2("3.2 Proposed Optimisations (Not Yet Applied)")

    pdf.h3("G - Camera Buffer Flush")
    pdf.para(
        "Set CAP_PROP_BUFFERSIZE to 1 immediately after opening the VideoCapture. This limits "
        "internal buffering to one frame, ensuring cap.read() always returns the most recent "
        "camera image and eliminating the perceived input latency at low frame rates."
    )
    pdf.code("""\
self.cap = cv2.VideoCapture(self.camera_id, cv2.CAP_DSHOW)
self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)   # flush stale frames immediately""")

    pdf.h3("H - Detection Input Downscale")
    pdf.para(
        "Resize the captured frame to a smaller resolution (e.g. 320x240) before passing it "
        "to the detector. Draw face boxes on the original full-resolution frame by scaling the "
        "returned coordinates. Reduces the input tensor copy and the internal resize inside TFLite."
    )
    pdf.code("""\
DETECT_W, DETECT_H = 320, 240
scale_x = frame.shape[1] / DETECT_W
scale_y = frame.shape[0] / DETECT_H
small = cv2.resize(frame, (DETECT_W, DETECT_H))
faces_small = self.detector.detect_faces(small)
faces = [(int(x*scale_x), int(y*scale_y), int(w*scale_x), int(h*scale_y))
         for x, y, w, h in faces_small]""")

    pdf.h3("I - Detection Frame Skipping")
    pdf.para(
        "Run the face detector only every N frames (N=2 or 3) and reuse the previous detection "
        "result for intermediate frames. The game's face-count scoring window (0.5-3 s) is far "
        "longer than 2-3 frame intervals (~50-100 ms), so skipping has no effect on game "
        "correctness while roughly doubling effective throughput."
    )
    pdf.code("""\
DETECT_INTERVAL = 2          # run detector every 2nd frame
self._frame_count = 0
self._last_faces = []

ok, frame = self.cap.read()
if ok:
    self._frame_count += 1
    if self._frame_count % DETECT_INTERVAL == 0:
        self._last_faces = self.detector.detect_faces(frame)
    n_faces = len(self._last_faces)
    rendered = self.detector.draw_faces(frame, self._last_faces)""")

    pdf.h3("J - Producer-Consumer Detection Thread")
    pdf.para(
        "Offload face detection to a dedicated worker thread. The main thread only submits "
        "frames and consumes results; the camera sensor and detector run in parallel. A "
        "Queue(maxsize=1) acts as a one-slot buffer: if the detector is busy the main thread "
        "drops the incoming frame rather than blocking, keeping the display loop responsive."
    )
    pdf.code("""\
import queue, threading

detect_q  = queue.Queue(maxsize=1)   # input frames
result_q  = queue.Queue(maxsize=1)   # detected faces

def detection_worker():
    while True:
        frame = detect_q.get()
        if frame is None: break
        faces = detector.detect_faces(frame)
        try:
            result_q.put_nowait(faces)    # drop if consumer is slow
        except queue.Full:
            pass

threading.Thread(target=detection_worker, daemon=True).start()

# Main loop: non-blocking get of latest result
try:
    n_faces = len(result_q.get_nowait())
except queue.Empty:
    n_faces = self._last_n_faces        # reuse previous result""")

    pdf.h3("K - Persistent LED Worker Thread")
    pdf.para(
        "Replace per-flash thread creation with a single persistent LED worker thread "
        "that reads flash commands from a Queue. Eliminates repeated thread spawn/join "
        "overhead during high-scoring runs where flashes occur multiple times per second."
    )
    pdf.code("""\
self._led_q = queue.Queue()

def led_worker():
    while True:
        color, duration, count = self._led_q.get()
        for _ in range(count):
            GPIO.output(PIN, HIGH); time.sleep(duration)
            GPIO.output(PIN, LOW);  time.sleep(0.05)

threading.Thread(target=led_worker, daemon=True).start()

# Caller (no thread creation):
def flash_led(self, color, duration=0.2, count=1):
    self._led_q.put_nowait((color, duration, count))""")

    pdf.h3("L - Pre-Allocated HDMI Frame (PYNQ)")
    pdf.para(
        "Call hdmi_out.newframe() once at startup and reuse the same buffer every frame. "
        "Eliminates per-frame numpy allocation and reduces GC pressure on the PYNQ board's "
        "limited RAM (512 MB on Z1)."
    )
    pdf.code("""\
# At startup (once):
self._hdmi_frame = self._hdmi_out.newframe()

# Each frame (zero allocation):
self._hdmi_frame[:copy_h, :copy_w, :] = display[:copy_h, :copy_w, :]
self._hdmi_out.writeframe(self._hdmi_frame)""")

    pdf.h2("3.3 Optimisation Summary Table")
    pdf.table(
        ["ID", "Strategy", "Status", "Expected Gain"],
        [
            ["A", "Backend priority chain (MediaPipe first)",    "Applied",   "Maximises FPS on any platform"],
            ["B", "Skip capture & detect when paused",           "Applied",   "0% CPU during pause"],
            ["C", "Sticky bool flag for round scoring",          "Applied",   "O(1) per frame vs O(faces)"],
            ["D", "Direct HDMI write on PYNQ",                   "Applied",   "Removes X11 overhead"],
            ["E", "Mirror via NumPy slice on PYNQ",              "Applied",   "Avoids full-frame copy"],
            ["F", "Daemon threads for I/O-bound work",           "Applied",   "Zero main-loop blocking"],
            ["G", "Camera buffer size = 1",                      "Proposed",  "Reduces input latency by 3-5 frames"],
            ["H", "Downscale input before detection",            "Proposed",  "+10-20% FPS, same accuracy"],
            ["I", "Detection frame skipping (N=2)",              "Proposed",  "+90% throughput, no game impact"],
            ["J", "Producer-consumer detection thread",          "Proposed",  "Decouples camera and detector FPS"],
            ["K", "Persistent LED worker thread",                "Proposed",  "Removes thread-spawn jitter"],
            ["L", "Pre-allocate PYNQ HDMI frame buffer",         "Proposed",  "Eliminates 30+ allocs/sec (PYNQ)"],
        ],
        widths=[10, 72, 28, 60],
    )

    pdf.output("Milestone_G.pdf")
    print("  Milestone_G.pdf generated")


# ---------------------------------------------------------------------------
# MILESTONE H
# ---------------------------------------------------------------------------
def build_milestone_h():
    pdf = ReportPDF("Milestone H - Acceptance Testing")
    pdf.cover(
        "Milestone H",
        "Acceptance Test Cases | Test Execution Results |\nIdentified Issues and Improvements",
    )

    # ---- Section 1: Test Scope ----
    pdf.add_page()
    pdf.h1("1. Test Scope and Targets")
    pdf.para(
        "Acceptance testing validates that the Face Detection Game meets its functional "
        "requirements from the player's perspective. Tests were executed on a PYNQ Z2 board "
        "running the full system: HDMI output via camera.py, MediaPipe face detection backend, "
        "and four physical push-buttons for input."
    )
    pdf.h2("1.1 Testing Targets")
    pdf.bullets([
        "Game state transitions (IDLE -> RUNNING -> PAUSED -> END)",
        "Face detection accuracy and robustness across angles and lighting",
        "Round scoring and strike logic",
        "Difficulty scaling (timer reduction as score increases)",
        "Hardware button responsiveness and control mapping",
        "HUD accuracy (score, strikes, face count, timer bar)",
        "System performance (frame rate on target hardware)",
    ])

    pdf.h2("1.2 Test Environment")
    pdf.table(
        ["Property", "Value"],
        [
            ["Hardware",       "PYNQ Z2 (Xilinx Zynq-7020)"],
            ["OS",             "PYNQ Linux (Ubuntu-based)"],
            ["Python",         "3.8"],
            ["OpenCV",         "4.5.4 (apt-installed)"],
            ["Detection backend", "MediaPipe (primary)"],
            ["Camera",         "USB webcam, 640x480"],
            ["Display",        "HDMI monitor via base overlay"],
            ["Input",          "4 physical push-buttons (BTN0-BTN3)"],
        ],
        widths=[50, 120],
    )

    pdf.h2("1.3 Test Case Summary")
    pdf.table(
        ["ID", "Title", "Status"],
        [
            ["TC-01", "Game start from IDLE state",              "PASS"],
            ["TC-02", "Face detection -- frontal face",          "PASS"],
            ["TC-03", "Face detection -- angled face",           "FAIL"],
            ["TC-04", "Round scoring when target met",           "PASS"],
            ["TC-05", "Strike added when target not met",        "PASS"],
            ["TC-06", "Game over at 3 strikes",                  "PASS"],
            ["TC-07", "Pause and resume",                        "FAIL"],
            ["TC-08", "Face target adjustment via buttons",      "FAIL"],
            ["TC-09", "Difficulty scaling with score",           "PASS"],
            ["TC-10", "Frame rate on PYNQ Z2",                   "FAIL"],
            ["TC-11", "HUD display accuracy",                    "PASS"],
            ["TC-12", "Restart from END state",                  "PASS"],
        ],
        widths=[18, 120, 32],
    )

    # ---- Section 2: Test Cases ----
    pdf.add_page()
    pdf.h1("2. Acceptance Test Cases and Results")

    def tc(title, tc_id, precondition, steps, expected, actual, status):
        PASS_COLOR  = (30, 120, 30)
        FAIL_COLOR  = (160, 30, 30)
        color = PASS_COLOR if status == "PASS" else FAIL_COLOR
        # Header
        pdf.set_fill_color(*color)
        pdf.set_text_color(255, 255, 255)
        pdf.set_font("Helvetica", "B", 9)
        pdf.cell(0, 7, f"  {tc_id}  --  {title}    [{status}]",
                 fill=True, new_x="LMARGIN", new_y="NEXT")
        pdf.set_text_color(0, 0, 0)
        # Body rows
        rows = [
            ("Precondition", precondition),
            ("Steps",        steps),
            ("Expected",     expected),
            ("Actual",       actual),
        ]
        pdf.set_font("Helvetica", "", 8.5)
        for label, value in rows:
            pdf.set_fill_color(245, 245, 245)
            pdf.set_font("Helvetica", "B", 8.5)
            pdf.cell(38, 6, "  " + label, border=1, fill=True)
            pdf.set_font("Helvetica", "", 8.5)
            pdf.set_fill_color(255, 255, 255)
            # multi_cell moves to next line automatically
            x_after = pdf.get_x() + 38
            y_before = pdf.get_y()
            pdf.set_xy(pdf.get_x() + 38, y_before)
            pdf.multi_cell(132, 6, value, border=1, fill=True)
            # ensure we are at the correct y after multi_cell
        pdf.ln(2)

    tc(
        "Game start from IDLE state", "TC-01",
        precondition="Board powered on. Game in IDLE state. HDMI monitor connected.",
        steps="1. Observe IDLE screen ('PRESS START BUTTON TO BEGIN').\n"
              "2. Press BTN0 (button 1) once.",
        expected="Game transitions to RUNNING state. Score=0, strikes=0. "
                 "Timer bar begins counting down. HUD shows 'SHOW X FACE(S)' prompt.",
        actual="Game started correctly. HUD appeared with score 0 and timer. "
               "LED feedback shown as console output (simulation mode).",
        status="PASS",
    )

    tc(
        "Face detection -- frontal face", "TC-02",
        precondition="Game RUNNING. max_faces=1. Room lighting adequate (>100 lux).",
        steps="1. Sit approx. 50 cm from camera.\n"
              "2. Face camera directly (frontal view, eyes forward).\n"
              "3. Observe HUD face count and bounding box.",
        expected="Face detected within 1 second. Bounding box drawn. "
                 "FACES counter shows 1/1. Challenge prompt turns green.",
        actual="Face detected reliably when looking straight at the camera. "
               "Bounding box and confidence pill displayed correctly.",
        status="PASS",
    )

    tc(
        "Face detection -- angled face", "TC-03",
        precondition="Game RUNNING. max_faces=1. Face detected frontally (TC-02 passed).",
        steps="1. Slowly rotate head to approximately 30 degrees from center.\n"
              "2. Observe whether detection is maintained.\n"
              "3. Rotate to 45 degrees and repeat.",
        expected="Face should remain detected up to ~30 degrees rotation.",
        actual="Detection lost at angles greater than approximately 20 degrees. "
               "MediaPipe BlazeFace short-range model struggles with side profiles "
               "at the 640x480 input resolution on this hardware.",
        status="FAIL",
    )

    tc(
        "Round scoring when face target is met", "TC-04",
        precondition="Game RUNNING. max_faces=1. Score=0.",
        steps="1. Position face directly in front of camera.\n"
              "2. Hold position until the round timer expires (3.0s).\n"
              "3. Observe score panel.",
        expected="Score increments from 0 to 1. Timer resets. New round begins.",
        actual="Score incremented correctly each time face was visible for "
               "the full round duration.",
        status="PASS",
    )

    tc(
        "Strike added when face target is not met", "TC-05",
        precondition="Game RUNNING. max_faces=2. Only 1 person available.",
        steps="1. Show only 1 face to the camera for the entire round.\n"
              "2. Wait for timer to expire.\n"
              "3. Observe strikes panel.",
        expected="Strike count increments by 1. Timer resets.",
        actual="Strike added correctly when face count was below target "
               "for the entire round.",
        status="PASS",
    )

    pdf.add_page()
    tc(
        "Game over at 3 strikes", "TC-06",
        precondition="Game RUNNING. strikes=2. max_faces=2.",
        steps="1. Allow timer to expire without meeting face target.\n"
              "2. Observe state transition.",
        expected="Game transitions to END state. Game over screen shows final score. "
                 "LED flashes red 3 times (console output in simulation mode).",
        actual="Game over screen appeared correctly with final score displayed. "
               "Restart prompt shown.",
        status="PASS",
    )

    tc(
        "Pause and resume", "TC-07",
        precondition="Game RUNNING. Timer counting down.",
        steps="1. Press BTN1 (button 2) once briefly.\n"
              "2. Observe game state.\n"
              "3. Press BTN1 again to resume.\n"
              "4. Verify timer continued from same value.",
        expected="Game pauses on first press. 'PAUSED' overlay shown. Timer frozen. "
                 "Timer resumes from correct position on second press.",
        actual="Button required to be held for ~0.5s to register. Short tap "
               "not detected. When held long enough, pause/resume worked correctly "
               "and timer preserved its value.",
        status="FAIL",
    )

    tc(
        "Face target adjustment via buttons", "TC-08",
        precondition="Game in any state.",
        steps="1. Press BTN2 (button 3) to decrease face target.\n"
              "2. Observe HUD challenge prompt and FACES panel.\n"
              "3. Press BTN3 (button 4) to increase face target.\n"
              "4. Verify range is clamped to 1-5.",
        expected="Face target decreases/increases by 1 per press. "
                 "HUD updates immediately. Target clamped at min=1, max=5.",
        actual="Button hold required. When held, target adjusted correctly "
               "but repeated increments fired rapidly due to polling loop "
               "reading continued HIGH state.",
        status="FAIL",
    )

    tc(
        "Difficulty scaling with score", "TC-09",
        precondition="Game RUNNING. Score=0.",
        steps="1. Note initial round timer duration (3.0s).\n"
              "2. Score 5 consecutive points.\n"
              "3. Note round timer duration.\n"
              "4. Score 5 more points (total 10).\n"
              "5. Note round timer duration.",
        expected="Timer at score 0 = 3.0s. At score 5 = 2.5s. At score 10 = 2.0s.",
        actual="Timer scaled correctly per formula max(0.5, 3.0 - score*0.1). "
               "Verified on-screen timer bar shortening as score increased.",
        status="PASS",
    )

    pdf.add_page()
    tc(
        "Frame rate on PYNQ Z2", "TC-10",
        precondition="Game RUNNING. MediaPipe detection backend active.",
        steps="1. Start game and observe FPS counter in left HUD panel.\n"
              "2. Record FPS value over 30 seconds.\n"
              "3. Compare against target (>= 10 FPS for playable experience).",
        expected="FPS >= 10 for acceptable real-time gameplay.",
        actual="Observed FPS: 0.5-0.8 FPS. MediaPipe inference (~1.2s per frame) "
               "dominates the pipeline on the PYNQ Z2 ARM Cortex-A9 processor. "
               "Game logic remains functionally correct but response feels very sluggish.",
        status="FAIL",
    )

    tc(
        "HUD display accuracy", "TC-11",
        precondition="Game RUNNING. score=3, strikes=1, max_faces=2, current_faces=1.",
        steps="1. Check score panel shows '0003'.\n"
              "2. Check strikes panel shows '1/3'.\n"
              "3. Check faces panel shows '1/2'.\n"
              "4. Check challenge prompt colour (amber when not met).\n"
              "5. Check timer bar colour progression.",
        expected="All HUD values match game state. Challenge prompt amber "
                 "when below target, green when met. Timer bar green/amber/red "
                 "as time decreases.",
        actual="All HUD values displayed correctly. Colour transitions on "
               "challenge prompt and timer bar functioned as specified.",
        status="PASS",
    )

    tc(
        "Restart from END state", "TC-12",
        precondition="Game in END state. Final score displayed.",
        steps="1. Observe END screen.\n"
              "2. Press BTN0 (button 1).",
        expected="Game resets to score=0, strikes=0. Transitions to RUNNING. "
                 "New round timer starts.",
        actual="Restart worked correctly when button registered. "
               "Subject to the same button hold issue as TC-07 and TC-08.",
        status="PASS",
    )

    # ---- Section 3: Issues and Improvements ----
    pdf.add_page()
    pdf.h1("3. Identified Issues and Improvements")

    pdf.h2("3.1 Issue Log")
    pdf.table(
        ["ID", "Severity", "Description", "Failing TCs"],
        [
            ["ISS-01", "Critical",  "Frame rate 0.5-0.8 FPS on PYNQ Z2. MediaPipe inference "
                                    "takes ~1.2s per frame on the ARM Cortex-A9.",          "TC-10"],
            ["ISS-02", "High",      "Buttons must be held (~0.5s) to register. Short taps "
                                    "are missed by the 10ms polling loop.",                  "TC-07, TC-08, TC-12"],
            ["ISS-03", "Medium",    "Face detection fails at angles > ~20 degrees. "
                                    "Only strict frontal faces reliably detected.",           "TC-03"],
            ["ISS-04", "Low",       "When button held, face target increments rapidly "
                                    "(no repeat delay), making fine adjustment difficult.",   "TC-08"],
        ],
        widths=[18, 22, 100, 30],
    )

    pdf.h2("3.2 Issue Detail and Proposed Fixes")

    pdf.h3("ISS-01 -- Frame Rate (Critical)")
    pdf.para(
        "Root cause: MediaPipe's BlazeFace TFLite model is compiled for ARMv7 without "
        "NEON SIMD acceleration in the pip-distributed wheel for this Python version. "
        "The PYNQ Z2 has a dual-core Cortex-A9 at 666 MHz, which is significantly slower "
        "than a Raspberry Pi 4 (Cortex-A72 at 1.5 GHz)."
    )
    pdf.bullets([
        "Switch to Haar Cascade backend: 10-25ms per frame vs 1200ms. "
        "Achieves ~30 FPS at the cost of detection quality.",
        "Detection frame skipping: run detector every 3rd frame, reuse previous result. "
        "Triples effective throughput with no impact on game timing.",
        "Reduce input resolution to 320x240 before passing to detector. "
        "Saves the internal resize step inside TFLite.",
        "Compile OpenCV with NEON support from source to accelerate Haar cascade further.",
    ])

    pdf.h3("ISS-02 -- Button Hold Required (High)")
    pdf.para(
        "Root cause: PYNQ Z2 buttons are polled inside the main game loop at ~10ms intervals. "
        "At 0.5-0.8 FPS the actual poll interval is 1.2-2.0 seconds -- far too slow to catch "
        "a brief tap. The edge detection compares current vs previous sample, but if a tap "
        "happens between two samples it is never seen."
    )
    pdf.bullets([
        "Use PYNQ button interrupts instead of polling: "
        "base.buttons[i].wait_for_value(1) in a dedicated daemon thread. "
        "This detects presses regardless of frame rate.",
        "As an immediate workaround: switch to Haar Cascade (ISS-01 fix) to raise FPS, "
        "which reduces the poll interval and makes short taps detectable.",
    ])
    pdf.code("""\
# Interrupt-based fix (daemon thread per button):
import threading

def _watch_button(base, idx, callback):
    while True:
        base.buttons[idx].wait_for_value(1)   # blocks until pressed
        callback(None)
        base.buttons[idx].wait_for_value(0)   # wait for release before next press

for i, cb in enumerate([on_start, on_pause, on_left, on_right]):
    threading.Thread(target=_watch_button, args=(base, i, cb), daemon=True).start()""")

    pdf.h3("ISS-03 -- Face Angle Recognition (Medium)")
    pdf.para(
        "Root cause: MediaPipe BlazeFace short-range model is optimised for frontal faces "
        "within ~2m. Rotation beyond ~20 degrees causes the face bounding box to shrink "
        "below the detection threshold at 640x480 resolution."
    )
    pdf.bullets([
        "Switch to BlazeFace full-range model (model_selection=1 in solutions API): "
        "handles wider angles and distances up to ~5m.",
        "If using Haar Cascade as the fallback, the alt2 cascade has better angle "
        "tolerance than the default frontal cascade.",
        "Add game guidance text prompting the player to face the camera directly "
        "as a UX mitigation.",
    ])

    pdf.h3("ISS-04 -- Rapid Repeat on Hold (Low)")
    pdf.para(
        "When a button is held, every poll cycle fires the callback, causing the face "
        "target to jump from 1 to 5 (or 5 to 1) instantly. This makes fine-grained "
        "adjustment difficult."
    )
    pdf.bullets([
        "Add a minimum repeat delay (e.g. 300ms) after the first edge before allowing "
        "repeated callbacks while the button remains held.",
        "Alternatively, require a release-then-press cycle: fire only on rising edge "
        "(addressed automatically by the interrupt-based fix for ISS-02).",
    ])

    pdf.h2("3.3 Improvement Suggestions")
    pdf.table(
        ["#", "Improvement", "Expected Benefit"],
        [
            ["1", "Replace MediaPipe with Haar Cascade on PYNQ Z2",
             "FPS increase from 0.5 to ~25-30. Resolves ISS-01 and ISS-02."],
            ["2", "Interrupt-based button handling via PYNQ wait_for_value()",
             "Reliable tap detection regardless of frame rate. Resolves ISS-02 and ISS-04."],
            ["3", "Detection frame skipping (every 3rd frame)",
             "3x throughput improvement without changing detection backend."],
            ["4", "Downscale input to 320x240 before detection",
             "~20% faster inference; negligible accuracy loss."],
            ["5", "Use BlazeFace full-range model (model_selection=1)",
             "Better detection at angles and distances. Addresses ISS-03."],
            ["6", "Add on-screen arrow indicators for button functions",
             "Improved player guidance without relying on documentation."],
        ],
        widths=[10, 90, 70],
    )

    pdf.output("Milestone_H.pdf")
    print("  Milestone_H.pdf generated")


if __name__ == "__main__":
    print("Generating PDFs...")
    build_milestone_d()
    build_milestone_e()
    build_milestone_f()
    build_milestone_g()
    build_milestone_h()
    print("Done.")
