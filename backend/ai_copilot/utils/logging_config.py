"""
Logging Configuration for AI Copilot

Structured logging with different levels and output formats.

Author: Enterprise Scanner Team
Version: 1.0.0
"""

import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional


class ColoredFormatter(logging.Formatter):
    """Colored console formatter"""
    
    # ANSI color codes
    COLORS = {
        'DEBUG': '\033[36m',     # Cyan
        'INFO': '\033[32m',      # Green
        'WARNING': '\033[33m',   # Yellow
        'ERROR': '\033[31m',     # Red
        'CRITICAL': '\033[35m',  # Magenta
        'RESET': '\033[0m'       # Reset
    }
    
    def format(self, record):
        """Format log record with colors"""
        if record.levelname in self.COLORS:
            record.levelname = (
                f"{self.COLORS[record.levelname]}{record.levelname}"
                f"{self.COLORS['RESET']}"
            )
        return super().format(record)


def setup_logging(
    log_level: str = "INFO",
    log_file: Optional[str] = None,
    enable_colors: bool = True,
    log_format: str = "standard"
) -> logging.Logger:
    """
    Setup logging configuration
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional log file path
        enable_colors: Enable colored console output
        log_format: Format style ('standard', 'detailed', 'json')
        
    Returns:
        Configured logger
    """
    # Get root logger
    logger = logging.getLogger('ai_copilot')
    logger.setLevel(getattr(logging, log_level.upper()))
    
    # Remove existing handlers
    logger.handlers.clear()
    
    # Choose format
    if log_format == "detailed":
        fmt = (
            '%(asctime)s | %(name)-30s | %(levelname)-8s | '
            '%(filename)s:%(lineno)d | %(funcName)s() | %(message)s'
        )
    elif log_format == "json":
        fmt = '{"time":"%(asctime)s","logger":"%(name)s","level":"%(levelname)s","message":"%(message)s"}'
    else:  # standard
        fmt = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, log_level.upper()))
    
    if enable_colors and log_format != "json":
        formatter = ColoredFormatter(fmt, datefmt='%Y-%m-%d %H:%M:%S')
    else:
        formatter = logging.Formatter(fmt, datefmt='%Y-%m-%d %H:%M:%S')
    
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler (if specified)
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)  # Log everything to file
        
        # File logs are always detailed
        file_formatter = logging.Formatter(
            '%(asctime)s | %(name)s | %(levelname)s | %(filename)s:%(lineno)d | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
    
    return logger


# Export
__all__ = ['setup_logging', 'ColoredFormatter']
