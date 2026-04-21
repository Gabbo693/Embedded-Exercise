#include <iostream>
#include <memory>
#include <thread>
#include <chrono>
#include <iomanip>
#include <sstream>
#include <conio.h>
#include "USBCamera.h"
#include "FaceDetector.h"
#include "ImageProcessor.h"
#include "CameraConfig.h"
#include "Logger.h"
#include <opencv2/opencv.hpp>

using namespace std;

void displayMainMenu() {
    cout << "\n" << string(50, '=') << endl;
    cout << "USB CAMERA FACE DETECTION SYSTEM" << endl;
    cout << string(50, '=') << endl;
    cout << "1. Connect to Camera" << endl;
    cout << "2. Capture Image" << endl;
    cout << "3. Capture Image with Face Detection" << endl;
    cout << "4. Enable Face Detection" << endl;
    cout << "5. Disable Face Detection" << endl;
    cout << "6. Set Camera Resolution" << endl;
    cout << "7. Set Camera Brightness" << endl;
    cout << "8. Live Preview (Press ESC to stop)" << endl;
    cout << "9. View Statistics" << endl;
    cout << "10. Save Configuration" << endl;
    cout << "11. Load Configuration" << endl;
    cout << "0. Exit" << endl;
    cout << string(50, '=') << endl;
    cout << "Select option: ";
}

