"""
Ride request models and validation

This module provides request models and validation for ride-related operations.
"""

import re
from typing import Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime
from werkzeug.exceptions import BadRequest

from exceptions import ValidationError
from utils.validators import validate_source_destination, validate_timestamp_format


@dataclass
class RideRequest:
    """Base class for ride requests"""
    
    def validate(self) -> None:
        """Validate the request data"""
        raise NotImplementedError("Subclasses must implement validate()")


@dataclass
class CreateRideRequest(RideRequest):
    """Request model for creating a new ride"""
    
    created_by: str
    source: int
    destination: int
    timestamp: str
    
    def __post_init__(self):
        """Validate request data after initialization"""
        self.validate()
    
    def validate(self) -> None:
        """Validate ride creation request"""
        try:
            self.created_by = self._validate_username(self.created_by)
            self.source = validate_source_destination(self.source, "source")
            self.destination = validate_source_destination(self.destination, "destination")
            self.timestamp = validate_timestamp_format(self.timestamp)
        except ValidationError as e:
            raise ValidationError(f"Invalid ride data: {str(e)}")
    
    @staticmethod
    def _validate_username(username: str) -> str:
        """Validate username format"""
        if not username:
            raise ValidationError("Created_by is required")
        
        if not isinstance(username, str):
            raise ValidationError("Created_by must be a string")
        
        if len(username.strip()) == 0:
            raise ValidationError("Created_by cannot be empty")
        
        if len(username) > 50:
            raise ValidationError("Created_by too long (max 50 characters)")
        
        # Check for valid characters (alphanumeric and underscore)
        if not re.match(r'^[a-zA-Z0-9_]+$', username):
            raise ValidationError("Created_by can only contain letters, numbers, and underscores")
        
        return username.strip()
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CreateRideRequest':
        """
        Create CreateRideRequest from dictionary
        
        Args:
            data: Dictionary containing ride data
            
        Returns:
            CreateRideRequest instance
            
        Raises:
            ValidationError: If required fields are missing
        """
        if not isinstance(data, dict):
            raise ValidationError("Request data must be a dictionary")
        
        required_fields = ['created_by', 'source', 'destination', 'timestamp']
        missing_fields = [field for field in required_fields if field not in data]
        
        if missing_fields:
            raise ValidationError(f"Missing required fields: {', '.join(missing_fields)}")
        
        return cls(
            created_by=data['created_by'],
            source=data['source'],
            destination=data['destination'],
            timestamp=data['timestamp']
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert request to dictionary"""
        return {
            'created_by': self.created_by,
            'source': self.source,
            'destination': self.destination,
            'timestamp': self.timestamp
        }


class RideRequestValidator:
    """Validator for ride requests"""
    
    @staticmethod
    def validate_source_format(source: Any) -> int:
        """
        Validate source location format
        
        Args:
            source: Source location to validate
            
        Returns:
            Validated source location
            
        Raises:
            ValidationError: If source is invalid
        """
        try:
            source_int = int(source)
            return validate_source_destination(source_int, "source")
        except (ValueError, TypeError):
            raise ValidationError("Source must be a valid integer")
    
    @staticmethod
    def validate_destination_format(destination: Any) -> int:
        """
        Validate destination location format
        
        Args:
            destination: Destination location to validate
            
        Returns:
            Validated destination location
            
        Raises:
            ValidationError: If destination is invalid
        """
        try:
            destination_int = int(destination)
            return validate_source_destination(destination_int, "destination")
        except (ValueError, TypeError):
            raise ValidationError("Destination must be a valid integer")
    
    @staticmethod
    def validate_timestamp_format(timestamp: str) -> str:
        """
        Validate timestamp format
        
        Args:
            timestamp: Timestamp string to validate
            
        Returns:
            Validated timestamp
            
        Raises:
            ValidationError: If timestamp format is invalid
        """
        return validate_timestamp_format(timestamp)
    
    @staticmethod
    def validate_ride_exists(ride_id: int, ride_list: list) -> bool:
        """
        Check if ride exists in the system
        
        Args:
            ride_id: Ride ID to check
            ride_list: List of existing ride IDs
            
        Returns:
            True if ride exists, False otherwise
        """
        return ride_id in ride_list


# Legacy compatibility classes (keeping for backward compatibility)
class Requests:
    """Base class for legacy request handling"""
    
    def getEntityObject(self):
        """Get entity object - to be implemented by subclasses"""
        pass
    
    def __init__(self, json_data: Dict[str, Any]):
        """Initialize with JSON data"""
        pass


def strauto(cls):
    """Decorator to add string representation to classes"""
    def __str__(self):
        return '%s(%s)' % (
            type(self).__name__,
            ', '.join('%s=%s' % member for member in vars(self).items())
        )
    cls.__str__ = __str__
    return cls


@strauto
class CreateRideRequests(Requests):
    """Legacy class for creating ride requests"""
    
    def getRideId(self) -> Optional[int]:
        """Get ride ID"""
        return getattr(self, '_rideId', None)
    
    def getCreatedBy(self) -> str:
        """Get created by username"""
        return self._created_by
    
    def getSource(self) -> int:
        """Get source location"""
        return self._source
    
    def getDestination(self) -> int:
        """Get destination location"""
        return self._destination
    
    def getTimestamp(self) -> datetime:
        """Get timestamp"""
        return self._timestamp
    
    @staticmethod
    def validateSource(source: Any) -> int:
        """
        Validate source location
        
        Args:
            source: Source location to validate
            
        Returns:
            Validated source location
            
        Raises:
            BadRequest: If source is invalid
        """
        try:
            source_int = int(source)
            if source_int < 1 or source_int > 198:
                raise BadRequest("Invalid source passed")
            return source_int
        except (ValueError, TypeError):
            raise BadRequest("Invalid source passed")
    
    @staticmethod
    def validateDestination(destination: Any) -> int:
        """
        Validate destination location
        
        Args:
            destination: Destination location to validate
            
        Returns:
            Validated destination location
            
        Raises:
            BadRequest: If destination is invalid
        """
        try:
            destination_int = int(destination)
            if destination_int < 1 or destination_int > 198:
                raise BadRequest("Invalid destination passed")
            return destination_int
        except (ValueError, TypeError):
            raise BadRequest("Invalid destination passed")
    
    @staticmethod
    def validateTimestamp(timestamp: str) -> datetime:
        """
        Validate timestamp format and convert to datetime
        
        Args:
            timestamp: Timestamp string to validate
            
        Returns:
            Datetime object
            
        Raises:
            BadRequest: If timestamp format is invalid
        """
        try:
            return datetime.strptime(timestamp, "%d-%m-%Y:%S-%M-%H")
        except Exception as ex:
            raise BadRequest(
                f"Invalid timestamp {timestamp}. Please use the format DD-MM-YYYY:SS-MM-HH"
            )
    
    def getEntityObject(self):
        """Get entity object for database operations"""
        # This would typically return a database entity
        # For now, return the request data
        return {
            'created_by': self._created_by,
            'source': self._source,
            'destination': self._destination,
            'timestamp': self._timestamp
        }
    
    def __init__(self, json_data: Dict[str, Any]):
        """Initialize with JSON data"""
        if 'created_by' not in json_data:
            raise BadRequest('Created_by not passed in the request')
        if 'timestamp' not in json_data:
            raise BadRequest('Timestamp not passed in the request')
        if 'source' not in json_data:
            raise BadRequest('Source not passed in the request')
        if 'destination' not in json_data:
            raise BadRequest('Destination not passed in the request')
        
        self._created_by = json_data['created_by']
        self._source = CreateRideRequests.validateSource(json_data['source'])
        self._destination = CreateRideRequests.validateDestination(json_data['destination'])
        self._timestamp = CreateRideRequests.validateTimestamp(json_data['timestamp'])
