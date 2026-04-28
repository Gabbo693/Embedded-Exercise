"""
Face Detection Module - High-accuracy real-time face detection.

Detection backend priority (highest accuracy first):
    1. MediaPipe Face Detection (Google) - state-of-the-art, very fast
    2. OpenCV DNN SSD ResNet (auto-downloaded if missing)
    3. Haar Cascade (classical fallback, always available)

The live preview renders a modern HUD-style overlay:
    - Corner-bracket bounding boxes (no boxy outlines)
    - Per-face confidence pill
    - Optional facial keypoints (eyes / nose / mouth) when available
    - Translucent stats panel with FPS, face count, backend, resolution
    - Subtle title bar and footer hint
"""
from __future__ import annotations

import os
import time
import urllib.request
from collections import deque
from typing import Deque, List, Optional, Sequence, Tuple

import cv2
import numpy as np

# ---------------------------------------------------------------------------
# Optional MediaPipe import (graceful fallback if not installed)
# Supports BOTH the legacy `mediapipe.solutions` API and the new Tasks API.
# ---------------------------------------------------------------------------
_MP_AVAILABLE = False
_MP_MODE: Optional[str] = None  # 'solutions' | 'tasks'
_mp = None
_mp_tasks = None

try:  # pragma: no cover - import guard
    import mediapipe as _mp  # type: ignore
    if hasattr(_mp, "solutions") and hasattr(_mp.solutions, "face_detection"):
        _MP_MODE = "solutions"
        _MP_AVAILABLE = True
    else:
        try:
            from mediapipe.tasks import python as _mp_tasks_python  # type: ignore
            from mediapipe.tasks.python import vision as _mp_vision  # type: ignore
            _mp_tasks = (_mp_tasks_python, _mp_vision)
            _MP_MODE = "tasks"
            _MP_AVAILABLE = True
        except Exception:
            _MP_AVAILABLE = False
except Exception:  # pragma: no cover - import guard
    _mp = None
    _MP_AVAILABLE = False


# ---------------------------------------------------------------------------
# Theme (modern dark HUD)
# ---------------------------------------------------------------------------
class Theme:
    ACCENT = (255, 200, 80)        # warm cyan/amber (BGR)
    ACCENT_SOFT = (255, 170, 60)
    GOOD = (120, 230, 140)         # green for high confidence
    WARN = (60, 200, 255)          # amber for medium
    BAD = (90, 90, 240)            # red for low
    PANEL = (24, 24, 28)
    PANEL_BORDER = (90, 90, 100)
    TEXT = (235, 235, 240)
    TEXT_DIM = (170, 170, 180)
    SHADOW = (0, 0, 0)
    FONT = cv2.FONT_HERSHEY_SIMPLEX


def _confidence_color(score: float) -> Tuple[int, int, int]:
    if score >= 0.85:
        return Theme.GOOD
    if score >= 0.6:
        return Theme.WARN
    return Theme.BAD


def _draw_translucent_rect(img: np.ndarray, p1: Tuple[int, int],
                           p2: Tuple[int, int], color: Tuple[int, int, int],
                           alpha: float = 0.55) -> None:
    overlay = img.copy()
    cv2.rectangle(overlay, p1, p2, color, -1)
    cv2.addWeighted(overlay, alpha, img, 1 - alpha, 0, img)


def _draw_corner_box(img: np.ndarray, x: int, y: int, w: int, h: int,
                     color: Tuple[int, int, int], thickness: int = 2,
                     corner_len_ratio: float = 0.18) -> None:
    """Draw a modern corner-bracket bounding box."""
    x2, y2 = x + w, y + h
    cl = max(8, int(min(w, h) * corner_len_ratio))

    # top-left
    cv2.line(img, (x, y), (x + cl, y), color, thickness, cv2.LINE_AA)
    cv2.line(img, (x, y), (x, y + cl), color, thickness, cv2.LINE_AA)
    # top-right
    cv2.line(img, (x2, y), (x2 - cl, y), color, thickness, cv2.LINE_AA)
    cv2.line(img, (x2, y), (x2, y + cl), color, thickness, cv2.LINE_AA)
    # bottom-left
    cv2.line(img, (x, y2), (x + cl, y2), color, thickness, cv2.LINE_AA)
    cv2.line(img, (x, y2), (x, y2 - cl), color, thickness, cv2.LINE_AA)
    # bottom-right
    cv2.line(img, (x2, y2), (x2 - cl, y2), color, thickness, cv2.LINE_AA)
    cv2.line(img, (x2, y2), (x2, y2 - cl), color, thickness, cv2.LINE_AA)

    # very faint full rectangle for depth
    overlay = img.copy()
    cv2.rectangle(overlay, (x, y), (x2, y2), color, 1, cv2.LINE_AA)
    cv2.addWeighted(overlay, 0.18, img, 0.82, 0, img)


