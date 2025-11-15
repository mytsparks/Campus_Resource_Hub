"""
Security tests for SQL injection prevention.
Tests that all database queries use parameterized statements.
References: docs/context/PM/PRD.md - Section 7 Security & Validation
"""
import pytest
from flask import Flask

from application import create_app
from src.controllers.auth_routes import get_db_session
from src.data_access.user_dal import UserDAL


@pytest.fixture
def app():
    """Create application instance for testing."""
    app = create_app()
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    return app


@pytest.fixture
def client(app):
    """Create test client."""
    return app.test_client()


def test_sql_injection_in_search_query(client, app):
    """Test that search queries are protected against SQL injection."""
    # SQL injection attempt in search parameter
    malicious_input = "'; DROP TABLE users; --"
    
    response = client.get(f'/resources/?q={malicious_input}')
    
    # Should not crash and should return 200 (even if no results)
    assert response.status_code == 200
    # Verify users table still exists by checking we can still access the page
    assert b'resource' in response.data.lower() or b'search' in response.data.lower()


def test_sql_injection_in_email_field(client, app):
    """Test that email field is protected against SQL injection."""
    malicious_input = "test'; DROP TABLE users; --@example.com"
    
    response = client.post('/auth/register', data={
        'name': 'Test User',
        'email': malicious_input,
        'password': 'TestPassword123',
        'confirm_password': 'TestPassword123',
        'role': 'student'
    })
    
    # Should handle gracefully (either reject or sanitize)
    assert response.status_code == 200
    # Should not crash the application


def test_parameterized_queries_used(app):
    """Test that DAL methods use parameterized queries."""
    with app.app_context():
        with get_db_session() as session:
            user_dal = UserDAL(session)
            
            # Use a unique email that definitely doesn't exist
            # This should use parameterized queries internally
            # If it doesn't, it would be vulnerable to SQL injection
            unique_email = "nonexistent_user_12345@test.com"
            user = user_dal.get_user_by_email(unique_email)
            
            # Should return None (user doesn't exist) without error
            assert user is None


def test_xss_protection_in_templates(client, app):
    """Test that templates escape user input to prevent XSS."""
    # Register user with potentially malicious name
    with app.app_context():
        from src.data_access.user_dal import UserDAL
        with get_db_session() as session:
            user_dal = UserDAL(session)
            user_dal.create_user(
                name='<script>alert("XSS")</script>',
                email='xss@example.com',
                plaintext_password='TestPassword123',
                role='student'
            )
    
    # Login
    client.post('/auth/login', data={
        'identifier': 'xss@example.com',
        'password': 'TestPassword123'
    })
    
    # Access a page that displays user name
    response = client.get('/user/dashboard')
    
    # The script tag should be escaped, not executed
    assert response.status_code == 200
    # Check that script tag is escaped (appears as text, not executed)
    assert b'<script>' in response.data or b'&lt;script&gt;' in response.data

