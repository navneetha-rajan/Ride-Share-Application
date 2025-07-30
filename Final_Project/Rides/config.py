"""
Configuration management for Rides Service

This module handles all configuration settings including environment variables,
default values, and configuration validation.
"""

import os
from typing import Optional
from dataclasses import dataclass


@dataclass
class Config:
    """Configuration class for Rides Service"""
    
    # Service Configuration
    PORT: int = int(os.getenv('PORT', 80))
    DEBUG: bool = os.getenv('DEBUG', 'false').lower() == 'true'
    VERSION: str = os.getenv('VERSION', '1.0.0')
    
    # Database Configuration
    DATABASE_URL: str = os.getenv('DATABASE_URL', 'http://52.86.125.105')
    REQUEST_TIMEOUT: int = int(os.getenv('REQUEST_TIMEOUT', 30))
    
    # User Service Configuration
    USER_SERVICE_URL: str = os.getenv('USER_SERVICE_URL', 'http://52.86.125.105')
    
    # Logging Configuration
    LOG_LEVEL: str = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FORMAT: str = os.getenv('LOG_FORMAT', '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # Security Configuration
    MAX_REQUEST_SIZE: int = int(os.getenv('MAX_REQUEST_SIZE', 16 * 1024 * 1024))  # 16MB
    ALLOWED_CONTENT_TYPES: list = None
    
    # Ride Configuration
    MAX_SOURCE_DESTINATION: int = int(os.getenv('MAX_SOURCE_DESTINATION', 198))
    MIN_SOURCE_DESTINATION: int = int(os.getenv('MIN_SOURCE_DESTINATION', 1))
    
    def __post_init__(self):
        """Post-initialization validation and setup"""
        if self.ALLOWED_CONTENT_TYPES is None:
            self.ALLOWED_CONTENT_TYPES = ['application/json']
        
        # Validate configuration
        self._validate_config()
    
    def _validate_config(self):
        """Validate configuration values"""
        if self.PORT < 1 or self.PORT > 65535:
            raise ValueError(f"Invalid port number: {self.PORT}")
        
        if not self.DATABASE_URL:
            raise ValueError("DATABASE_URL is required")
        
        if not self.USER_SERVICE_URL:
            raise ValueError("USER_SERVICE_URL is required")
        
        if self.REQUEST_TIMEOUT < 1:
            raise ValueError(f"Invalid request timeout: {self.REQUEST_TIMEOUT}")
        
        if self.MAX_SOURCE_DESTINATION < self.MIN_SOURCE_DESTINATION:
            raise ValueError("MAX_SOURCE_DESTINATION must be greater than MIN_SOURCE_DESTINATION")
    
    def to_dict(self) -> dict:
        """Convert configuration to dictionary"""
        return {
            'port': self.PORT,
            'debug': self.DEBUG,
            'version': self.VERSION,
            'database_url': self.DATABASE_URL,
            'user_service_url': self.USER_SERVICE_URL,
            'request_timeout': self.REQUEST_TIMEOUT,
            'log_level': self.LOG_LEVEL,
            'max_request_size': self.MAX_REQUEST_SIZE,
            'max_source_destination': self.MAX_SOURCE_DESTINATION,
            'min_source_destination': self.MIN_SOURCE_DESTINATION
        } 