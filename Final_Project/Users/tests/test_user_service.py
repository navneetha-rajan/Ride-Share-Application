"""
Unit tests for User Service

This module contains comprehensive tests for the user service endpoints
and functionality.
"""

import json
import pytest
from unittest.mock import patch, MagicMock
from flask import Flask

from main_user import app
from user_requests import CreateUserRequest, CreateUserRequests
from exceptions import ValidationError


@pytest.fixture
def client():
    """Create a test client for the Flask app"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


@pytest.fixture
def valid_user_data():
    """Valid user data for testing"""
    return {
        'username': 'testuser',
        'password': 'a94a8fe5ccb19ba61c4c0873d391e987982fbbd3'  # SHA1 of 'test'
    }


class TestUserEndpoints:
    """Test cases for user endpoints"""
    
    def test_root_endpoint(self, client):
        """Test root endpoint"""
        response = client.get('/')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['data']['service'] == 'user-service'
        assert 'endpoints' in data['data']
    
    def test_health_check(self, client):
        """Test health check endpoint"""
        response = client.get('/health')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['data']['status'] == 'healthy'
        assert data['data']['service'] == 'user-service'
    
    def test_metrics_endpoint(self, client):
        """Test metrics endpoint"""
        response = client.get('/metrics')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'total_requests' in data['data']
        assert 'successful_requests' in data['data']
        assert 'failed_requests' in data['data']
        assert 'http_request_counter' in data['data']
    
    def test_get_request_count(self, client):
        """Test request count endpoint"""
        response = client.get('/api/v1/_count')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert isinstance(data['data'], list)
        assert len(data['data']) == 1
        assert isinstance(data['data'][0], int)
    
    def test_reset_request_count(self, client):
        """Test reset request count endpoint"""
        response = client.delete('/api/v1/_count')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['message'] == 'Request counter reset successfully'
    
    @patch('main_user.requests.post')
    def test_create_user_success(self, mock_post, client, valid_user_data):
        """Test successful user creation"""
        # Mock database responses
        mock_post.side_effect = [
            MagicMock(status_code=404),  # User doesn't exist
            MagicMock(status_code=200)   # User created successfully
        ]
        
        response = client.put(
            '/api/v1/users',
            data=json.dumps(valid_user_data),
            content_type='application/json'
        )
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['message'] == 'User created successfully'
    
    @patch('main_user.requests.post')
    def test_create_user_already_exists(self, mock_post, client, valid_user_data):
        """Test user creation when user already exists"""
        # Mock database response - user exists
        mock_post.return_value = MagicMock(status_code=200)
        
        response = client.put(
            '/api/v1/users',
            data=json.dumps(valid_user_data),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'already exists' in data['error']['message']
    
    def test_create_user_invalid_content_type(self, client, valid_user_data):
        """Test user creation with invalid content type"""
        response = client.put(
            '/api/v1/users',
            data=json.dumps(valid_user_data),
            content_type='text/plain'
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'Content-Type' in data['error']['message']
    
    def test_create_user_missing_fields(self, client):
        """Test user creation with missing fields"""
        invalid_data = {'username': 'testuser'}  # Missing password
        
        response = client.put(
            '/api/v1/users',
            data=json.dumps(invalid_data),
            content_type='application/json'
        )
        
        assert response.status_code == 400
    
    @patch('main_user.requests.post')
    def test_delete_user_success(self, mock_post, client):
        """Test successful user deletion"""
        # Mock database responses
        mock_post.side_effect = [
            MagicMock(status_code=200),  # User exists
            MagicMock(status_code=200)   # User deleted successfully
        ]
        
        response = client.delete('/api/v1/users/testuser')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['message'] == 'User deleted successfully'
    
    @patch('main_user.requests.post')
    def test_delete_user_not_found(self, mock_post, client):
        """Test user deletion when user doesn't exist"""
        # Mock database response - user doesn't exist
        mock_post.return_value = MagicMock(status_code=404)
        
        response = client.delete('/api/v1/users/nonexistent')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'not found' in data['error']['message']
    
    @patch('main_user.requests.post')
    def test_list_users_success(self, mock_post, client):
        """Test successful user listing"""
        # Mock database response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = ['user1', 'user2', 'user3']
        mock_post.return_value = mock_response
        
        response = client.get('/api/v1/users')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['data'] == ['user1', 'user2', 'user3']
    
    @patch('main_user.requests.post')
    def test_list_users_database_error(self, mock_post, client):
        """Test user listing when database fails"""
        # Mock database error
        mock_post.return_value = MagicMock(status_code=500)
        
        response = client.get('/api/v1/users')
        
        assert response.status_code == 500
        data = json.loads(response.data)
        assert 'Internal server error' in data['error']['message']


