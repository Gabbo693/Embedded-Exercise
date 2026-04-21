#ifndef PROTOCOLS_H
#define PROTOCOLS_H

/*
 * USB CAMERA FACE DETECTION SYSTEM - PROTOCOLS DOCUMENTATION
 * 
 * This system implements the following communication and detection protocols:
 */

// ============================================================================
// 1. VIDEO CAPTURE PROTOCOL (USB/DirectShow)
// ============================================================================
/*
 * Backend: OpenCV VideoCapture (DirectShow on Windows, V4L2 on Linux)
 * 
 * Features:
 * - Automatic device enumeration
 * - Multi-camera support
 * - Resolution configuration
 * - Frame rate control
 * - Brightness/Contrast/Saturation adjustment
 * - Real-time frame capture
 * 
 * Specifications:
 * - Supported Formats: MJPEG, YUV422, RGB, BGR
 * - Max Resolution: 4K+ (depends on hardware)
 * - Frame Rate: 1-120 FPS (typical cameras: 30 FPS)
 * - Latency: <50ms per frame
 */

// ============================================================================
// 2. FACE DETECTION PROTOCOLS
// ============================================================================

/*
 * A) Haar Cascade Classifier Protocol
 * 
 * Standard: Haar Feature-based Cascade Classifiers (OpenCV)
 * 
 * Features:
 * - Pre-trained frontal face detector
 * - Fast real-time detection
 * - Scalable search
 * - False positive control
 * 
 * Parameters:
 * - Scale Factor: 1.1 (pyramid scale)
 * - Min Neighbors: 4 (false positive reduction)
 * - Min Face Size: 30x30 pixels
 * - Detection Time: ~50-100ms per frame
 * 
 * Files:
 * - haarcascade_frontalface_default.xml
 * - haarcascade_frontalface_alt.xml
 * - haarcascade_frontalface_alt2.xml
 */

/*
 * B) Deep Neural Network (DNN) Protocol
 * 
 * Supported Models:
 * 1. Caffe Framework
 *    - res10_300x300_ssd_iter_140000.caffemodel
 *    - deploy.prototxt
 * 
 * 2. TensorFlow
 *    - opencv_face_detector_uint8.pb
 *    - opencv_face_detector.pbtxt
 * 
 * 3. ONNX Runtime
 *    - face_detection.onnx
 * 
 * Features:
 * - Higher accuracy than Haar Cascade
 * - Multi-scale face detection
 * - Confidence scores
 * - Handles rotations (up to 45°)
 * 
 * Input Size: 300x300 or 416x416 (depends on model)
 * Confidence Threshold: 0.5-0.8 (configurable)
 * Detection Time: ~100-200ms per frame
 */

// ============================================================================
// 3. IMAGE PROCESSING PROTOCOL
// ============================================================================

/*
 * Enhancement Methods:
 * 
 * 1. Contrast Enhancement (CLAHE)
 *    - Alpha: 1.2
 *    - Improves visibility in low-light conditions
 * 
 * 2. Noise Reduction (Bilateral Filter)
 *    - Kernel Size: 9
 *    - Diameter: 75 pixels
 *    - Preserves edges while reducing thermal noise
 * 
 * 3. Color Space Conversions
 *    - BGR/RGB Standard
 *    - Grayscale for processing
 *    - HSV for color-based detection
 *    - LAB for perceptual uniformity
 * 
 * 4. Image Analysis
 *    - Sharpness: Laplacian variance
 *    - Brightness: Mean pixel intensity
 *    - Histogram: 256-bin analysis
 */

// ============================================================================
// 4. DATA STORAGE PROTOCOL
// ============================================================================

/*
 * Format Support:
 * - JPEG: Quality 95%, Compression enabled
 * - PNG: Lossless, Metadata support
 * - BMP: Uncompressed, Full color depth
 * 
 * Directory Structure:
 * /output/          - Captured images
 * /config/          - Configuration files (JSON)
 * /logs/            - Application logs
 * /models/          - Pre-trained ML models
 * 
 * Metadata:
 * - Timestamp
 * - Resolution
 * - Face count
 * - Detection confidence
 * - Processing time
 */

// ============================================================================
// 5. CONFIGURATION PROTOCOL (JSON)
// ============================================================================

/*
 * Schema:
 * 
 * {
 *   "camera": {
 *     "index": 0-255,              // Camera device index
 *     "width": 320-3840,           // Frame width (pixels)
 *     "height": 240-2160,          // Frame height (pixels)
 *     "frameRate": 1.0-120.0       // Frames per second
 *   },
 *   "faceDetection": {
 *     "enabled": true/false,       // Enable face detection
 *     "method": "cascade|dnn",     // Detection method
 *     "confidenceThreshold": 0.0-1.0  // Confidence threshold
 *   },
 *   "output": {
 *     "autoSave": true/false,      // Auto-save images
 *     "directory": "string",       // Output directory
 *     "displayLiveView": true/false // Show preview
 *   }
 * }
 */

// ============================================================================
// 6. LOGGING PROTOCOL
// ============================================================================

/*
 * Log Levels:
 * - DEBUG (0): Detailed diagnostic info
 * - INFO (1): General information
 * - WARNING (2): Warning messages
 * - ERROR (3): Error conditions
 * - CRITICAL (4): Critical failures
 * 
 * Format: [YYYY-MM-DD HH:MM:SS.mmm] [LEVEL] Message
 * 
 * Output Destinations:
 * - Console (stdout/stderr)
 * - File (camera_app.log)
 * - Rotation: 10MB per file
 */

// ============================================================================
// 7. THREADING PROTOCOL
// ============================================================================

/*
 * Main Thread:
 * - User interface
 * - Command processing
 * - Configuration management
 * 
 * Camera Thread:
 * - Frame capture (continuous)
 * - Face detection (async)
 * - Image processing
 * 
 * Synchronization:
 * - Mutex locks for frame access
 * - Queue-based frame buffering
 * - Thread-safe logging
 */

// ============================================================================
// 8. ERROR HANDLING PROTOCOL
// ============================================================================

/*
 * Exception Types:
 * - Camera not connected
 * - Invalid resolution
 * - Face detection model not found
 * - Invalid configuration file
 * - File I/O errors
 * - Memory allocation failures
 * 
 * Recovery Actions:
 * - Automatic reconnection attempts
 * - Graceful degradation
 * - Detailed error logging
 * - User notifications
 */

// ============================================================================
// 9. PERFORMANCE OPTIMIZATION PROTOCOL
// ============================================================================

/*
 * Real-time Performance Targets:
 * - Frame Capture: <16ms (60 FPS)
 * - Face Detection (Cascade): 50-100ms
 * - Face Detection (DNN): 100-200ms
 * - Image Saving: 50-200ms
 * - Total Pipeline: <300ms per frame
 * 
 * Memory Management:
 * - Frame Buffer: ~5MB per HD frame
 * - Model Cache: 50-100MB (DNN models)
 * - Log Rotation: Max 100MB per session
 * 
 * Optimization Techniques:
 * - Image downsampling for detection
 * - GPU acceleration support (CUDA)
 * - Frame skipping in high load
 * - Efficient matrix operations (OpenCV optimized)
 */

// ============================================================================
// 10. SECURITY PROTOCOL
// ============================================================================

/*
 * Data Protection:
 * - No network transmission (local processing)
 * - No cloud uploads by default
 * - Output directory access control
 * - Configuration file encryption (optional)
 * 
 * Privacy:
 * - Automatic face cropping
 * - Metadata anonymization
 * - Secure temporary file handling
 * - Audit logging
 */

#endif // PROTOCOLS_H
