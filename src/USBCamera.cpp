#include "USBCamera.h"
#include "ImageProcessor.h"
#include "Logger.h"
#include <iostream>
#include <chrono>

USBCamera::USBCamera() 
    : connected_(false), frameWidth_(0), frameHeight_(0), cameraIndex_(0),
      frameCount_(0), fps_(0.0), faceDetectionEnabled_(false),
      averageBrightness_(0.0), imageSharpness_(0.0) {
    
    faceDetector_ = std::make_shared<FaceDetector>();
}

USBCamera::~USBCamera() {
    if (connected_) {
        disconnect();
    }
}

bool USBCamera::connect(int cameraIndex) {
    try {
        cameraIndex_ = cameraIndex;
        LOG_INFO("Opening USB Camera (index: " + std::to_string(cameraIndex_) + ")...");
        
        camera_.open(cameraIndex_);
        
        if (!camera_.isOpened()) {
            LOG_ERROR("Cannot open USB camera at index " + std::to_string(cameraIndex_));
            connected_ = false;
            return false;
        }
        
        // Get default resolution
        frameWidth_ = static_cast<int>(camera_.get(cv::CAP_PROP_FRAME_WIDTH));
        frameHeight_ = static_cast<int>(camera_.get(cv::CAP_PROP_FRAME_HEIGHT));
        fps_ = camera_.get(cv::CAP_PROP_FPS);
        if (fps_ == 0.0) fps_ = 30.0;  // Default FPS if not available
        
        connected_ = true;
        frameCount_ = 0;
        
        LOG_INFO("USB camera connected successfully!");
        LOG_INFO("Resolution: " + std::to_string(frameWidth_) + "x" + std::to_string(frameHeight_));
        LOG_INFO("FPS: " + std::to_string(fps_));
        
        return true;
    } catch (const std::exception& e) {
        LOG_ERROR("Camera connection failed: " + std::string(e.what()));
        connected_ = false;
        return false;
    }
}

bool USBCamera::disconnect() {
    if (connected_) {
        try {
            camera_.release();
            connected_ = false;
            currentFrame_.release();
            frameWithDetections_.release();
            LOG_INFO("USB camera disconnected");
            return true;
        } catch (const std::exception& e) {
            LOG_ERROR("Error disconnecting camera: " + std::string(e.what()));
            return false;
        }
    }
    return false;
}

bool USBCamera::isConnected() const {
    return connected_ && camera_.isOpened();
}

int USBCamera::findUSBCamera(int maxIndex) {
    LOG_INFO("Scanning for USB cameras (indices 1-" + std::to_string(maxIndex) + ")...");
    
    // Skip index 0 (usually built-in laptop camera), start from index 1 for USB devices
    for (int i = 1; i <= maxIndex; ++i) {
        cv::VideoCapture testCamera(i);
        if (testCamera.isOpened()) {
            // Get camera properties to confirm it's a real camera
            double width = testCamera.get(cv::CAP_PROP_FRAME_WIDTH);
            double height = testCamera.get(cv::CAP_PROP_FRAME_HEIGHT);
            
            if (width > 0 && height > 0) {
                LOG_INFO("Found USB camera at index " + std::to_string(i) + 
                        " (" + std::to_string((int)width) + "x" + std::to_string((int)height) + ")");
                testCamera.release();
                return i;
            }
            testCamera.release();
        }
    }
    
    LOG_WARNING("No USB camera found. Falling back to index 0 (built-in camera)");
    return 0;  // Fall back to default if no USB camera found
}

bool USBCamera::connectToUSBCamera() {
    int usbCameraIndex = findUSBCamera();
    LOG_INFO("Attempting to connect to camera at index: " + std::to_string(usbCameraIndex));
    return connect(usbCameraIndex);
}

