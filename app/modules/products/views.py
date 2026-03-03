"""
Product routes/views.
"""
from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt
from marshmallow import ValidationError
from app.modules.products import products_bp
from app.modules.products.services import ProductService
from app.modules.products.helpers import format_product_for_frontend, format_charge_response, get_product_categories
from app.schemas.product_schemas import ProductCreateSchema, ProductUpdateSchema
from app.utils.auth_helpers import get_current_tenant, check_admin_access
from app.extensions import limiter


@products_bp.route('', methods=['POST'])
@jwt_required()
@limiter.limit("20 per minute")
def create_product():
    """
    Create a new product.
    ---
    tags:
      - Products
    security:
      - Bearer: []
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - name
            - price
          properties:
            name:
              type: string
              example: "Curso de Python"
            description:
              type: string
              example: "Curso completo de Python para iniciantes"
            sku:
              type: string
              example: "CURSO-PY-001"
            price:
              type: number
              format: decimal
              example: 197.00
            currency:
              type: string
              default: BRL
              example: "BRL"
            image_url:
              type: string
              format: uri
              example: "https://example.com/image.jpg"
            category:
              type: string
              example: "Cursos"
            metadata:
              type: object
            stock_quantity:
              type: integer
              example: 100
            track_stock:
              type: boolean
              default: false
    responses:
      201:
        description: Product created successfully
      400:
        description: Validation error
      403:
        description: Tenant not found
    """
    try:
        claims = get_jwt()
        tenant = get_current_tenant(claims)
        
        if not tenant:
            return jsonify({'error': 'No tenant associated with this user'}), 403
        
        # Validate input
        schema = ProductCreateSchema()
        data = schema.load(request.json)
        
        # Create product
        product, error = ProductService.create_product(tenant, data)
        
        if error:
            return jsonify({'error': error}), 400
        
        # Return formatted for frontend
        return jsonify({
            'message': 'Product created successfully',
            'product': format_product_for_frontend(product)
        }), 201
        
    except ValidationError as err:
        return jsonify({'error': 'Validation error', 'details': err.messages}), 400
    except Exception as e:
        return jsonify({'error': 'Product creation failed', 'details': str(e)}), 500


