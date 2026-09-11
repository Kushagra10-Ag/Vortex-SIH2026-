"""
Centralized Logging Module for Edge-AI
Provides structured logging with file and console output
"""

import logging
import os
from datetime import datetime
from logging.handlers import RotatingFileHandler
import sys

# Import LogConfig to avoid circular dependency
try:
    from .constants import LogConfig
except ImportError:
    # Fallback if constants import fails
    class LogConfig:
        LOG_LEVEL = "INFO"
        LOG_FILE = "logs/edge_ai.log"
        LOG_FORMAT = "%(asctime)s - [%(name)s] - [%(levelname)s] - %(message)s"
        LOG_RETENTION_DAYS = 7


class EdgeAILogger:
    """Singleton logger for edge-ai module with structured formatting"""
    
    _instance = None
    _logger = None
    
    def __new__(cls):
        """Ensure only one logger instance exists"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init_logger()
        return cls._instance
    
    def _init_logger(self):
        """Initialize logger with file and console handlers"""
        
        # Create logger
        self._logger = logging.getLogger("edge_ai")
        self._logger.setLevel(logging.DEBUG)  # Capture all levels
        
        # Prevent duplicate handlers
        if self._logger.handlers:
            return
        
        # Create logs directory if it doesn't exist
        log_dir = os.path.dirname(LogConfig.LOG_FILE)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)
        
        # Formatter
        formatter = logging.Formatter(
            fmt="%(asctime)s - [%(name)s] - [%(levelname)s] - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        
        # Console Handler (stdout) — INFO and above
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(getattr(logging, LogConfig.LOG_LEVEL))
        console_handler.setFormatter(formatter)
        self._logger.addHandler(console_handler)
        
        # File Handler with rotation — DEBUG and above
        try:
            file_handler = RotatingFileHandler(
                LogConfig.LOG_FILE,
                maxBytes=10 * 1024 * 1024,  # 10 MB
                backupCount=5
            )
            file_handler.setLevel(logging.DEBUG)
            file_handler.setFormatter(formatter)
            self._logger.addHandler(file_handler)
        except Exception as e:
            print(f"Warning: Could not create file handler: {e}")
    
    def debug(self, message: str, **kwargs):
        """Log debug message"""
        self._logger.debug(message, extra=kwargs)
    
    def info(self, message: str, **kwargs):
        """Log info message"""
        self._logger.info(message, extra=kwargs)
    
    def warning(self, message: str, **kwargs):
        """Log warning message"""
        self._logger.warning(message, extra=kwargs)
    
    def error(self, message: str, **kwargs):
        """Log error message"""
        self._logger.error(message, extra=kwargs)
    
    def critical(self, message: str, **kwargs):
        """Log critical message"""
        self._logger.critical(message, extra=kwargs)
    
    def exception(self, message: str):
        """Log exception with traceback"""
        self._logger.exception(message)


# Global logger instance
logger = EdgeAILogger()


# Convenience functions
def log_debug(message: str):
    """Quick debug log"""
    logger.debug(message)


def log_info(message: str):
    """Quick info log"""
    logger.info(message)


def log_warning(message: str):
    """Quick warning log"""
    logger.warning(message)


def log_error(message: str):
    """Quick error log"""
    logger.error(message)


def log_critical(message: str):
    """Quick critical log"""
    logger.critical(message)


def log_exception(message: str):
    """Log exception with traceback"""
    logger.exception(message)