bool USBCamera::captureFrame() {
    if (!isConnected()) {
        LOG_ERROR("Camera not connected");
        return false;
    }
    
    try {
        auto startTime = std::chrono::high_resolution_clock::now();
        
        camera_ >> currentFrame_;
        
        if (currentFrame_.empty()) {
            LOG_ERROR("Failed to capture frame from camera");
            return false;
        }
        
        frameWidth_ = currentFrame_.cols;
        frameHeight_ = currentFrame_.rows;
        frameCount_++;
        
        // Calculate image quality metrics
        averageBrightness_ = ImageProcessor::calculateBrightness(currentFrame_);
        imageSharpness_ = ImageProcessor::calculateImageSharpness(currentFrame_);
        
        // Perform face detection if enabled
        if (faceDetectionEnabled_) {
            lastDetectedFaces_ = faceDetector_->detectFaces(currentFrame_);
            frameWithDetections_ = faceDetector_->detectAndDraw(currentFrame_);
        }
        
        auto endTime = std::chrono::high_resolution_clock::now();
        auto elapsed = std::chrono::duration<double>(endTime - startTime).count();
        
        LOG_DEBUG("Frame captured: " + std::to_string(frameCount_) + 
                 " (" + std::to_string(elapsed * 1000) + " ms)");
        
        return true;
    } catch (const std::exception& e) {
        LOG_ERROR("Error capturing frame: " + std::string(e.what()));
        return false;
    }
}

cv::Mat USBCamera::getFrame() const {
    return currentFrame_;
}

cv::Mat USBCamera::getFrameWithDetections() const {
    return frameWithDetections_.empty() ? currentFrame_ : frameWithDetections_;
}

std::vector<unsigned char> USBCamera::getFrameData() const {
    if (currentFrame_.empty()) {
        return std::vector<unsigned char>();
    }
    
    std::vector<unsigned char> data;
    if (currentFrame_.isContinuous()) {
        data.assign(currentFrame_.datastart, currentFrame_.dataend);
    } else {
        for (int i = 0; i < currentFrame_.rows; ++i) {
            data.insert(data.end(),
                       currentFrame_.ptr(i),
                       currentFrame_.ptr(i) + currentFrame_.cols * currentFrame_.channels());
        }
    }
    return data;
}

int USBCamera::getFrameWidth() const {
    return frameWidth_;
}

int USBCamera::getFrameHeight() const {
    return frameHeight_;
}

int USBCamera::getFrameCount() const {
    return frameCount_;
}

double USBCamera::getFPS() const {
    return fps_;
}

bool USBCamera::setResolution(int width, int height) {
    if (!isConnected()) {
        LOG_ERROR("Camera not connected");
        return false;
    }
    
    try {
        camera_.set(cv::CAP_PROP_FRAME_WIDTH, width);
        camera_.set(cv::CAP_PROP_FRAME_HEIGHT, height);
        
        frameWidth_ = static_cast<int>(camera_.get(cv::CAP_PROP_FRAME_WIDTH));
        frameHeight_ = static_cast<int>(camera_.get(cv::CAP_PROP_FRAME_HEIGHT));
        
        LOG_INFO("Resolution set to: " + std::to_string(frameWidth_) + "x" + std::to_string(frameHeight_));
        return true;
    } catch (const std::exception& e) {
        LOG_ERROR("Error setting resolution: " + std::string(e.what()));
        return false;
    }
}

bool USBCamera::setFrameRate(double fps) {
    if (!isConnected()) {
        LOG_ERROR("Camera not connected");
        return false;
    }
    
    try {
        camera_.set(cv::CAP_PROP_FPS, fps);
        fps_ = camera_.get(cv::CAP_PROP_FPS);
        LOG_INFO("Frame rate set to: " + std::to_string(fps_) + " FPS");
        return true;
    } catch (const std::exception& e) {
        LOG_ERROR("Error setting frame rate: " + std::string(e.what()));
        return false;
    }
}

bool USBCamera::setBrightness(double brightness) {
    if (!isConnected()) {
        LOG_ERROR("Camera not connected");
        return false;
    }
    
    try {
        camera_.set(cv::CAP_PROP_BRIGHTNESS, brightness);
        LOG_INFO("Brightness set to: " + std::to_string(brightness));
        return true;
    } catch (const std::exception& e) {
        LOG_ERROR("Error setting brightness: " + std::string(e.what()));
        return false;
    }
}