@products_bp.route('', methods=['GET'])
@jwt_required()
def list_products():
    """
    List products for current tenant.
    ---
    tags:
      - Products
    security:
      - Bearer: []
    parameters:
      - in: query
        name: category
        type: string
      - in: query
        name: is_active
        type: boolean
      - in: query
        name: page
        type: integer
        default: 1
      - in: query
        name: per_page
        type: integer
        default: 20
    responses:
      200:
        description: List of products
      403:
        description: Tenant not found
    """
    try:
        claims = get_jwt()
        tenant = get_current_tenant(claims)
        
        if not tenant:
            return jsonify({'error': 'No tenant associated with this user'}), 403
        
        # Parse filters
        category = request.args.get('category')
        is_active_str = request.args.get('is_active')
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        is_active = None
        if is_active_str is not None:
            is_active = is_active_str.lower() in ('true', '1', 'yes')
        
        # Get products
        products, total = ProductService.list_products(
            tenant=tenant,
            category=category,
            is_active=is_active,
            page=page,
            per_page=per_page
        )
        
        # Return formatted for frontend
        return jsonify({
            'products': [format_product_for_frontend(p) for p in products],
            'total': total,
            'page': page,
            'per_page': per_page,
            'has_more': page * per_page < total
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to list products', 'details': str(e)}), 500


@products_bp.route('/<uuid:product_id>', methods=['GET'])
@jwt_required()
def get_product(product_id):
    """
    Get product by ID.
    ---
    tags:
      - Products
    security:
      - Bearer: []
    parameters:
      - in: path
        name: product_id
        type: string
        format: uuid
        required: true
    responses:
      200:
        description: Product data
      403:
        description: Access forbidden
      404:
        description: Product not found
    """
    try:
        claims = get_jwt()
        tenant = get_current_tenant(claims)
        
        if not tenant:
            return jsonify({'error': 'No tenant associated with this user'}), 403
        
        product = ProductService.get_product(product_id)
        
        if not product:
            return jsonify({'error': 'Product not found'}), 404
        
        # Check if product belongs to tenant
        if str(product.tenant_id) != str(tenant.id):
            return jsonify({'error': 'Access forbidden'}), 403
        
        # Return formatted for frontend
        return jsonify({
            'product': format_product_for_frontend(product)
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to get product', 'details': str(e)}), 500


@products_bp.route('/<uuid:product_id>', methods=['PUT', 'PATCH'])
@jwt_required()
def update_product(product_id):
    """
    Update product.
    ---
    tags:
      - Products
    security:
      - Bearer: []
    parameters:
      - in: path
        name: product_id
        type: string
        format: uuid
        required: true
      - in: body
        name: body
        schema:
          type: object
    responses:
      200:
        description: Product updated successfully
      403:
        description: Access forbidden
      404:
        description: Product not found
    """
    try:
        claims = get_jwt()
        tenant = get_current_tenant(claims)
        
        if not tenant:
            return jsonify({'error': 'No tenant associated with this user'}), 403
        
        product = ProductService.get_product(product_id)
        
        if not product:
            return jsonify({'error': 'Product not found'}), 404
        
        # Check if product belongs to tenant
        if str(product.tenant_id) != str(tenant.id):
            return jsonify({'error': 'Access forbidden'}), 403
        
        # Validate input
        schema = ProductUpdateSchema()
        data = schema.load(request.json, partial=True)
        
        # Update product
        success, error = ProductService.update_product(product, data)
        
        if not success:
            return jsonify({'error': error}), 400
        
        # Return formatted for frontend
        return jsonify({
            'message': 'Product updated successfully',
            'product': format_product_for_frontend(product)
        }), 200
        
    except ValidationError as err:
        return jsonify({'error': 'Validation error', 'details': err.messages}), 400
    except Exception as e:
        return jsonify({'error': 'Product update failed', 'details': str(e)}), 500


@products_bp.route('/<uuid:product_id>', methods=['DELETE'])
@jwt_required()
def delete_product(product_id):
    """
    Delete product (soft delete).
    ---
    tags:
      - Products
    security:
      - Bearer: []
    parameters:
      - in: path
        name: product_id
        type: string
        format: uuid
        required: true
    responses:
      200:
        description: Product deleted successfully
      403:
        description: Access forbidden
      404:
        description: Product not found
    """
    try:
        claims = get_jwt()
        tenant = get_current_tenant(claims)
        
        if not tenant:
            return jsonify({'error': 'No tenant associated with this user'}), 403
        
        product = ProductService.get_product(product_id)
        
        if not product:
            return jsonify({'error': 'Product not found'}), 404
        
        # Check if product belongs to tenant
        if str(product.tenant_id) != str(tenant.id):
            return jsonify({'error': 'Access forbidden'}), 403
        
        success, error = ProductService.delete_product(product)
        
        if not success:
            return jsonify({'error': error}), 400
        
        return jsonify({'message': 'Product deleted successfully'}), 200
        
    except Exception as e:
        return jsonify({'error': 'Product deletion failed', 'details': str(e)}), 500


@products_bp.route('/<uuid:product_id>/charge', methods=['POST'])
@jwt_required()
@limiter.limit("10 per minute")
def create_charge_from_product(product_id):
    """
    Create a payment charge from a product - OPTIMIZED FOR FRONTEND.
    Returns complete payment data ready to display.
    ---
    tags:
      - Products
    security:
      - Bearer: []
    parameters:
      - in: path
        name: product_id
        type: string
        format: uuid
        required: true
      - in: body
        name: body
        schema:
          type: object
          properties:
            quantity:
              type: integer
              default: 1
            external_id:
              type: string
            expires_in_minutes:
              type: integer
              default: 60
    responses:
      201:
        description: Complete charge data ready for frontend display
        schema:
          type: object
          properties:
            success:
              type: boolean
            transaction:
              type: object
            payment:
              type: object
              properties:
                qr_code_image:
                  type: string
                qr_code_text:
                  type: string
            product:
              type: object
            instructions:
              type: object
      400:
        description: Validation error or insufficient stock
      403:
        description: Access forbidden
      404:
        description: Product not found
    """
    try:
        claims = get_jwt()
        tenant = get_current_tenant(claims)
        
        if not tenant:
            return jsonify({'error': 'No tenant associated with this user'}), 403
        
        product = ProductService.get_product(product_id)
        
        if not product:
            return jsonify({'error': 'Product not found'}), 404
        
        # Check if product belongs to tenant
        if str(product.tenant_id) != str(tenant.id):
            return jsonify({'error': 'Access forbidden'}), 403
        
        if not product.is_active:
            return jsonify({'error': 'Product is not active'}), 400
        
        # Get quantity
        data = request.json or {}
        quantity = data.get('quantity', 1)
        
        # Validate quantity
        if quantity < 1:
            return jsonify({'error': 'Quantity must be at least 1'}), 400
        
        # Check stock
        if not product.has_stock(quantity):
            return jsonify({
                'error': 'Insufficient stock',
                'available': product.stock_quantity or 0,
                'requested': quantity
            }), 400
        
        # Calculate total amount
        from decimal import Decimal
        total_amount = product.price * Decimal(quantity)
        
        # Create charge
        from app.modules.payments.services import PaymentService
        
        description = f"{product.name}"
        if quantity > 1:
            description += f" (x{quantity})"
        
        transaction, error = PaymentService.create_charge(
            tenant=tenant,
            amount=total_amount,
            description=description,
            external_id=data.get('external_id'),
            expires_in_minutes=data.get('expires_in_minutes', 60),
            product_id=product.id
        )
        
        if error:
            return jsonify({'error': error}), 400
        
        # Decrease stock if tracking
        if product.track_stock:
            success, stock_error = ProductService.check_and_decrease_stock(product, quantity)
            if not success:
                # Rollback transaction if stock failed
                from app.extensions import db
                db.session.delete(transaction)
                db.session.commit()
                return jsonify({'error': stock_error}), 400
        
        # Return formatted response optimized for frontend
        response = format_charge_response(transaction, product, quantity)
        
        return jsonify(response), 201
        
    except Exception as e:
        return jsonify({'error': 'Charge creation failed', 'details': str(e)}), 500


@products_bp.route('/categories', methods=['GET'])
@jwt_required()
def get_categories():
    """
    Get all product categories for current tenant.
    ---
    tags:
      - Products
    security:
      - Bearer: []
    responses:
      200:
        description: List of categories
        schema:
          type: object
          properties:
            categories:
              type: array
              items:
                type: string
      403:
        description: Tenant not found
    """
    try:
        claims = get_jwt()
        tenant = get_current_tenant(claims)
        
        if not tenant:
            return jsonify({'error': 'No tenant associated with this user'}), 403
        
        categories = get_product_categories(tenant.id)
        
        return jsonify({
            'categories': categories
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to get categories', 'details': str(e)}), 500
