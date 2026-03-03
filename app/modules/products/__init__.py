"""
Products module.
"""
from flask import Blueprint

products_bp = Blueprint('products', __name__, url_prefix='/api/v1/products')

from app.modules.products import views