def _put_text(img: np.ndarray, text: str, org: Tuple[int, int],
              scale: float = 0.5, color: Tuple[int, int, int] = Theme.TEXT,
              thickness: int = 1, shadow: bool = True) -> None:
    if shadow:
        cv2.putText(img, text, (org[0] + 1, org[1] + 1), Theme.FONT, scale,
                    Theme.SHADOW, thickness + 1, cv2.LINE_AA)
    cv2.putText(img, text, org, Theme.FONT, scale, color, thickness, cv2.LINE_AA)


# ---------------------------------------------------------------------------
# DNN model auto-download
# ---------------------------------------------------------------------------
_DNN_PROTO_URL = (
    "https://raw.githubusercontent.com/opencv/opencv/master/samples/dnn/"
    "face_detector/deploy.prototxt"
)
_DNN_MODEL_URL = (
    "https://raw.githubusercontent.com/opencv/opencv_3rdparty/"
    "dnn_samples_face_detector_20180205_fp16/"
    "res10_300x300_ssd_iter_140000_fp16.caffemodel"
)
_MP_TASK_MODEL_URL = (
    "https://storage.googleapis.com/mediapipe-models/face_detector/"
    "blaze_face_short_range/float16/1/blaze_face_short_range.tflite"
)


def _download_file(url: str, dest: str) -> bool:
    try:
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        if not os.path.exists(dest):
            urllib.request.urlretrieve(url, dest)
        return os.path.exists(dest)
    except Exception:
        return False


def _download_dnn_models(dest_dir: str) -> Optional[Tuple[str, str]]:
    try:
        os.makedirs(dest_dir, exist_ok=True)
        proto = os.path.join(dest_dir, "deploy.prototxt")
        model = os.path.join(dest_dir, "res10_300x300_ssd.caffemodel")
        if not os.path.exists(proto):
            urllib.request.urlretrieve(_DNN_PROTO_URL, proto)
        if not os.path.exists(model):
            urllib.request.urlretrieve(_DNN_MODEL_URL, model)
        return proto, model
    except Exception:
        return None


