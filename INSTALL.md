# Installation Guide

## System Requirements

### Minimum Requirements
- **OS**: Windows 7+, Ubuntu 16.04+, macOS 10.12+
- **CPU**: Dual-core processor (2 GHz or higher)
- **RAM**: 2GB minimum, 4GB recommended
- **Storage**: 500MB free space
- **USB**: USB 2.0 camera

### Recommended Requirements
- **OS**: Windows 10/11, Ubuntu 20.04+, macOS 12+
- **CPU**: Quad-core processor (3 GHz or higher)
- **RAM**: 8GB or more
- **Storage**: SSD with 1GB free space
- **USB**: USB 3.0 camera
- **GPU**: NVIDIA (CUDA) or AMD (OpenCL) for acceleration

## Step-by-Step Installation

### Windows Installation

#### 1. Install Visual Studio Build Tools
```bash
# Download from: https://visualstudio.microsoft.com/visual-cpp-build-tools/
# Install C++ build tools
```

#### 2. Install CMake
```bash
# Option 1: Using Chocolatey
choco install cmake

# Option 2: Download from https://cmake.org/download/
# Add to PATH
```

#### 3. Install OpenCV
**Option A: Using vcpkg (Recommended)**
```bash
# Clone vcpkg
git clone https://github.com/Microsoft/vcpkg.git
cd vcpkg

# Build vcpkg
.\bootstrap-vcpkg.bat

# Install OpenCV
.\vcpkg install opencv:x64-windows
.\vcpkg install nlohmann-json:x64-windows

# Integrate with Visual Studio
.\vcpkg integrate install
```

**Option B: Manual Installation**
```bash
# Download from https://github.com/opencv/opencv/releases
# Extract to C:\opencv

# Build OpenCV
cd C:\opencv
mkdir build
cd build
cmake -G "Visual Studio 16 2019" -A x64 ..
cmake --build . --config Release
cmake --install .

# Set environment variable
setx OpenCV_DIR "C:\opencv\build"
```

#### 4. Install nlohmann JSON
```bash
# Using vcpkg (already done above)

# Or manual:
git clone https://github.com/nlohmann/json.git
cd json
mkdir build
cd build
cmake ..
cmake --install .
```

#### 5. Build the Project
```bash
cd "c:\Users\User\Desktop\Milestone A"
build.bat
```

---

### Linux Installation (Ubuntu/Debian)

#### 1. Install Dependencies
```bash
sudo apt-get update
sudo apt-get install -y \
    build-essential \
    cmake \
    git \
    libopencv-dev \
    nlohmann-json3-dev \
    pkg-config
```

#### 2. Install OpenCV (Optional - if not in package manager)
```bash
# Check if libopencv-dev is sufficient
pkg-config --modversion opencv

# If manual build needed:
git clone https://github.com/opencv/opencv.git
cd opencv
mkdir build
cd build
cmake -DCMAKE_BUILD_TYPE=Release ..
make -j$(nproc)
sudo make install
sudo ldconfig
```

#### 3. Build the Project
```bash
cd ~/Desktop/Milestone\ A
chmod +x build.sh
./build.sh
```

---

### macOS Installation

#### 1. Install Homebrew
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

#### 2. Install Dependencies
```bash
brew install opencv cmake nlohmann-json
```

#### 3. Build the Project
```bash
cd ~/Desktop/Milestone\ A
chmod +x build.sh
./build.sh
```

---

## Face Detection Models

### Haar Cascade Models

Models should be placed in `models/` directory or obtained from OpenCV installation.

**Default Location**:
- Windows: `C:\opencv\data\haarcascades\`
- Linux: `/usr/local/share/opencv4/haarcascades/`
- macOS: `/usr/local/Cellar/opencv/.../ haarcascades/`

**Available Models**:
```
haarcascade_frontalface_default.xml      (Best for frontal faces)
haarcascade_frontalface_alt.xml          (Alternative 1)
haarcascade_frontalface_alt2.xml         (Alternative 2)
haarcascade_frontalface_alt_tree.xml     (Tree-based)
```

**Usage**:
```cpp
camera.enableFaceDetection("models/haarcascade_frontalface_default.xml");
```

### DNN Models (Optional)

For higher accuracy, download and place in `models/`:

**Caffe Model**:
```bash
cd models
wget https://raw.githubusercontent.com/opencv/opencv_3rdparty/dnn_samples_face_detector_20170830/res10_300x300_ssd_iter_140000.caffemodel
wget https://raw.githubusercontent.com/opencv/opencv/master/samples/dnn/face_detector/deploy.prototxt
```

**TensorFlow Model**:
```bash
cd models
wget https://raw.githubusercontent.com/opencv/opencv_3rdparty/dnn_samples_face_detector_20170830/opencv_face_detector_uint8.pb
wget https://raw.githubusercontent.com/opencv/opencv/master/samples/dnn/face_detector/opencv_face_detector.pbtxt
```

---

## Post-Installation Configuration

### 1. Create Required Directories
```bash
# Windows
mkdir output config logs

