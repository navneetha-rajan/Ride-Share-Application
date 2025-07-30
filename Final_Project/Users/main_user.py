"""
User Service for Ride-Share Application

This module provides REST API endpoints for user management operations
including user creation, deletion, and listing.
"""

import os
import json
import logging
from typing import Dict, Any, Optional
from dataclasses import dataclass
from contextlib import contextmanager

from gevent import monkey
monkey.patch_all()
from gevent.pywsgi import WSGIServer

from flask import Flask, request, Response, jsonify
from werkzeug.exceptions import BadRequest, NotFound, InternalServerError
import requests

from user_requests import CreateUserRequests
from config import Config
from exceptions import UserServiceException, ValidationError
from utils.logger import setup_logger
from utils.validators import validate_json_content_type
from utils.response_helpers import create_response, create_error_response

# Setup logging
logger = setup_logger(__name__)

# Initialize Flask app
app = Flask(__name__)

# Load configuration
config = Config()

# Global counter for HTTP requests
http_request_counter = 0

@dataclass
class ServiceMetrics:
    """Service metrics tracking"""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0

metrics = ServiceMetrics()

@app.before_request
def before_request_handler():
    """Middleware to handle pre-request processing"""
    global http_request_counter
    http_request_counter += 1
    
    # Validate content type for PUT/POST requests
    if request.method in ['PUT', 'POST']:
        validate_json_content_type(request)
    
    logger.info(f"Request {http_request_counter}: {request.method} {request.path}")

@app.after_request
def after_request_handler(response):
    """Middleware to handle post-request processing"""
    logger.info(f"Response status: {response.status_code}")
    return response

@app.errorhandler(Exception)
def handle_exceptions(error):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {str(error)}", exc_info=True)
    return create_error_response(
        "Internal server error",
        status_code=500
    )

@app.errorhandler(BadRequest)
def handle_bad_request(error):
    """Handle bad request errors"""
    logger.warning(f"Bad request: {str(error)}")
    return create_error_response(
        str(error),
        status_code=400
    )

@app.route("/api/v1/users", methods=['PUT'])
def add_user():
    """
    Create a new user
    
    Expected JSON payload:
    {
        "username": "string",
        "password": "sha1_hash"
    }
    
    Returns:
        201: User created successfully
        400: Bad request (validation error, user already exists)
        500: Internal server error
    """
    try:
        global metrics
        metrics.total_requests += 1
        
        # Validate request body
        if not request.is_json:
            raise ValidationError("Content-Type must be application/json")
        
        body = request.get_json()
        if not body:
            raise ValidationError("Request body is required")
        
        # Validate user request
        user_request = CreateUserRequests(body)
        
        # Check if user already exists
        check_user_body = {
            'action': 'get_user',
            'username': user_request.getUsername()
        }
        
        response = requests.post(
            f"{config.DATABASE_URL}/api/v1/db/read",
            json=check_user_body,
            timeout=config.REQUEST_TIMEOUT
        )
        
        if response.status_code == 200:
            raise ValidationError(f"User {user_request.getUsername()} already exists")
        
        # Create user
        create_user_body = {
            'action': 'add_user',
            'username': user_request.getUsername(),
            'password': user_request.getPassword()
        }
        
        response = requests.post(
            f"{config.DATABASE_URL}/api/v1/db/write",
            json=create_user_body,
            timeout=config.REQUEST_TIMEOUT
        )
        
        if response.status_code != 200:
            logger.error(f"Database write failed: {response.text}")
            raise InternalServerError("Failed to create user")
        
        metrics.successful_requests += 1
        logger.info(f"User {user_request.getUsername()} created successfully")
        
        return create_response(
            message="User created successfully",
            status_code=201
        )
        
    except (ValidationError, BadRequest) as e:
        metrics.failed_requests += 1
        logger.warning(f"Validation error: {str(e)}")
        return create_error_response(str(e), status_code=400)
    except Exception as e:
        metrics.failed_requests += 1
        logger.error(f"Error creating user: {str(e)}", exc_info=True)
        return create_error_response("Internal server error", status_code=500)

