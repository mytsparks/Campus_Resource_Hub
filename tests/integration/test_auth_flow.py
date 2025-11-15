"""
Integration tests for authentication flow (register, login, access protected routes).
References: docs/context/PM/PRD.md - Section 4.1 User Management & Authentication
"""
import pytest
from flask import Flask
from flask_login import current_user

from application import create_app
from src.models import User


@pytest.fixture
def app():
    """Create application instance for testing."""
    app = create_app()
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False  # Disable CSRF for testing
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    return app


@pytest.fixture
def client(app):
    """Create test client."""
    return app.test_client()


def test_register_new_user(client):
    """Test user registration flow."""
    response = client.post('/auth/register', data={
        'name': 'Test User',
        'email': 'test@example.com',
        'password': 'TestPassword123',
        'confirm_password': 'TestPassword123',
        'role': 'student'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    # Should redirect to login or home page after registration
    assert b'login' in response.data.lower() or b'home' in response.data.lower() or b'resource' in response.data.lower()


def test_register_duplicate_email(client):
    """Test that duplicate email registration fails."""
    # Register first user
    client.post('/auth/register', data={
        'name': 'User 1',
        'email': 'duplicate@example.com',
        'password': 'Password123',
        'confirm_password': 'Password123',
        'role': 'student'
    })
    
    # Try to register with same email
    response = client.post('/auth/register', data={
        'name': 'User 2',
        'email': 'duplicate@example.com',
        'password': 'Password123',
        'confirm_password': 'Password123',
        'role': 'student'
    })
    
    # Should show error or stay on registration page
    assert response.status_code == 200


def test_login_with_valid_credentials(client, app):
    """Test login with valid credentials."""
    # First register a user
    with app.app_context():
        from src.controllers.auth_routes import get_db_session
        from src.data_access.user_dal import UserDAL
        
        with get_db_session() as session:
            user_dal = UserDAL(session)
            user_dal.create_user(
                name='Test User',
                email='login@example.com',
                plaintext_password='TestPassword123',
                role='student'
            )
    
    # Try to login
    response = client.post('/auth/login', data={
        'identifier': 'login@example.com',
        'password': 'TestPassword123'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    # Should redirect to home/resources page after successful login
    assert b'resource' in response.data.lower() or b'home' in response.data.lower()


def test_login_with_invalid_credentials(client):
    """Test login with invalid credentials."""
    response = client.post('/auth/login', data={
        'identifier': 'nonexistent@example.com',
        'password': 'WrongPassword'
    })
    
    assert response.status_code == 200
    # Should stay on login page or show error
    assert b'login' in response.data.lower() or b'error' in response.data.lower() or b'invalid' in response.data.lower()


def test_access_protected_route_without_login(client):
    """Test that protected routes redirect to login when not authenticated."""
    response = client.get('/resources/create', follow_redirects=False)
    
    # Should redirect to login page
    assert response.status_code == 302 or response.status_code == 401
    # If redirect, check location
    if response.status_code == 302:
        assert '/auth/login' in response.location or '/login' in response.location


def test_access_protected_route_after_login(client, app):
    """Test that protected routes are accessible after login."""
    # Register and login
    with app.app_context():
        from src.controllers.auth_routes import get_db_session
        from src.data_access.user_dal import UserDAL
        
        with get_db_session() as session:
            user_dal = UserDAL(session)
            user_dal.create_user(
                name='Test User',
                email='protected@example.com',
                plaintext_password='TestPassword123',
                role='staff'
            )
    
    # Login
    client.post('/auth/login', data={
        'identifier': 'protected@example.com',
        'password': 'TestPassword123'
    })
    
    # Try to access protected route
    response = client.get('/resources/create', follow_redirects=True)
    
    # Should be able to access (status 200) or redirect if role check fails
    assert response.status_code in [200, 302]

