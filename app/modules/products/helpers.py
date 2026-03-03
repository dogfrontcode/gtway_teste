"""
Helper functions for product operations.
"""
from typing import Dict, List
from app.models.product import Product


def format_product_for_frontend(product: Product) -> Dict:
    """
    Format product data optimized for frontend display.
    Includes all data needed for immediate rendering.
    
    Args:
        product: Product instance
        
    Returns:
        Dict with formatted product data
    """
    return {
        'id': str(product.id),
        'name': product.name,
        'description': product.description or '',
        'price': float(product.price),
        'price_formatted': f"R$ {float(product.price):.2f}",
        'sku': product.sku or '',
        'category': product.category or 'Sem categoria',
        'image_url': product.image_url or '',
        'has_image': bool(product.image_url),
        'stock': {
            'tracking': product.track_stock,
            'quantity': product.stock_quantity if product.track_stock else None,
            'available': product.stock_quantity > 0 if product.track_stock and product.stock_quantity is not None else True,
            'display': f"{product.stock_quantity} unidades" if product.track_stock and product.stock_quantity else "Ilimitado"
        },
        'is_active': product.is_active,
        'metadata': {
            'created_at': product.created_at.isoformat() if product.created_at else None,
            'updated_at': product.updated_at.isoformat() if product.updated_at else None,
        }
    }


def format_charge_response(transaction, product, quantity: int = 1) -> Dict:
    """
    Format charge response optimized for frontend.
    Returns everything needed to display payment screen.
    
    Args:
        transaction: Transaction instance
        product: Product instance
        quantity: Quantity purchased
        
    Returns:
        Dict with complete charge data
    """
    return {
        'success': True,
        'transaction': {
            'id': str(transaction.id),
            'txid': transaction.txid,
            'amount': float(transaction.amount),
            'amount_formatted': f"R$ {float(transaction.amount):.2f}",
            'currency': transaction.currency,
            'status': transaction.status,
            'description': transaction.description,
            'created_at': transaction.created_at.isoformat() if transaction.created_at else None,
            'expires_at': transaction.expires_at.isoformat() if transaction.expires_at else None,
        },
        'payment': {
            'qr_code_image': transaction.qr_code,
            'qr_code_text': transaction.qr_code_text,
            'pix_key': transaction.pix_key,
        },
        'product': {
            'id': str(product.id),
            'name': product.name,
            'unit_price': float(product.price),
            'unit_price_formatted': f"R$ {float(product.price):.2f}",
            'quantity': quantity,
            'total_price': float(transaction.amount),
            'total_price_formatted': f"R$ {float(transaction.amount):.2f}",
        },
        'instructions': {
            'title': 'Como pagar',
            'steps': [
                'Abra o app do seu banco',
                'Escolha Pix',
                'Escaneie o QR Code ou use o código copia e cola',
                'Confirme o pagamento',
                'Pronto! Pagamento será confirmado automaticamente'
            ]
        }
    }


def get_product_categories(tenant_id) -> List[str]:
    """
    Get all unique categories for a tenant's products.
    
    Args:
        tenant_id: Tenant UUID
        
    Returns:
        List of category names
    """
    from app.extensions import db
    
    categories = db.session.query(Product.category)\
        .filter_by(tenant_id=tenant_id, is_active=True)\
        .distinct()\
        .all()
    
    return [c[0] for c in categories if c[0]]
