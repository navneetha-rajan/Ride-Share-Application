"""
Custom exceptions for Rides Service

This module defines custom exception classes for different types of errors
that can occur in the rides service.
"""

from werkzeug.exceptions import HTTPException


class RideServiceException(Exception):
    """Base exception for Rides Service"""
    
    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class ValidationError(RideServiceException):
    """Exception raised for validation errors"""
    
    def __init__(self, message: str):
        super().__init__(message, status_code=400)


class DatabaseError(RideServiceException):
    """Exception raised for database-related errors"""
    
    def __init__(self, message: str):
        super().__init__(message, status_code=500)


class RideNotFoundError(RideServiceException):
    """Exception raised when a ride is not found"""
    
    def __init__(self, ride_id: int):
        super().__init__(f"Ride {ride_id} not found", status_code=404)


class UserNotFoundError(RideServiceException):
    """Exception raised when a user is not found"""
    
    def __init__(self, username: str):
        super().__init__(f"User '{username}' not found", status_code=404)


class InvalidLocationError(RideServiceException):
    """Exception raised for invalid location parameters"""
    
    def __init__(self, location_type: str, value: int, min_val: int, max_val: int):
        super().__init__(
            f"Invalid {location_type}: {value}. Must be between {min_val} and {max_val}",
            status_code=400
        )


class ConfigurationError(RideServiceException):
    """Exception raised for configuration errors"""
    
    def __init__(self, message: str):
        super().__init__(message, status_code=500)


class ExternalServiceError(RideServiceException):
    """Exception raised when external service calls fail"""
    
    def __init__(self, service_name: str, message: str):
        super().__init__(f"{service_name} service error: {message}", status_code=502) 