# Exemplos de Uso da API

Este documento fornece exemplos práticos de como usar a API do Payment Gateway.

## 📝 Índice

- [Autenticação](#autenticação)
- [Gerenciamento de Tenants](#gerenciamento-de-tenants)
- [Pagamentos](#pagamentos)
- [Webhooks](#webhooks)
- [Administração](#administração)

---

## Autenticação

### 1. Login

```bash
curl -X POST http://localhost:5000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@gateway.com",
    "password": "admin123"
  }'
```

**Resposta:**
```json
{
  "user": {
    "id": "uuid",
    "email": "admin@gateway.com",
    "full_name": "Admin User",
    "role": "admin"
  },
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

### 2. Refresh Token

```bash
curl -X POST http://localhost:5000/api/v1/auth/refresh \
  -H "Authorization: Bearer <refresh_token>"
```

### 3. Obter Usuário Atual

```bash
curl -X GET http://localhost:5000/api/v1/auth/me \
  -H "Authorization: Bearer <access_token>"
```

---

## Gerenciamento de Tenants

### 1. Criar Tenant (Admin Only)

```bash
curl -X POST http://localhost:5000/api/v1/tenants \
  -H "Authorization: Bearer <admin_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Loja do João",
    "legal_name": "João Silva ME",
    "cnpj": "12345678000100",
    "email": "contato@lojadojoao.com",
    "phone": "+5511999999999",
    "pix_key": "contato@lojadojoao.com",
    "bank_provider": "mock",
    "webhook_url": "https://lojadojoao.com/webhooks/payment",
    "settings": {
      "primary_color": "#FF5733",
      "secondary_color": "#C70039",
      "logo_url": "https://lojadojoao.com/logo.png",
      "company_name": "Loja do João"
    }
  }'
```

**Resposta:**
```json
{
  "message": "Tenant created successfully",
  "tenant": {
    "id": "uuid",
    "slug": "loja-do-joao",
    "name": "Loja do João",
    "email": "contato@lojadojoao.com",
    "pix_key": "contato@lojadojoao.com",
    "api_key": "sk_live_abc123...",
    "webhook_secret": "whsec_xyz789...",
    "is_active": true
  }
}
```

### 2. Listar Tenants

```bash
curl -X GET "http://localhost:5000/api/v1/tenants?page=1&per_page=20" \
  -H "Authorization: Bearer <admin_token>"
```

### 3. Obter Tenant Específico

```bash
curl -X GET http://localhost:5000/api/v1/tenants/<tenant_id> \
  -H "Authorization: Bearer <admin_token>"
```

### 4. Atualizar Tenant

```bash
curl -X PUT http://localhost:5000/api/v1/tenants/<tenant_id> \
  -H "Authorization: Bearer <admin_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Loja do João - Atualizada",
    "phone": "+5511988888888",
    "settings": {
      "primary_color": "#3B82F6"
    }
  }'
```

### 5. Obter Configurações do Tenant (Para White Label)

```bash
curl -X GET http://localhost:5000/api/v1/tenants/settings \
  -H "Authorization: Bearer <tenant_token>"
```

**Resposta:**
```json
{
  "settings": {
    "primary_color": "#FF5733",
    "secondary_color": "#C70039",
    "logo_url": "https://lojadojoao.com/logo.png",
    "company_name": "Loja do João"
  },
  "name": "Loja do João",
  "slug": "loja-do-joao"
}
```

### 6. Regenerar API Key

```bash
curl -X POST http://localhost:5000/api/v1/tenants/<tenant_id>/regenerate-api-key \
  -H "Authorization: Bearer <admin_token>"
```

---

## Pagamentos

### 1. Criar Cobrança PIX

```bash
curl -X POST http://localhost:5000/api/v1/payments/charge \
  -H "Authorization: Bearer <tenant_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "amount": 150.75,
    "description": "Pagamento do Pedido #12345",
    "external_id": "ORDER_12345",
    "expires_in_minutes": 60
  }'
```

**Resposta:**
```json
{
  "message": "Charge created successfully",
  "transaction": {
    "id": "uuid",
    "txid": "TXN202503021430ABC123",
    "external_id": "ORDER_12345",
    "amount": "150.75",
    "currency": "BRL",
    "description": "Pagamento do Pedido #12345",
    "status": "pending",
    "qr_code": "data:image/png;base64,iVBORw0KG...",
    "qr_code_text": "00020126580014br.gov.bcb.pix...",
    "pix_key": "contato@lojadojoao.com",
    "created_at": "2025-03-02T14:30:00Z",
    "expires_at": "2025-03-02T15:30:00Z"
  }
}
```

### 2. Listar Transações

```bash
# Todas as transações
curl -X GET "http://localhost:5000/api/v1/payments/transactions?page=1&per_page=20" \
  -H "Authorization: Bearer <tenant_token>"

# Filtrar por status
curl -X GET "http://localhost:5000/api/v1/payments/transactions?status=paid" \
  -H "Authorization: Bearer <tenant_token>"

# Filtrar por data
curl -X GET "http://localhost:5000/api/v1/payments/transactions?start_date=2025-03-01T00:00:00Z&end_date=2025-03-31T23:59:59Z" \
  -H "Authorization: Bearer <tenant_token>"
```

### 3. Consultar Transação por ID

```bash
curl -X GET http://localhost:5000/api/v1/payments/transactions/<transaction_id> \
  -H "Authorization: Bearer <tenant_token>"
```

### 4. Consultar Transação por TXID

```bash
curl -X GET http://localhost:5000/api/v1/payments/transactions/txid/TXN202503021430ABC123 \
  -H "Authorization: Bearer <tenant_token>"
```

### 5. Verificar Status com Provider

```bash
curl -X GET http://localhost:5000/api/v1/payments/transactions/<transaction_id>/status \
  -H "Authorization: Bearer <tenant_token>"
```

### 6. Cancelar Transação

```bash
curl -X POST http://localhost:5000/api/v1/payments/transactions/<transaction_id>/cancel \
  -H "Authorization: Bearer <tenant_token>"
```

### 7. Obter Estatísticas

```bash
curl -X GET "http://localhost:5000/api/v1/payments/statistics" \
  -H "Authorization: Bearer <tenant_token>"
```

**Resposta:**
```json
{
  "statistics": {
    "total_amount": 5432.50,
    "total_transactions": 42,
    "paid_transactions": 38,
    "pending_transactions": 4,
    "conversion_rate": 90.48
  }
}
```

---

## Webhooks

### 1. Receber Webhook do Banco (Público)

```bash
curl -X POST http://localhost:5000/api/v1/webhooks/bank \
  -H "Content-Type: application/json" \
  -H "X-Signature: abc123signature..." \
  -d '{
    "txid": "TXN202503021430ABC123",
    "status": "paid",
    "amount": 150.75,
    "payer": {
      "name": "Maria Santos",
      "document": "12345678900"
    },
    "paid_at": "2025-03-02T14:45:00Z"
  }'
```

### 2. Simular Webhook (Desenvolvimento)

```bash
curl -X POST http://localhost:5000/api/v1/webhooks/test \
  -H "Content-Type: application/json" \
  -d '{
    "txid": "TXN202503021430ABC123",
    "status": "paid"
  }'
