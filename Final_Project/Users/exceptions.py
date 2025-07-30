"""
Custom exceptions for User Service

This module defines custom exception classes for different types of errors
that can occur in the user service.
"""

from werkzeug.exceptions import HTTPException


class UserServiceException(Exception):
    """Base exception for User Service"""
    
    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class ValidationError(UserServiceException):
    """Exception raised for validation errors"""
    
    def __init__(self, message: str):
        super().__init__(message, status_code=400)


class DatabaseError(UserServiceException):
    """Exception raised for database-related errors"""
    
    def __init__(self, message: str):
        super().__init__(message, status_code=500)


class UserNotFoundError(UserServiceException):
    """Exception raised when a user is not found"""
    
    def __init__(self, username: str):
        super().__init__(f"User '{username}' not found", status_code=404)


class UserAlreadyExistsError(UserServiceException):
    """Exception raised when trying to create a user that already exists"""
    
    def __init__(self, username: str):
        super().__init__(f"User '{username}' already exists", status_code=409)


class ConfigurationError(UserServiceException):
    """Exception raised for configuration errors"""
    
    def __init__(self, message: str):
        super().__init__(message, status_code=500)


class ExternalServiceError(UserServiceException):
    """Exception raised when external service calls fail"""
    
    def __init__(self, service_name: str, message: str):
        super().__init__(f"{service_name} service error: {message}", status_code=502) 