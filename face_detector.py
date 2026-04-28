"""
Face Detection Module - Detects faces in camera stream and draws bounding boxes
Uses OpenCV DNN for high accuracy face detection (trained on pre-existing models)
"""
import cv2
import numpy as np
from typing import List, Tuple
import os


class FaceDetector:
    """Detects faces in images using OpenCV DNN with high accuracy"""
    
    def __init__(self, use_dnn: bool = True, min_detection_confidence: float = 0.5):
        """
        Initialize the face detector
        
        Args:
            use_dnn: Use OpenCV DNN (True) for high accuracy or Haar Cascade (False)
            min_detection_confidence: Confidence threshold (0.0-1.0)
        """
        self.use_dnn = use_dnn
        self.min_detection_confidence = min_detection_confidence
        self.net = None
        self.face_cascade = None
        
        if use_dnn:
            self._init_dnn_detector()
        else:
            self._init_haar_cascade()
    
    def _init_dnn_detector(self):
        """Initialize OpenCV DNN face detector with pre-trained model"""
        try:
            # Use OpenCV's pre-trained SSD model for face detection
            model_file = cv2.data.haarcascades.replace('haarcascades', '') + 'opencv_face_detector_uint8.pb'
            config_file = cv2.data.haarcascades.replace('haarcascades', '') + 'opencv_face_detector.pbtxt'
            
            # If model files don't exist, download or use alternative
            if os.path.exists(model_file) and os.path.exists(config_file):
                self.net = cv2.dnn.readNetFromTensorflow(model_file, config_file)
            else:
                # Fallback: use Haar Cascade if DNN models not available
                print("DNN models not found locally, using Haar Cascade")
                self.use_dnn = False
                self._init_haar_cascade()
        except Exception as e:
            print(f"DNN initialization warning: {e}, falling back to Haar Cascade")
            self.use_dnn = False
            self._init_haar_cascade()
    
    def _init_haar_cascade(self):
        """Initialize Haar Cascade fallback - improved parameters"""
        cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_alt2.xml'
        self.face_cascade = cv2.CascadeClassifier(cascade_path)
        if self.face_cascade.empty():
            # Try alternative cascade if first one fails
            cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
            self.face_cascade = cv2.CascadeClassifier(cascade_path)
            if self.face_cascade.empty():
                raise ValueError(f"Failed to load cascade classifier")

    
    def detect_faces(self, image: np.ndarray) -> List[Tuple[int, int, int, int]]:
        """
        Detect faces in an image
        
        Args:
            image: Input image as BGR numpy array
            
        Returns:
            List of face rectangles (x, y, w, h)
        """
        if self.use_dnn and self.net is not None:
            return self._detect_faces_dnn(image)
        else:
            return self._detect_faces_haar(image)
    
    def _detect_faces_dnn(self, image: np.ndarray) -> List[Tuple[int, int, int, int]]:
        """Detect faces using OpenCV DNN"""
        h, w, _ = image.shape
        blob = cv2.dnn.blobFromImage(image, 1.0, (300, 300), [104, 117, 123], False, False)
        self.net.setInput(blob)
        detections = self.net.forward()
        
        faces = []
        for i in range(detections.shape[2]):
            confidence = detections[0, 0, i, 2]
            if confidence > self.min_detection_confidence:
                box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
                x, y, x_end, y_end = box.astype(int)
                
                # Convert to (x, y, w, h) format
                face_w = max(1, x_end - x)
                face_h = max(1, y_end - y)
                
                # Ensure coordinates are within bounds
                x = max(0, min(x, w - 1))
                y = max(0, min(y, h - 1))
                face_w = min(face_w, w - x)
                face_h = min(face_h, h - y)
                
                faces.append((x, y, face_w, face_h))
        
        return faces
    
    def _detect_faces_haar(self, image: np.ndarray) -> List[Tuple[int, int, int, int]]:
        """Detect faces using Haar Cascade with improved parameters"""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Strict parameters to prevent nose/partial face detection
        # Higher minNeighbors prevents detecting just a nose or part of a face
        faces = self.face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.05,    # Smaller scale factor for careful detection
            minNeighbors=8,      # STRICT threshold - prevents partial detections (nose, etc.)
            flags=cv2.CASCADE_SCALE_IMAGE,
            minSize=(40, 40),    # Minimum face size (prevents tiny false positives)
            maxSize=(350, 350)   # Maximum face size (prevents detecting large regions as face)
        )
        
        return list(faces)
    
    def draw_faces(self, image: np.ndarray, faces: List[Tuple[int, int, int, int]], 
                   color: Tuple[int, int, int] = (0, 255, 0), thickness: int = 2) -> np.ndarray:
        """
        Draw bounding boxes and numbers on detected faces
        
        Args:
            image: Input image
            faces: List of face rectangles
            color: Color of bounding boxes (BGR)
            thickness: Thickness of bounding box lines
            
        Returns:
            Image with drawn faces
        """
        result = image.copy()
        
        for idx, (x, y, w, h) in enumerate(faces, 1):
            # Draw rectangle around face
            cv2.rectangle(result, (x, y), (x + w, y + h), color, thickness)
            
            # Draw face number
            text = f"Face {idx}"
            font = cv2.FONT_HERSHEY_SIMPLEX
            font_scale = 0.6
            font_thickness = 2
            text_size = cv2.getTextSize(text, font, font_scale, font_thickness)[0]
            
            # Draw background for text
            cv2.rectangle(result, (x, y - 25), (x + text_size[0] + 5, y), color, -1)
            cv2.putText(result, text, (x + 2, y - 7), font, font_scale, (0, 0, 0), font_thickness)
        
        return result
    
    def process_frame(self, frame: np.ndarray) -> Tuple[np.ndarray, int, str]:
        """
        Process a single frame: detect faces and draw them
        
        Args:
            frame: Input frame
            
        Returns:
            Tuple of (processed_frame, num_faces, message)
        """
        faces = self.detect_faces(frame)
        processed_frame = self.draw_faces(frame, faces)
        
        num_faces = len(faces)
        if num_faces == 0:
            message = "No faces detected"
        else:
            message = f"{num_faces} face(s) detected"
        
        return processed_frame, num_faces, message


