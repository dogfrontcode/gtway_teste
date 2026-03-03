"""
Tests for payments module.
"""
import pytest
from decimal import Decimal


def test_create_charge(client, tenant_token):
    """Test creating a payment charge."""
    headers = {'Authorization': f'Bearer {tenant_token}'}
    response = client.post('/api/v1/payments/charge', headers=headers, json={
        'amount': 100.50,
        'description': 'Test payment',
        'external_id': 'TEST123'
    })
    
    assert response.status_code == 201
    assert 'transaction' in response.json
    assert response.json['transaction']['amount'] == '100.50'
    assert response.json['transaction']['status'] == 'pending'
    assert 'qr_code' in response.json['transaction']


def test_create_charge_invalid_amount(client, tenant_token):
    """Test creating charge with invalid amount."""
    headers = {'Authorization': f'Bearer {tenant_token}'}
    response = client.post('/api/v1/payments/charge', headers=headers, json={
        'amount': -100,
        'description': 'Test payment'
    })
    
    assert response.status_code == 400


def test_create_charge_no_auth(client):
    """Test creating charge without authentication."""
    response = client.post('/api/v1/payments/charge', json={
        'amount': 100.50,
        'description': 'Test payment'
    })
    
    assert response.status_code == 401


def test_list_transactions(client, tenant_token):
    """Test listing transactions."""
    # First create a charge
    headers = {'Authorization': f'Bearer {tenant_token}'}
    client.post('/api/v1/payments/charge', headers=headers, json={
        'amount': 100.50,
        'description': 'Test payment'
    })
    
    # Then list transactions
    response = client.get('/api/v1/payments/transactions', headers=headers)
    
    assert response.status_code == 200
    assert 'transactions' in response.json
    assert len(response.json['transactions']) > 0


def test_get_transaction_by_id(client, tenant_token):
    """Test getting transaction by ID."""
    # Create a charge
    headers = {'Authorization': f'Bearer {tenant_token}'}
    create_response = client.post('/api/v1/payments/charge', headers=headers, json={
        'amount': 100.50,
        'description': 'Test payment'
    })
    
    transaction_id = create_response.json['transaction']['id']
    
    # Get transaction
    response = client.get(f'/api/v1/payments/transactions/{transaction_id}', headers=headers)
    
    assert response.status_code == 200
    assert response.json['transaction']['id'] == transaction_id


def test_cancel_transaction(client, tenant_token):
    """Test cancelling a transaction."""
    # Create a charge
    headers = {'Authorization': f'Bearer {tenant_token}'}
    create_response = client.post('/api/v1/payments/charge', headers=headers, json={
        'amount': 100.50,
        'description': 'Test payment'
    })
    
    transaction_id = create_response.json['transaction']['id']
    
    # Cancel transaction
    response = client.post(
        f'/api/v1/payments/transactions/{transaction_id}/cancel',
        headers=headers
    )
    
    assert response.status_code == 200
    assert response.json['transaction']['status'] == 'cancelled'


def test_get_statistics(client, tenant_token):
    """Test getting payment statistics."""
    # Create some charges
    headers = {'Authorization': f'Bearer {tenant_token}'}
    for i in range(3):
        client.post('/api/v1/payments/charge', headers=headers, json={
            'amount': 100.0 * (i + 1),
            'description': f'Test payment {i}'
        })
    
    # Get statistics
    response = client.get('/api/v1/payments/statistics', headers=headers)
    
    assert response.status_code == 200
    assert 'statistics' in response.json
    assert response.json['statistics']['total_transactions'] >= 3
