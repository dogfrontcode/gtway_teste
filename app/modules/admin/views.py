"""
Admin routes/views.
"""
from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt
from datetime import datetime
from sqlalchemy import func, text
from app.modules.admin import admin_bp
from app.extensions import db
from app.models import Tenant, User, Transaction, WebhookAttempt
from app.utils.auth_helpers import check_admin_access


@admin_bp.route('/dashboard', methods=['GET'])
@jwt_required()
def get_dashboard():
    """
    Get admin dashboard statistics.
    ---
    tags:
      - Admin
    security:
      - Bearer: []
    responses:
      200:
        description: Dashboard statistics
        schema:
          type: object
          properties:
            tenants:
              type: object
            transactions:
              type: object
            webhooks:
              type: object
      403:
        description: Admin access required
    """
    try:
        claims = get_jwt()
        if not check_admin_access(claims):
            return jsonify({'error': 'Admin access required'}), 403
        
        # Tenant statistics
        total_tenants = Tenant.query.count()
        active_tenants = Tenant.query.filter_by(is_active=True).count()
        
        # Transaction statistics
        total_transactions = Transaction.query.count()
        paid_transactions = Transaction.query.filter_by(status='paid').count()
        pending_transactions = Transaction.query.filter_by(status='pending').count()
        
        # Calculate total amount (paid only)
        total_amount = db.session.query(
            func.sum(Transaction.amount)
        ).filter_by(status='paid').scalar() or 0
        
        # Transactions today
        today = datetime.utcnow().date()
        transactions_today = Transaction.query.filter(
            func.date(Transaction.created_at) == today
        ).count()
        
        # Webhook statistics
        total_webhook_attempts = WebhookAttempt.query.count()
        successful_webhooks = WebhookAttempt.query.filter_by(status='success').count()
        failed_webhooks = WebhookAttempt.query.filter_by(status='failed').count()
        
        return jsonify({
            'tenants': {
                'total': total_tenants,
                'active': active_tenants,
                'inactive': total_tenants - active_tenants
            },
            'transactions': {
                'total': total_transactions,
                'paid': paid_transactions,
                'pending': pending_transactions,
                'today': transactions_today,
                'total_amount': float(total_amount)
            },
            'webhooks': {
                'total_attempts': total_webhook_attempts,
                'successful': successful_webhooks,
                'failed': failed_webhooks,
                'success_rate': (successful_webhooks / total_webhook_attempts * 100) if total_webhook_attempts > 0 else 0
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to get dashboard', 'details': str(e)}), 500


@admin_bp.route('/transactions', methods=['GET'])
@jwt_required()
def list_all_transactions():
    """
    List all transactions across all tenants (admin only).
    ---
    tags:
      - Admin
    security:
      - Bearer: []
    parameters:
      - in: query
        name: tenant_id
        type: string
        format: uuid
      - in: query
        name: status
        type: string
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
        description: Admin access required
    """
    try:
        claims = get_jwt()
        if not check_admin_access(claims):
            return jsonify({'error': 'Admin access required'}), 403
        
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        tenant_id = request.args.get('tenant_id')
        status = request.args.get('status')
        
        query = Transaction.query
        
        if tenant_id:
            query = query.filter_by(tenant_id=tenant_id)
        
        if status:
            query = query.filter_by(status=status)
        
        query = query.order_by(Transaction.created_at.desc())
        
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        
        transactions = [t.to_dict() for t in pagination.items]
        
        return jsonify({
            'transactions': transactions,
            'total': pagination.total,
            'page': page,
            'per_page': per_page
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to list transactions', 'details': str(e)}), 500


@admin_bp.route('/users', methods=['GET'])
@jwt_required()
def list_all_users():
    """
    List all users (admin only).
    ---
    tags:
      - Admin
    security:
      - Bearer: []
    parameters:
      - in: query
        name: tenant_id
        type: string
        format: uuid
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
        description: List of users
      403:
        description: Admin access required
    """
    try:
        claims = get_jwt()
        if not check_admin_access(claims):
            return jsonify({'error': 'Admin access required'}), 403
        
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        tenant_id = request.args.get('tenant_id')
        
        query = User.query
        
        if tenant_id:
            query = query.filter_by(tenant_id=tenant_id)
        
        query = query.order_by(User.created_at.desc())
        
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        
        users = [u.to_dict() for u in pagination.items]
        
        return jsonify({
            'users': users,
            'total': pagination.total,
            'page': page,
            'per_page': per_page
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to list users', 'details': str(e)}), 500


@admin_bp.route('/webhooks/attempts', methods=['GET'])
@jwt_required()
def list_webhook_attempts():
    """
    List webhook attempts (admin only).
    ---
    tags:
      - Admin
    security:
      - Bearer: []
    parameters:
      - in: query
        name: transaction_id
        type: string
        format: uuid
      - in: query
        name: status
        type: string
        enum: [pending, success, failed]
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
        description: List of webhook attempts
      403:
        description: Admin access required
    """
    try:
        claims = get_jwt()
        if not check_admin_access(claims):
            return jsonify({'error': 'Admin access required'}), 403
        
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        transaction_id = request.args.get('transaction_id')
        status = request.args.get('status')
        
        query = WebhookAttempt.query
        
        if transaction_id:
            query = query.filter_by(transaction_id=transaction_id)
        
        if status:
            query = query.filter_by(status=status)
        
        query = query.order_by(WebhookAttempt.created_at.desc())
        
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        
        attempts = [a.to_dict() for a in pagination.items]
        
        return jsonify({
            'attempts': attempts,
            'total': pagination.total,
            'page': page,
            'per_page': per_page
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to list webhook attempts', 'details': str(e)}), 500


@admin_bp.route('/system/health', methods=['GET'])
def health_check():
    """
    System health check endpoint.
    ---
    tags:
      - Admin
    responses:
      200:
        description: System is healthy
        schema:
          type: object
          properties:
            status:
              type: string
            database:
              type: string
            timestamp:
              type: string
    """
    try:
        # Check database connection
        db.session.execute(text('SELECT 1'))
        db_status = 'connected'
    except Exception as e:
        db_status = f'error: {str(e)}'
    
    return jsonify({
        'status': 'healthy' if db_status == 'connected' else 'unhealthy',
        'database': db_status,
        'timestamp': datetime.utcnow().isoformat()
    }), 200
