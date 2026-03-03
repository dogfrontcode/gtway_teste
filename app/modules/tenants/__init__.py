"""
Tenants module.
Manages tenant (merchant) accounts and configurations.
"""
from flask import Blueprint

tenants_bp = Blueprint('tenants', __name__, url_prefix='/api/v1/tenants')

from app.modules.tenants import views
