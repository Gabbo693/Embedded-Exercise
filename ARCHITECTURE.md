# USB Camera Face Detection System
# Project Architecture & Protocols Summary

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                   Application Layer                          │
│  (Main Menu Interface, User Input Handling)                  │
└────────────────────┬────────────────────────────────────────┘
                     │
        ┌────────────┴──────────────┬──────────────┐
        │                           │              │
┌───────▼──────────┐   ┌───────────▼─────┐  ┌────▼───────────┐
│  Camera Module   │   │ Detection Module │  │ Image Processor │
│ (USBCamera.cpp)  │   │(FaceDetector.cpp)│  │(ImageProc.cpp) │
└────────┬─────────┘   └────────┬────────┘  └─────┬──────────┘
         │                       │                 │
┌────────▼──────────────────────▼─────────────────▼──────────┐
│              OpenCV Library (opencv2)                       │
│  ├─ Video Capture (VideoCapture)                           │
│  ├─ Image Processing (imgproc)                             │
│  ├─ DNN Module (dnn)                                       │
│  ├─ Image Codecs (imgcodecs)                               │
│  └─ GUI (highgui)                                          │
└────────┬───────────────────────────────────────────────────┘
         │
┌────────▼──────────────────────────────────────────────────┐
│         Operating System Layer                             │
│  ├─ Windows: DirectShow/Windows Media Foundation           │
│  ├─ Linux: V4L2 (Video for Linux 2)                        │
│  └─ macOS: AVFoundation/QTKit                              │
└────────┬───────────────────────────────────────────────────┘
         │
┌────────▼──────────────────────────────────────────────────┐
│              Hardware Layer                                │
│  ├─ USB Camera Devices                                     │
│  └─ CPU/GPU                                                │
└──────────────────────────────────────────────────────────┘
```

## Communication Protocols

### 1. USB Video Capture Protocol

**Standard**: USB Video Class (UVC) / DirectShow (Windows) / V4L2 (Linux)

```
Application
    ↓
VideoCapture Object
    ↓
OS Driver (DirectShow/V4L2)
    ↓
USB Device
    
Frame Flow:
USB Device → Driver → Buffer → VideoCapture → Application Memory
```

**Frame Format**:
- Raw: BGR/RGB 24-bit
- Compressed: MJPEG, H.264
- Resolution: 320x240 to 3840x2160
- Frame Rate: 1-120 FPS
- Latency: 33-100ms per frame

### 2. Face Detection Protocols

#### A. Haar Cascade Classifier Protocol
```
Input Image (Mat)
    ↓
Grayscale Conversion
    ↓
Integral Image Computation
    ↓
Multi-scale Scanning (Pyramid)
    ├─ Scale Factor: 1.1
    ├─ Search Step: 1-4 pixels
    ├─ Min Size: 30x30
    └─ Overlapping Windows: Merged
    ↓
Haar Feature Extraction
    ├─ Rectangle Features
    ├─ Edge Features
    └─ Line Features
    ↓
Cascade Classifier (AdaBoost)
    ├─ 20-30 stages
    ├─ 20+ weak classifiers per stage
    └─ Thresholding
    ↓
Non-Maximum Suppression
    ↓
Face Rectangles Output
```

**Performance**: 50-100ms per 640x480 frame
**Accuracy**: 95-99% (frontal faces)
**False Positive Rate**: 5-15%

#### B. Deep Neural Network (DNN) Protocol
```
Input Image (300x300 or 416x416)
    ↓
Normalization & Preprocessing
    ├─ Subtract Mean: [104, 177, 123]
    ├─ Scale: 1.0
    └─ Format: BGR
    ↓
Neural Network Inference
    ├─ Input Layer: 300x300x3
    ├─ Conv Layers (SSD)
    ├─ Multi-scale Feature Maps
    ├─ Detection Layers
    └─ Output: Predictions
    ↓
Post-processing
    ├─ Decode predictions
    ├─ Threshold (confidence > 0.5)
    ├─ NMS (IoU > 0.4)
    └─ Scale to original size
    ↓
Face Rectangles + Confidence Scores
```

**Performance**: 100-200ms per frame
**Accuracy**: 97-99.5% (multiple face orientations)
**False Positive Rate**: 2-5%

### 3. Image Processing Protocol

```
Raw Frame Buffer
    ↓
┌───────────────────────────────────┐
│ Enhancement Chain (Optional)      │
├───────────────────────────────────┤
│ 1. Contrast Enhancement (CLAHE)   │
│    Alpha: 1.2                     │
│    Impact: +15% visibility        │
├───────────────────────────────────┤
│ 2. Bilateral Filter (Denoising)   │
│    Kernel: 9x9                    │
│    Sigma: 75                      │
│    Impact: Reduces noise 30-50%   │
├───────────────────────────────────┤
│ 3. Gaussian Blur (Optional)       │
│    Kernel: 5x5 or 7x7            │
│    Impact: Smoothing             │
└───────────────────────────────────┘
    ↓
