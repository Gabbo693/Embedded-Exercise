@echo off
REM USB Camera Auto-Capture Application
REM This script runs the compiled application

echo.
echo ================================================
echo USB CAMERA AUTO-CAPTURE SYSTEM
echo ================================================
echo.

cd /d "c:\Users\User\Desktop\Milestone A\build\bin\Release"

REM Set OpenCV path for DLL dependencies
set PATH=C:\opencv\build\x64\vc16\bin;%PATH%

REM Run the application
echo Starting application...
echo.
usb_camera_app.exe

echo.
echo Application ended.
pause
