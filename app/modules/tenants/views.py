"""
Tenant routes/views.
"""
from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from marshmallow import ValidationError
from app.modules.tenants import tenants_bp
from app.modules.tenants.services import TenantService
from app.schemas.tenant_schemas import TenantCreateSchema, TenantUpdateSchema
from app.utils.auth_helpers import check_admin_access, check_tenant_access, get_current_tenant
from app.extensions import limiter


@tenants_bp.route('', methods=['POST'])
@jwt_required()
def create_tenant():
    """
    Create a new tenant (admin only).
    ---
    tags:
      - Tenants
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
            - email
          properties:
            name:
              type: string
            slug:
              type: string
            legal_name:
              type: string
            cnpj:
              type: string
            email:
              type: string
              format: email
            phone:
              type: string
            pix_key:
              type: string
            bank_provider:
              type: string
              enum: [mock, bradesco, openPix, inter]
            bank_credentials:
              type: object
            webhook_url:
              type: string
              format: uri
            settings:
              type: object
    responses:
      201:
        description: Tenant created successfully
      403:
        description: Admin access required
    """
    try:
        claims = get_jwt()
        if not check_admin_access(claims):
            return jsonify({'error': 'Admin access required'}), 403
        
        # Validate input
        schema = TenantCreateSchema()
        data = schema.load(request.json)
        
        # Create tenant
        tenant, error = TenantService.create_tenant(data)
        
        if error:
            return jsonify({'error': error}), 400
        
        # Return tenant data with API key
        return jsonify({
            'message': 'Tenant created successfully',
            'tenant': tenant.to_dict(include_sensitive=True)
        }), 201
        
    except ValidationError as err:
        return jsonify({'error': 'Validation error', 'details': err.messages}), 400
    except Exception as e:
        return jsonify({'error': 'Tenant creation failed', 'details': str(e)}), 500


