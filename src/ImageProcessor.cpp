#include "ImageProcessor.h"
#include "Logger.h"
#include <opencv2/imgproc.hpp>
#include <opencv2/imgcodecs.hpp>
#include <cmath>

ImageProcessor::ImageProcessor() {
}

ImageProcessor::~ImageProcessor() {
}

cv::Mat ImageProcessor::enhanceContrast(const cv::Mat& image) {
    try {
        cv::Mat result;
        image.convertTo(result, -1, CONTRAST_ALPHA, 0);
        LOG_DEBUG("Contrast enhanced");
        return result;
    } catch (const std::exception& e) {
        LOG_ERROR("Error enhancing contrast: " + std::string(e.what()));
        return image.clone();
    }
}

cv::Mat ImageProcessor::reduceThermalNoise(const cv::Mat& image) {
    try {
        cv::Mat result;
        cv::bilateralFilter(image, result, 9, 75, 75);
        LOG_DEBUG("Thermal noise reduced");
        return result;
    } catch (const std::exception& e) {
        LOG_ERROR("Error reducing noise: " + std::string(e.what()));
        return image.clone();
    }
}

cv::Mat ImageProcessor::applyGaussianBlur(const cv::Mat& image, int kernelSize) {
    try {
        cv::Mat result;
        cv::GaussianBlur(image, result, cv::Size(kernelSize, kernelSize), 0);
        LOG_DEBUG("Gaussian blur applied");
        return result;
    } catch (const std::exception& e) {
        LOG_ERROR("Error applying blur: " + std::string(e.what()));
        return image.clone();
    }
}

cv::Mat ImageProcessor::convertToGrayscale(const cv::Mat& image) {
    try {
        cv::Mat result;
        if (image.channels() == 3) {
            cv::cvtColor(image, result, cv::COLOR_BGR2GRAY);
        } else {
            result = image.clone();
        }
        return result;
    } catch (const std::exception& e) {
        LOG_ERROR("Error converting to grayscale: " + std::string(e.what()));
        return image.clone();
    }
}

cv::Mat ImageProcessor::convertToHSV(const cv::Mat& image) {
    try {
        cv::Mat result;
        cv::cvtColor(image, result, cv::COLOR_BGR2HSV);
        return result;
    } catch (const std::exception& e) {
        LOG_ERROR("Error converting to HSV: " + std::string(e.what()));
        return image.clone();
    }
}

cv::Mat ImageProcessor::convertToLAB(const cv::Mat& image) {
    try {
        cv::Mat result;
        cv::cvtColor(image, result, cv::COLOR_BGR2Lab);
        return result;
    } catch (const std::exception& e) {
        LOG_ERROR("Error converting to LAB: " + std::string(e.what()));
        return image.clone();
    }
}

cv::Mat ImageProcessor::resizeImage(const cv::Mat& image, int width, int height) {
    try {
        cv::Mat result;
        cv::resize(image, result, cv::Size(width, height));
        LOG_DEBUG("Image resized to: " + std::to_string(width) + "x" + std::to_string(height));
        return result;
    } catch (const std::exception& e) {
        LOG_ERROR("Error resizing image: " + std::string(e.what()));
        return image.clone();
    }
}

cv::Mat ImageProcessor::resizeImagePreservingAspect(const cv::Mat& image, int maxDim) {
    try {
        double scale = static_cast<double>(maxDim) / std::max(image.rows, image.cols);
        int newWidth = static_cast<int>(image.cols * scale);
        int newHeight = static_cast<int>(image.rows * scale);
        
        return resizeImage(image, newWidth, newHeight);
    } catch (const std::exception& e) {
        LOG_ERROR("Error resizing image: " + std::string(e.what()));
        return image.clone();
    }
}

bool ImageProcessor::saveImage(const cv::Mat& image, const std::string& filePath, int quality) {
    try {
        std::vector<int> compressionParams;
        compressionParams.push_back(cv::IMWRITE_JPEG_QUALITY);
        compressionParams.push_back(quality);
        
        bool success = cv::imwrite(filePath, image, compressionParams);
        if (success) {
            LOG_INFO("Image saved: " + filePath);
        } else {
            LOG_ERROR("Failed to save image: " + filePath);
        }
        return success;
    } catch (const std::exception& e) {
        LOG_ERROR("Error saving image: " + std::string(e.what()));
        return false;
    }
}

bool ImageProcessor::saveImageWithMetadata(const cv::Mat& image, const std::string& filePath,
                                          const std::string& metadata) {
    // This would require additional libraries for metadata writing
    // For now, just save with regular method
    return saveImage(image, filePath);
}

double ImageProcessor::calculateImageSharpness(const cv::Mat& image) {
    try {
        cv::Mat gray = convertToGrayscale(image);
        cv::Mat laplacian;
        cv::Laplacian(gray, laplacian, CV_64F);
        
        cv::Scalar mean, stdDev;
        cv::meanStdDev(laplacian, mean, stdDev);
        
        return stdDev.val[0] * stdDev.val[0];
    } catch (const std::exception& e) {
        LOG_ERROR("Error calculating sharpness: " + std::string(e.what()));
        return 0.0;
    }
}

double ImageProcessor::calculateBrightness(const cv::Mat& image) {
    try {
        cv::Mat gray = convertToGrayscale(image);
        return cv::mean(gray).val[0];
    } catch (const std::exception& e) {
        LOG_ERROR("Error calculating brightness: " + std::string(e.what()));
        return 0.0;
    }
}

cv::Mat ImageProcessor::calculateHistogram(const cv::Mat& image, int bins) {
    try {
        cv::Mat gray = convertToGrayscale(image);
        cv::Mat hist;
        
        int histSize[] = { bins };
        float range[] = { 0, 256 };
        const float* ranges[] = { range };
        
        cv::calcHist(&gray, 1, 0, cv::Mat(), hist, 1, histSize, ranges);
        
        return hist;
    } catch (const std::exception& e) {
        LOG_ERROR("Error calculating histogram: " + std::string(e.what()));
        return cv::Mat();
    }
}
