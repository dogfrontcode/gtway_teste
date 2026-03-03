"""
Admin module.
Provides administrative endpoints for system management.
"""
from flask import Blueprint

admin_bp = Blueprint('admin', __name__, url_prefix='/api/v1/admin')

from app.modules.admin import views
