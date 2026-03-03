"""
Tests for authentication module.
"""
import pytest


def test_login_success(client, admin_user):
    """Test successful login."""
    response = client.post('/api/v1/auth/login', json={
        'email': 'admin@test.com',
        'password': 'testpass123'
    })
    
    assert response.status_code == 200
    assert 'access_token' in response.json
    assert 'refresh_token' in response.json
    assert response.json['user']['email'] == 'admin@test.com'


def test_login_invalid_credentials(client, admin_user):
    """Test login with invalid credentials."""
    response = client.post('/api/v1/auth/login', json={
        'email': 'admin@test.com',
        'password': 'wrongpassword'
    })
    
    assert response.status_code == 401
    assert 'error' in response.json


def test_login_missing_fields(client):
    """Test login with missing fields."""
    response = client.post('/api/v1/auth/login', json={
        'email': 'admin@test.com'
    })
    
    assert response.status_code == 400


def test_get_current_user(client, admin_token):
    """Test getting current user information."""
    headers = {'Authorization': f'Bearer {admin_token}'}
    response = client.get('/api/v1/auth/me', headers=headers)
    
    assert response.status_code == 200
    assert response.json['user']['email'] == 'admin@test.com'


def test_get_current_user_no_token(client):
    """Test getting current user without token."""
    response = client.get('/api/v1/auth/me')
    
    assert response.status_code == 401


def test_refresh_token(client, admin_user):
    """Test token refresh."""
    # Login to get tokens
    login_response = client.post('/api/v1/auth/login', json={
        'email': 'admin@test.com',
        'password': 'testpass123'
    })
    
    refresh_token = login_response.json['refresh_token']
    
    # Refresh access token
    headers = {'Authorization': f'Bearer {refresh_token}'}
    response = client.post('/api/v1/auth/refresh', headers=headers)
    
    assert response.status_code == 200
    assert 'access_token' in response.json


def test_register_user_as_admin(client, admin_token, sample_tenant):
    """Test user registration by admin."""
    headers = {'Authorization': f'Bearer {admin_token}'}
    response = client.post('/api/v1/auth/register', headers=headers, json={
        'email': 'newuser@test.com',
        'password': 'testpass123',
        'full_name': 'New User',
        'role': 'tenant_user',
        'tenant_id': str(sample_tenant.id)
    })
    
    assert response.status_code == 201
    assert response.json['user']['email'] == 'newuser@test.com'


def test_register_user_as_non_admin(client, tenant_token):
    """Test user registration by non-admin (should fail)."""
    headers = {'Authorization': f'Bearer {tenant_token}'}
    response = client.post('/api/v1/auth/register', headers=headers, json={
        'email': 'newuser@test.com',
        'password': 'testpass123',
        'full_name': 'New User'
    })
    
    assert response.status_code == 403
