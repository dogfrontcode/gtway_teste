"""
Authentication module.
Handles user login, registration, and JWT token management.
"""
from flask import Blueprint

auth_bp = Blueprint('auth', __name__, url_prefix='/api/v1/auth')

from app.modules.auth import views
