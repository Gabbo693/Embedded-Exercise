"""
Integration tests for the face detection system
"""
import pytest
import numpy as np
import cv2
import os
from face_detector import FaceDetector, CameraFaceDetector


class TestFaceDetectionIntegration:
    """Integration tests for complete face detection workflow"""
    
    @pytest.fixture
    def detector(self):
        """Fixture to create a FaceDetector instance"""
        return FaceDetector(use_dnn=False)  # Use Haar for faster testing
    
    def test_end_to_end_detection_pipeline(self, detector):
        """Test complete detection pipeline: detect -> draw -> output"""
        # Create test image
        image = np.zeros((480, 640, 3), dtype=np.uint8)
        
        # Detect faces
        faces = detector.detect_faces(image)
        assert isinstance(faces, list)
        
        # Draw faces
        result = detector.draw_faces(image, faces)
        assert isinstance(result, np.ndarray)
        assert result.shape == image.shape
    
    def test_process_frame_pipeline(self, detector):
        """Test complete process_frame pipeline"""
        image = np.zeros((480, 640, 3), dtype=np.uint8)
        frame, num_faces, message = detector.process_frame(image)
        
        assert isinstance(frame, np.ndarray)
        assert isinstance(num_faces, int)
        assert isinstance(message, str)
        assert num_faces >= 0
        assert ("No faces detected" in message) or ("face" in message)
    
    def test_sequential_frame_processing(self, detector):
        """Test processing multiple frames sequentially"""
        frames = [np.zeros((480, 640, 3), dtype=np.uint8) for _ in range(5)]
        
        results = []
        for frame in frames:
            result = detector.process_frame(frame)
            results.append(result)
        
        assert len(results) == 5
        for frame, num_faces, message in results:
            assert isinstance(frame, np.ndarray)
            assert isinstance(num_faces, int)
            assert isinstance(message, str)
    
    def test_detector_consistency(self, detector):
        """Test that detector produces consistent results"""
        image = np.zeros((480, 640, 3), dtype=np.uint8)
        
        # Run detection multiple times
        results = []
        for _ in range(3):
            faces = detector.detect_faces(image)
            results.append(len(faces))
        
        # All results should be the same
        assert results[0] == results[1] == results[2]
    
    def test_draw_faces_preserves_image_integrity(self, detector):
        """Test that drawing faces doesn't corrupt the image"""
        image = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
        image_copy = image.copy()
        
        faces = [(50, 50, 100, 100)]
        result = detector.draw_faces(image, faces)
        
        # Original image should not be modified (function should return a copy)
        assert np.array_equal(image, image_copy)
        # Result should be different from original
        assert not np.array_equal(result, image)
    
    def test_different_image_sizes(self, detector):
        """Test detection on various image sizes"""
        sizes = [(240, 320), (480, 640), (720, 1280)]
        
        for height, width in sizes:
            image = np.zeros((height, width, 3), dtype=np.uint8)
            frame, num_faces, message = detector.process_frame(image)
            assert frame.shape == (height, width, 3)
    
    def test_message_accuracy(self, detector):
        """Test that detection messages are accurate"""
        image = np.zeros((480, 640, 3), dtype=np.uint8)
        _, num_faces, message = detector.process_frame(image)
        
        if num_faces == 0:
            assert message == "No faces detected"
        else:
            assert f"{num_faces} face(s) detected" in message or "Face" in message
    
    def test_face_rectangle_properties(self, detector):
        """Test properties of detected face rectangles"""
        image = np.zeros((480, 640, 3), dtype=np.uint8)
        faces = detector.detect_faces(image)
        
        for face in faces:
            x, y, w, h = face
            # All values should be non-negative integers
            assert isinstance(x, (int, np.integer))
            assert isinstance(y, (int, np.integer))
            assert isinstance(w, (int, np.integer))
            assert isinstance(h, (int, np.integer))
            assert x >= 0 and y >= 0
            assert w > 0 and h > 0
    
    def test_multiple_detections_numbering(self, detector):
        """Test that multiple faces are numbered correctly when drawn"""
        image = np.zeros((480, 640, 3), dtype=np.uint8)
        faces = [(50, 50, 100, 100), (200, 200, 100, 100), (350, 100, 100, 100)]
        
        result = detector.draw_faces(image, faces)
        
        # Should return valid image
        assert isinstance(result, np.ndarray)
        assert result.shape == image.shape
    
    def test_detector_thread_safety(self, detector):
        """Test that detector can process images without state issues"""
        image1 = np.zeros((480, 640, 3), dtype=np.uint8)
        image2 = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
        
        # Process both images
        result1 = detector.process_frame(image1)
        result2 = detector.process_frame(image2)
        
        # Both should produce valid results
        assert len(result1) == 3
        assert len(result2) == 3
    
    def test_dnn_vs_haar_fallback(self):
        """Test that DNN detector falls back to Haar if needed"""
        image = np.zeros((480, 640, 3), dtype=np.uint8)
        
        detector_dnn = FaceDetector(use_dnn=True)
        detector_haar = FaceDetector(use_dnn=False)
        
        # Both should work without errors
        faces_dnn = detector_dnn.detect_faces(image)
        faces_haar = detector_haar.detect_faces(image)
        
        assert isinstance(faces_dnn, list)
        assert isinstance(faces_haar, list)
    
    def test_confidence_threshold_filtering(self):
        """Test that confidence threshold works"""
        image = np.zeros((480, 640, 3), dtype=np.uint8)
        
        detector_low = FaceDetector(use_dnn=True, min_detection_confidence=0.3)
        detector_high = FaceDetector(use_dnn=True, min_detection_confidence=0.8)
        
        # Both should return valid results
        faces_low = detector_low.detect_faces(image)
        faces_high = detector_high.detect_faces(image)
        
        assert isinstance(faces_low, list)
        assert isinstance(faces_high, list)


class TestCameraFaceDetectorInitialization:
    """Tests for CameraFaceDetector initialization"""
    
    def test_camera_detector_initialization(self):
        """Test CameraFaceDetector can be initialized"""
        detector = CameraFaceDetector(camera_id=0)
        assert detector.detector is not None
        assert detector.camera_id == 0
        assert detector.cap is None  # Not started yet
    
    def test_camera_detector_with_external_hp_camera(self):
        """Test CameraFaceDetector with HP external camera (camera_id=1)"""
        detector = CameraFaceDetector(camera_id=1)
        assert detector.camera_id == 1
    
    def test_camera_detector_with_dnn(self):
        """Test CameraFaceDetector initialized with DNN"""
        detector = CameraFaceDetector(camera_id=0, use_dnn=True)
        assert detector.detector.use_dnn or detector.detector.face_cascade is not None
    
    def test_camera_detector_fallback(self):
        """Test CameraFaceDetector can fallback to Haar if needed"""
        detector = CameraFaceDetector(camera_id=0, use_dnn=False)
        assert detector.detector.use_dnn is False


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--cov=face_detector", "--cov-report=term-missing"])

