#include <opencv2/opencv.hpp>
#include <iostream>

int main() {
    std::cout << "Testing camera detection..." << std::endl;
    
    for (int i = 0; i < 5; i++) {
        cv::VideoCapture cap(i);
        if (cap.isOpened()) {
            std::cout << "Camera found at index " << i << std::endl;
            double width = cap.get(cv::CAP_PROP_FRAME_WIDTH);
            double height = cap.get(cv::CAP_PROP_FRAME_HEIGHT);
            double fps = cap.get(cv::CAP_PROP_FPS);
            std::cout << "  Resolution: " << (int)width << "x" << (int)height << std::endl;
            std::cout << "  FPS: " << fps << std::endl;
            cap.release();
        }
    }
    return 0;
}
