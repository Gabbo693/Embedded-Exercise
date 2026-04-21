#!/bin/bash
# Build Script for USB Camera Face Detection System
# Linux/macOS build script

set -e

echo "====================================="
echo "USB Camera Face Detection System"
echo "Build Script for Linux/macOS"
echo "====================================="
echo ""

# Check if CMake is installed
if ! command -v cmake &> /dev/null; then
    echo "ERROR: CMake not found. Please install CMake."
    exit 1
fi

# Check if OpenCV is installed
if [ -z "$OpenCV_DIR" ]; then
    echo "WARNING: OpenCV_DIR not set. Build may fail."
    echo "Set OpenCV_DIR environment variable to OpenCV installation directory."
    echo ""
fi

# Create build directory
echo "Creating build directory..."
mkdir -p build
cd build

# Run CMake
echo ""
echo "Running CMake..."
cmake -DCMAKE_BUILD_TYPE=Release ..

# Build project
echo ""
echo "Building project..."
cmake --build . --config Release

echo ""
echo "====================================="
echo "Build completed successfully!"
echo "Executable: ./bin/usb_camera_app"
echo "====================================="
echo ""
echo "Usage: ./bin/usb_camera_app"
echo ""

cd ..
