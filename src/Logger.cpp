#include "Logger.h"
#include <iomanip>

Logger& Logger::getInstance() {
    static Logger instance;
    return instance;
}

Logger::Logger() : minLogLevel_(LogLevel::INFO), consoleOutput_(true), fileOutput_(true) {
}

Logger::~Logger() {
    if (logFile_.is_open()) {
        logFile_.close();
    }
}

void Logger::initialize(const std::string& logFilePath, LogLevel minLevel) {
    std::lock_guard<std::mutex> lock(mutex_);
    
    minLogLevel_ = minLevel;
    
    if (logFile_.is_open()) {
        logFile_.close();
    }
    
    logFile_.open(logFilePath, std::ios::app);
    if (!logFile_.is_open()) {
        std::cerr << "Failed to open log file: " << logFilePath << std::endl;
        fileOutput_ = false;
    }
}

void Logger::log(LogLevel level, const std::string& message) {
    std::lock_guard<std::mutex> lock(mutex_);
    
    if (level < minLogLevel_) {
        return;
    }
    
    std::string formattedMessage = formatMessage(level, message);
    
    if (consoleOutput_) {
        std::cout << formattedMessage << std::endl;
    }
    
    if (fileOutput_ && logFile_.is_open()) {
        logFile_ << formattedMessage << std::endl;
        logFile_.flush();
    }
}

void Logger::debug(const std::string& message) {
    log(LogLevel::DEBUG, message);
}

void Logger::info(const std::string& message) {
    log(LogLevel::INFO, message);
}

void Logger::warning(const std::string& message) {
    log(LogLevel::WARNING, message);
}

void Logger::error(const std::string& message) {
    log(LogLevel::ERROR, message);
}

void Logger::critical(const std::string& message) {
    log(LogLevel::CRITICAL, message);
}

std::string Logger::getTimestamp() const {
    auto now = std::chrono::system_clock::now();
    auto time = std::chrono::system_clock::to_time_t(now);
    auto ms = std::chrono::duration_cast<std::chrono::milliseconds>(
        now.time_since_epoch()) % 1000;
    
    std::stringstream ss;
    ss << std::put_time(std::localtime(&time), "%Y-%m-%d %H:%M:%S");
    ss << "." << std::setfill('0') << std::setw(3) << ms.count();
    
    return ss.str();
}

std::string Logger::getLevelString(LogLevel level) const {
    switch (level) {
        case LogLevel::DEBUG: return "DEBUG";
        case LogLevel::INFO: return "INFO ";
        case LogLevel::WARNING: return "WARN ";
        case LogLevel::ERROR: return "ERROR";
        case LogLevel::CRITICAL: return "CRIT ";
        default: return "UNKNOWN";
    }
}

std::string Logger::formatMessage(LogLevel level, const std::string& message) const {
    std::stringstream ss;
    ss << "[" << getTimestamp() << "] [" << getLevelString(level) << "] " << message;
    return ss.str();
}
