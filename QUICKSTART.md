# Quick Start Guide

## Installation & Setup

### 1. Install Dependencies

**Windows:**
```bash
# Using vcpkg (recommended)
vcpkg install opencv:x64-windows nlohmann-json:x64-windows

# Set environment variables
set OpenCV_DIR=C:\path\to\opencv\build
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get install -y \
    libopencv-dev \
    cmake \
    build-essential

# Install nlohmann-json
sudo apt-get install nlohmann-json3-dev
```

**macOS:**
```bash
brew install opencv cmake nlohmann-json
```

### 2. Build the Project

**Windows:**
```bash
cd "c:\Users\User\Desktop\Milestone A"
build.bat
```

**Linux/macOS:**
```bash
cd ~/Desktop/Milestone\ A
chmod +x build.sh
./build.sh
```

### 3. Run the Application

**Windows:**
```bash
cd build
./bin/usb_camera_app.exe
```

**Linux/macOS:**
```bash
cd build
./bin/usb_camera_app
```

## First Run

1. **Connect Camera** (Option 1)
   - Select option 1 from main menu
   - Enter camera index (usually 0 for default)
   - Wait for connection confirmation

2. **Enable Face Detection** (Option 4)
   - Select option 4 from main menu
   - Press Enter to use default cascade file
   - Or provide custom cascade XML path

3. **Live Preview** (Option 8)
   - Select option 8 to see real-time camera feed
   - Faces will be highlighted with green rectangles
   - Press ESC to exit preview

4. **Capture Image** (Option 3)
   - With face detection enabled
   - Select option 3 to capture
   - Enter filename (e.g., my_photo.jpg)
   - Image saved to output/ folder

## Configuration

Edit `config/default_config.json` to customize:

```json
{
    "camera": {
        "width": 1280,       // Change resolution
        "height": 720,
        "frameRate": 30.0    // Change FPS
    },
    "faceDetection": {
        "method": "cascade"  // Use "cascade" or "dnn"
    }
}
```

## Troubleshooting

### Camera Not Found
```
Issue: "Cannot open USB camera"
Solution:
1. Check USB connection
2. Try different camera index (1, 2, 3)
3. Test with: lsusb (Linux) or Device Manager (Windows)
```

### Face Detection Not Working
```
Issue: No faces detected even with clear faces visible
Solution:
1. Verify cascade file location
2. Try different cascade variant:
   - haarcascade_frontalface_default.xml (best)
   - haarcascade_frontalface_alt.xml
   - haarcascade_frontalface_alt2.xml
3. Adjust lighting conditions
4. Ensure faces are frontal (not rotated)
```

### Build Errors
```
Issue: CMake can't find OpenCV
Solution:
Windows:
  set OpenCV_DIR=C:\opencv\build
  
Linux:
  export OpenCV_DIR=/usr/local/opencv/build
  
macOS:
  export OpenCV_DIR=/usr/local/Cellar/opencv/
```

### Slow Performance
```
Issue: Low FPS or choppy preview
Solution:
1. Reduce resolution (640x480 instead of 1280x720)
2. Disable live preview for faster capture
3. Use Haar Cascade instead of DNN
4. Close other applications
5. Update graphics drivers
```

## Key Directories

| Directory | Purpose |
|-----------|---------|
| `include/` | Header files |
| `src/` | Implementation files |
| `output/` | Captured images |
| `config/` | Configuration files |
| `models/` | ML model files (if using DNN) |
| `build/` | Compiled binaries |

## Useful Commands

```bash
# List available cameras
lsusb                          # Linux
wmic logicaldisk get name      # Windows

# Test camera access
v4l2-ctl --list-devices       # Linux (V4L2)

# View application log
type camera_app.log            # Windows
cat camera_app.log             # Linux/macOS

# Clean build
rm -rf build                   # Linux/macOS
rmdir /s /q build              # Windows

# Rebuild from scratch
./build.sh  # Linux/macOS
build.bat   # Windows
```

## Testing

Run the test suite to verify installation:

```bash
cd build
./bin/test_camera              # Linux/macOS
.\bin\test_camera.exe          # Windows
```

## Next Steps

1. ✅ Build the project
2. ✅ Run application with connected USB camera
3. ✅ Enable face detection
4. ✅ Capture some images
5. 📊 Check output/ folder for results
6. 📝 Review camera_app.log for diagnostics
7. ⚙️ Customize config/default_config.json
8. 🚀 Deploy to production

## Advanced Usage

### Custom Face Detection Models

```cpp
FaceDetector detector;

// Use DNN instead of Haar Cascade
detector.initializeDNN(
    "model.caffemodel",
    "deploy.prototxt",
    "caffe"
);

// Or TensorFlow
detector.initializeDNN(
    "model.pb",
    "model.pbtxt",
    "tensorflow"
);
```

### Batch Processing

```cpp
for (const auto& image_path : image_list) {
    cv::Mat image = cv::imread(image_path);
    auto faces = detector.detectFaces(image);
    
    // Process each face
    for (const auto& face : faces) {
        // Extract face ROI
        cv::Mat face_roi = image(face.boundingBox);
    }
}
```

### Performance Monitoring

```bash
# Check real-time performance
tail -f camera_app.log | grep "Frame captured"

# Monitor system resources
top -p PID                    # Linux
Get-Process usb_camera_app    # Windows
```

## Support & Help

- 📖 Check README.md for full documentation
- 🔧 Review include/Protocols.h for technical details
- 📊 Check logs: camera_app.log
- 🤝 Refer to OpenCV documentation: https://docs.opencv.org/

## Version Info

- **Project**: USB Camera Face Detection System
- **Version**: 1.0.0
- **Status**: Production Ready
- **Last Updated**: April 21, 2026

---

Enjoy! 🎉
