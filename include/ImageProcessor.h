#ifndef IMAGEPROCESSOR_H
#define IMAGEPROCESSOR_H

#include <opencv2/opencv.hpp>
#include <string>
#include <vector>

class ImageProcessor {
public:
    ImageProcessor();
    ~ImageProcessor();
    
    // Image enhancement
    static cv::Mat enhanceContrast(const cv::Mat& image);
    static cv::Mat reduceThermalNoise(const cv::Mat& image);
    static cv::Mat applyGaussianBlur(const cv::Mat& image, int kernelSize = 5);
    
    // Color space conversion
    static cv::Mat convertToGrayscale(const cv::Mat& image);
    static cv::Mat convertToHSV(const cv::Mat& image);
    static cv::Mat convertToLAB(const cv::Mat& image);
    
    // Image resizing
    static cv::Mat resizeImage(const cv::Mat& image, int width, int height);
    static cv::Mat resizeImagePreservingAspect(const cv::Mat& image, int maxDim);
    
    // Image saving
    static bool saveImage(const cv::Mat& image, const std::string& filePath, 
                         int quality = 95);
    static bool saveImageWithMetadata(const cv::Mat& image, const std::string& filePath,
                                     const std::string& metadata);
    
    // Image analysis
    static double calculateImageSharpness(const cv::Mat& image);
    static double calculateBrightness(const cv::Mat& image);
    static cv::Mat calculateHistogram(const cv::Mat& image, int bins = 256);
    
private:
    static constexpr float CONTRAST_ALPHA = 1.2f;
    static constexpr int NOISE_KERNEL = 5;
};

#endif // IMAGEPROCESSOR_H