# ---------------------------------------------------------------------------
# Core detector
# ---------------------------------------------------------------------------
class FaceDetector:
    """High-accuracy face detector with multiple backends.

    Public attributes preserved for backward compatibility:
        use_dnn (bool), face_cascade, net, min_detection_confidence
    Plus:
        backend (str): 'mediapipe' | 'dnn' | 'haar'
    """

    def __init__(self, use_dnn: bool = True,
                 min_detection_confidence: float = 0.5,
                 prefer_mediapipe: bool = True) -> None:
        self.use_dnn = use_dnn
        self.min_detection_confidence = float(min_detection_confidence)
        self.net = None
        self.face_cascade = None
        self.backend: str = "haar"

        # Per-detection metadata for the renderer
        self._last_scores: List[float] = []
        self._last_keypoints: List[List[Tuple[int, int]]] = []

        # MediaPipe handles
        self._mp_face = None
        self._mp_api: Optional[str] = None

        if use_dnn:
            if prefer_mediapipe and _MP_AVAILABLE and self._init_mediapipe():
                self.backend = "mediapipe"
                return
            if self._init_dnn_detector():
                self.backend = "dnn"
                return

        # Always have Haar as safety net
        self._init_haar_cascade()
        self.backend = "haar"
        if use_dnn:
            # Honor backward-compatible attribute meaning
            self.use_dnn = False

    # ---- backend init -----------------------------------------------------
    def _init_mediapipe(self) -> bool:
        try:
            if _MP_MODE == "solutions":
                mp_fd = _mp.solutions.face_detection
                self._mp_face = mp_fd.FaceDetection(
                    model_selection=1,
                    min_detection_confidence=self.min_detection_confidence,
                )
                self._mp_api = "solutions"
                return True
            if _MP_MODE == "tasks":
                tasks_python, vision = _mp_tasks
                cache_dir = os.path.join(
                    os.path.expanduser("~"), ".cache", "face_detector_models")
                model_path = os.path.join(cache_dir, "blaze_face_short_range.tflite")
                if not _download_file(_MP_TASK_MODEL_URL, model_path):
                    return False
                base_options = tasks_python.BaseOptions(model_asset_path=model_path)
                options = vision.FaceDetectorOptions(
                    base_options=base_options,
                    min_detection_confidence=self.min_detection_confidence,
                )
                self._mp_face = vision.FaceDetector.create_from_options(options)
                self._mp_api = "tasks"
                return True
            return False
        except Exception:
            self._mp_face = None
            return False

    def _init_dnn_detector(self) -> bool:
        try:
            cache_dir = os.path.join(
                os.path.expanduser("~"), ".cache", "face_detector_models")
            paths = _download_dnn_models(cache_dir)
            if not paths:
                return False
            proto, model = paths
            self.net = cv2.dnn.readNetFromCaffe(proto, model)
            return True
        except Exception:
            self.net = None
            return False

    def _init_haar_cascade(self) -> None:
        cascade_path = cv2.data.haarcascades + "haarcascade_frontalface_alt2.xml"
        self.face_cascade = cv2.CascadeClassifier(cascade_path)
        if self.face_cascade.empty():
            cascade_path = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
            self.face_cascade = cv2.CascadeClassifier(cascade_path)
            if self.face_cascade.empty():
                raise ValueError("Failed to load Haar cascade classifier")

    # ---- detection --------------------------------------------------------
    def detect_faces(self, image: np.ndarray) -> List[Tuple[int, int, int, int]]:
        """Return list of (x, y, w, h) face rectangles."""
        if image is None or image.size == 0:
            self._last_scores, self._last_keypoints = [], []
            return []

        if self.backend == "mediapipe" and self._mp_face is not None:
            return self._detect_mediapipe(image)
        if self.backend == "dnn" and self.net is not None:
            return self._detect_dnn(image)
        return self._detect_haar(image)

    def _detect_mediapipe(self, image: np.ndarray) -> List[Tuple[int, int, int, int]]:
        h, w = image.shape[:2]
        rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        faces: List[Tuple[int, int, int, int]] = []
        scores: List[float] = []
        keypoints: List[List[Tuple[int, int]]] = []

        if self._mp_api == "solutions":
            rgb.flags.writeable = False
            results = self._mp_face.process(rgb)
            detections = results.detections or []
            for det in detections:
                score = float(det.score[0]) if det.score else 0.0
                if score < self.min_detection_confidence:
                    continue
                bbox = det.location_data.relative_bounding_box
                x = int(max(0.0, bbox.xmin) * w)
                y = int(max(0.0, bbox.ymin) * h)
                fw = int(bbox.width * w)
                fh = int(bbox.height * h)
                x = max(0, min(x, w - 1))
                y = max(0, min(y, h - 1))
                fw = max(1, min(fw, w - x))
                fh = max(1, min(fh, h - y))
                faces.append((x, y, fw, fh))
                scores.append(score)
                pts = [(int(kp.x * w), int(kp.y * h))
                       for kp in det.location_data.relative_keypoints]
                keypoints.append(pts)
        else:  # tasks API
            mp_image = _mp.Image(image_format=_mp.ImageFormat.SRGB, data=rgb)
            result = self._mp_face.detect(mp_image)
            for det in (result.detections or []):
                score = float(det.categories[0].score) if det.categories else 0.0
                if score < self.min_detection_confidence:
                    continue
                bb = det.bounding_box
                x = max(0, int(bb.origin_x))
                y = max(0, int(bb.origin_y))
                fw = max(1, min(int(bb.width), w - x))
                fh = max(1, min(int(bb.height), h - y))
                faces.append((x, y, fw, fh))
                scores.append(score)
                pts = [(int(kp.x * w), int(kp.y * h)) for kp in (det.keypoints or [])]
                keypoints.append(pts)

        self._last_scores = scores
        self._last_keypoints = keypoints
        return faces

    def _detect_dnn(self, image: np.ndarray) -> List[Tuple[int, int, int, int]]:
        h, w = image.shape[:2]
        blob = cv2.dnn.blobFromImage(
            cv2.resize(image, (300, 300)), 1.0, (300, 300),
            (104.0, 177.0, 123.0), swapRB=False, crop=False)
        self.net.setInput(blob)
        detections = self.net.forward()

        faces: List[Tuple[int, int, int, int]] = []
        scores: List[float] = []
        for i in range(detections.shape[2]):
            score = float(detections[0, 0, i, 2])
            if score < self.min_detection_confidence:
                continue
            box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
            x1, y1, x2, y2 = box.astype(int)
            x1 = max(0, min(x1, w - 1))
            y1 = max(0, min(y1, h - 1))
            x2 = max(0, min(x2, w - 1))
            y2 = max(0, min(y2, h - 1))
            fw, fh = max(1, x2 - x1), max(1, y2 - y1)
            faces.append((x1, y1, fw, fh))
            scores.append(score)

        self._last_scores = scores
        self._last_keypoints = [[] for _ in faces]
        return faces

    def _detect_haar(self, image: np.ndarray) -> List[Tuple[int, int, int, int]]:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        gray = cv2.equalizeHist(gray)
        rects = self.face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=6,
            flags=cv2.CASCADE_SCALE_IMAGE,
            minSize=(40, 40),
        )
        faces = [tuple(map(int, r)) for r in rects]
        # Haar gives no real confidence; synthesize a stable placeholder.
        self._last_scores = [0.9 for _ in faces]
        self._last_keypoints = [[] for _ in faces]
        return faces

    # ---- rendering --------------------------------------------------------
    def draw_faces(self, image: np.ndarray,
                   faces: Sequence[Tuple[int, int, int, int]],
                   color: Optional[Tuple[int, int, int]] = None,
                   thickness: int = 2) -> np.ndarray:
        """Render detected faces on a copy of the image."""
        result = image.copy()
        scores = self._last_scores if len(self._last_scores) == len(faces) else []
        keypoints = self._last_keypoints if len(self._last_keypoints) == len(faces) else []

        for idx, (x, y, w, h) in enumerate(faces, start=1):
            score = scores[idx - 1] if scores else 1.0
            box_color = color if color is not None else _confidence_color(score)

            _draw_corner_box(result, int(x), int(y), int(w), int(h),
                             box_color, thickness=thickness)

            # Keypoints (MediaPipe provides 6 per face)
            if keypoints and idx - 1 < len(keypoints):
                for px, py in keypoints[idx - 1]:
                    cv2.circle(result, (px, py), 2, box_color, -1, cv2.LINE_AA)
                    cv2.circle(result, (px, py), 4, box_color, 1, cv2.LINE_AA)

            # Confidence pill above the box
            label = f"FACE {idx:02d}  {int(round(score * 100))}%"
            (tw, th), _ = cv2.getTextSize(label, Theme.FONT, 0.5, 1)
            pad_x, pad_y = 8, 6
            pill_y2 = max(th + pad_y * 2, int(y))
            pill_y1 = pill_y2 - (th + pad_y * 2)
            pill_x1 = int(x)
            pill_x2 = pill_x1 + tw + pad_x * 2
            _draw_translucent_rect(result, (pill_x1, pill_y1),
                                   (pill_x2, pill_y2), Theme.PANEL, 0.7)
            cv2.line(result, (pill_x1, pill_y2 - 1), (pill_x2, pill_y2 - 1),
                     box_color, 1, cv2.LINE_AA)
            _put_text(result, label, (pill_x1 + pad_x, pill_y2 - pad_y - 1),
                      0.5, Theme.TEXT, 1)

        return result

    # ---- pipeline ---------------------------------------------------------
    def process_frame(self, frame: np.ndarray) -> Tuple[np.ndarray, int, str]:
        faces = self.detect_faces(frame)
        rendered = self.draw_faces(frame, faces)
        n = len(faces)
        message = "No faces detected" if n == 0 else f"{n} face(s) detected"
        return rendered, n, message