bool USBCamera::setContrast(double contrast) {
    if (!isConnected()) {
        LOG_ERROR("Camera not connected");
        return false;
    }
    
    try {
        camera_.set(cv::CAP_PROP_CONTRAST, contrast);
        LOG_INFO("Contrast set to: " + std::to_string(contrast));
        return true;
    } catch (const std::exception& e) {
        LOG_ERROR("Error setting contrast: " + std::string(e.what()));
        return false;
    }
}

bool USBCamera::setSaturation(double saturation) {
    if (!isConnected()) {
        LOG_ERROR("Camera not connected");
        return false;
    }
    
    try {
        camera_.set(cv::CAP_PROP_SATURATION, saturation);
        LOG_INFO("Saturation set to: " + std::to_string(saturation));
        return true;
    } catch (const std::exception& e) {
        LOG_ERROR("Error setting saturation: " + std::string(e.what()));
        return false;
    }
}

bool USBCamera::enableFaceDetection(const std::string& cascadePath) {
    try {
        std::string path = cascadePath.empty() ? 
            "C:\\opencv\\data\\haarcascades\\haarcascade_frontalface_default.xml" : cascadePath;
        
        if (!faceDetector_->initializeCascade(path)) {
            LOG_ERROR("Failed to initialize face detector with cascade: " + path);
            return false;
        }
        
        faceDetectionEnabled_ = true;
        LOG_INFO("Face detection enabled");
        return true;
    } catch (const std::exception& e) {
        LOG_ERROR("Error enabling face detection: " + std::string(e.what()));
        return false;
    }
}

bool USBCamera::disableFaceDetection() {
    faceDetectionEnabled_ = false;
    lastDetectedFaces_.clear();
    frameWithDetections_.release();
    LOG_INFO("Face detection disabled");
    return true;
}

bool USBCamera::isFaceDetectionEnabled() const {
    return faceDetectionEnabled_;
}

std::vector<FaceResult> USBCamera::getDetectedFaces() const {
    return lastDetectedFaces_;
}

int USBCamera::getDetectedFaceCount() const {
    return static_cast<int>(lastDetectedFaces_.size());
}

bool USBCamera::captureAndSave(const std::string& filePath) {
    if (!captureFrame()) {
        return false;
    }
    return ImageProcessor::saveImage(currentFrame_, filePath);
}

bool USBCamera::captureAndSaveWithDetections(const std::string& filePath) {
    if (!captureFrame()) {
        return false;
    }
    
    if (faceDetectionEnabled_ && !frameWithDetections_.empty()) {
        return ImageProcessor::saveImage(frameWithDetections_, filePath);
    }
    
    return ImageProcessor::saveImage(currentFrame_, filePath);
}

std::string USBCamera::getStatistics() const {
    std::string stats = "=== Camera Statistics ===\n";
    stats += "Connected: " + std::string(connected_ ? "Yes" : "No") + "\n";
    stats += "Resolution: " + std::to_string(frameWidth_) + "x" + std::to_string(frameHeight_) + "\n";
    stats += "FPS: " + std::to_string(fps_) + "\n";
    stats += "Total Frames: " + std::to_string(frameCount_) + "\n";
    stats += "Average Brightness: " + std::to_string(averageBrightness_) + "\n";
    stats += "Image Sharpness: " + std::to_string(imageSharpness_) + "\n";
    stats += "Face Detection: " + std::string(faceDetectionEnabled_ ? "Enabled" : "Disabled") + "\n";
    stats += "Detected Faces: " + std::to_string(getDetectedFaceCount()) + "\n";
    
    return stats;
}

double USBCamera::getAverageBrightness() const {
    return averageBrightness_;
}

double USBCamera::getImageSharpness() const {
    return imageSharpness_;
}
