#ifndef USBCAMERA_H
#define USBCAMERA_H

#include <opencv2/opencv.hpp>
#include <string>
#include <vector>
#include <memory>
#include "FaceDetector.h"

class USBCamera {
public:
    USBCamera();
    ~USBCamera();
    
    // Connection management
    bool connect(int cameraIndex = 0);
    bool connectToUSBCamera();  // Auto-detect and connect to first available USB camera
    bool disconnect();
    bool isConnected() const;
    
    // Capture operations
    bool captureFrame();
    cv::Mat getFrame() const;
    cv::Mat getFrameWithDetections() const;
    std::vector<unsigned char> getFrameData() const;
    int getFrameWidth() const;
    int getFrameHeight() const;
    int getFrameCount() const;
    double getFPS() const;
    
    // Camera settings
    bool setResolution(int width, int height);
    bool setFrameRate(double fps);
    bool setBrightness(double brightness);
    bool setContrast(double contrast);
    bool setSaturation(double saturation);
    
    // Face detection
    bool enableFaceDetection(const std::string& cascadePath = "");
    bool disableFaceDetection();
    bool isFaceDetectionEnabled() const;
    std::vector<FaceResult> getDetectedFaces() const;
    int getDetectedFaceCount() const;
    
    // Image saving
    bool captureAndSave(const std::string& filePath);
    bool captureAndSaveWithDetections(const std::string& filePath);
    
    // Statistics
    std::string getStatistics() const;
    double getAverageBrightness() const;
    double getImageSharpness() const;
    
private:
    cv::VideoCapture camera_;
    cv::Mat currentFrame_;
    cv::Mat frameWithDetections_;
    bool connected_;
    int frameWidth_;
    int frameHeight_;
    int cameraIndex_;
    
    // Helper method to find USB camera
    int findUSBCamera(int maxIndex = 10);
    int frameCount_;
    double fps_;
    
    std::shared_ptr<FaceDetector> faceDetector_;
    bool faceDetectionEnabled_;
    std::vector<FaceResult> lastDetectedFaces_;
    
    double averageBrightness_;
    double imageSharpness_;
};

#endif // USBCAMERA_H