Output Mat (Ready for Detection)
```

### 4. Configuration Protocol (JSON)

```json
{
    "camera": {
        "index": <0-255>,          // Device index
        "width": <320-3840>,       // Pixel width
        "height": <240-2160>,      // Pixel height
        "frameRate": <1.0-120.0>   // FPS
    },
    "faceDetection": {
        "enabled": <bool>,         // On/Off
        "method": <"cascade"|"dnn">,
        "confidenceThreshold": <0.0-1.0>,
        "minFaceSize": <10-500>,   // Pixels
        "scaleFactor": <1.01-1.5>
    },
    "output": {
        "autoSave": <bool>,
        "directory": <"path">,
        "displayLiveView": <bool>,
        "imageQuality": <0-100>
    }
}
```

### 5. Logging Protocol

```
[TIMESTAMP] [LEVEL] Message

Format: YYYY-MM-DD HH:MM:SS.mmm [LEVEL] [MODULE] Message

Example:
2026-04-21 15:30:45.123 [INFO ] [Camera] Frame captured: 150 (45.2ms)
2026-04-21 15:30:46.234 [DEBUG] [Detector] 3 faces detected
2026-04-21 15:30:46.456 [ERROR] [FileIO] Cannot save image to path

Levels:
0 = DEBUG   (Detailed diagnostic)
1 = INFO    (General information)
2 = WARNING (Warning messages)
3 = ERROR   (Error conditions)
4 = CRITICAL (Fatal failures)
```

### 6. Threading Protocol

```
Main Thread (UI)
├─ Accept user input
├─ Manage camera state
├─ Save configuration
└─ Display menu

Sync Points:
├─ Mutex: Frame access
├─ Condition Variable: New frame ready
└─ Queue: Frame buffer

Data Flow:
┌─ Camera Thread ─┐
│ Capture Frame   │
│ Detect Faces    │
└─ Process Frame ─┘
    ↓ (via mutex/queue)
┌──── Main Thread ────┐
│ Display Results     │
│ Save to File       │
└─────────────────────┘
```

## API Reference

### USBCamera Class

```cpp
// Connection
bool connect(int cameraIndex = 1);
bool disconnect();
bool isConnected() const;

// Capture
bool captureFrame();
cv::Mat getFrame() const;
cv::Mat getFrameWithDetections() const;

// Settings
bool setResolution(int width, int height);
bool setFrameRate(double fps);
bool setBrightness(double brightness);

// Statistics
int getFrameCount() const;
double getFPS() const;
std::string getStatistics() const;
```

### FaceDetector Class

```cpp
// Initialization
bool initializeCascade(const std::string& cascadePath);
bool initializeDNN(const std::string& modelPath, 
                   const std::string& configPath,
                   const std::string& framework);

// Detection
std::vector<FaceResult> detectFaces(const cv::Mat& image,
                                    float confidenceThreshold = 0.5f);
cv::Mat detectAndDraw(const cv::Mat& image,
                      const cv::Scalar& color = cv::Scalar(0, 255, 0));

// Configuration
void setScaleFactor(double scale);
void setMinNeighbors(int minNeighbors);
void setConfidenceThreshold(float threshold);
```

### ImageProcessor Class

```cpp
// Enhancement
static cv::Mat enhanceContrast(const cv::Mat& image);
static cv::Mat reduceThermalNoise(const cv::Mat& image);

// Conversion
static cv::Mat convertToGrayscale(const cv::Mat& image);
static cv::Mat convertToHSV(const cv::Mat& image);

// Analysis
static double calculateImageSharpness(const cv::Mat& image);
static double calculateBrightness(const cv::Mat& image);

// I/O
static bool saveImage(const cv::Mat& image,
                      const std::string& filePath,
                      int quality = 95);
```

## Performance Metrics

| Component | Metric | Value |
|-----------|--------|-------|
| Frame Capture | Latency | <16ms |
| Frame Capture | Buffer Size | ~5MB |
| Haar Detection | Time | 50-100ms |
| DNN Detection | Time | 100-200ms |
| Image Saving | Time | 50-200ms |
| Total Pipeline | Time | <300ms |
| Memory Usage | App | ~100MB |
| Memory Usage | Models | 50-100MB |

## Error Codes

```
0x00 = Success
0x01 = Camera not found
0x02 = Camera connection failed
0x03 = Invalid resolution
0x04 = Face detection model not found
0x05 = Invalid configuration file
0x06 = File I/O error
0x07 = Insufficient memory
0x08 = Invalid frame data
0x09 = Detection timeout
0x0A = Frame capture timeout
```

## Optimization Strategies

1. **Resolution Scaling**
   - Capture at 1280x720 → Detect on 640x360
   - 4x reduction in detection area

2. **Frame Skipping**
   - Capture every frame
   - Detect every 2nd or 3rd frame
   - Display all frames

3. **GPU Acceleration**
   - CUDA for DNN inference
   - OpenCL for image processing
   - 5-10x speedup

4. **Model Optimization**
   - Quantization (FP32 → INT8)
   - Pruning (remove redundant layers)
   - 2-4x faster inference

## Deployment Checklist

- [ ] Build tested on target platform
- [ ] All dependencies installed
- [ ] Configuration files validated
- [ ] Face detection models available
- [ ] Output directory writable
- [ ] Logging enabled
- [ ] Performance benchmarked
- [ ] Error handling verified
- [ ] Documentation complete
- [ ] Version control initialized

---

**Document Version**: 1.0
**Last Updated**: April 21, 2026
