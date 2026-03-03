"""
Payment routes/views.
"""
from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt
from marshmallow import ValidationError
from app.modules.payments import payments_bp
from app.modules.payments.services import PaymentService
from app.utils.auth_helpers import get_current_tenant, require_tenant, parse_date_range
from app.schemas.transaction_schemas import TransactionCreateSchema
from app.extensions import limiter


@payments_bp.route('/charge', methods=['POST'])
@jwt_required()
@limiter.limit("10 per minute")
def create_charge():
    """
    Create a new payment charge.
    ---
    tags:
      - Payments
    security:
      - Bearer: []
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - amount
          properties:
            amount:
              type: number
              format: decimal
              example: 100.50
            description:
              type: string
              example: Payment for order #123
            external_id:
              type: string
              example: ORDER123
            expires_in_minutes:
              type: integer
              default: 60
              example: 60
    responses:
      201:
        description: Charge created successfully
        schema:
          type: object
          properties:
            transaction:
              type: object
            qr_code:
              type: string
            qr_code_text:
              type: string
      400:
        description: Validation error
      403:
        description: Tenant not found or inactive
    """
    try:
        claims = get_jwt()
        tenant = get_current_tenant(claims)
        
        if not tenant:
            return jsonify({'error': 'No tenant associated with this user'}), 403
        
        # Validate input
        schema = TransactionCreateSchema()
        data = schema.load(request.json)
        
        # Create charge
        transaction, error = PaymentService.create_charge(
            tenant=tenant,
            amount=data['amount'],
            description=data.get('description'),
            external_id=data.get('external_id'),
            expires_in_minutes=data.get('expires_in_minutes', 60)
        )
        
        if error:
            return jsonify({'error': error}), 400
        
        # Return transaction with sensitive data
        return jsonify({
            'message': 'Charge created successfully',
            'transaction': transaction.to_dict(include_sensitive=True)
        }), 201
        
    except ValidationError as err:
        return jsonify({'error': 'Validation error', 'details': err.messages}), 400
    except Exception as e:
        return jsonify({'error': 'Charge creation failed', 'details': str(e)}), 500


