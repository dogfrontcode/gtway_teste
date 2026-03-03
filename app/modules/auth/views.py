"""
Authentication routes/views.
"""
from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from marshmallow import ValidationError
from flasgger import swag_from
from app.modules.auth import auth_bp
from app.modules.auth.services import AuthService
from app.schemas.auth_schemas import LoginSchema, RegisterSchema, PasswordChangeSchema
from app.extensions import limiter


@auth_bp.route('/login', methods=['POST'])
@limiter.limit("5 per minute")
def login():
    """
    User login endpoint.
    ---
    tags:
      - Authentication
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - email
            - password
          properties:
            email:
              type: string
              format: email
              example: user@example.com
            password:
              type: string
              example: password123
    responses:
      200:
        description: Login successful
        schema:
          type: object
          properties:
            user:
              type: object
            access_token:
              type: string
            refresh_token:
              type: string
      400:
        description: Validation error
      401:
        description: Invalid credentials
    """
    try:
        # Validate input
        schema = LoginSchema()
        data = schema.load(request.json)
        
        # Attempt login
        result, error = AuthService.login(data['email'], data['password'])
        
        if error:
            return jsonify({'error': error}), 401
        
        return jsonify(result), 200
        
    except ValidationError as err:
        return jsonify({'error': 'Validation error', 'details': err.messages}), 400
    except Exception as e:
        return jsonify({'error': 'Login failed', 'details': str(e)}), 500


@auth_bp.route('/register', methods=['POST'])
@jwt_required()
def register():
    """
    Register a new user (admin only).
    ---
    tags:
      - Authentication
    security:
      - Bearer: []
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - email
            - password
            - full_name
          properties:
            email:
              type: string
              format: email
            password:
              type: string
              minLength: 6
            full_name:
              type: string
            role:
              type: string
              enum: [admin, tenant_admin, tenant_user]
            tenant_id:
              type: string
              format: uuid
    responses:
      201:
        description: User created successfully
      400:
        description: Validation error
      403:
        description: Forbidden - admin only
    """
    try:
        # Check if user is admin
        claims = get_jwt()
        if claims.get('role') != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        
        # Validate input
        schema = RegisterSchema()
        data = schema.load(request.json)
        
        # Register user
        user, error = AuthService.register(
            email=data['email'],
            password=data['password'],
            full_name=data['full_name'],
            role=data.get('role', 'tenant_user'),
            tenant_id=data.get('tenant_id')
        )
        
        if error:
            return jsonify({'error': error}), 400
        
        return jsonify({
            'message': 'User registered successfully',
            'user': user.to_dict()
        }), 201
        
    except ValidationError as err:
        return jsonify({'error': 'Validation error', 'details': err.messages}), 400
    except Exception as e:
        return jsonify({'error': 'Registration failed', 'details': str(e)}), 500


@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """
    Refresh access token.
    ---
    tags:
      - Authentication
    security:
      - Bearer: []
    responses:
      200:
        description: New access token
        schema:
          type: object
          properties:
            access_token:
              type: string
    """
    try:
        identity = get_jwt_identity()
        claims = get_jwt()
        access_token = AuthService.refresh_access_token(
            identity,
            {k: v for k, v in claims.items() if k in ('email', 'role', 'tenant_id')}
        )
        
        return jsonify({'access_token': access_token}), 200
        
    except Exception as e:
        return jsonify({'error': 'Token refresh failed', 'details': str(e)}), 500


@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """
    Get current user information.
    ---
    tags:
      - Authentication
    security:
      - Bearer: []
    responses:
      200:
        description: Current user data
      404:
        description: User not found
    """
    try:
        identity = get_jwt_identity()
        user = AuthService.get_user_by_id(identity)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        return jsonify({'user': user.to_dict()}), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to get user', 'details': str(e)}), 500


@auth_bp.route('/change-password', methods=['POST'])
@jwt_required()
def change_password():
    """
    Change user password.
    ---
    tags:
      - Authentication
    security:
      - Bearer: []
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - old_password
            - new_password
          properties:
            old_password:
              type: string
            new_password:
              type: string
              minLength: 6
    responses:
      200:
        description: Password changed successfully
      400:
        description: Validation error
      401:
        description: Invalid current password
    """
    try:
        identity = get_jwt_identity()
        user = AuthService.get_user_by_id(identity)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Validate input
        schema = PasswordChangeSchema()
        data = schema.load(request.json)
        
        # Change password
        success, error = AuthService.change_password(
            user,
            data['old_password'],
            data['new_password']
        )
        
        if not success:
            return jsonify({'error': error}), 401
        
        return jsonify({'message': 'Password changed successfully'}), 200
        
    except ValidationError as err:
        return jsonify({'error': 'Validation error', 'details': err.messages}), 400
    except Exception as e:
        return jsonify({'error': 'Password change failed', 'details': str(e)}), 500
