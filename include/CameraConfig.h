#ifndef CAMERACONFIG_H
#define CAMERACONFIG_H

#include <string>
#include <nlohmann/json.hpp>

using json = nlohmann::json;

class CameraConfig {
public:
    CameraConfig();
    ~CameraConfig();
    
    // Load/Save configuration
    bool loadFromFile(const std::string& configPath);
    bool saveToFile(const std::string& configPath) const;
    
    // Camera settings
    int getCameraIndex() const { return cameraIndex_; }
    int getWidth() const { return width_; }
    int getHeight() const { return height_; }
    double getFrameRate() const { return frameRate_; }
    
    void setCameraIndex(int index) { cameraIndex_ = index; }
    void setResolution(int width, int height) { width_ = width; height_ = height; }
    void setFrameRate(double fps) { frameRate_ = fps; }
    
    // Face detection settings
    bool getFaceDetectionEnabled() const { return faceDetectionEnabled_; }
    std::string getFaceDetectionMethod() const { return faceDetectionMethod_; }
    float getFaceConfidenceThreshold() const { return faceConfidenceThreshold_; }
    
    void setFaceDetectionEnabled(bool enabled) { faceDetectionEnabled_ = enabled; }
    void setFaceDetectionMethod(const std::string& method) { faceDetectionMethod_ = method; }
    void setFaceConfidenceThreshold(float threshold) { faceConfidenceThreshold_ = threshold; }
    
    // Output settings
    bool getAutoSaveImages() const { return autoSaveImages_; }
    std::string getOutputDirectory() const { return outputDirectory_; }
    bool getDisplayLiveView() const { return displayLiveView_; }
    
    void setAutoSaveImages(bool save) { autoSaveImages_ = save; }
    void setOutputDirectory(const std::string& dir) { outputDirectory_ = dir; }
    void setDisplayLiveView(bool display) { displayLiveView_ = display; }
    
    // Get as JSON
    json toJson() const;
    void fromJson(const json& j);
    
private:
    // Camera settings
    int cameraIndex_;
    int width_;
    int height_;
    double frameRate_;
    
    // Face detection settings
    bool faceDetectionEnabled_;
    std::string faceDetectionMethod_;  // "cascade" or "dnn"
    float faceConfidenceThreshold_;
    
    // Output settings
    bool autoSaveImages_;
    std::string outputDirectory_;
    bool displayLiveView_;
};

#endif // CAMERACONFIG_H
