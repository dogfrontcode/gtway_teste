"""
Webhooks module.
Handles incoming webhooks from banks and outgoing webhooks to tenants.
"""
from flask import Blueprint

webhooks_bp = Blueprint('webhooks', __name__, url_prefix='/api/v1/webhooks')

from app.modules.webhooks import views
