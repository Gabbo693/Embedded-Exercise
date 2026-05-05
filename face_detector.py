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
from datetime import datetime
from typing import Deque, List, Optional, Sequence, Tuple

import cv2
import numpy as np

# cv2.data.haarcascades is absent in older apt-installed OpenCV builds
import glob as _glob
import site as _site

def _find_haar_dir() -> str:
    try:
        d = cv2.data.haarcascades
        if os.path.isdir(d):
            return d
    except AttributeError:
        pass
    known = [
        "/usr/share/opencv4/haarcascades/",
        "/usr/share/opencv/haarcascades/",
        "/usr/share/OpenCV/haarcascades/",
        "/usr/local/share/opencv4/haarcascades/",
        "/usr/local/share/opencv/haarcascades/",
    ]
    for sp in _site.getsitepackages():
        known.append(os.path.join(sp, "cv2", "data") + os.sep)
    for p in known:
        if os.path.isdir(p):
            return p
    # last resort: scan the filesystem
    hits = _glob.glob("/usr/**/haarcascade_frontalface_alt2.xml", recursive=True)
    if hits:
        return os.path.dirname(hits[0]) + os.sep
    return ""

_HAAR_DIR = _find_haar_dir()

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

# CAP_DSHOW only exists on Windows; on Linux let OpenCV pick the default backend
import platform as _platform
_WINDOWS = _platform.system() == "Windows"

# PYNQ camera (Xilinx FPGA board) — graceful fallback on standard machines
_PYNQ_AVAILABLE = False
try:
    import camera as _camera_module
    _PYNQ_AVAILABLE = True
except ImportError:
    _camera_module = None  # type: ignore

# Hardware and monitoring imports
from hardware_controller import HardwareController, LEDColor, ButtonEvent
from monitoring_server import MonitoringServer, GameStatus, GameState


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
        cascade_path = _HAAR_DIR + "haarcascade_frontalface_alt2.xml"
        self.face_cascade = cv2.CascadeClassifier(cascade_path)
        if self.face_cascade.empty():
            cascade_path = _HAAR_DIR + "haarcascade_frontalface_default.xml"
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


def _draw_game_hud(img: np.ndarray, score: int, strikes: int,
                   switch_time_remaining: float, current_switch_time: float,
                   max_faces: int = 1, current_faces: int = 0) -> None:
    h, w = img.shape[:2]

    # ---- center challenge prompt ----
    face_met = current_faces >= max_faces
    s = 'S' if max_faces != 1 else ''
    challenge = f"SHOW  {max_faces}  FACE{s}"
    (tw, th), _ = cv2.getTextSize(challenge, Theme.FONT, 0.85, 2)
    cx = w // 2 - tw // 2
    cy = 78
    _draw_translucent_rect(img, (cx - 14, cy - th - 8), (cx + tw + 14, cy + 8),
                           Theme.PANEL, 0.65)
    prompt_color = Theme.GOOD if face_met else Theme.ACCENT
    _put_text(img, challenge, (cx, cy), 0.85, prompt_color, 2)

    # ---- right game stats panel ----
    panel_x = w - 260
    panel_y = 52
    panel_w, panel_h = 240, 135

    _draw_translucent_rect(img, (panel_x, panel_y),
                           (panel_x + panel_w, panel_y + panel_h),
                           Theme.PANEL, 0.6)
    cv2.rectangle(img, (panel_x, panel_y),
                  (panel_x + panel_w, panel_y + panel_h),
                  Theme.PANEL_BORDER, 1, cv2.LINE_AA)
    cv2.line(img, (panel_x, panel_y), (panel_x + panel_w, panel_y),
             Theme.ACCENT, 2, cv2.LINE_AA)

    _put_text(img, "GAME", (panel_x + 12, panel_y + 22), 0.55, Theme.ACCENT, 1)

    score_str = f"{score:04d}"
    strikes_str = f"{strikes}/3"
    faces_str = f"{current_faces}/{max_faces}"

    _put_text(img, "SCORE", (panel_x + 12, panel_y + 44), 0.45, Theme.TEXT_DIM, 1)
    _put_text(img, score_str, (panel_x + 12, panel_y + 60), 0.65, Theme.GOOD, 1)

    _put_text(img, "STRIKES", (panel_x + 12, panel_y + 80), 0.45, Theme.TEXT_DIM, 1)
    strike_color = Theme.GOOD if strikes < 3 else Theme.BAD
    _put_text(img, strikes_str, (panel_x + 12, panel_y + 96), 0.65, strike_color, 1)

    _put_text(img, "FACES", (panel_x + 12, panel_y + 114), 0.45, Theme.TEXT_DIM, 1)
    face_color = Theme.GOOD if face_met else Theme.WARN
    _put_text(img, faces_str, (panel_x + 12, panel_y + 130), 0.65, face_color, 1)

    # ---- timer bar (bottom center) ----
    timer_y = h - 70
    timer_h = 20
    timer_x1 = w // 2 - 150
    timer_x2 = w // 2 + 150

    _draw_translucent_rect(img, (timer_x1, timer_y),
                           (timer_x2, timer_y + timer_h),
                           Theme.PANEL, 0.6)
    cv2.rectangle(img, (timer_x1, timer_y),
                  (timer_x2, timer_y + timer_h),
                  Theme.PANEL_BORDER, 1, cv2.LINE_AA)

    safe_switch = current_switch_time if current_switch_time > 0 else 1.0
    progress = max(0.0, min(1.0, switch_time_remaining / safe_switch))
    fill_w = int((timer_x2 - timer_x1) * progress)

    if progress > 0.3:
        bar_color = Theme.GOOD
    elif progress > 0.1:
        bar_color = Theme.WARN
    else:
        bar_color = Theme.BAD

    if fill_w > 0:
        _draw_translucent_rect(img, (timer_x1, timer_y),
                               (timer_x1 + fill_w, timer_y + timer_h),
                               bar_color, 0.7)

    timer_text = f"{max(0.0, switch_time_remaining):.1f}s"
    _put_text(img, timer_text, (timer_x1 + 8, timer_y + 15), 0.6, Theme.TEXT, 1)


