"""
Validation utilities for User Service

This module provides validation functions for request data and content types.
"""

from flask import Request
from werkzeug.exceptions import BadRequest
from exceptions import ValidationError


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


def validate_password(password: str) -> str:
    """
    Validate password format (SHA1 hash)
    
    Args:
        password: Password to validate
        
    Returns:
        Validated password
        
    Raises:
        ValidationError: If password is invalid
    """
    if not password:
        raise ValidationError("Password is required")
    
    if not isinstance(password, str):
        raise ValidationError("Password must be a string")
    
    # Validate SHA1 format (40 hexadecimal characters)
    import re
    sha1_pattern = re.compile(r'^[a-fA-F0-9]{40}$')
    
    if not sha1_pattern.match(password):
        raise ValidationError("Password must be a valid SHA1 hash (40 hexadecimal characters)")
    
    return password


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