# ---------------------------------------------------------------------------
# HUD overlay (stats panel + title + hint)
# ---------------------------------------------------------------------------
def _draw_hud(img: np.ndarray, fps: float, n_faces: int, backend: str,
              avg_score: Optional[float]) -> None:
    h, w = img.shape[:2]

    # ---- top title bar
    _draw_translucent_rect(img, (0, 0), (w, 38), Theme.PANEL, 0.55)
    cv2.line(img, (0, 38), (w, 38), Theme.ACCENT, 1, cv2.LINE_AA)
    _put_text(img, "FACE  DETECTION  /  LIVE", (14, 25), 0.65,
              Theme.TEXT, 1)
    backend_label = {
        "mediapipe": "MediaPipe (Google)",
        "dnn": "OpenCV DNN SSD",
        "haar": "Haar Cascade",
    }.get(backend, backend)
    rt = f"BACKEND  {backend_label}"
    (tw, _), _ = cv2.getTextSize(rt, Theme.FONT, 0.5, 1)
    _put_text(img, rt, (w - tw - 14, 25), 0.5, Theme.ACCENT, 1)

    # ---- left stats panel
    panel_x, panel_y = 14, 52
    panel_w, panel_h = 220, 110
    _draw_translucent_rect(img, (panel_x, panel_y),
                           (panel_x + panel_w, panel_y + panel_h),
                           Theme.PANEL, 0.6)
    cv2.rectangle(img, (panel_x, panel_y),
                  (panel_x + panel_w, panel_y + panel_h),
                  Theme.PANEL_BORDER, 1, cv2.LINE_AA)
    cv2.line(img, (panel_x, panel_y), (panel_x + panel_w, panel_y),
             Theme.ACCENT, 2, cv2.LINE_AA)

    _put_text(img, "STATS", (panel_x + 12, panel_y + 22), 0.55,
              Theme.ACCENT, 1)

    rows = [
        ("FPS", f"{fps:5.1f}"),
        ("FACES", f"{n_faces}"),
        ("CONF", "—" if avg_score is None else f"{int(round(avg_score * 100))}%"),
        ("RES", f"{w}x{h}"),
    ]
    for i, (k, v) in enumerate(rows):
        y_row = panel_y + 44 + i * 16
        _put_text(img, k, (panel_x + 12, y_row), 0.45, Theme.TEXT_DIM, 1)
        _put_text(img, v, (panel_x + 90, y_row), 0.5, Theme.TEXT, 1)

    # ---- bottom hint bar
    _draw_translucent_rect(img, (0, h - 28), (w, h), Theme.PANEL, 0.55)
    cv2.line(img, (0, h - 28), (w, h - 28), Theme.ACCENT, 1, cv2.LINE_AA)
    _put_text(img, "[Q] quit   [F] fullscreen   [S] save snapshot   [SPACE] pause",
              (14, h - 9), 0.5, Theme.TEXT_DIM, 1)


