"""
Pytest fixtures and configuration.
"""
import pytest
from decimal import Decimal
from app import create_app, db
from app.models import User, Tenant
from app.models.product import Product


@pytest.fixture(scope='function')
def app():
    """Create application for testing (fresh DB per test)."""
    app = create_app('testing')
    
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture(scope='function')
def client(app):
    """Create test client."""
    return app.test_client()


@pytest.fixture
def admin_user(app):
    """Create admin user for testing."""
    with app.app_context():
        user = User(
            email='admin@test.com',
            full_name='Test Admin',
            role='admin',
            is_active=True
        )
        user.set_password('testpass123')
        db.session.add(user)
        db.session.commit()
        yield user


@pytest.fixture
def sample_tenant(app):
    """Create sample tenant for testing."""
    with app.app_context():
        tenant = Tenant(
            slug='test-tenant',
            name='Test Tenant',
            email='test@tenant.com',
            pix_key='test@tenant.com',
            bank_provider='mock',
            api_key='sk_test_123456',
            is_active=True
        )
        db.session.add(tenant)
        db.session.commit()
        yield tenant


@pytest.fixture
def tenant_user(app, sample_tenant):
    """Create tenant user for testing."""
    with app.app_context():
        user = User(
            email='user@tenant.com',
            full_name='Tenant User',
            role='tenant_admin',
            tenant_id=sample_tenant.id,
            is_active=True
        )
        user.set_password('testpass123')
        db.session.add(user)
        db.session.commit()
        yield user


@pytest.fixture
def admin_token(client, admin_user):
    """Get JWT token for admin user."""
    response = client.post('/api/v1/auth/login', json={
        'email': 'admin@test.com',
        'password': 'testpass123'
    })
    return response.json['access_token']


@pytest.fixture
def tenant_token(client, tenant_user):
    """Get JWT token for tenant user."""
    response = client.post('/api/v1/auth/login', json={
        'email': 'user@tenant.com',
        'password': 'testpass123'
    })
    return response.json['access_token']


def get_auth_headers(token):
    """Helper to get authorization headers."""
    return {'Authorization': f'Bearer {token}'}


@pytest.fixture
def tenant(app, sample_tenant):
    """Alias for sample_tenant."""
    return sample_tenant


@pytest.fixture
def product(app, sample_tenant):
    """Create sample product for testing."""
    with app.app_context():
        product = Product(
            tenant_id=sample_tenant.id,
            name='Test Product',
            description='Test description',
            sku='TEST-PROD-001',
            price=Decimal('99.99'),
            category='Test',
            track_stock=True,
            stock_quantity=100,
            is_active=True
        )
        db.session.add(product)
        db.session.commit()
        db.session.refresh(product)
        yield product
