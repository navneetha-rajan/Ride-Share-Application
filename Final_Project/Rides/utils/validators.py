"""
Validation utilities for Rides Service

This module provides validation functions for request data and content types.
"""

from flask import Request
from werkzeug.exceptions import BadRequest
from exceptions import ValidationError, InvalidLocationError
from config import Config


def validate_json_content_type(request: Request) -> None:
    """
    Validate that request has JSON content type
    
    Args:
        request: Flask request object
        
    Raises:
        ValidationError: If content type is not application/json
    """
    if not request.is_json:
        raise ValidationError("Content-Type must be application/json")


def validate_source_destination(value: int, location_type: str) -> int:
    """
    Validate source or destination location
    
    Args:
        value: Location value to validate
        location_type: Type of location (source or destination)
        
    Returns:
        Validated location value
        
    Raises:
        InvalidLocationError: If location is invalid
    """
    config = Config()
    
    if not isinstance(value, int):
        raise ValidationError(f"{location_type} must be an integer")
    
    if value < config.MIN_SOURCE_DESTINATION or value > config.MAX_SOURCE_DESTINATION:
        raise InvalidLocationError(
            location_type, 
            value, 
            config.MIN_SOURCE_DESTINATION, 
            config.MAX_SOURCE_DESTINATION
        )
    
    return value


def validate_ride_id(ride_id: int) -> int:
    """
    Validate ride ID
    
    Args:
        ride_id: Ride ID to validate
        
    Returns:
        Validated ride ID
        
    Raises:
        ValidationError: If ride ID is invalid
    """
    if not isinstance(ride_id, int):
        raise ValidationError("Ride ID must be an integer")
    
    if ride_id <= 0:
        raise ValidationError("Ride ID must be a positive integer")
    
    return ride_id


def validate_timestamp_format(timestamp: str) -> str:
    """
    Validate timestamp format (DD-MM-YYYY:SS-MM-HH)
    
    Args:
        timestamp: Timestamp string to validate
        
    Returns:
        Validated timestamp
        
    Raises:
        ValidationError: If timestamp format is invalid
    """
    if not timestamp:
        raise ValidationError("Timestamp is required")
    
    if not isinstance(timestamp, str):
        raise ValidationError("Timestamp must be a string")
    
    # Validate format DD-MM-YYYY:SS-MM-HH
    import re
    timestamp_pattern = re.compile(r'^\d{2}-\d{2}-\d{4}:\d{2}-\d{2}-\d{2}$')
    
    if not timestamp_pattern.match(timestamp):
        raise ValidationError(
            "Invalid timestamp format. Please use DD-MM-YYYY:SS-MM-HH"
        )
    
    return timestamp


def validate_request_body(body: dict, required_fields: list) -> dict:
    """
    Validate request body contains required fields
    
    Args:
        body: Request body dictionary
        required_fields: List of required field names
        
    Returns:
        Validated body
        
    Raises:
        ValidationError: If required fields are missing
    """
    if not body:
        raise ValidationError("Request body is required")
    
    if not isinstance(body, dict):
        raise ValidationError("Request body must be a JSON object")
    
    missing_fields = []
    for field in required_fields:
        if field not in body or body[field] is None:
            missing_fields.append(field)
    
    if missing_fields:
        raise ValidationError(f"Missing required fields: {', '.join(missing_fields)}")
    
    return body


def validate_username(username: str) -> str:
    """
    Validate username format
    
    Args:
        username: Username to validate
        
    Returns:
        Validated username
        
    Raises:
        ValidationError: If username is invalid
    """
    if not username:
        raise ValidationError("Username is required")
    
    if not isinstance(username, str):
        raise ValidationError("Username must be a string")
    
    if len(username.strip()) == 0:
        raise ValidationError("Username cannot be empty")
    
    if len(username) > 50:
        raise ValidationError("Username too long (max 50 characters)")
    
    # Check for valid characters (alphanumeric and underscore)
    import re
    if not re.match(r'^[a-zA-Z0-9_]+$', username):
        raise ValidationError("Username can only contain letters, numbers, and underscores")
    
    return username.strip() 