@payments_bp.route('/transactions', methods=['GET'])
@jwt_required()
def list_transactions():
    """
    List transactions for current tenant.
    ---
    tags:
      - Payments
    security:
      - Bearer: []
    parameters:
      - in: query
        name: status
        type: string
        enum: [pending, paid, expired, cancelled, refunded]
      - in: query
        name: start_date
        type: string
        format: date-time
      - in: query
        name: end_date
        type: string
        format: date-time
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
        description: List of transactions
      403:
        description: Tenant not found
    """
    try:
        claims = get_jwt()
        tenant = get_current_tenant(claims)
        
        if not tenant:
            return jsonify({'error': 'No tenant associated with this user'}), 403
        
        # Parse filters
        status = request.args.get('status')
        start_date, end_date = parse_date_range(request)
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        # Get transactions
        transactions, total = PaymentService.list_transactions(
            tenant=tenant,
            status=status,
            start_date=start_date,
            end_date=end_date,
            page=page,
            per_page=per_page
        )
        
        return jsonify({
            'transactions': [t.to_dict() for t in transactions],
            'total': total,
            'page': page,
            'per_page': per_page
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to list transactions', 'details': str(e)}), 500


@payments_bp.route('/transactions/<uuid:transaction_id>', methods=['GET'])
@jwt_required()
def get_transaction(transaction_id):
    """
    Get transaction by ID.
    ---
    tags:
      - Payments
    security:
      - Bearer: []
    parameters:
      - in: path
        name: transaction_id
        type: string
        format: uuid
        required: true
    responses:
      200:
        description: Transaction data
      403:
        description: Access forbidden
      404:
        description: Transaction not found
    """
    try:
        claims = get_jwt()
        tenant = get_current_tenant(claims)
        
        if not tenant:
            return jsonify({'error': 'No tenant associated with this user'}), 403
        
        transaction = PaymentService.get_transaction(transaction_id)
        
        if not transaction:
            return jsonify({'error': 'Transaction not found'}), 404
        
        # Check if transaction belongs to tenant
        if str(transaction.tenant_id) != str(tenant.id):
            return jsonify({'error': 'Access forbidden'}), 403
        
        return jsonify({
            'transaction': transaction.to_dict(include_sensitive=True)
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to get transaction', 'details': str(e)}), 500


@payments_bp.route('/transactions/txid/<string:txid>', methods=['GET'])
@jwt_required()
def get_transaction_by_txid(txid):
    """
    Get transaction by txid.
    ---
    tags:
      - Payments
    security:
      - Bearer: []
    parameters:
      - in: path
        name: txid
        type: string
        required: true
    responses:
      200:
        description: Transaction data
      403:
        description: Access forbidden
      404:
        description: Transaction not found
    """
    try:
        claims = get_jwt()
        tenant = get_current_tenant(claims)
        
        if not tenant:
            return jsonify({'error': 'No tenant associated with this user'}), 403
        
        transaction = PaymentService.get_transaction_by_txid(txid)
        
        if not transaction:
            return jsonify({'error': 'Transaction not found'}), 404
        
        # Check if transaction belongs to tenant
        if str(transaction.tenant_id) != str(tenant.id):
            return jsonify({'error': 'Access forbidden'}), 403
        
        return jsonify({
            'transaction': transaction.to_dict(include_sensitive=True)
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to get transaction', 'details': str(e)}), 500


@payments_bp.route('/transactions/<uuid:transaction_id>/status', methods=['GET'])
@jwt_required()
def check_transaction_status(transaction_id):
    """
    Check transaction status with payment provider.
    ---
    tags:
      - Payments
    security:
      - Bearer: []
    parameters:
      - in: path
        name: transaction_id
        type: string
        format: uuid
        required: true
    responses:
      200:
        description: Current status
      403:
        description: Access forbidden
      404:
        description: Transaction not found
    """
    try:
        claims = get_jwt()
        tenant = get_current_tenant(claims)
        
        if not tenant:
            return jsonify({'error': 'No tenant associated with this user'}), 403
        
        transaction = PaymentService.get_transaction(transaction_id)
        
        if not transaction:
            return jsonify({'error': 'Transaction not found'}), 404
        
        # Check if transaction belongs to tenant
        if str(transaction.tenant_id) != str(tenant.id):
            return jsonify({'error': 'Access forbidden'}), 403
        
        # Check status with provider
        status_data, error = PaymentService.check_charge_status(transaction)
        
        if error:
            return jsonify({'error': error}), 400
        
        return jsonify({
            'status': status_data
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to check status', 'details': str(e)}), 500


@payments_bp.route('/transactions/<uuid:transaction_id>/cancel', methods=['POST'])
@jwt_required()
def cancel_transaction(transaction_id):
    """
    Cancel a pending transaction.
    ---
    tags:
      - Payments
    security:
      - Bearer: []
    parameters:
      - in: path
        name: transaction_id
        type: string
        format: uuid
        required: true
    responses:
      200:
        description: Transaction cancelled
      400:
        description: Cannot cancel transaction
      403:
        description: Access forbidden
      404:
        description: Transaction not found
    """
    try:
        claims = get_jwt()
        tenant = get_current_tenant(claims)
        
        if not tenant:
            return jsonify({'error': 'No tenant associated with this user'}), 403
        
        transaction = PaymentService.get_transaction(transaction_id)
        
        if not transaction:
            return jsonify({'error': 'Transaction not found'}), 404
        
        # Check if transaction belongs to tenant
        if str(transaction.tenant_id) != str(tenant.id):
            return jsonify({'error': 'Access forbidden'}), 403
        
        # Cancel transaction
        success, error = PaymentService.cancel_charge(transaction)
        
        if not success:
            return jsonify({'error': error}), 400
        
        return jsonify({
            'message': 'Transaction cancelled successfully',
            'transaction': transaction.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to cancel transaction', 'details': str(e)}), 500


@payments_bp.route('/statistics', methods=['GET'])
@jwt_required()
def get_statistics():
    """
    Get payment statistics for current tenant.
    ---
    tags:
      - Payments
    security:
      - Bearer: []
    parameters:
      - in: query
        name: start_date
        type: string
        format: date-time
      - in: query
        name: end_date
        type: string
        format: date-time
    responses:
      200:
        description: Payment statistics
      403:
        description: Tenant not found
    """
    try:
        claims = get_jwt()
        tenant = get_current_tenant(claims)
        
        if not tenant:
            return jsonify({'error': 'No tenant associated with this user'}), 403
        
        start_date, end_date = parse_date_range(request)
        stats = PaymentService.get_payment_statistics(tenant, start_date, end_date)
        
        return jsonify({
            'statistics': stats
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to get statistics', 'details': str(e)}), 500
