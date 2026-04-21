@echo off
REM Build Script for USB Camera Face Detection System
REM Windows batch file for automated building

setlocal enabledelayedexpansion

echo =====================================
echo USB Camera Face Detection System
echo Build Script for Windows
echo =====================================
echo.

REM Set up Visual Studio environment
echo Setting up Visual Studio 2022 environment...
call "C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools\VC\Auxiliary\Build\vcvars64.bat"

REM Ensure compiler is in PATH
set "PATH=C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools\VC\Tools\MSVC\14.44.35207\bin\Hostx64\x64;C:\Program Files\CMake\bin;%PATH%"

REM Check if CMake is installed
where cmake >nul 2>nul
if errorlevel 1 (
    echo ERROR: CMake not found. Please install CMake.
    exit /b 1
)

REM Set OpenCV_DIR if not already set
if not defined OpenCV_DIR (
    set "OpenCV_DIR=C:\opencv\build"
    echo Setting OpenCV_DIR to: !OpenCV_DIR!
)

REM Create build directory if it doesn't exist
if not exist "build" (
    echo Creating build directory...
    mkdir build
)

cd build

REM Run CMake
echo.
echo Running CMake...
cmake -G "Visual Studio 17 2022" -A x64 -DOpenCV_DIR="%OpenCV_DIR%" ..
if errorlevel 1 (
    echo CMake configuration failed!
    exit /b 1
)

REM Build project
echo.
echo Building project...
cmake --build . --config Release
if errorlevel 1 (
    echo Build failed!
    exit /b 1
)

echo.
echo =====================================
echo Build completed successfully!
echo Executable: .\bin\usb_camera_app.exe
echo =====================================
echo.
echo Usage: .\bin\usb_camera_app.exe
echo.

cd ..
pause
