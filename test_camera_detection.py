#!/usr/bin/env python3
"""
Camera Detection Diagnostic Tool
Tests which cameras are available and connects to the best one
"""

import cv2
import sys


def check_camera(camera_id: int) -> bool:
    """Check if a camera device is available"""
    try:
        cap = cv2.VideoCapture(camera_id)
        if cap.isOpened():
            ret, frame = cap.read()
            cap.release()
            return ret
        return False
    except Exception as e:
        print(f"  Error checking camera {camera_id}: {e}")
        return False


def get_camera_info(camera_id: int):
    """Get details about a camera device"""
    try:
        cap = cv2.VideoCapture(camera_id)
        if cap.isOpened():
            width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
            height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
            fps = cap.get(cv2.CAP_PROP_FPS)
            cap.release()
            return {
                "width": int(width),
                "height": int(height),
                "fps": int(fps)
            }
    except:
        pass
    return None


def main():
    print("\n" + "="*60)
    print("CAMERA DETECTION DIAGNOSTIC TOOL")
    print("="*60 + "\n")
    
    print("Scanning for available cameras...\n")
    
    available_cameras = []
    for camera_id in range(5):  # Check first 5 camera slots
        if check_camera(camera_id):
            available_cameras.append(camera_id)
            info = get_camera_info(camera_id)
            
            camera_names = {
                0: "Default (Laptop Camera)",
                1: "External (HP Camera)",
                2: "External Camera 2",
                3: "External Camera 3",
                4: "External Camera 4"
            }
            name = camera_names.get(camera_id, f"Unknown Camera {camera_id}")
            
            print(f"✓ Camera ID {camera_id}: {name}")
            if info:
                print(f"  Resolution: {info['width']}x{info['height']}")
                if info['fps'] > 0:
                    print(f"  FPS: {info['fps']}")
            print()
    
    if not available_cameras:
        print("✗ No cameras found!")
        return False
    
    print(f"Found {len(available_cameras)} camera(s): {available_cameras}\n")
    
    # Determine which camera to use
    if 1 in available_cameras:
        camera_to_use = 1
        print("✓ Using Camera ID 1 (External/HP Camera)\n")
    elif 0 in available_cameras:
        camera_to_use = 0
        print("⚠ Camera ID 1 not found, using Camera ID 0 (Default/Laptop Camera)\n")
    else:
        print("✗ No suitable camera found!")
        return False
    
    # Try to start detection
    print("Starting face detection test...")
    print("(Press 'q' to quit)\n")
    
    try:
        from face_detector import CameraFaceDetector
        
        detector = CameraFaceDetector(camera_id=camera_to_use, use_dnn=False, auto_detect=False)
        detector.start_detection()
        return True
        
    except Exception as e:
        print(f"\n✗ Error starting face detection: {e}")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
