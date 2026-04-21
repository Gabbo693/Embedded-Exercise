#include <iostream>
#include <memory>
#include "USBCamera.h"
#include "FaceDetector.h"
#include "ImageProcessor.h"
#include "CameraConfig.h"
#include "Logger.h"

using namespace std;

int main() {
    try {
        cout << "===== USB Camera Face Detection - Test Suite =====" << endl;
        cout << endl;
        
        // Initialize logger
        Logger::getInstance().initialize("test_camera.log", LogLevel::DEBUG);
        Logger::getInstance().setConsoleOutput(true);
        
        LOG_INFO("Test suite started");
        
        // Test 1: Camera Connection
        cout << "Test 1: Camera Connection" << endl;
        auto camera = make_unique<USBCamera>();
        
        if (camera->connect(0)) {
            cout << "✅ Camera connected successfully" << endl;
            cout << "   Resolution: " << camera->getFrameWidth() << "x" 
                 << camera->getFrameHeight() << endl;
            cout << "   FPS: " << camera->getFPS() << endl;
        } else {
            cout << "❌ Failed to connect camera" << endl;
            return 1;
        }
        cout << endl;
        
        // Test 2: Resolution Setting
        cout << "Test 2: Resolution Setting" << endl;
        if (camera->setResolution(640, 480)) {
            cout << "✅ Resolution set to 640x480" << endl;
        } else {
            cout << "⚠️  Resolution setting not supported" << endl;
        }
        cout << endl;
        
        // Test 3: Frame Capture
        cout << "Test 3: Frame Capture" << endl;
        for (int i = 0; i < 5; i++) {
            if (camera->captureFrame()) {
                cout << "✅ Frame " << (i + 1) << " captured" << endl;
            }
        }
        cout << "   Total frames captured: " << camera->getFrameCount() << endl;
        cout << endl;
        
        // Test 4: Image Processing
        cout << "Test 4: Image Processing" << endl;
        cv::Mat frame = camera->getFrame();
        if (!frame.empty()) {
            double brightness = ImageProcessor::calculateBrightness(frame);
            double sharpness = ImageProcessor::calculateImageSharpness(frame);
            cout << "✅ Image analysis completed" << endl;
            cout << "   Brightness: " << brightness << endl;
            cout << "   Sharpness: " << sharpness << endl;
        }
        cout << endl;
        
        // Test 5: Face Detection
        cout << "Test 5: Face Detection" << endl;
        cout << "Attempting to enable face detection..." << endl;
        if (camera->enableFaceDetection()) {
            cout << "✅ Face detection enabled" << endl;
            
            // Capture a few frames for face detection
            for (int i = 0; i < 3; i++) {
                if (camera->captureFrame()) {
                    int faceCount = camera->getDetectedFaceCount();
                    cout << "   Frame " << (i + 1) << ": " << faceCount << " face(s) detected" << endl;
                }
            }
        } else {
            cout << "⚠️  Face detection models not found" << endl;
            cout << "   You can enable it manually with a valid cascade file" << endl;
        }
        cout << endl;
        
        // Test 6: Image Saving
        cout << "Test 6: Image Saving" << endl;
        if (camera->captureAndSave("output/test_image.jpg")) {
            cout << "✅ Image saved to output/test_image.jpg" << endl;
        } else {
            cout << "⚠️  Image saving may have failed" << endl;
        }
        cout << endl;
        
        // Test 7: Configuration
        cout << "Test 7: Configuration" << endl;
        CameraConfig config;
        config.setResolution(640, 480);
        config.setFrameRate(30.0);
        config.setFaceDetectionEnabled(true);
        if (config.saveToFile("config/test_config.json")) {
            cout << "✅ Configuration saved" << endl;
        }
        cout << endl;
        
        // Test 8: Statistics
        cout << "Test 8: Statistics" << endl;
        cout << camera->getStatistics();
        cout << endl;
        
        // Cleanup
        cout << "Cleaning up..." << endl;
        camera->disconnect();
        LOG_INFO("Test suite completed successfully");
        
        cout << "===== All tests completed =====" << endl;
        cout << "Check 'test_camera.log' for detailed information" << endl;
        
    } catch (const exception& e) {
        LOG_CRITICAL("Fatal error: " + string(e.what()));
        cerr << "Fatal error: " << e.what() << endl;
        return 1;
    }
    
    return 0;
}