# Linux/macOS
mkdir -p output config logs
```

### 2. Configure Default Settings
Edit `config/default_config.json`:
```json
{
    "camera": {
        "index": 0,
        "width": 1280,
        "height": 720,
        "frameRate": 30.0
    },
    "faceDetection": {
        "enabled": true,
        "method": "cascade",
        "confidenceThreshold": 0.5
    },
    "output": {
        "autoSave": false,
        "directory": "./output",
        "displayLiveView": true
    }
}
```

### 3. Verify Installation

**Run Test Suite**:
```bash
# Windows
.\build\bin\test_camera.exe

# Linux/macOS
./build/bin/test_camera
```

**Expected Output**:
```
===== USB Camera Face Detection - Test Suite =====

Test 1: Camera Connection
✅ Camera connected successfully

Test 2: Resolution Setting
✅ Resolution set to 640x480

Test 3: Frame Capture
✅ Frame 1 captured
...
===== All tests completed =====
```

### 4. Connect USB Camera
- Connect USB camera to your computer
- On Linux, verify: `lsusb`
- On Windows, check Device Manager

### 5. Run Application
```bash
# Windows
.\build\bin\usb_camera_app.exe

# Linux/macOS
./build/bin/usb_camera_app
```

---

## Troubleshooting Installation

### OpenCV Not Found
**Problem**: CMake can't find OpenCV
**Solution**:
```bash
# Windows
setx OpenCV_DIR "C:\path\to\opencv\build"

# Linux
export OpenCV_DIR=/usr/local/opencv/build

# macOS
export OpenCV_DIR=/usr/local/Cellar/opencv/x.x.x/
```

### CMake Not Found
**Problem**: CMake command not recognized
**Solution**:
- Reinstall CMake with "Add to PATH" option
- Or add manually to PATH environment variable

### Compiler Errors on Linux
**Problem**: Missing build tools
**Solution**:
```bash
sudo apt-get install build-essential
sudo apt-get install g++ gcc
```

### Permission Denied (Linux/macOS)
**Problem**: Cannot execute build script
**Solution**:
```bash
chmod +x build.sh
./build.sh
```

### Visual Studio Not Installed (Windows)
**Problem**: MSVC compiler not found
**Solution**:
```bash
# Install Visual Studio Build Tools or:
cmake -G "MinGW Makefiles" ..
```

### JSON Header Not Found
**Problem**: nlohmann/json.hpp not found
**Solution**:
```bash
# Manually install header
cd include
wget https://github.com/nlohmann/json/releases/download/v3.11.2/json.hpp
```

---

## Environment Variables

### Windows
```bash
# Set OpenCV directory
setx OpenCV_DIR "C:\path\to\opencv\build"

# Set CMAKE
setx CMAKE_PREFIX_PATH "%OpenCV_DIR%"

# Verify
echo %OpenCV_DIR%
```

### Linux/macOS
```bash
# Add to ~/.bashrc or ~/.zshrc
export OpenCV_DIR=/usr/local/opencv/build
export CMAKE_PREFIX_PATH=$OpenCV_DIR

# Reload
source ~/.bashrc
```

---

## Verification Checklist

- [ ] C++ Compiler installed (MSVC, GCC, or Clang)
- [ ] CMake installed and in PATH
- [ ] OpenCV installed and OpenCV_DIR set
- [ ] nlohmann/json installed
- [ ] Project directory structure correct
- [ ] config/ and output/ directories exist
- [ ] Test suite runs successfully
- [ ] USB camera connected
- [ ] Main application launches
- [ ] Camera preview works
- [ ] Face detection works

---

## Uninstallation

### Windows
```bash
# Remove build directory
rmdir /s /q build

# Uninstall dependencies via Control Panel
# Or if using Chocolatey:
choco uninstall cmake
```

### Linux
```bash
# Remove build directory
rm -rf build

# Uninstall packages
sudo apt-get remove cmake libopencv-dev nlohmann-json3-dev

# Remove custom OpenCV
sudo apt-get remove opencv-dev
```

### macOS
```bash
# Remove build directory
rm -rf build

# Uninstall via Homebrew
brew uninstall opencv cmake nlohmann-json
```

---

## Support & Help

**For OpenCV Issues**:
- Visit: https://docs.opencv.org/
- Forum: https://stackoverflow.com/questions/tagged/opencv

**For Build Issues**:
- Check CMake output for errors
- Review compiler flags
- Check PATH environment variables

**For Camera Issues**:
- Verify USB connection
- Check camera permissions
- Test with another application

**For Face Detection Issues**:
- Verify cascade file path
- Check file permissions
- Test with different images
- Review application log

---

## Next Steps After Installation

1. ✅ Review README.md
2. ✅ Run test suite
3. ✅ Configure default_config.json
4. ✅ Connect USB camera
5. ✅ Launch application
6. ✅ Enable face detection
7. ✅ Capture test images
8. ✅ Review output/

## Version Information

- **Last Updated**: April 21, 2026
- **Install Guide Version**: 1.0
- **Supported OpenCV**: 4.0+
- **Supported C++**: C++17 or later

---

**Installation Complete!** 🎉

You're ready to start using the USB Camera Face Detection System.
