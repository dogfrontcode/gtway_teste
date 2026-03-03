"""
Tests for webhooks module.
"""
import pytest


def test_receive_bank_webhook(client, sample_tenant, tenant_user):
    """Test receiving webhook from bank."""
    # First create a transaction
    from app.models import Transaction
    from app.extensions import db
    from decimal import Decimal
    
    transaction = Transaction(
        tenant_id=sample_tenant.id,
        txid='TEST123456',
        amount=Decimal('100.50'),
        pix_key='test@tenant.com',
        status='pending'
    )
    db.session.add(transaction)
    db.session.commit()
    
    # Send webhook
    response = client.post('/api/v1/webhooks/bank', json={
        'txid': 'TEST123456',
        'status': 'paid',
        'amount': 100.50,
        'payer': {
            'name': 'Test Payer',
            'document': '12345678900'
        }
    })
    
    assert response.status_code == 200
    assert response.json['txid'] == 'TEST123456'
    
    # Verify transaction was updated
    db.session.refresh(transaction)
    assert transaction.status == 'paid'


def test_receive_bank_webhook_invalid_txid(client):
    """Test receiving webhook with invalid txid."""
    response = client.post('/api/v1/webhooks/bank', json={
        'txid': 'INVALID123',
        'status': 'paid'
    })
    
    assert response.status_code == 404


def test_test_webhook(client, sample_tenant):
    """Test the test webhook endpoint."""
    # Create a transaction
    from app.models import Transaction
    from app.extensions import db
    from decimal import Decimal
    
    transaction = Transaction(
        tenant_id=sample_tenant.id,
        txid='TEST999',
        amount=Decimal('50.00'),
        pix_key='test@tenant.com',
        status='pending'
    )
    db.session.add(transaction)
    db.session.commit()
    
    # Send test webhook
    response = client.post('/api/v1/webhooks/test', json={
        'txid': 'TEST999',
        'status': 'paid'
    })
    
    assert response.status_code == 200