class TestUserRequests:
    """Test cases for user request models"""
    
    def test_create_user_request_valid(self, valid_user_data):
        """Test valid user request creation"""
        request = CreateUserRequest.from_dict(valid_user_data)
        
        assert request.username == 'testuser'
        assert request.password == 'a94a8fe5ccb19ba61c4c0873d391e987982fbbd3'
    
    def test_create_user_request_missing_fields(self):
        """Test user request with missing fields"""
        invalid_data = {'username': 'testuser'}  # Missing password
        
        with pytest.raises(ValidationError) as exc_info:
            CreateUserRequest.from_dict(invalid_data)
        
        assert 'Missing required fields' in str(exc_info.value)
    
    def test_create_user_request_invalid_username(self):
        """Test user request with invalid username"""
        invalid_data = {
            'username': '',  # Empty username
            'password': 'a94a8fe5ccb19ba61c4c0873d391e987982fbbd3'
        }
        
        with pytest.raises(ValidationError):
            CreateUserRequest.from_dict(invalid_data)
    
    def test_create_user_request_invalid_password(self):
        """Test user request with invalid password"""
        invalid_data = {
            'username': 'testuser',
            'password': 'invalid_hash'  # Not SHA1
        }
        
        with pytest.raises(ValidationError):
            CreateUserRequest.from_dict(invalid_data)
    
    def test_legacy_create_user_requests(self, valid_user_data):
        """Test legacy CreateUserRequests class"""
        request = CreateUserRequests(valid_user_data)
        
        assert request.getUsername() == 'testuser'
        assert request.getPassword() == 'a94a8fe5ccb19ba61c4c0873d391e987982fbbd3'
    
    def test_legacy_create_user_requests_missing_fields(self):
        """Test legacy CreateUserRequests with missing fields"""
        invalid_data = {'username': 'testuser'}  # Missing password
        
        with pytest.raises(Exception):  # BadRequest in legacy code
            CreateUserRequests(invalid_data)


class TestValidation:
    """Test cases for validation functions"""
    
    def test_validate_username_valid(self):
        """Test valid username validation"""
        from utils.validators import validate_username
        
        valid_usernames = ['user123', 'test_user', 'User123']
        
        for username in valid_usernames:
            result = validate_username(username)
            assert result == username
    
    def test_validate_username_invalid(self):
        """Test invalid username validation"""
        from utils.validators import validate_username
        
        invalid_usernames = ['', 'a' * 51, 'user@123', 'user-123']
        
        for username in invalid_usernames:
            with pytest.raises(ValidationError):
                validate_username(username)
    
    def test_validate_password_valid(self):
        """Test valid password validation"""
        from utils.validators import validate_password
        
        valid_password = 'a94a8fe5ccb19ba61c4c0873d391e987982fbbd3'
        result = validate_password(valid_password)
        assert result == valid_password
    
    def test_validate_password_invalid(self):
        """Test invalid password validation"""
        from utils.validators import validate_password
        
        invalid_passwords = ['', 'invalid', 'a94a8fe5ccb19ba61c4c0873d391e987982fbbd3x']
        
        for password in invalid_passwords:
            with pytest.raises(ValidationError):
                validate_password(password)


if __name__ == '__main__':
    pytest.main([__file__]) 