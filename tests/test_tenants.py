"""
Tests for tenants module.
"""
import pytest


def test_create_tenant(client, admin_token):
    """Test creating a tenant."""
    headers = {'Authorization': f'Bearer {admin_token}'}
    response = client.post('/api/v1/tenants', headers=headers, json={
        'name': 'New Tenant',
        'email': 'newtenant@test.com',
        'pix_key': 'newtenant@test.com',
        'bank_provider': 'mock'
    })
    
    assert response.status_code == 201
    assert 'tenant' in response.json
    assert response.json['tenant']['name'] == 'New Tenant'
    assert 'api_key' in response.json['tenant']


def test_create_tenant_as_non_admin(client, tenant_token):
    """Test creating tenant as non-admin (should fail)."""
    headers = {'Authorization': f'Bearer {tenant_token}'}
    response = client.post('/api/v1/tenants', headers=headers, json={
        'name': 'New Tenant',
        'email': 'newtenant@test.com'
    })
    
    assert response.status_code == 403


def test_list_tenants(client, admin_token, sample_tenant):
    """Test listing tenants."""
    headers = {'Authorization': f'Bearer {admin_token}'}
    response = client.get('/api/v1/tenants', headers=headers)
    
    assert response.status_code == 200
    assert 'tenants' in response.json
    assert len(response.json['tenants']) > 0


def test_get_tenant(client, admin_token, sample_tenant):
    """Test getting specific tenant."""
    headers = {'Authorization': f'Bearer {admin_token}'}
    response = client.get(f'/api/v1/tenants/{sample_tenant.id}', headers=headers)
    
    assert response.status_code == 200
    assert response.json['tenant']['id'] == str(sample_tenant.id)


def test_update_tenant(client, admin_token, sample_tenant):
    """Test updating tenant."""
    headers = {'Authorization': f'Bearer {admin_token}'}
    response = client.put(f'/api/v1/tenants/{sample_tenant.id}', headers=headers, json={
        'name': 'Updated Tenant Name'
    })
    
    assert response.status_code == 200
    assert response.json['tenant']['name'] == 'Updated Tenant Name'


def test_get_tenant_settings(client, tenant_token):
    """Test getting tenant settings."""
    headers = {'Authorization': f'Bearer {tenant_token}'}
    response = client.get('/api/v1/tenants/settings', headers=headers)
    
    assert response.status_code == 200
    assert 'settings' in response.json
    assert 'name' in response.json