# ---------------------------------------------------------------------------
# Camera runner
# ---------------------------------------------------------------------------
class CameraFaceDetector:
    """Real-time face detection from a camera with a polished HUD."""

    WINDOW_NAME = "Face Detection — Live"

    def __init__(self, camera_id: int = 0, use_dnn: bool = True,
                 auto_detect: bool = False,
                 min_detection_confidence: float = 0.5) -> None:
        self.detector = FaceDetector(
            use_dnn=use_dnn,
            min_detection_confidence=min_detection_confidence,
        )
        self.camera_id = camera_id
        self.cap: Optional[cv2.VideoCapture] = None
        self.auto_detect = auto_detect
        self._fps_samples: Deque[float] = deque(maxlen=30)

    # ---- camera selection -------------------------------------------------
    def _check_camera_available(self, camera_id: int) -> bool:
        try:
            cap = cv2.VideoCapture(camera_id, cv2.CAP_DSHOW)
            if cap.isOpened():
                ok, _ = cap.read()
                cap.release()
                return bool(ok)
            return False
        except Exception:
            return False

    def _find_available_camera(self) -> int:
        """Scan camera IDs and return the first one that works.

        Order: 0 (built-in front) → 1, 2, 3 (external USB cameras).
        """
        print("Detecting available cameras...")
        for cid, label in (
            (0, "built-in front (laptop)"),
            (1, "external #1"),
            (2, "external #2"),
            (3, "external #3"),
        ):
            if self._check_camera_available(cid):
                print(f"  ✓ Found {label} camera at ID {cid}")
                return cid
            print(f"  ✗ No camera at ID {cid}")
        raise RuntimeError("No camera devices found!")

    # ---- run loop ---------------------------------------------------------
    def start_detection(self) -> None:
        if self.auto_detect:
            self.camera_id = self._find_available_camera()

        # CAP_DSHOW is faster/more reliable on Windows
        self.cap = cv2.VideoCapture(self.camera_id, cv2.CAP_DSHOW)
        if not self.cap.isOpened():
            raise RuntimeError(f"Failed to open camera device {self.camera_id}")
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

        ok, _ = self.cap.read()
        if not ok:
            self.cap.release()
            raise RuntimeError(f"Camera {self.camera_id} opened but cannot read frames")

        cam_desc = "external (ID 1+)" if self.camera_id >= 1 else "built-in front (ID 0)"
        print(f"\n✓ Connected to {cam_desc} camera (ID {self.camera_id})")
        print(f"✓ Detection backend: {self.detector.backend}")
        print("  Hotkeys:  Q=quit  F=fullscreen  S=snapshot  SPACE=pause\n")

        cv2.namedWindow(self.WINDOW_NAME, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(self.WINDOW_NAME, 1280, 720)

        paused = False
        fullscreen = False
        last_frame: Optional[np.ndarray] = None
        prev_t = time.perf_counter()
        snap_idx = 0

        try:
            while True:
                if not paused:
                    ok, frame = self.cap.read()
                    if not ok:
                        print("Failed to read frame from camera")
                        break
                    frame = cv2.flip(frame, 1)  # mirror for natural feel

                    rendered, n_faces, _ = self.detector.process_frame(frame)

                    now = time.perf_counter()
                    dt = max(1e-6, now - prev_t)
                    prev_t = now
                    self._fps_samples.append(1.0 / dt)
                    fps = sum(self._fps_samples) / len(self._fps_samples)

                    scores = self.detector._last_scores
                    avg_score = (sum(scores) / len(scores)) if scores else None
                    _draw_hud(rendered, fps, n_faces,
                              self.detector.backend, avg_score)
                    last_frame = rendered

                if last_frame is not None:
                    display = last_frame
                    if paused:
                        display = last_frame.copy()
                        h, w = display.shape[:2]
                        _draw_translucent_rect(
                            display, (w // 2 - 80, h // 2 - 24),
                            (w // 2 + 80, h // 2 + 24), Theme.PANEL, 0.7)
                        _put_text(display, "PAUSED",
                                  (w // 2 - 42, h // 2 + 6), 0.9,
                                  Theme.ACCENT, 2)
                    cv2.imshow(self.WINDOW_NAME, display)

                key = cv2.waitKey(1) & 0xFF
                if key == ord('q') or key == 27:  # q or ESC
                    break
                if key == ord(' '):
                    paused = not paused
                if key == ord('f'):
                    fullscreen = not fullscreen
                    cv2.setWindowProperty(
                        self.WINDOW_NAME, cv2.WND_PROP_FULLSCREEN,
                        cv2.WINDOW_FULLSCREEN if fullscreen else cv2.WINDOW_NORMAL)
                if key == ord('s') and last_frame is not None:
                    snap_idx += 1
                    fname = f"snapshot_{int(time.time())}_{snap_idx:02d}.png"
                    cv2.imwrite(fname, last_frame)
                    print(f"  📸 Saved {fname}")
        finally:
            self.stop_detection()

    def stop_detection(self) -> None:
        if self.cap is not None:
            self.cap.release()
            self.cap = None
        cv2.destroyAllWindows()


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
def main() -> None:
    """Entry point.

    Camera selection
    ----------------
    By default this uses the **built-in front (laptop) camera** (ID 0).

    To use a different camera (e.g. an external USB / HP camera), either:
      * set ``camera_id=1`` (or 2, 3, ... depending on how many are plugged in), or
      * set ``auto_detect=True`` to scan IDs and pick the first one that works.
    """
    try:
        detector = CameraFaceDetector(
            camera_id=0,            # 0 = built-in front camera (laptop)
            use_dnn=True,           # prefer MediaPipe / DNN
            auto_detect=False,      # set True to auto-pick when plugging externals
            min_detection_confidence=0.6,
        )
        detector.start_detection()
    except RuntimeError as e:
        print(f"Error: {e}")
        raise


if __name__ == "__main__":
    main()
