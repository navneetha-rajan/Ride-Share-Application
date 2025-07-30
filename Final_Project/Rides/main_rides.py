"""
Rides Service for Ride-Share Application

This module provides REST API endpoints for ride management operations
including ride creation, listing, joining, and deletion.
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

from ride_requests import CreateRideRequests
from config import Config
from exceptions import RideServiceException, ValidationError
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
    
    # Validate content type for POST requests
    if request.method == 'POST':
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
    return create_error_response(str(error), status_code=400)

@app.route("/api/v1/rides", methods=['POST'])
def add_ride():
    """
    Create a new ride
    
    Expected JSON payload:
    {
        "created_by": "username",
        "source": "int",
        "destination": "int", 
        "timestamp": "DD-MM-YYYY:SS-MM-HH"
    }
    
    Returns:
        201: Ride created successfully
        400: Bad request (validation error, user not found)
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
        
        # Validate ride request
        ride_request = CreateRideRequests(body)
        
        # Check if user exists
        check_user_body = {'username': ride_request.getCreatedBy()}
        response = requests.get(
            f"{config.USER_SERVICE_URL}/api/v1/users",
            json=check_user_body,
            timeout=config.REQUEST_TIMEOUT
        )
        
        if ride_request.getCreatedBy() not in response.text:
            raise ValidationError(f"User {ride_request.getCreatedBy()} not found")
        
        # Create ride
        create_ride_body = {
            'action': 'add_ride',
            'created_by': ride_request.getCreatedBy(),
            'source': ride_request.getSource(),
            'destination': ride_request.getDestination(),
            'timestamp': ride_request.getTimestamp().strftime("%d-%m-%Y:%S-%M-%H")
        }
        
        response = requests.post(
            f"{config.DATABASE_URL}/api/v1/db/write",
            json=create_ride_body,
            timeout=config.REQUEST_TIMEOUT
        )
        
        if response.status_code != 200:
            logger.error(f"Database write failed: {response.text}")
            raise InternalServerError("Failed to create ride")
        
        metrics.successful_requests += 1
        logger.info(f"Ride created successfully by {ride_request.getCreatedBy()}")
        
        return create_response(
            data=response.json(),
            status_code=201
        )
        
    except (ValidationError, BadRequest) as e:
        metrics.failed_requests += 1
        logger.warning(f"Validation error: {str(e)}")
        return create_error_response(str(e), status_code=400)
    except Exception as e:
        metrics.failed_requests += 1
        logger.error(f"Error creating ride: {str(e)}", exc_info=True)
        return create_error_response("Internal server error", status_code=500)

@app.route("/api/v1/rides", methods=['GET'])
def list_upcoming_rides():
    """
    Get list of upcoming rides with source and destination filters
    
    Query Parameters:
        source: Source location ID (1-198)
        destination: Destination location ID (1-198)
    
    Returns:
        200: List of rides
        204: No rides found
        400: Bad request (invalid parameters)
        500: Internal server error
    """
    try:
        global metrics
        metrics.total_requests += 1
        
        # Validate query parameters
        source = request.args.get("source")
        destination = request.args.get("destination")
        
        if not source or not destination:
            raise ValidationError("Source and destination parameters are required")
        
        # Validate source and destination
        try:
            source = int(source)
            destination = int(destination)
            
            if source < 1 or source > 198:
                raise ValidationError("Source must be between 1 and 198")
            if destination < 1 or destination > 198:
                raise ValidationError("Destination must be between 1 and 198")
        except ValueError:
            raise ValidationError("Source and destination must be valid integers")
        
        # Get rides from database
        body = {
            "action": "list_upcoming_ride",
            "source": str(source),
            "destination": str(destination)
        }
        
        response = requests.post(
            f"{config.DATABASE_URL}/api/v1/db/read",
            json=body,
            timeout=config.REQUEST_TIMEOUT
        )
        
        if response.status_code != 200:
            logger.error(f"Database read failed: {response.text}")
            raise InternalServerError("Failed to retrieve rides")
        
        rides = response.json()
        
        if not rides or len(rides) == 0:
            metrics.successful_requests += 1
            return create_response(
                status_code=204
            )
        
        metrics.successful_requests += 1
        logger.info(f"Retrieved {len(rides)} rides")
        
        return create_response(
            data=rides,
            status_code=200
        )
        
    except (ValidationError, BadRequest) as e:
        metrics.failed_requests += 1
        logger.warning(f"Validation error: {str(e)}")
        return create_error_response(str(e), status_code=400)
    except Exception as e:
        metrics.failed_requests += 1
        logger.error(f"Error listing rides: {str(e)}", exc_info=True)
        return create_error_response("Internal server error", status_code=500)

@app.route("/api/v1/rides/<int:ride_id>", methods=['GET'])
def get_ride(ride_id: int):
    """
    Get details of a specific ride
    
    Args:
        ride_id: ID of the ride to retrieve
        
    Returns:
        200: Ride details
        204: Ride not found
        500: Internal server error
    """
    try:
        global metrics
        metrics.total_requests += 1
        
        if ride_id <= 0:
            raise ValidationError("Ride ID must be a positive integer")
        
        body = {
            "action": "get_ride",
            "ride_id": ride_id
        }
        
        response = requests.post(
            f"{config.DATABASE_URL}/api/v1/db/read",
            json=body,
            timeout=config.REQUEST_TIMEOUT
        )
        
        if response.status_code != 200:
            metrics.successful_requests += 1
            return create_response(
                status_code=204
            )
        
        ride_data = response.json()
        metrics.successful_requests += 1
        logger.info(f"Retrieved ride {ride_id}")
        
        return create_response(
            data=ride_data,
            status_code=200
        )
        
    except ValidationError as e:
        metrics.failed_requests += 1
        logger.warning(f"Validation error: {str(e)}")
        return create_error_response(str(e), status_code=400)
    except Exception as e:
        metrics.failed_requests += 1
        logger.error(f"Error getting ride: {str(e)}", exc_info=True)
        return create_error_response("Internal server error", status_code=500)

