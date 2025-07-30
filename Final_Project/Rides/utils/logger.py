"""
Logging utility for Rides Service

This module provides centralized logging configuration and setup.
"""

import logging
import sys
from typing import Optional
from config import Config


def setup_logger(name: str, level: Optional[str] = None) -> logging.Logger:
    """
    Setup and configure logger
    
    Args:
        name: Logger name
        level: Log level (optional, uses config default if not provided)
        
    Returns:
        Configured logger instance
    """
    config = Config()
    
    # Create logger
    logger = logging.getLogger(name)
    
    # Set log level
    log_level = level or config.LOG_LEVEL
    logger.setLevel(getattr(logging, log_level.upper()))
    
    # Avoid adding handlers if they already exist
    if logger.handlers:
        return logger
    
    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, log_level.upper()))
    
    # Create formatter
    formatter = logging.Formatter(config.LOG_FORMAT)
    console_handler.setFormatter(formatter)
    
    # Add handler to logger
    logger.addHandler(console_handler)
    
    return logger


def get_logger(name: str) -> logging.Logger:
    """
    Get logger instance
    
    Args:
        name: Logger name
        
    Returns:
        Logger instance
    """
    return logging.getLogger(name) 