def _draw_game_over(img: np.ndarray, final_score: int) -> None:
    """Draw game over screen with final score.
    
    Args:
        img: Image to draw on
        final_score: Final score achieved
    """
    h, w = img.shape[:2]
    
    # Semi-transparent overlay
    overlay = img.copy()
    _draw_translucent_rect(overlay, (0, 0), (w, h), Theme.PANEL, 0.85)
    cv2.addWeighted(overlay, 0.3, img, 0.7, 0, img)
    
    # Game over text
    game_over_text = "GAME OVER"
    (tw, th), _ = cv2.getTextSize(game_over_text, Theme.FONT, 2.0, 3)
    _put_text(img, game_over_text, 
              (w // 2 - tw // 2, h // 2 - 60), 2.0, Theme.BAD, 3)
    
    # Final score
    score_text = f"Final Score: {final_score}"
    (tw, th), _ = cv2.getTextSize(score_text, Theme.FONT, 1.0, 2)
    _put_text(img, score_text,
              (w // 2 - tw // 2, h // 2 + 20), 1.0, Theme.TEXT, 2)
    
    # Instructions
    inst_text = "Press [Q] to quit   [ENTER] or [R] to restart"
    (tw, th), _ = cv2.getTextSize(inst_text, Theme.FONT, 0.6, 1)
    _put_text(img, inst_text,
              (w // 2 - tw // 2, h // 2 + 80), 0.6, Theme.TEXT_DIM, 1)


# ---------------------------------------------------------------------------
# Camera runner
# ---------------------------------------------------------------------------
class CameraFaceDetector:
    """Real-time face detection from a camera with a polished HUD and hardware integration."""

    WINDOW_NAME = "Face Detection — Live"

    def __init__(self, camera_id: int = 0, use_dnn: bool = True,
                 auto_detect: bool = False,
                 min_detection_confidence: float = 0.5,
                 use_hardware: bool = True,
                 enable_monitoring: bool = True) -> None:
        self.detector = FaceDetector(
            use_dnn=use_dnn,
            min_detection_confidence=min_detection_confidence,
        )
        self.camera_id = camera_id
        self.cap: Optional[cv2.VideoCapture] = None
        self._hdmi_out = None
        self.auto_detect = auto_detect
        self._fps_samples: Deque[float] = deque(maxlen=30)
        
        # Hardware control
        self.hardware = HardwareController(use_real_gpio=use_hardware)
        self.monitoring = MonitoringServer() if enable_monitoring else None
        
        # Game state machine
        self.state = GameState.IDLE
        self.score = 0
        self.strikes = 0
        self.game_over = False
        self.paused = False
        self.max_faces = 2  # Adjustable max face count
        self.current_faces = 0
        self.faces_detected_this_switch = False
        
        # Timing variables (all in seconds)
        self.switch_start_time = 0.0
        self.pause_start_time = 0.0
        self.paused_time_accumulated = 0.0
        self.base_switch_time = 3.0  # Initial time limit
        
        # Register button callbacks
        self._register_button_handlers()
        
        # Register monitoring callbacks
        if self.monitoring:
            self.monitoring.set_game_state_callback(self._get_status)
            self.monitoring.set_start_game_callback(self.start_game)
            self.monitoring.set_pause_game_callback(self.toggle_pause)
            self.monitoring.set_adjust_max_faces_callback(self._adjust_max_faces)
            self.monitoring.start()
    
    def _register_button_handlers(self) -> None:
        """Register hardware button event handlers"""
        self.hardware.register_button_callback("button_start", self._on_button_start)
        self.hardware.register_button_callback("button_pause", self._on_button_pause)
        self.hardware.register_button_callback("button_left", self._on_button_left)
        self.hardware.register_button_callback("button_right", self._on_button_right)
    
    def _on_button_start(self, event: ButtonEvent) -> None:
        """Handler for start button"""
        if self.state == GameState.IDLE or self.state == GameState.END:
            self.start_game()
    
    def _on_button_pause(self, event: ButtonEvent) -> None:
        """Handler for pause button"""
        if self.state == GameState.RUNNING or self.state == GameState.PAUSED:
            self.toggle_pause()
    
    def _on_button_left(self, event: Optional[ButtonEvent]) -> None:
        """Handler for left button (decrease max faces)"""
        self._adjust_max_faces(self.max_faces - 1, 'down')
    
    def _on_button_right(self, event: Optional[ButtonEvent]) -> None:
        """Handler for right button (increase max faces)"""
        self._adjust_max_faces(self.max_faces + 1, 'up')
    
    def _adjust_max_faces(self, new_max: int, direction: Optional[str] = None) -> None:
        """Adjust maximum face count
        
        Args:
            new_max: New maximum value
            direction: 'up' or 'down' for increment/decrement
        """
        if direction == 'up':
            self.max_faces = min(5, self.max_faces + 1)
        elif direction == 'down':
            self.max_faces = max(1, self.max_faces - 1)
        else:
            self.max_faces = max(1, min(5, new_max))
        
        print(f"  Max faces set to: {self.max_faces}")
    
    def _get_status(self) -> GameStatus:
        """Get current game status for monitoring
        
        Returns:
            GameStatus object with current game state
        """
        fps = sum(self._fps_samples) / len(self._fps_samples) if self._fps_samples else 0.0
        
        if self.state == GameState.RUNNING and not self.paused:
            switch_time_remaining = max(0, self.get_switch_time() - self.get_switch_elapsed_time())
        else:
            switch_time_remaining = self.get_switch_time()
        
        return GameStatus(
            state=self.state.value,
            score=self.score,
            strikes=self.strikes,
            max_faces=self.max_faces,
            current_faces=self.current_faces,
            fps=fps,
            switch_time_remaining=switch_time_remaining,
            current_switch_time=self.get_switch_time(),
            game_over=self.game_over,
            timestamp=datetime.now().isoformat(),
            backend=self.detector.backend
        )
    
    # ---- game state management --------------------------------------------
    def start_game(self) -> None:
        """Start or restart a game (with ≤2s response time)"""
        print("Starting game...")
        self.state = GameState.START
        self.score = 0
        self.strikes = 0
        self.game_over = False
        self.paused = False
        self.paused_time_accumulated = 0.0
        self.faces_detected_this_switch = False
        self.reset_switch_timer()
        
        # LED feedback: flash green on start
        self.hardware.flash_led(LEDColor.GREEN, duration=0.2, count=2)
        
        # Transition to running state
        self.state = GameState.RUNNING
        print("✓ Game started")
    
    def toggle_pause(self) -> None:
        """Pause or resume the game with timing preservation"""
        if self.state != GameState.RUNNING and self.state != GameState.PAUSED:
            return
        
        if self.paused:
            # Resume: add accumulated paused time to the switch start time
            pause_duration = time.perf_counter() - self.pause_start_time
            self.switch_start_time += pause_duration
            self.paused = False
            self.state = GameState.RUNNING
            print("✓ Game resumed")
        else:
            # Pause: record pause start time
            self.pause_start_time = time.perf_counter()
            self.paused = True
            self.state = GameState.PAUSED
            print("✓ Game paused")
    
    def end_game(self) -> None:
        """End the current game"""
        self.state = GameState.END
        self.game_over = True
        print(f"✓ Game ended. Final score: {self.score}")
        
        # LED feedback: red flash on game over
        self.hardware.flash_led(LEDColor.RED, duration=0.5, count=3)

    # ---- game mechanics ---------------------------------------------------
    def get_switch_time(self) -> float:
        """Calculate dynamic switch time based on current score.
        
        Time decreases as score increases for difficulty scaling.
        Formula: base_time - (score * 0.1) with minimum of 0.5 seconds
        """
        time_limit = self.base_switch_time - (self.score * 0.1)
        return max(0.5, time_limit)  # Minimum 0.5 seconds
    
    def reset_switch_timer(self) -> None:
        """Reset the switch timer to current time."""
        self.switch_start_time = time.perf_counter()
        self.paused_time_accumulated = 0.0
    
    def get_switch_elapsed_time(self) -> float:
        """Get elapsed time since switch started (excluding paused time)."""
        if self.paused:
            # While paused, return the time up to pause
            return (self.pause_start_time - self.switch_start_time) - self.paused_time_accumulated
        else:
            # While running, subtract accumulated paused time
            return (time.perf_counter() - self.switch_start_time) - self.paused_time_accumulated
    
    def add_score(self) -> None:
        """Add to score (called when face is detected)."""
        self.score += 1
        # LED feedback: green flash on successful detection
        self.hardware.flash_led(LEDColor.GREEN, duration=0.2, count=1)
    
    def add_strike(self) -> None:
        """Add a strike. Game ends at 3 strikes."""
        self.strikes += 1
        # LED feedback: red flash on strike
        self.hardware.flash_led(LEDColor.RED, duration=0.2, count=1)
        
        if self.strikes >= 3:
            self.end_game()
    
    def reset_game(self) -> None:
        """Reset game state for a new game."""
        self.score = 0
        self.strikes = 0
        self.game_over = False
        self.paused = False
        self.reset_switch_timer()

    # ---- camera selection -------------------------------------------------
    def _check_camera_available(self, camera_id: int) -> bool:
        try:
            cap = cv2.VideoCapture(camera_id, cv2.CAP_DSHOW) if _WINDOWS else cv2.VideoCapture(camera_id)
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
        if _PYNQ_AVAILABLE:
            self._hdmi_out, self.cap = _camera_module.setup()
            if not self.cap.isOpened():
                raise RuntimeError("PYNQ camera failed to open")
            print(f"\n✓ PYNQ camera ready (HDMI out active)")
        else:
            if self.auto_detect:
                self.camera_id = self._find_available_camera()

            self.cap = cv2.VideoCapture(self.camera_id, cv2.CAP_DSHOW) if _WINDOWS else cv2.VideoCapture(self.camera_id)
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
            cv2.namedWindow(self.WINDOW_NAME, cv2.WINDOW_NORMAL)
            cv2.resizeWindow(self.WINDOW_NAME, 1280, 720)

        print(f"✓ Detection backend: {self.detector.backend}")
        print("  Hotkeys:  [START]=press or ENTER  [PAUSE]=SPACE  [LEFT/RIGHT]=A/D  Q=quit")
        if self.monitoring:
            print(f"  HTTP API: http://localhost:5000/game/status\n")
        else:
            print()

        fullscreen = False
        last_frame: Optional[np.ndarray] = None
        prev_t = time.perf_counter()
        snap_idx = 0

        try:
            while True:
                n_faces = 0
                current_switch_time = self.get_switch_time()
                elapsed = self.get_switch_elapsed_time()

                # ---- Frame acquisition (skipped only when paused) ----
                if not self.paused:
                    if _PYNQ_AVAILABLE:
                        # camera.get_frame() already applies horizontal mirror
                        frame = _camera_module.get_frame(self.cap)
                        ok = frame is not False
                    else:
                        ok, frame = self.cap.read()
                        if ok:
                            frame = cv2.flip(frame, 1)

                    if ok:
                        rendered, n_faces, _ = self.detector.process_frame(frame)
                        self.current_faces = n_faces

                        now = time.perf_counter()
                        dt = max(1e-6, now - prev_t)
                        prev_t = now
                        self._fps_samples.append(1.0 / dt)
                        fps = sum(self._fps_samples) / len(self._fps_samples)

                        scores = self.detector._last_scores
                        avg_score = (sum(scores) / len(scores)) if scores else None
                        _draw_hud(rendered, fps, n_faces, self.detector.backend, avg_score)
                        last_frame = rendered
                    elif self.state == GameState.RUNNING:
                        print("Failed to read frame from camera")
                        break

                if last_frame is None:
                    last_frame = np.zeros((720, 1280, 3), dtype=np.uint8)

                display = last_frame.copy()

                # ---- State-specific logic and overlays ----
                if self.state == GameState.RUNNING:
                    if not self.paused:
                        # Score only when face target is met
                        if n_faces >= self.max_faces:
                            self.faces_detected_this_switch = True

                        if elapsed >= current_switch_time:
                            if self.faces_detected_this_switch:
                                self.add_score()
                            else:
                                self.add_strike()
                            self.faces_detected_this_switch = False
                            self.reset_switch_timer()
                            elapsed = 0.0
                            current_switch_time = self.get_switch_time()

                    if self.state == GameState.RUNNING:  # may have transitioned to END
                        switch_remaining = max(0.0, current_switch_time - elapsed)
                        _draw_game_hud(display, self.score, self.strikes,
                                       switch_remaining, current_switch_time,
                                       self.max_faces, self.current_faces)
                        if self.paused:
                            h_d, w_d = display.shape[:2]
                            _draw_translucent_rect(
                                display, (w_d // 2 - 80, h_d // 2 - 24),
                                (w_d // 2 + 80, h_d // 2 + 24), Theme.PANEL, 0.7)
                            _put_text(display, "PAUSED",
                                      (w_d // 2 - 42, h_d // 2 + 6), 0.9, Theme.ACCENT, 2)
                    else:
                        _draw_game_over(display, self.score)

                elif self.state == GameState.IDLE:
                    h_d, w_d = display.shape[:2]
                    _draw_translucent_rect(display, (0, h_d // 2 - 50),
                                           (w_d, h_d // 2 + 50), Theme.PANEL, 0.65)
                    msg = "PRESS [ENTER] OR START BUTTON TO BEGIN"
                    (tw, _), _ = cv2.getTextSize(msg, Theme.FONT, 0.8, 2)
                    _put_text(display, msg, (w_d // 2 - tw // 2, h_d // 2 + 10),
                              0.8, Theme.ACCENT, 2)

                elif self.state == GameState.END:
                    _draw_game_over(display, self.score)

                # ---- Display output ----
                if _PYNQ_AVAILABLE:
                    outframe = self._hdmi_out.newframe()
                    h_out, w_out = outframe.shape[:2]
                    h_d, w_d = display.shape[:2]
                    copy_h = min(h_d, h_out)
                    copy_w = min(w_d, w_out)
                    outframe[:copy_h, :copy_w, :] = display[:copy_h, :copy_w, :]
                    self._hdmi_out.writeframe(outframe)
                else:
                    cv2.imshow(self.WINDOW_NAME, display)

                # ---- Keyboard input (OpenCV window only; PYNQ uses hardware buttons) ----
                if not _PYNQ_AVAILABLE:
                    key = cv2.waitKey(1) & 0xFF
                    if key == ord('q') or key == 27:
                        break
                    if key in (ord('\r'), ord('\n')):
                        if self.state in (GameState.IDLE, GameState.END):
                            self.start_game()
                    if key == ord(' '):
                        self.toggle_pause()
                    if key == ord('a'):
                        self._on_button_left(None)
                    if key == ord('d'):
                        self._on_button_right(None)
                    if key == ord('r'):
                        self.start_game()
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
        """Clean up resources"""
        if _PYNQ_AVAILABLE and self._hdmi_out is not None:
            _camera_module.clean_up(self.cap, self._hdmi_out)
            self.cap = None
            self._hdmi_out = None
        elif self.cap is not None:
            self.cap.release()
            self.cap = None
            cv2.destroyAllWindows()

        self.hardware.cleanup()
        print("✓ Cleanup complete")


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