@app.route("/api/v1/users/<username>", methods=['DELETE'])
def delete_user(username: str):
    """
    Delete a user by username
    
    Args:
        username: The username to delete
        
    Returns:
        200: User deleted successfully
        400: Bad request (user not found)
        500: Internal server error
    """
    try:
        global metrics
        metrics.total_requests += 1
        
        if not username:
            raise ValidationError("Username is required")
        
        # Check if user exists
        check_user_body = {
            'action': 'get_user',
            'username': username
        }
        
        response = requests.post(
            f"{config.DATABASE_URL}/api/v1/db/read",
            json=check_user_body,
            timeout=config.REQUEST_TIMEOUT
        )
        
        if response.status_code != 200:
            raise NotFound(f"User {username} not found")
        
        # Delete user
        delete_user_body = {
            'action': 'delete_user',
            'username': username
        }
        
        response = requests.post(
            f"{config.DATABASE_URL}/api/v1/db/write",
            json=delete_user_body,
            timeout=config.REQUEST_TIMEOUT
        )
        
        if response.status_code != 200:
            logger.error(f"Database write failed: {response.text}")
            raise InternalServerError("Failed to delete user")
        
        metrics.successful_requests += 1
        logger.info(f"User {username} deleted successfully")
        
        return create_response(
            message="User deleted successfully",
            status_code=200
        )
        
    except (ValidationError, NotFound) as e:
        metrics.failed_requests += 1
        logger.warning(f"Error deleting user: {str(e)}")
        return create_error_response(str(e), status_code=400)
    except Exception as e:
        metrics.failed_requests += 1
        logger.error(f"Error deleting user: {str(e)}", exc_info=True)
        return create_error_response("Internal server error", status_code=500)

@app.route("/api/v1/users", methods=['GET'])
def list_users():
    """
    Get list of all users
    
    Returns:
        200: List of users
        500: Internal server error
    """
    try:
        global metrics
        metrics.total_requests += 1
        
        body = {"action": "list_users"}
        
        response = requests.post(
            f"{config.DATABASE_URL}/api/v1/db/read",
            json=body,
            timeout=config.REQUEST_TIMEOUT
        )
        
        if response.status_code != 200:
            logger.error(f"Database read failed: {response.text}")
            raise InternalServerError("Failed to retrieve users")
        
        users = response.json()
        metrics.successful_requests += 1
        logger.info(f"Retrieved {len(users)} users")
        
        return create_response(
            data=users,
            status_code=200
        )
        
    except Exception as e:
        metrics.failed_requests += 1
        logger.error(f"Error listing users: {str(e)}", exc_info=True)
        return create_error_response("Internal server error", status_code=500)

@app.route("/api/v1/_count", methods=['GET'])
def get_request_count():
    """
    Get the number of HTTP requests made to this service
    
    Returns:
        200: Request count
    """
    return create_response(
        data=[http_request_counter],
        status_code=200
    )

@app.route("/api/v1/_count", methods=['DELETE'])
def reset_request_count():
    """
    Reset the HTTP request counter
    
    Returns:
        200: Counter reset successfully
    """
    global http_request_counter
    http_request_counter = 0
    
    logger.info("Request counter reset")
    return create_response(
        message="Request counter reset successfully",
        status_code=200
    )

@app.route("/health", methods=['GET'])
def health_check():
    """
    Health check endpoint
    
    Returns:
        200: Service is healthy
    """
    return create_response(
        data={
            "status": "healthy",
            "service": "user-service",
            "version": config.VERSION
        },
        status_code=200
    )

@app.route("/metrics", methods=['GET'])
def get_metrics():
    """
    Get service metrics
    
    Returns:
        200: Service metrics
    """
    return create_response(
        data={
            "total_requests": metrics.total_requests,
            "successful_requests": metrics.successful_requests,
            "failed_requests": metrics.failed_requests,
            "http_request_counter": http_request_counter
        },
        status_code=200
    )

@app.route("/")
def root():
    """Root endpoint"""
    return create_response(
        data={
            "service": "user-service",
            "version": config.VERSION,
            "endpoints": [
                "PUT /api/v1/users",
                "DELETE /api/v1/users/<username>",
                "GET /api/v1/users",
                "GET /api/v1/_count",
                "DELETE /api/v1/_count",
                "GET /health",
                "GET /metrics"
            ]
        },
        status_code=200
    )

if __name__ == "__main__":
    logger.info(f"Starting User Service on port {config.PORT}")
    logger.info(f"Database URL: {config.DATABASE_URL}")
    
    if config.DEBUG:
        app.run(
            debug=True,
            port=config.PORT,
            host='0.0.0.0'
        )
    else:
        http_server = WSGIServer(('0.0.0.0', config.PORT), app)
        logger.info("Starting WSGI server...")
        http_server.serve_forever()
