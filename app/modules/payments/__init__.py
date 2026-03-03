"""
Payments module.
Handles payment processing, charge creation, and bank integrations.
"""
from flask import Blueprint

payments_bp = Blueprint('payments', __name__, url_prefix='/api/v1/payments')

from app.modules.payments import views
