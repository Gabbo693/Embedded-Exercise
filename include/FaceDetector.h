#ifndef FACEDETECTOR_H
#define FACEDETECTOR_H

#include <opencv2/opencv.hpp>
#include <opencv2/dnn.hpp>
#include <vector>
#include <string>
#include <memory>

struct FaceResult {
    cv::Rect boundingBox;
    float confidence;
    int id;
    std::vector<cv::Point2f> landmarks;
};

class FaceDetector {
public:
    FaceDetector();
    ~FaceDetector();
    
    // Initialize with cascade classifier
    bool initializeCascade(const std::string& cascadePath);
    
    // Initialize with DNN model
    bool initializeDNN(const std::string& modelPath, const std::string& configPath, 
                       const std::string& framework = "caffe");
    
    // Detect faces in image
    std::vector<FaceResult> detectFaces(const cv::Mat& image, float confidenceThreshold = 0.5f);
    
    // Detect and draw faces
    cv::Mat detectAndDraw(const cv::Mat& image, const cv::Scalar& color = cv::Scalar(0, 255, 0));
    
    // Set parameters
    void setScaleFactor(double scale);
    void setMinNeighbors(int minNeighbors);
    void setMinFaceSize(int minWidth, int minHeight);
    void setConfidenceThreshold(float threshold);
    
    // Get statistics
    int getLastDetectionCount() const;
    double getLastProcessingTime() const;
    
private:
    enum DetectionMethod { CASCADE, DNN };
    
    DetectionMethod method_;
    cv::CascadeClassifier cascade_;
    cv::dnn::Net dnnNet_;
    
    double scaleFactor_;
    int minNeighbors_;
    cv::Size minFaceSize_;
    float confidenceThreshold_;
    
    int lastDetectionCount_;
    double lastProcessingTime_;
    
    // Helper functions
    std::vector<FaceResult> detectUsingCascade(const cv::Mat& image);
    std::vector<FaceResult> detectUsingDNN(const cv::Mat& image);
};

#endif // FACEDETECTOR_H