@tenants_bp.route('', methods=['GET'])
@jwt_required()
def list_tenants():
    """
    List all tenants (admin only).
    ---
    tags:
      - Tenants
    security:
      - Bearer: []
    parameters:
      - in: query
        name: page
        type: integer
        default: 1
      - in: query
        name: per_page
        type: integer
        default: 20
      - in: query
        name: is_active
        type: boolean
    responses:
      200:
        description: List of tenants
      403:
        description: Admin access required
    """
    try:
        claims = get_jwt()
        if not check_admin_access(claims):
            return jsonify({'error': 'Admin access required'}), 403
        
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        is_active_str = request.args.get('is_active')
        
        is_active = None
        if is_active_str is not None:
            is_active = is_active_str.lower() in ('true', '1', 'yes')
        
        tenants, total = TenantService.list_tenants(page, per_page, is_active)
        
        return jsonify({
            'tenants': [t.to_dict() for t in tenants],
            'total': total,
            'page': page,
            'per_page': per_page
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to list tenants', 'details': str(e)}), 500


@tenants_bp.route('/<uuid:tenant_id>', methods=['GET'])
@jwt_required()
def get_tenant(tenant_id):
    """
    Get tenant by ID.
    ---
    tags:
      - Tenants
    security:
      - Bearer: []
    parameters:
      - in: path
        name: tenant_id
        type: string
        format: uuid
        required: true
    responses:
      200:
        description: Tenant data
      403:
        description: Access forbidden
      404:
        description: Tenant not found
    """
    try:
        claims = get_jwt()
        
        # Check access
        if not check_tenant_access(claims, tenant_id):
            return jsonify({'error': 'Access forbidden'}), 403
        
        tenant = TenantService.get_tenant(tenant_id)
        
        if not tenant:
            return jsonify({'error': 'Tenant not found'}), 404
        
        # Include sensitive data only for admins
        include_sensitive = check_admin_access(claims)
        
        return jsonify({
            'tenant': tenant.to_dict(include_sensitive=include_sensitive)
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to get tenant', 'details': str(e)}), 500


@tenants_bp.route('/<uuid:tenant_id>', methods=['PUT', 'PATCH'])
@jwt_required()
def update_tenant(tenant_id):
    """
    Update tenant.
    ---
    tags:
      - Tenants
    security:
      - Bearer: []
    parameters:
      - in: path
        name: tenant_id
        type: string
        format: uuid
        required: true
      - in: body
        name: body
        schema:
          type: object
    responses:
      200:
        description: Tenant updated successfully
      403:
        description: Access forbidden
      404:
        description: Tenant not found
    """
    try:
        claims = get_jwt()
        
        # Check access
        if not check_tenant_access(claims, tenant_id):
            return jsonify({'error': 'Access forbidden'}), 403
        
        tenant = TenantService.get_tenant(tenant_id)
        
        if not tenant:
            return jsonify({'error': 'Tenant not found'}), 404
        
        # Validate input
        schema = TenantUpdateSchema()
        data = schema.load(request.json, partial=True)
        
        # Update tenant
        success, error = TenantService.update_tenant(tenant, data)
        
        if not success:
            return jsonify({'error': error}), 400
        
        return jsonify({
            'message': 'Tenant updated successfully',
            'tenant': tenant.to_dict()
        }), 200
        
    except ValidationError as err:
        return jsonify({'error': 'Validation error', 'details': err.messages}), 400
    except Exception as e:
        return jsonify({'error': 'Tenant update failed', 'details': str(e)}), 500


@tenants_bp.route('/<uuid:tenant_id>', methods=['DELETE'])
@jwt_required()
def delete_tenant(tenant_id):
    """
    Delete tenant (soft delete - admin only).
    ---
    tags:
      - Tenants
    security:
      - Bearer: []
    parameters:
      - in: path
        name: tenant_id
        type: string
        format: uuid
        required: true
    responses:
      200:
        description: Tenant deleted successfully
      403:
        description: Admin access required
      404:
        description: Tenant not found
    """
    try:
        claims = get_jwt()
        if not check_admin_access(claims):
            return jsonify({'error': 'Admin access required'}), 403
        
        tenant = TenantService.get_tenant(tenant_id)
        
        if not tenant:
            return jsonify({'error': 'Tenant not found'}), 404
        
        success, error = TenantService.delete_tenant(tenant)
        
        if not success:
            return jsonify({'error': error}), 400
        
        return jsonify({'message': 'Tenant deleted successfully'}), 200
        
    except Exception as e:
        return jsonify({'error': 'Tenant deletion failed', 'details': str(e)}), 500


@tenants_bp.route('/<uuid:tenant_id>/regenerate-api-key', methods=['POST'])
@jwt_required()
def regenerate_api_key(tenant_id):
    """
    Regenerate tenant API key (admin only).
    ---
    tags:
      - Tenants
    security:
      - Bearer: []
    parameters:
      - in: path
        name: tenant_id
        type: string
        format: uuid
        required: true
    responses:
      200:
        description: API key regenerated
      403:
        description: Admin access required
      404:
        description: Tenant not found
    """
    try:
        claims = get_jwt()
        if not check_admin_access(claims):
            return jsonify({'error': 'Admin access required'}), 403
        
        tenant = TenantService.get_tenant(tenant_id)
        
        if not tenant:
            return jsonify({'error': 'Tenant not found'}), 404
        
        new_api_key, error = TenantService.regenerate_api_key(tenant)
        
        if error:
            return jsonify({'error': error}), 400
        
        return jsonify({
            'message': 'API key regenerated successfully',
            'api_key': new_api_key
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'API key regeneration failed', 'details': str(e)}), 500


@tenants_bp.route('/settings', methods=['GET'])
@jwt_required()
def get_tenant_settings():
    """
    Get current tenant's settings (for white label customization).
    ---
    tags:
      - Tenants
    security:
      - Bearer: []
    responses:
      200:
        description: Tenant settings
      404:
        description: Tenant not found
    """
    try:
        claims = get_jwt()
        tenant_id = claims.get('tenant_id')
        
        if not tenant_id:
            return jsonify({'error': 'No tenant associated with this user'}), 400
        
        tenant = TenantService.get_tenant(tenant_id)
        
        if not tenant:
            return jsonify({'error': 'Tenant not found'}), 404
        
        return jsonify({
            'settings': tenant.settings or {},
            'name': tenant.name,
            'slug': tenant.slug
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to get settings', 'details': str(e)}), 500