@app.route("/api/v1/rides/count", methods=['GET'])
def get_ride_count():
    """
    Get total number of rides
    
    Returns:
        200: Ride count
        500: Internal server error
    """
    try:
        global metrics
        metrics.total_requests += 1
        
        body = {"action": "num_ride"}
        
        response = requests.post(
            f"{config.DATABASE_URL}/api/v1/db/read",
            json=body,
            timeout=config.REQUEST_TIMEOUT
        )
        
        if response.status_code != 200:
            logger.error(f"Database read failed: {response.text}")
            raise InternalServerError("Failed to get ride count")
        
        count_data = response.json()
        metrics.successful_requests += 1
        logger.info(f"Retrieved ride count: {count_data}")
        
        return create_response(
            data=count_data,
            status_code=200
        )
        
    except Exception as e:
        metrics.failed_requests += 1
        logger.error(f"Error getting ride count: {str(e)}", exc_info=True)
        return create_error_response("Internal server error", status_code=500)

@app.route("/api/v1/rides/<int:ride_id>", methods=['POST'])
def join_ride(ride_id: int):
    """
    Join an existing ride
    
    Args:
        ride_id: ID of the ride to join
        
    Expected JSON payload:
    {
        "username": "username"
    }
    
    Returns:
        200: Successfully joined ride
        400: Bad request (validation error, user not found)
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
        
        if 'username' not in body:
            raise ValidationError("Username is required in request body")
        
        username = body['username']
        
        # Check if user exists
        check_user_body = {'username': username}
        response = requests.get(
            f"{config.USER_SERVICE_URL}/api/v1/users",
            json=check_user_body,
            timeout=config.REQUEST_TIMEOUT
        )
        
        if username not in response.text:
            raise ValidationError(f"User {username} not found")
        
        # Join ride
        join_ride_body = {
            "action": "join_ride",
            "ride_id": ride_id,
            "username": username
        }
        
        response = requests.post(
            f"{config.DATABASE_URL}/api/v1/db/write",
            json=join_ride_body,
            timeout=config.REQUEST_TIMEOUT
        )
        
        if response.status_code != 200:
            logger.error(f"Database write failed: {response.text}")
            raise InternalServerError("Failed to join ride")
        
        metrics.successful_requests += 1
        logger.info(f"User {username} joined ride {ride_id}")
        
        return create_response(
            message="Successfully joined ride",
            status_code=200
        )
        
    except (ValidationError, BadRequest) as e:
        metrics.failed_requests += 1
        logger.warning(f"Validation error: {str(e)}")
        return create_error_response(str(e), status_code=400)
    except Exception as e:
        metrics.failed_requests += 1
        logger.error(f"Error joining ride: {str(e)}", exc_info=True)
        return create_error_response("Internal server error", status_code=500)

@app.route("/api/v1/rides/<int:ride_id>", methods=['DELETE'])
def delete_ride(ride_id: int):
    """
    Delete a ride
    
    Args:
        ride_id: ID of the ride to delete
        
    Returns:
        200: Ride deleted successfully
        500: Internal server error
    """
    try:
        global metrics
        metrics.total_requests += 1
        
        if ride_id <= 0:
            raise ValidationError("Ride ID must be a positive integer")
        
        body = {
            "action": "delete_ride",
            "ride_id": ride_id
        }
        
        response = requests.post(
            f"{config.DATABASE_URL}/api/v1/db/write",
            json=body,
            timeout=config.REQUEST_TIMEOUT
        )
        
        if response.status_code != 200:
            logger.error(f"Database write failed: {response.text}")
            raise InternalServerError("Failed to delete ride")
        
        metrics.successful_requests += 1
        logger.info(f"Ride {ride_id} deleted successfully")
        
        return create_response(
            message="Ride deleted successfully",
            status_code=200
        )
        
    except ValidationError as e:
        metrics.failed_requests += 1
        logger.warning(f"Validation error: {str(e)}")
        return create_error_response(str(e), status_code=400)
    except Exception as e:
        metrics.failed_requests += 1
        logger.error(f"Error deleting ride: {str(e)}", exc_info=True)
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
            "service": "ride-service",
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
            "service": "ride-service",
            "version": config.VERSION,
            "endpoints": [
                "POST /api/v1/rides",
                "GET /api/v1/rides",
                "GET /api/v1/rides/<ride_id>",
                "GET /api/v1/rides/count",
                "POST /api/v1/rides/<ride_id>",
                "DELETE /api/v1/rides/<ride_id>",
                "GET /api/v1/_count",
                "DELETE /api/v1/_count",
                "GET /health",
                "GET /metrics"
            ]
        },
        status_code=200
    )

if __name__ == "__main__":
    logger.info(f"Starting Ride Service on port {config.PORT}")
    logger.info(f"Database URL: {config.DATABASE_URL}")
    logger.info(f"User Service URL: {config.USER_SERVICE_URL}")
    
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