class CameraFaceDetector:
    """Real-time face detection from camera"""
    
    def __init__(self, camera_id: int = 0, use_dnn: bool = True, auto_detect: bool = False):
        """
        Initialize camera face detector
        
        Args:
            camera_id: ID of the camera device (0 for default, 1 for external HP camera, etc.)
            use_dnn: Use OpenCV DNN (True) for high accuracy
            auto_detect: Automatically detect best available camera (True = try 1, then 0)
        """
        self.detector = FaceDetector(use_dnn=use_dnn)
        self.camera_id = camera_id
        self.cap = None
        self.auto_detect = auto_detect
    
    def _check_camera_available(self, camera_id: int) -> bool:
        """Check if a camera device is available"""
        try:
            cap = cv2.VideoCapture(camera_id)
            if cap.isOpened():
                # Verify we can actually read from it
                ret, _ = cap.read()
                cap.release()
                return ret
            return False
        except:
            return False
    
    def _find_available_camera(self) -> int:
        """Find the best available camera (prefers external camera ID 1)"""
        # Try external camera first
        print("Detecting available cameras...")
        
        # Try camera 1 (external HP camera)
        if self._check_camera_available(1):
            print("  ✓ Found external camera at ID 1 (HP camera)")
            return 1
        else:
            print("  ✗ External camera not found at ID 1")
        
        # Fall back to camera 0 (default)
        if self._check_camera_available(0):
            print("  ✓ Found default camera at ID 0 (laptop camera)")
            return 0
        else:
            print("  ✗ Default camera not found at ID 0")
        
        # No camera found
        raise RuntimeError("No camera devices found!")
    
    def start_detection(self):
        """Start real-time face detection from camera"""
        # Auto-detect best camera if enabled
        if self.auto_detect:
            best_camera = self._find_available_camera()
            self.camera_id = best_camera
        
        self.cap = cv2.VideoCapture(self.camera_id)
        
        if not self.cap.isOpened():
            raise RuntimeError(f"Failed to open camera device {self.camera_id}")
        
        # Verify we can read from it
        ret, _ = self.cap.read()
        if not ret:
            self.cap.release()
            raise RuntimeError(f"Camera {self.camera_id} opened but cannot read frames")
        
        camera_desc = "external (HP)" if self.camera_id == 1 else "default (laptop)"
        print(f"\n✓ Successfully connected to {camera_desc} camera (ID: {self.camera_id})")
        print("Using Haar Cascade detector with strict parameters")
        print("Press 'q' to quit...\n")
        
        try:
            frame_count = 0
            while True:
                ret, frame = self.cap.read()
                
                if not ret:
                    print("Failed to read frame from camera")
                    break
                
                processed_frame, num_faces, message = self.detector.process_frame(frame)
                
                # Display message at top of frame
                cv2.putText(processed_frame, message, (10, 30), 
                           cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                
                # Show frame
                cv2.imshow('Face Detection', processed_frame)
                
                frame_count += 1
                
                # Press 'q' to exit
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    print(f"\nProcessed {frame_count} frames. Exiting...")
                    break
        
        finally:
            self.stop_detection()
    
    def stop_detection(self):
        """Stop camera and close windows"""
        if self.cap:
            self.cap.release()
        cv2.destroyAllWindows()


def main():
    """Main entry point - auto-detects best available camera"""
    try:
        # Create detector with auto-detect enabled (will try camera 1 first, then 0)
        detector = CameraFaceDetector(camera_id=1, use_dnn=False, auto_detect=True)
        detector.start_detection()
    except RuntimeError as e:
        print(f"Error: {e}")
        raise


if __name__ == "__main__":
    main()

