"""
Constantes do sistema - evita magic strings espalhados pelo código.
"""

# Roles de usuário
ROLE_ADMIN = 'admin'
ROLE_TENANT_ADMIN = 'tenant_admin'
ROLE_TENANT_USER = 'tenant_user'

ROLES = (ROLE_ADMIN, ROLE_TENANT_ADMIN, ROLE_TENANT_USER)

# Status de transação
TX_STATUS_PENDING = 'pending'
TX_STATUS_PAID = 'paid'
TX_STATUS_EXPIRED = 'expired'
TX_STATUS_CANCELLED = 'cancelled'
TX_STATUS_REFUNDED = 'refunded'

TX_STATUSES = (TX_STATUS_PENDING, TX_STATUS_PAID, TX_STATUS_EXPIRED, TX_STATUS_CANCELLED, TX_STATUS_REFUNDED)

# Status de webhook
WEBHOOK_PENDING = 'pending'
WEBHOOK_SUCCESS = 'success'
WEBHOOK_FAILED = 'failed'
