cmake_minimum_required(VERSION 3.10)
project(USBCameraFaceDetection VERSION 1.0.0 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Find OpenCV
find_package(OpenCV REQUIRED)

# Add include directories
include_directories(${OpenCV_INCLUDE_DIRS})
include_directories(${CMAKE_SOURCE_DIR}/include)

# Find nlohmann_json (for configuration)
find_package(nlohmann_json 3.2.0 QUIET)
if(NOT nlohmann_json_FOUND)
    # Include it as a single header library
    include_directories(${CMAKE_SOURCE_DIR}/extern)
endif()

# Source files
set(SOURCES
    src/USBCamera.cpp
    src/FaceDetector.cpp
    src/ImageProcessor.cpp
    src/CameraConfig.cpp
    src/Logger.cpp
)

# Main executable
add_executable(usb_camera_app main_usb_camera.cpp ${SOURCES})
target_link_libraries(usb_camera_app ${OpenCV_LIBS})

# Optional: Test executable
add_executable(test_camera test_camera.cpp ${SOURCES})
target_link_libraries(test_camera ${OpenCV_LIBS})

# Compiler flags
if(MSVC)
    add_compile_options(/W4 /permissive-)
else()
    add_compile_options(-Wall -Wextra -Wpedantic)
endif()

# Output directories
set_target_properties(usb_camera_app PROPERTIES
    RUNTIME_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/bin"
)

set_target_properties(test_camera PROPERTIES
    RUNTIME_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/bin"
)

message(STATUS "OpenCV version: ${OpenCV_VERSION}")
message(STATUS "Project: ${PROJECT_NAME} ${PROJECT_VERSION}")
