#include "CameraConfig.h"
#include "Logger.h"
#include <fstream>

CameraConfig::CameraConfig()
    : cameraIndex_(0), width_(1280), height_(720), frameRate_(30.0),
      faceDetectionEnabled_(true), faceDetectionMethod_("cascade"),
      faceConfidenceThreshold_(0.5f), autoSaveImages_(false),
      outputDirectory_("./output"), displayLiveView_(true) {
}

CameraConfig::~CameraConfig() {
}

bool CameraConfig::loadFromFile(const std::string& configPath) {
    try {
        std::ifstream file(configPath);
        if (!file.is_open()) {
            LOG_WARNING("Config file not found: " + configPath);
            return false;
        }
        
        json j;
        file >> j;
        file.close();
        
        fromJson(j);
        LOG_INFO("Configuration loaded from: " + configPath);
        return true;
    } catch (const std::exception& e) {
        LOG_ERROR("Error loading config: " + std::string(e.what()));
        return false;
    }
}

bool CameraConfig::saveToFile(const std::string& configPath) const {
    try {
        std::ofstream file(configPath);
        if (!file.is_open()) {
            LOG_ERROR("Cannot open config file for writing: " + configPath);
            return false;
        }
        
        json j = toJson();
        file << j.dump(4);
        file.close();
        
        LOG_INFO("Configuration saved to: " + configPath);
        return true;
    } catch (const std::exception& e) {
        LOG_ERROR("Error saving config: " + std::string(e.what()));
        return false;
    }
}

json CameraConfig::toJson() const {
    json j;
    
    j["camera"]["index"] = cameraIndex_;
    j["camera"]["width"] = width_;
    j["camera"]["height"] = height_;
    j["camera"]["frameRate"] = frameRate_;
    
    j["faceDetection"]["enabled"] = faceDetectionEnabled_;
    j["faceDetection"]["method"] = faceDetectionMethod_;
    j["faceDetection"]["confidenceThreshold"] = faceConfidenceThreshold_;
    
    j["output"]["autoSave"] = autoSaveImages_;
    j["output"]["directory"] = outputDirectory_;
    j["output"]["displayLiveView"] = displayLiveView_;
    
    return j;
}

void CameraConfig::fromJson(const json& j) {
    try {
        if (j.contains("camera")) {
            if (j["camera"].contains("index")) cameraIndex_ = j["camera"]["index"];
            if (j["camera"].contains("width")) width_ = j["camera"]["width"];
            if (j["camera"].contains("height")) height_ = j["camera"]["height"];
            if (j["camera"].contains("frameRate")) frameRate_ = j["camera"]["frameRate"];
        }
        
        if (j.contains("faceDetection")) {
            if (j["faceDetection"].contains("enabled")) faceDetectionEnabled_ = j["faceDetection"]["enabled"];
            if (j["faceDetection"].contains("method")) faceDetectionMethod_ = j["faceDetection"]["method"];
            if (j["faceDetection"].contains("confidenceThreshold")) 
                faceConfidenceThreshold_ = j["faceDetection"]["confidenceThreshold"];
        }
        
        if (j.contains("output")) {
            if (j["output"].contains("autoSave")) autoSaveImages_ = j["output"]["autoSave"];
            if (j["output"].contains("directory")) outputDirectory_ = j["output"]["directory"];
            if (j["output"].contains("displayLiveView")) displayLiveView_ = j["output"]["displayLiveView"];
        }
    } catch (const std::exception& e) {
        LOG_ERROR("Error parsing JSON config: " + std::string(e.what()));
    }
}
