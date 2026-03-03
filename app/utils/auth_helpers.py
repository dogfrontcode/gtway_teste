"""
Helpers centralizados para autenticação e controle de tenant.
"""
from datetime import datetime
from functools import wraps
from flask import jsonify
from flask_jwt_extended import get_jwt, verify_jwt_in_request

from app.constants import ROLE_ADMIN
from app.modules.tenants.services import TenantService


def get_current_tenant(claims: dict):
    """
    Obtém o tenant atual a partir dos claims JWT.
    
    Returns:
        Tenant ou None se o usuário não tiver tenant_id
    """
    tenant_id = claims.get('tenant_id')
    if not tenant_id:
        return None
    return TenantService.get_tenant(tenant_id)


def require_admin(f):
    """Decorator que exige role admin."""
    @wraps(f)
    def decorated(*args, **kwargs):
        verify_jwt_in_request()
        claims = get_jwt()
        if claims.get('role') != ROLE_ADMIN:
            return jsonify({'error': 'Admin access required'}), 403
        return f(*args, **kwargs)
    return decorated


def require_tenant(f):
    """
    Decorator que exige tenant associado ao usuário.
    Retorna 403 se o usuário não tiver tenant (ex: admin sem contexto).
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        verify_jwt_in_request()
        claims = get_jwt()
        tenant = get_current_tenant(claims)
        if not tenant:
            return jsonify({'error': 'No tenant associated with this user'}), 403
        return f(*args, **kwargs)
    return decorated


def check_admin_access(claims: dict) -> bool:
    """Verifica se o usuário tem role admin."""
    return claims.get('role') == ROLE_ADMIN


def check_tenant_access(claims: dict, tenant_id) -> bool:
    """
    Verifica se o usuário tem acesso ao tenant.
    Admin tem acesso a todos. Demais só ao próprio tenant.
    """
    if claims.get('role') == ROLE_ADMIN:
        return True
    return str(claims.get('tenant_id')) == str(tenant_id)


def parse_date_range(request, start_key='start_date', end_key='end_date'):
    """
    Extrai start_date e end_date da request (query ou body).
    
    Returns:
        Tuple (start_date, end_date) - podem ser None
    """
    body = request.get_json(silent=True) or {}
    start_str = request.args.get(start_key) or body.get(start_key)
    end_str = request.args.get(end_key) or body.get(end_key)
    
    start_date = None
    end_date = None
    
    if start_str:
        try:
            start_date = datetime.fromisoformat(start_str.replace('Z', '+00:00'))
        except (ValueError, TypeError):
            pass
    if end_str:
        try:
            end_date = datetime.fromisoformat(end_str.replace('Z', '+00:00'))
        except (ValueError, TypeError):
            pass
    
    return start_date, end_date
