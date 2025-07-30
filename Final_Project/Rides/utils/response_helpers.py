"""
Response helper utilities for Rides Service

This module provides standardized response formatting and error handling.
"""

import json
from typing import Any, Dict, Optional
from flask import Response, jsonify
from werkzeug.exceptions import HTTPException


def create_response(
    data: Any = None,
    message: str = None,
    status_code: int = 200,
    headers: Optional[Dict[str, str]] = None
) -> Response:
    """
    Create a standardized API response
    
    Args:
        data: Response data
        message: Response message
        status_code: HTTP status code
        headers: Additional response headers
        
    Returns:
        Flask Response object
    """
    response_data = {}
    
    if data is not None:
        response_data['data'] = data
    
    if message:
        response_data['message'] = message
    
    response = jsonify(response_data)
    response.status_code = status_code
    
    # Set default headers
    response.headers['Content-Type'] = 'application/json'
    
    # Add custom headers
    if headers:
        for key, value in headers.items():
            response.headers[key] = value
    
    return response


def create_error_response(
    message: str,
    status_code: int = 400,
    error_code: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None
) -> Response:
    """
    Create a standardized error response
    
    Args:
        message: Error message
        status_code: HTTP status code
        error_code: Optional error code
        details: Optional error details
        
    Returns:
        Flask Response object
    """
    error_data = {
        'error': {
            'message': message,
            'status_code': status_code
        }
    }
    
    if error_code:
        error_data['error']['code'] = error_code
    
    if details:
        error_data['error']['details'] = details
    
    response = jsonify(error_data)
    response.status_code = status_code
    response.headers['Content-Type'] = 'application/json'
    
    return response


def create_pagination_response(
    data: list,
    page: int,
    per_page: int,
    total: int,
    status_code: int = 200
) -> Response:
    """
    Create a paginated response
    
    Args:
        data: List of items
        page: Current page number
        per_page: Items per page
        total: Total number of items
        status_code: HTTP status code
        
    Returns:
        Flask Response object
    """
    total_pages = (total + per_page - 1) // per_page
    
    pagination_data = {
        'data': data,
        'pagination': {
            'page': page,
            'per_page': per_page,
            'total': total,
            'total_pages': total_pages,
            'has_next': page < total_pages,
            'has_prev': page > 1
        }
    }
    
    return create_response(
        data=pagination_data,
        status_code=status_code
    )


def handle_http_exception(error: HTTPException) -> Response:
    """
    Handle HTTP exceptions
    
    Args:
        error: HTTPException instance
        
    Returns:
        Flask Response object
    """
    return create_error_response(
        message=str(error),
        status_code=error.code
    )


def create_health_response(
    service_name: str,
    version: str,
    status: str = "healthy",
    additional_info: Optional[Dict[str, Any]] = None
) -> Response:
    """
    Create a health check response
    
    Args:
        service_name: Name of the service
        version: Service version
        status: Health status
        additional_info: Additional health information
        
    Returns:
        Flask Response object
    """
    health_data = {
        'service': service_name,
        'version': version,
        'status': status,
        'timestamp': None  # Will be set by the caller if needed
    }
    
    if additional_info:
        health_data.update(additional_info)
    
    return create_response(
        data=health_data,
        status_code=200
    ) 