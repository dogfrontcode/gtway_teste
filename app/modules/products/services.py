"""
Product service layer.
"""
import uuid
from typing import Dict, List, Optional, Tuple
from decimal import Decimal
from flask import current_app
from app.extensions import db
from app.models import Tenant
from app.models.product import Product


class ProductService:
    """Service for product operations."""
    
    @staticmethod
    def create_product(tenant: Tenant, data: Dict) -> Tuple[Optional[Product], Optional[str]]:
        """
        Create a new product for a tenant.
        
        Args:
            tenant: Tenant instance
            data: Product data
            
        Returns:
            Tuple of (product, error_message)
        """
        try:
            # Check if SKU is unique for this tenant
            if data.get('sku'):
                existing = Product.query.filter_by(
                    tenant_id=tenant.id,
                    sku=data['sku']
                ).first()
                
                if existing:
                    return None, f"SKU '{data['sku']}' already exists for this tenant"
            
            # Create product
            product = Product(
                tenant_id=tenant.id,
                name=data['name'],
                description=data.get('description'),
                sku=data.get('sku'),
                price=data['price'],
                currency=data.get('currency', 'BRL'),
                image_url=data.get('image_url'),
                category=data.get('category'),
                extra_data=data.get('extra_data', {}),
                stock_quantity=data.get('stock_quantity'),
                track_stock=data.get('track_stock', False),
                is_active=data.get('is_active', True)
            )
            
            db.session.add(product)
            db.session.commit()
            
            # Custom log
            from app.utils.logger import log_success
            log_success(f"Produto criado: {product.name} - R$ {float(product.price):.2f}")
            
            current_app.logger.info(
                f"Product created: {product.name} ({product.id}) for tenant {tenant.slug}"
            )
            
            return product, None
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Product creation error: {e}")
            return None, f"Failed to create product: {str(e)}"
    
    @staticmethod
    def get_product(product_id: uuid.UUID) -> Optional[Product]:
        """Get product by ID."""
        if isinstance(product_id, str):
            product_id = uuid.UUID(product_id)
        return Product.query.get(product_id)
    
    @staticmethod
    def get_product_by_sku(tenant: Tenant, sku: str) -> Optional[Product]:
        """Get product by SKU for a tenant."""
        return Product.query.filter_by(tenant_id=tenant.id, sku=sku).first()
    
    @staticmethod
    def list_products(
        tenant: Tenant,
        category: Optional[str] = None,
        is_active: Optional[bool] = None,
        page: int = 1,
        per_page: int = 20
    ) -> Tuple[List[Product], int]:
        """
        List products for a tenant.
        
        Args:
            tenant: Tenant instance
            category: Filter by category
            is_active: Filter by active status
            page: Page number
            per_page: Items per page
            
        Returns:
            Tuple of (products, total_count)
        """
        query = Product.query.filter_by(tenant_id=tenant.id)
        
        if category:
            query = query.filter_by(category=category)
        
        if is_active is not None:
            query = query.filter_by(is_active=is_active)
        
        query = query.order_by(Product.created_at.desc())
        
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        
        return pagination.items, pagination.total
    
    @staticmethod
    def update_product(product: Product, data: Dict) -> Tuple[bool, Optional[str]]:
        """
        Update product information.
        
        Args:
            product: Product instance
            data: Update data
            
        Returns:
            Tuple of (success, error_message)
        """
        try:
            # Check SKU uniqueness if changed
            if 'sku' in data and data['sku'] != product.sku:
                existing = Product.query.filter_by(
                    tenant_id=product.tenant_id,
                    sku=data['sku']
                ).first()
                
                if existing:
                    return False, f"SKU '{data['sku']}' already exists"
            
            # Update fields
            if 'name' in data:
                product.name = data['name']
            if 'description' in data:
                product.description = data['description']
            if 'sku' in data:
                product.sku = data['sku']
            if 'price' in data:
                product.price = data['price']
            if 'currency' in data:
                product.currency = data['currency']
            if 'image_url' in data:
                product.image_url = data['image_url']
            if 'category' in data:
                product.category = data['category']
            if 'extra_data' in data:
                product.extra_data = data['extra_data']
            if 'stock_quantity' in data:
                product.stock_quantity = data['stock_quantity']
            if 'track_stock' in data:
                product.track_stock = data['track_stock']
            if 'is_active' in data:
                product.is_active = data['is_active']
            
            db.session.commit()
            
            current_app.logger.info(f"Product updated: {product.name} ({product.id})")
            return True, None
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Product update error: {e}")
            return False, f"Failed to update product: {str(e)}"
    
    @staticmethod
    def delete_product(product: Product, hard_delete: bool = False) -> Tuple[bool, Optional[str]]:
        """
        Delete product (soft delete by default, hard delete optional).
        
        Args:
            product: Product instance
            hard_delete: If True, permanently delete. If False, just mark as inactive.
            
        Returns:
            Tuple of (success, error_message)
        """
        try:
            if hard_delete:
                # Hard delete - remove from database
                db.session.delete(product)
                log_msg = f"Product permanently deleted: {product.name}"
            else:
                # Soft delete - mark as inactive
                product.is_active = False
                log_msg = f"Product deactivated: {product.name}"
            
            db.session.commit()
            
            # Custom log
            from app.utils.logger import log_success
            log_success(f"Produto deletado: {product.name}")
            
            current_app.logger.info(log_msg)
            return True, None
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Product deletion error: {e}")
            return False, f"Failed to delete product: {str(e)}"
    
    @staticmethod
    def check_and_decrease_stock(product: Product, quantity: int = 1) -> Tuple[bool, Optional[str]]:
        """
        Check stock availability and decrease if available.
        
        Args:
            product: Product instance
            quantity: Quantity to decrease
            
        Returns:
            Tuple of (success, error_message)
        """
        try:
            if not product.has_stock(quantity):
                return False, f"Insufficient stock. Available: {product.stock_quantity or 0}"
            
            product.decrease_stock(quantity)
            db.session.commit()
            
            current_app.logger.info(
                f"Stock decreased for product {product.name}: -{quantity}"
            )
            
            return True, None
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Stock decrease error: {e}")
            return False, f"Failed to decrease stock: {str(e)}"