int main() {
    try {
        // Initialize logger
        Logger::getInstance().initialize("camera_app.log", LogLevel::INFO);
        Logger::getInstance().setConsoleOutput(true);
        
        LOG_INFO("USB Camera Face Detection System Started");
        
        // Create camera instance
        auto camera = make_unique<USBCamera>();
        auto config = make_unique<CameraConfig>();
        
        // AUTO-CONNECT TO USB CAMERA
        cout << "\n" << string(50, '=') << endl;
        cout << "USB CAMERA AUTO-CAPTURE SYSTEM" << endl;
        cout << string(50, '=') << endl;
        cout << "Scanning for USB camera on ports...\n";
        
        bool connected = camera->connectToUSBCamera();
        
        if (!connected) {
            cout << "❌ Failed to find USB camera on any port\n";
            LOG_ERROR("Failed to auto-detect USB camera");
            return 1;
        }
        
        cout << "✅ USB Camera connected successfully!\n";
        LOG_INFO("USB camera connected via auto-detection");
        
        // Enable face detection
        cout << "\nEnabling face detection...\n";
        if (camera->enableFaceDetection("C:\\opencv\\build\\etc\\haarcascades\\haarcascade_frontalface_default.xml")) {
            cout << "✅ Face detection enabled\n";
            LOG_INFO("Face detection enabled");
        } else {
            cout << "⚠️  Face detection not available\n";
            LOG_WARNING("Face detection initialization failed");
        }
        
        // AUTO-CAPTURE IMAGES
        cout << "\n" << string(50, '=') << endl;
        cout << "Starting automatic image capture..." << endl;
        cout << "Press 'q' to quit, 'p' to pause/resume, 's' for statistics" << endl;
        cout << string(50, '=') << endl;
        
        int captureCount = 0;
        bool capturing = true;
        auto startTime = chrono::high_resolution_clock::now();
        
        cout << "\nCapturing images from USB camera...\n";
        cout << "Press Ctrl+C to stop\n\n";
        
        while (capturing && connected) {
            // Capture frame
            if (camera->captureFrame()) {
                // Generate simple numbered filename
                string filename = "output/capture_" + to_string(captureCount + 1) + ".jpg";
                
                // Save with face detection if enabled
                bool saveSuccess = false;
                if (camera->isFaceDetectionEnabled()) {
                    saveSuccess = camera->captureAndSaveWithDetections(filename);
                } else {
                    saveSuccess = camera->captureAndSave(filename);
                }
                
                if (saveSuccess) {
                    captureCount++;
                    cout << "[" << captureCount << "] ✅ Image saved: " << filename;
                    
                    int faceCount = camera->getDetectedFaceCount();
                    if (faceCount > 0) {
                        cout << " | Faces: " << faceCount;
                    }
                    cout << endl;
                    
                    LOG_INFO("Captured image #" + to_string(captureCount) + ": " + filename);
                } else {
                    LOG_ERROR("Failed to save image: " + filename);
                }
                
                // Delay between captures (2 per second)
                this_thread::sleep_for(chrono::milliseconds(500));
            } else {
                LOG_ERROR("Failed to capture frame from camera");
                break;
            }
            
            // Check for user input (non-blocking) - press 'q' to quit
            if (_kbhit()) {
                int key = _getch();
                if (key == 'q' || key == 'Q') {
                    capturing = false;
                    cout << "\nStopping capture...\n";
                    LOG_INFO("User requested stop");
                }
            }
        }
        
        // Summary
        auto endTime = chrono::high_resolution_clock::now();
        auto duration = chrono::duration_cast<chrono::seconds>(endTime - startTime);
        
        cout << "\n" << string(50, '=') << endl;
        cout << "Capture Complete" << endl;
        cout << "Total images captured: " << captureCount << endl;
        cout << "Duration: " << duration.count() << " seconds" << endl;
        cout << "Average: " << (duration.count() > 0 ? captureCount / duration.count() : 0) << " images/second" << endl;
        cout << string(50, '=') << "\n";
        
        // Disconnect
        if (connected) {
            camera->disconnect();
            cout << "✅ Camera disconnected\n";
        }
        
        LOG_INFO("Auto-capture session ended. Total captures: " + to_string(captureCount));
        return 0;
        
        // ORIGINAL MENU-DRIVEN CODE (kept for reference, now unreachable)
        int choice;
        
        while (false) {
            displayMainMenu();
            cin >> choice;
            cin.ignore();  // Clear input buffer
            
            switch (choice) {
                case 1: {
                    cout << "\nCamera Connection Options:\n";
                    cout << "1. Auto-detect USB camera\n";
                    cout << "2. Manual camera index (0 for default)\n";
                    cout << "Select option: ";
                    int connOption;
                    cin >> connOption;
                    cin.ignore();
                    
                    if (connOption == 1) {
                        cout << "Scanning for USB cameras on ports...\n";
                        if (camera->connectToUSBCamera()) {
                            connected = true;
                            cout << "✅ USB Camera connected successfully!\n";
                            LOG_INFO("USB camera connected via auto-detection");
                        } else {
                            cout << "❌ Failed to find USB camera\n";
                            LOG_ERROR("Auto-detection failed to find USB camera");
                        }
                    } else {
                        cout << "Enter camera index (0 for default): ";
                        int index;
                        cin >> index;
                        cin.ignore();
                        
                        if (camera->connect(index)) {
                            connected = true;
                            cout << "✅ Camera connected successfully!\n";
                            LOG_INFO("Camera connected at index " + std::to_string(index));
                        } else {
                            cout << "❌ Failed to connect camera\n";
                            LOG_ERROR("Failed to connect camera at index " + std::to_string(index));
                        }
                    }
                    break;
                }
                
                case 2: {
                    if (!connected) {
                        cout << "❌ Camera not connected\n";
                        break;
                    }
                    
                    if (camera->captureFrame()) {
                        cout << "Enter filename to save (e.g., image.jpg): ";
                        string filename;
                        getline(cin, filename);
                        
                        string filepath = "output/" + filename;
                        if (camera->captureAndSave(filepath)) {
                            cout << "✅ Image saved to: " << filepath << "\n";
                            LOG_INFO("Image saved: " + filepath);
                        } else {
                            cout << "❌ Failed to save image\n";
                        }
                    }
                    break;
                }
                
                case 3: {
                    if (!connected) {
                        cout << "❌ Camera not connected\n";
                        break;
                    }
                    
                    if (!camera->isFaceDetectionEnabled()) {
                        cout << "⚠️  Face detection not enabled. Enable it first (option 4)\n";
                        break;
                    }
                    
                    if (camera->captureFrame()) {
                        cout << "Enter filename to save (e.g., face_detection.jpg): ";
                        string filename;
                        getline(cin, filename);
                        
                        string filepath = "output/" + filename;
                        if (camera->captureAndSaveWithDetections(filepath)) {
                            cout << "✅ Image with detections saved to: " << filepath << "\n";
                            cout << "   Faces detected: " << camera->getDetectedFaceCount() << "\n";
                            LOG_INFO("Face detection image saved: " + filepath);
                        } else {
                            cout << "❌ Failed to save image\n";
                        }
                    }
                    break;
                }
                
                case 4: {
                    if (!connected) {
                        cout << "❌ Camera not connected\n";
                        break;
                    }
                    
                    cout << "Enter cascade file path (press Enter for default): ";
                    string cascadePath;
                    getline(cin, cascadePath);
                    
                    if (camera->enableFaceDetection(cascadePath)) {
                        cout << "✅ Face detection enabled\n";
                        LOG_INFO("Face detection enabled");
                    } else {
                        cout << "❌ Failed to enable face detection\n";
                        cout << "   Make sure the cascade file exists\n";
                        LOG_ERROR("Failed to enable face detection");
                    }
                    break;
                }
                
                case 5: {
                    camera->disableFaceDetection();
                    cout << "✅ Face detection disabled\n";
                    break;
                }
                
                case 6: {
                    if (!connected) {
                        cout << "❌ Camera not connected\n";
                        break;
                    }
                    
                    int width, height;
                    cout << "Enter resolution (width height, e.g., 1280 720): ";
                    cin >> width >> height;
                    cin.ignore();
                    
                    if (camera->setResolution(width, height)) {
                        cout << "✅ Resolution set to: " << width << "x" << height << "\n";
                    } else {
                        cout << "❌ Failed to set resolution\n";
                    }
                    break;
                }
                
                case 7: {
                    if (!connected) {
                        cout << "❌ Camera not connected\n";
                        break;
                    }
                    
                    double brightness;
                    cout << "Enter brightness value (0-100): ";
                    cin >> brightness;
                    cin.ignore();
                    
                    if (camera->setBrightness(brightness)) {
                        cout << "✅ Brightness set\n";
                    } else {
                        cout << "❌ Failed to set brightness\n";
                    }
                    break;
                }
                
                case 8: {
                    if (!connected) {
                        cout << "❌ Camera not connected\n";
                        break;
                    }
                    
                    cout << "Starting live preview... Press ESC to stop\n";
                    bool previewing = true;
                    
                    while (previewing) {
                        if (camera->captureFrame()) {
                            cv::Mat frame = camera->getFrameWithDetections();
                            
                            if (camera->getDetectedFaceCount() > 0) {
                                string faceText = "Faces: " + to_string(camera->getDetectedFaceCount());
                                cv::putText(frame, faceText, cv::Point(10, 30),
                                           cv::FONT_HERSHEY_SIMPLEX, 1, cv::Scalar(0, 255, 0), 2);
                            }
                            
                            cv::imshow("Live Preview", frame);
                            
                            int key = cv::waitKey(1);
                            if (key == 27) {  // ESC
                                previewing = false;
                            }
                        }
                    }
                    cv::destroyAllWindows();
                    break;
                }
                
                case 9: {
                    if (!connected) {
                        cout << "❌ Camera not connected\n";
                        break;
                    }
                    
                    cout << "\n" << camera->getStatistics() << "\n";
                    break;
                }
                
                case 10: {
                    cout << "Enter config filename (e.g., camera_config.json): ";
                    string configFile;
                    getline(cin, configFile);
                    
                    if (config->saveToFile("config/" + configFile)) {
                        cout << "✅ Configuration saved\n";
                    } else {
                        cout << "❌ Failed to save configuration\n";
                    }
                    break;
                }
                
                case 11: {
                    cout << "Enter config filename to load: ";
                    string configFile;
                    getline(cin, configFile);
                    
                    if (config->loadFromFile("config/" + configFile)) {
                        cout << "✅ Configuration loaded\n";
                        cout << "   Resolution: " << config->getWidth() << "x" << config->getHeight() << "\n";
                        cout << "   Face Detection: " << (config->getFaceDetectionEnabled() ? "Enabled" : "Disabled") << "\n";
                    } else {
                        cout << "❌ Failed to load configuration\n";
                    }
                    break;
                }
                
                case 0: {
                    cout << "Shutting down...\n";
                    if (connected) {
                        camera->disconnect();
                    }
                    LOG_INFO("Application closed");
                    return 0;
                }
                
                default:
                    cout << "❌ Invalid option. Please try again.\n";
            }
        }
        
        
    } catch (const exception& e) {
        LOG_CRITICAL("Fatal error: " + string(e.what()));
        cerr << "Fatal error: " << e.what() << "\n";
        return 1;
    }
    
    return 0;
}