```

---

## Administração

### 1. Dashboard

```bash
curl -X GET http://localhost:5000/api/v1/admin/dashboard \
  -H "Authorization: Bearer <admin_token>"
```

**Resposta:**
```json
{
  "tenants": {
    "total": 25,
    "active": 23,
    "inactive": 2
  },
  "transactions": {
    "total": 1543,
    "paid": 1402,
    "pending": 141,
    "today": 87,
    "total_amount": 234567.89
  },
  "webhooks": {
    "total_attempts": 1523,
    "successful": 1498,
    "failed": 25,
    "success_rate": 98.36
  }
}
```

### 2. Listar Todas as Transações (Admin)

```bash
curl -X GET "http://localhost:5000/api/v1/admin/transactions?page=1&per_page=50" \
  -H "Authorization: Bearer <admin_token>"

# Filtrar por tenant
curl -X GET "http://localhost:5000/api/v1/admin/transactions?tenant_id=<tenant_uuid>" \
  -H "Authorization: Bearer <admin_token>"
```

### 3. Listar Todos os Usuários

```bash
curl -X GET "http://localhost:5000/api/v1/admin/users?page=1" \
  -H "Authorization: Bearer <admin_token>"
```

### 4. Listar Tentativas de Webhook

```bash
curl -X GET "http://localhost:5000/api/v1/admin/webhooks/attempts?status=failed" \
  -H "Authorization: Bearer <admin_token>"
```

### 5. Health Check

```bash
curl -X GET http://localhost:5000/api/v1/admin/system/health
```

**Resposta:**
```json
{
  "status": "healthy",
  "database": "connected",
  "timestamp": "2025-03-02T14:30:00Z"
}
```

---

## Validando Webhooks Recebidos (Para Tenants)

Quando o gateway envia um webhook para seu sistema, valide a assinatura:

### Python

```python
import hmac
import hashlib
import json

def verify_webhook_signature(payload, signature, secret):
    """Verifica assinatura do webhook."""
    message = json.dumps(payload, sort_keys=True).encode()
    expected_signature = hmac.new(
        secret.encode(),
        message,
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(signature, expected_signature)

# Uso
signature = request.headers.get('X-Webhook-Signature')
payload = request.json
webhook_secret = 'whsec_xyz789...'

if verify_webhook_signature(payload, signature, webhook_secret):
    # Webhook válido, processar pagamento
    transaction_id = payload['transaction_id']
    status = payload['status']
    # ...
else:
    # Webhook inválido
    return 401
```

### Node.js

```javascript
const crypto = require('crypto');

function verifyWebhookSignature(payload, signature, secret) {
    const message = JSON.stringify(payload, Object.keys(payload).sort());
    const expectedSignature = crypto
        .createHmac('sha256', secret)
        .update(message)
        .digest('hex');
    
    return crypto.timingSafeEqual(
        Buffer.from(signature),
        Buffer.from(expectedSignature)
    );
}

// Uso
const signature = req.headers['x-webhook-signature'];
const payload = req.body;
const webhookSecret = 'whsec_xyz789...';

if (verifyWebhookSignature(payload, signature, webhookSecret)) {
    // Webhook válido
    const transactionId = payload.transaction_id;
    const status = payload.status;
    // ...
} else {
    // Webhook inválido
    res.status(401).send('Invalid signature');
}
```

---

## Testando com Postman/Insomnia

Importe a documentação Swagger para gerar automaticamente uma collection:

1. Acesse: http://localhost:5000/swagger/
2. Baixe o JSON da especificação: http://localhost:5000/apispec.json
3. Importe no Postman/Insomnia

---

## Notas Importantes

- **Rate Limiting**: A API tem limites de requisições. Veja os headers `X-RateLimit-*` nas respostas.
- **Tokens**: Access tokens expiram em 1 hora. Use o refresh token para renovar.
- **Timestamps**: Todas as datas estão em formato ISO 8601 (UTC).
- **Valores Monetários**: Sempre em formato decimal com 2 casas decimais.
- **IDs**: Todos os IDs são UUIDs no formato string.

---

Para mais detalhes, consulte a documentação Swagger em `/swagger/`.
