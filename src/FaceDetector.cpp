#include "FaceDetector.h"
#include "Logger.h"
#include <iostream>
#include <chrono>

FaceDetector::FaceDetector()
    : method_(CASCADE), scaleFactor_(1.1), minNeighbors_(4),
      minFaceSize_(30, 30), confidenceThreshold_(0.5f),
      lastDetectionCount_(0), lastProcessingTime_(0.0) {
}

FaceDetector::~FaceDetector() {
}

bool FaceDetector::initializeCascade(const std::string& cascadePath) {
    try {
        if (!cascade_.load(cascadePath)) {
            LOG_ERROR("Failed to load cascade classifier: " + cascadePath);
            return false;
        }
        method_ = CASCADE;
        LOG_INFO("Cascade classifier loaded successfully: " + cascadePath);
        return true;
    } catch (const std::exception& e) {
        LOG_ERROR("Exception loading cascade: " + std::string(e.what()));
        return false;
    }
}

bool FaceDetector::initializeDNN(const std::string& modelPath, 
                                 const std::string& configPath, 
                                 const std::string& framework) {
    try {
        if (framework == "caffe") {
            dnnNet_ = cv::dnn::readNetFromCaffe(configPath, modelPath);
        } else if (framework == "tensorflow") {
            dnnNet_ = cv::dnn::readNetFromTensorflow(modelPath, configPath);
        } else if (framework == "onnx") {
            dnnNet_ = cv::dnn::readNetFromONNX(modelPath);
        } else {
            LOG_ERROR("Unknown framework: " + framework);
            return false;
        }
        
        if (dnnNet_.empty()) {
            LOG_ERROR("Failed to load DNN model: " + modelPath);
            return false;
        }
        
        method_ = DNN;
        LOG_INFO("DNN model loaded successfully: " + modelPath);
        return true;
    } catch (const std::exception& e) {
        LOG_ERROR("Exception loading DNN model: " + std::string(e.what()));
        return false;
    }
}

std::vector<FaceResult> FaceDetector::detectFaces(const cv::Mat& image, float confidenceThreshold) {
    confidenceThreshold_ = confidenceThreshold;
    
    auto startTime = std::chrono::high_resolution_clock::now();
    
    std::vector<FaceResult> results;
    if (method_ == CASCADE) {
        results = detectUsingCascade(image);
    } else if (method_ == DNN) {
        results = detectUsingDNN(image);
    }
    
    auto endTime = std::chrono::high_resolution_clock::now();
    lastProcessingTime_ = std::chrono::duration<double>(endTime - startTime).count();
    lastDetectionCount_ = results.size();
    
    LOG_INFO("Detected " + std::to_string(lastDetectionCount_) + " faces in " + 
             std::to_string(lastProcessingTime_ * 1000) + " ms");
    
    return results;
}

std::vector<FaceResult> FaceDetector::detectUsingCascade(const cv::Mat& image) {
    std::vector<FaceResult> results;
    cv::Mat grayImage;
    
    if (image.channels() == 3) {
        cv::cvtColor(image, grayImage, cv::COLOR_BGR2GRAY);
    } else {
        grayImage = image.clone();
    }
    
    std::vector<cv::Rect> faces;
    cascade_.detectMultiScale(grayImage, faces, scaleFactor_, minNeighbors_, 
                             0, minFaceSize_);
    
    for (size_t i = 0; i < faces.size(); i++) {
        FaceResult result;
        result.boundingBox = faces[i];
        result.confidence = 0.95f;  // Cascade doesn't provide confidence
        result.id = static_cast<int>(i);
        results.push_back(result);
    }
    
    return results;
}

std::vector<FaceResult> FaceDetector::detectUsingDNN(const cv::Mat& image) {
    std::vector<FaceResult> results;
    
    cv::Mat blob = cv::dnn::blobFromImage(image, 1.0, cv::Size(300, 300),
                                         cv::Scalar(104.0, 177.0, 123.0), false, false);
    dnnNet_.setInput(blob);
    cv::Mat detections = dnnNet_.forward();
    
    float* data = (float*)detections.data;
    int rows = detections.size[2];
    
    for (int i = 0; i < rows; i++) {
        float confidence = data[i * 7 + 2];
        
        if (confidence > confidenceThreshold_) {
            int x1 = static_cast<int>(data[i * 7 + 3] * image.cols);
            int y1 = static_cast<int>(data[i * 7 + 4] * image.rows);
            int x2 = static_cast<int>(data[i * 7 + 5] * image.cols);
            int y2 = static_cast<int>(data[i * 7 + 6] * image.rows);
            
            FaceResult result;
            result.boundingBox = cv::Rect(x1, y1, x2 - x1, y2 - y1);
            result.confidence = confidence;
            result.id = static_cast<int>(results.size());
            results.push_back(result);
        }
    }
    
    return results;
}

cv::Mat FaceDetector::detectAndDraw(const cv::Mat& image, const cv::Scalar& color) {
    cv::Mat result = image.clone();
    std::vector<FaceResult> faces = detectFaces(image);
    
    for (const auto& face : faces) {
        cv::rectangle(result, face.boundingBox, color, 2);
        
        // Draw confidence
        std::string label = "Face: " + std::to_string(static_cast<int>(face.confidence * 100)) + "%";
        cv::putText(result, label, cv::Point(face.boundingBox.x, face.boundingBox.y - 10),
                   cv::FONT_HERSHEY_SIMPLEX, 0.5, color, 2);
    }
    
    return result;
}

void FaceDetector::setScaleFactor(double scale) {
    scaleFactor_ = scale;
    LOG_DEBUG("Scale factor set to: " + std::to_string(scaleFactor_));
}

void FaceDetector::setMinNeighbors(int minNeighbors) {
    minNeighbors_ = minNeighbors;
    LOG_DEBUG("Min neighbors set to: " + std::to_string(minNeighbors_));
}

void FaceDetector::setMinFaceSize(int minWidth, int minHeight) {
    minFaceSize_ = cv::Size(minWidth, minHeight);
    LOG_DEBUG("Min face size set to: " + std::to_string(minWidth) + "x" + std::to_string(minHeight));
}

void FaceDetector::setConfidenceThreshold(float threshold) {
    confidenceThreshold_ = threshold;
    LOG_DEBUG("Confidence threshold set to: " + std::to_string(confidenceThreshold_));
}

int FaceDetector::getLastDetectionCount() const {
    return lastDetectionCount_;
}

double FaceDetector::getLastProcessingTime() const {
    return lastProcessingTime_;
}
