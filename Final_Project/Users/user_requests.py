"""
User request models and validation

This module provides request models and validation for user-related operations.
"""

import hashlib
import re
from typing import Dict, Any, Optional
from dataclasses import dataclass
from werkzeug.exceptions import BadRequest

from exceptions import ValidationError
from utils.validators import validate_username, validate_password


@dataclass
class UserRequest:
    """Base class for user requests"""
    
    def validate(self) -> None:
        """Validate the request data"""
        raise NotImplementedError("Subclasses must implement validate()")


@dataclass
class CreateUserRequest(UserRequest):
    """Request model for creating a new user"""
    
    username: str
    password: str
    
    def __post_init__(self):
        """Validate request data after initialization"""
        self.validate()
    
    def validate(self) -> None:
        """Validate user creation request"""
        try:
            self.username = validate_username(self.username)
            self.password = validate_password(self.password)
        except ValidationError as e:
            raise ValidationError(f"Invalid user data: {str(e)}")
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CreateUserRequest':
        """
        Create CreateUserRequest from dictionary
        
        Args:
            data: Dictionary containing user data
            
        Returns:
            CreateUserRequest instance
            
        Raises:
            ValidationError: If required fields are missing
        """
        if not isinstance(data, dict):
            raise ValidationError("Request data must be a dictionary")
        
        required_fields = ['username', 'password']
        missing_fields = [field for field in required_fields if field not in data]
        
        if missing_fields:
            raise ValidationError(f"Missing required fields: {', '.join(missing_fields)}")
        
        return cls(
            username=data['username'],
            password=data['password']
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert request to dictionary"""
        return {
            'username': self.username,
            'password': self.password
        }


class UserRequestValidator:
    """Validator for user requests"""
    
    @staticmethod
    def validate_username_format(username: str) -> str:
        """
        Validate username format
        
        Args:
            username: Username to validate
            
        Returns:
            Validated username
            
        Raises:
            ValidationError: If username is invalid
        """
        return validate_username(username)
    
    @staticmethod
    def validate_password_format(password: str) -> str:
        """
        Validate password format (SHA1 hash)
        
        Args:
            password: Password to validate
            
        Returns:
            Validated password
            
        Raises:
            ValidationError: If password is invalid
        """
        return validate_password(password)
    
    @staticmethod
    def validate_user_exists(username: str, user_list: list) -> bool:
        """
        Check if user exists in the system
        
        Args:
            username: Username to check
            user_list: List of existing usernames
            
        Returns:
            True if user exists, False otherwise
        """
        return username in user_list


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
class CreateUserRequests(Requests):
    """Legacy class for creating user requests"""
    
    def getUsername(self) -> str:
        """Get username"""
        return self._username
    
    def getPassword(self) -> str:
        """Get password"""
        return self._password
    
    @staticmethod
    def validatePassword(password: str) -> str:
        """
        Validate password format (SHA1 hash)
        
        Args:
            password: Password to validate
            
        Returns:
            Validated password
            
        Raises:
            BadRequest: If password is invalid
        """
        sha1_re = re.compile("^[a-fA-F0-9]{40}$")
        
        if sha1_re.search(password) is None:
            raise BadRequest("Password is not in SHA1 format")
        
        return password
    
    def getEntityObject(self):
        """Get entity object for database operations"""
        from database_users import User
        return User(
            username=self._username,
            password=hashlib.sha1(self._password.encode()).hexdigest()
        )
    
    def __init__(self, json_data: Dict[str, Any]):
        """Initialize with JSON data"""
        if 'username' not in json_data:
            raise BadRequest('Username not passed in the request')
        if 'password' not in json_data:
            raise BadRequest('Password not passed in the request')
        
        self._username = json_data['username']
        self._password = CreateUserRequests.validatePassword(json_data['password'])


