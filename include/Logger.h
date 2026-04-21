#ifndef LOGGER_H
#define LOGGER_H

#include <string>
#include <fstream>
#include <iostream>
#include <sstream>
#include <chrono>
#include <mutex>

enum class LogLevel {
    DEBUG = 0,
    INFO = 1,
    WARNING = 2,
    ERROR = 3,
    CRITICAL = 4
};

class Logger {
public:
    static Logger& getInstance();
    
    void initialize(const std::string& logFilePath, LogLevel minLevel = LogLevel::INFO);
    
    void log(LogLevel level, const std::string& message);
    void debug(const std::string& message);
    void info(const std::string& message);
    void warning(const std::string& message);
    void error(const std::string& message);
    void critical(const std::string& message);
    
    void setConsoleOutput(bool enabled) { consoleOutput_ = enabled; }
    void setFileOutput(bool enabled) { fileOutput_ = enabled; }
    void setMinLogLevel(LogLevel level) { minLogLevel_ = level; }
    
private:
    Logger();
    ~Logger();
    
    Logger(const Logger&) = delete;
    Logger& operator=(const Logger&) = delete;
    
    std::string getTimestamp() const;
    std::string getLevelString(LogLevel level) const;
    std::string formatMessage(LogLevel level, const std::string& message) const;
    
    std::ofstream logFile_;
    LogLevel minLogLevel_;
    bool consoleOutput_;
    bool fileOutput_;
    std::mutex mutex_;
};

#define LOG_DEBUG(msg) Logger::getInstance().debug(msg)
#define LOG_INFO(msg) Logger::getInstance().info(msg)
#define LOG_WARNING(msg) Logger::getInstance().warning(msg)
#define LOG_ERROR(msg) Logger::getInstance().error(msg)
#define LOG_CRITICAL(msg) Logger::getInstance().critical(msg)

#endif // LOGGER_H
