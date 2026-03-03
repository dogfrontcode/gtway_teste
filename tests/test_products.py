"""
Tests for product module.
"""
import pytest
from decimal import Decimal
from app.models.product import Product
from app.modules.products.services import ProductService


class TestProductModel:
    """Test Product model."""
    
    def test_product_creation(self, app, tenant):
        """Test creating a product."""
        with app.app_context():
            product = Product(
                tenant_id=tenant.id,
                name='Test Product',
                price=Decimal('99.99'),
                sku='TEST-001'
            )
            
            assert product.name == 'Test Product'
            assert product.price == Decimal('99.99')
            assert product.sku == 'TEST-001'
    
    def test_product_to_dict(self, app, tenant):
        """Test product to_dict method."""
        with app.app_context():
            product = Product(
                tenant_id=tenant.id,
                name='Test Product',
                price=Decimal('99.99'),
                description='Test description',
                category='Test Category'
            )
            
            data = product.to_dict()
            
            assert data['name'] == 'Test Product'
            assert data['price'] == '99.99'
            assert data['description'] == 'Test description'
            assert data['category'] == 'Test Category'
    
    def test_stock_management(self, app, tenant):
        """Test stock management."""
        with app.app_context():
            product = Product(
                tenant_id=tenant.id,
                name='Product with Stock',
                price=Decimal('50.00'),
                track_stock=True,
                stock_quantity=10
            )
            
            assert product.has_stock(5) is True
            assert product.has_stock(15) is False
            
            product.decrease_stock(3)
            assert product.stock_quantity == 7


class TestProductService:
    """Test ProductService."""
    
    def test_create_product(self, app, tenant):
        """Test creating a product via service."""
        with app.app_context():
            data = {
                'name': 'Service Test Product',
                'price': Decimal('149.90'),
                'description': 'Test description',
                'sku': 'SVC-TEST-001',
                'category': 'Test'
            }
            
            product, error = ProductService.create_product(tenant, data)
            
            assert error is None
            assert product is not None
            assert product.name == 'Service Test Product'
            assert product.tenant_id == tenant.id
    
    def test_create_product_duplicate_sku(self, app, tenant, db):
        """Test creating product with duplicate SKU."""
        with app.app_context():
            # Create first product
            data1 = {
                'name': 'Product 1',
                'price': Decimal('100.00'),
                'sku': 'DUPLICATE-SKU'
            }
            product1, _ = ProductService.create_product(tenant, data1)
            
            # Try to create second with same SKU
            data2 = {
                'name': 'Product 2',
                'price': Decimal('200.00'),
                'sku': 'DUPLICATE-SKU'
            }
            product2, error = ProductService.create_product(tenant, data2)
            
            assert product2 is None
            assert 'already exists' in error.lower()
    
    def test_list_products(self, app, tenant, db):
        """Test listing products."""
        with app.app_context():
            # Create multiple products
            for i in range(3):
                data = {
                    'name': f'Product {i}',
                    'price': Decimal('100.00'),
                    'category': 'Category' if i < 2 else 'Other'
                }
                ProductService.create_product(tenant, data)
            
            # List all
            products, total = ProductService.list_products(tenant)
            assert total >= 3
            
            # Filter by category
            products, total = ProductService.list_products(tenant, category='Category')
            assert total >= 2
    
    def test_update_product(self, app, tenant, db):
        """Test updating a product."""
        with app.app_context():
            # Create product
            data = {
                'name': 'Original Name',
                'price': Decimal('100.00')
            }
            product, _ = ProductService.create_product(tenant, data)
            
            # Update product
            update_data = {
                'name': 'Updated Name',
                'price': Decimal('150.00')
            }
            success, error = ProductService.update_product(product, update_data)
            
            assert success is True
            assert error is None
            assert product.name == 'Updated Name'
            assert product.price == Decimal('150.00')
    
    def test_delete_product(self, app, tenant, db):
        """Test deleting a product (soft delete)."""
        with app.app_context():
            # Create product
            data = {
                'name': 'To Delete',
                'price': Decimal('100.00')
            }
            product, _ = ProductService.create_product(tenant, data)
            assert product.is_active is True
            
            # Delete product
            success, error = ProductService.delete_product(product)
            
            assert success is True
            assert error is None
            assert product.is_active is False


class TestProductEndpoints:
    """Test product API endpoints."""
    
    def test_create_product_endpoint(self, client, tenant_token):
        """Test POST /api/v1/products."""
        response = client.post(
            '/api/v1/products',
            json={
                'name': 'API Test Product',
                'price': 99.99,
                'category': 'Test'
            },
            headers={'Authorization': f'Bearer {tenant_token}'}
        )
        
        assert response.status_code == 201
        data = response.get_json()
        assert data['message'] == 'Product created successfully'
        assert data['product']['name'] == 'API Test Product'
    
    def test_list_products_endpoint(self, client, tenant_token):
        """Test GET /api/v1/products."""
        response = client.get(
            '/api/v1/products',
            headers={'Authorization': f'Bearer {tenant_token}'}
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'products' in data
        assert 'total' in data
    
    def test_get_product_endpoint(self, client, tenant_token, product):
        """Test GET /api/v1/products/<id>."""
        response = client.get(
            f'/api/v1/products/{product.id}',
            headers={'Authorization': f'Bearer {tenant_token}'}
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['product']['id'] == str(product.id)
    
    def test_create_charge_from_product(self, client, tenant_token, product):
        """Test POST /api/v1/products/<id>/charge."""
        response = client.post(
            f'/api/v1/products/{product.id}/charge',
            json={'quantity': 2},
            headers={'Authorization': f'Bearer {tenant_token}'}
        )
        
        assert response.status_code == 201
        data = response.get_json()
        assert 'transaction' in data
        assert 'product' in data
        assert data['product']['quantity'] == 2
        
        # Check total price calculation
        expected_total = float(product.price) * 2
        assert float(data['transaction']['amount']) == expected_total
