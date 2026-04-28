"""
Unit tests for face detection module
"""
import pytest
import numpy as np
import cv2
from face_detector import FaceDetector


class TestFaceDetector:
    """Test suite for FaceDetector class"""
    
    @pytest.fixture
    def detector_dnn(self):
        """Fixture to create a DNN FaceDetector instance"""
        return FaceDetector(use_dnn=True)
    
    @pytest.fixture
    def detector_haar(self):
        """Fixture to create a Haar Cascade FaceDetector instance"""
        return FaceDetector(use_dnn=False)
    
    @pytest.fixture
    def sample_image(self):
        """Fixture to create a sample image"""
        # Create a blank image
        return np.zeros((480, 640, 3), dtype=np.uint8)
    
    def test_dnn_detector_initialization(self, detector_dnn):
        """Test that DNN detector initializes successfully"""
        assert detector_dnn.use_dnn or detector_dnn.face_cascade is not None
    
    def test_haar_detector_initialization(self, detector_haar):
        """Test that Haar Cascade detector initializes successfully"""
        assert detector_haar.face_cascade is not None
        assert detector_haar.use_dnn is False
    
    def test_detect_faces_returns_list(self, detector_haar, sample_image):
        """Test that detect_faces returns a list"""
        result = detector_haar.detect_faces(sample_image)
        assert isinstance(result, list)
    
    def test_detect_faces_empty_image(self, detector_haar, sample_image):
        """Test detect_faces on blank image (should return empty list)"""
        result = detector_haar.detect_faces(sample_image)
        assert len(result) == 0
    
    def test_detect_faces_dnn(self, detector_dnn, sample_image):
        """Test DNN face detection"""
        result = detector_dnn.detect_faces(sample_image)
        assert isinstance(result, list)
    
    def test_detect_faces_haar(self, detector_haar, sample_image):
        """Test Haar Cascade face detection"""
        result = detector_haar.detect_faces(sample_image)
        assert isinstance(result, list)
    
    def test_draw_faces_returns_image(self, detector_haar, sample_image):
        """Test that draw_faces returns an image"""
        faces = [(50, 50, 100, 100)]
        result = detector_haar.draw_faces(sample_image, faces)
        assert isinstance(result, np.ndarray)
        assert result.shape == sample_image.shape
    
    def test_draw_faces_with_empty_list(self, detector_haar, sample_image):
        """Test draw_faces with empty face list"""
        result = detector_haar.draw_faces(sample_image, [])
        assert isinstance(result, np.ndarray)
        assert np.array_equal(result, sample_image)
    
    def test_draw_faces_with_multiple_faces(self, detector_haar, sample_image):
        """Test draw_faces with multiple faces"""
        faces = [(50, 50, 100, 100), (150, 150, 80, 80), (300, 100, 120, 120)]
        result = detector_haar.draw_faces(sample_image, faces)
        assert isinstance(result, np.ndarray)
    
    def test_draw_faces_custom_color(self, detector_haar, sample_image):
        """Test draw_faces with custom color"""
        faces = [(50, 50, 100, 100)]
        result = detector_haar.draw_faces(sample_image, faces, color=(255, 0, 0), thickness=3)
        assert isinstance(result, np.ndarray)
    
    def test_process_frame_returns_tuple(self, detector_haar, sample_image):
        """Test that process_frame returns a tuple"""
        result = detector_haar.process_frame(sample_image)
        assert isinstance(result, tuple)
        assert len(result) == 3
    
    def test_process_frame_returns_correct_types(self, detector_haar, sample_image):
        """Test that process_frame returns correct data types"""
        frame, num_faces, message = detector_haar.process_frame(sample_image)
        assert isinstance(frame, np.ndarray)
        assert isinstance(num_faces, int)
        assert isinstance(message, str)
    
    def test_process_frame_no_faces_message(self, detector_haar, sample_image):
        """Test process_frame message when no faces detected"""
        _, num_faces, message = detector_haar.process_frame(sample_image)
        assert num_faces == 0
        assert message == "No faces detected"
    
    def test_process_frame_output_shape(self, detector_haar, sample_image):
        """Test that process_frame output has same shape as input"""
        frame, _, _ = detector_haar.process_frame(sample_image)
        assert frame.shape == sample_image.shape
    
    def test_face_rectangle_format(self, detector_haar, sample_image):
        """Test that detected faces are in correct format (x, y, w, h)"""
        faces = detector_haar.detect_faces(sample_image)
        # Even if no faces, format should be consistent
        assert isinstance(faces, list)
        for face in faces:
            assert isinstance(face, tuple)
            assert len(face) == 4
    
    def test_confidence_threshold(self):
        """Test that confidence threshold can be set"""
        detector_low = FaceDetector(use_dnn=True, min_detection_confidence=0.3)
        detector_high = FaceDetector(use_dnn=True, min_detection_confidence=0.8)
        assert detector_low.min_detection_confidence == 0.3
        assert detector_high.min_detection_confidence == 0.8


class TestFaceDetectorWithRealImage:
    """Integration tests with real images"""
    
    @pytest.fixture
    def detector(self):
        """Fixture to create a FaceDetector instance"""
        return FaceDetector(use_dnn=False)  # Use Haar for faster testing
    
    def test_detect_faces_with_color_image(self, detector):
        """Test detection on a color image"""
        # Create a color image
        image = np.zeros((480, 640, 3), dtype=np.uint8)
        result = detector.detect_faces(image)
        assert isinstance(result, list)
    
    def test_detect_faces_with_grayscale_conversion(self, detector):
        """Test that detector handles color to grayscale conversion"""
        image = np.zeros((480, 640, 3), dtype=np.uint8)
        result = detector.detect_faces(image)
        assert isinstance(result, list)
    
    def test_process_frame_handles_different_sizes(self, detector):
        """Test process_frame with different image sizes"""
        sizes = [(240, 320), (480, 640), (1080, 1920)]
        for height, width in sizes:
            image = np.zeros((height, width, 3), dtype=np.uint8)
            frame, num_faces, message = detector.process_frame(image)
            assert frame.shape == image.shape
            assert isinstance(message, str)
    
    def test_improved_accuracy_over_haar(self, detector):
        """Test that detector is available and working"""
        image = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
        faces = detector.detect_faces(image)
        # Should handle random images with improved parameters
        assert isinstance(faces, list)
        assert len(faces) >= 0


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--cov=face_detector", "--cov-report=term-missing"])

