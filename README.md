# 💳 Payment Gateway - White Label

Um gateway de pagamentos white label completo desenvolvido em Python/Flask, projetado para ser totalmente desacoplado do frontend e permitir multitenancy (múltiplos clientes utilizando a mesma infraestrutura).

## 🚀 Características

### Core Features

- **Multitenancy**: Cada tenant (empresa) tem seus próprios dados isolados e configurações personalizadas
- **White Label**: Sistema totalmente customizável por tenant (cores, logo, domínio)
- **API RESTful**: Backend 100% API, consumível por qualquer frontend
- **Autenticação JWT**: Sistema robusto de autenticação com tokens de acesso e refresh
- **Integração PIX**: Suporte para pagamentos via PIX (extensível para outros métodos)
- **Sistema de Webhooks**: 
  - Recebe notificações dos bancos/PSPs
  - Envia notificações para os tenants com retry automático
- **Providers Abstratos**: Arquitetura modular para integrar diferentes bancos/PSPs
- **Rate Limiting**: Proteção contra abuso da API
- **Documentação Swagger**: API totalmente documentada e testável via browser

### Tecnologias

- **Framework**: Flask 3.0
- **Database**: PostgreSQL (SQLAlchemy ORM)
- **Cache/Queue**: Redis + Celery
- **Autenticação**: Flask-JWT-Extended
- **Validação**: Marshmallow
- **Testes**: Pytest com cobertura
- **Containerização**: Docker + Docker Compose
- **Documentação**: Swagger/OpenAPI (Flasgger)

## 📋 Pré-requisitos

- Python 3.10+
- Docker e Docker Compose (recomendado)
- PostgreSQL (se não usar Docker)
- Redis (se não usar Docker)

## ⚡ Makefile

Para facilitar o desenvolvimento, use o Makefile:

```bash
make help          # Lista todos os comandos
make install       # Instala dependências
make db-init       # Cria tabelas
make db-seed       # Popula dados (admin + tenant)
make dev-backend   # Inicia backend (porta 5001)
make dev-frontend  # Inicia frontend (porta 5173)
make test          # Testes com cobertura
make test-fast     # Testes rápidos
make up            # Docker: PostgreSQL + Redis + App
make prod          # Gunicorn (produção local)
```

## 🔧 Instalação e Configuração

### Opção 1: Com Docker (Recomendado)

1. **Clone o repositório**:
```bash
git clone <repository-url>
cd payment-gateway
```

2. **Configure as variáveis de ambiente**:
```bash
cp .env.example .env
# Edite .env com suas configurações
```

3. **Inicie os containers**:
```bash
docker-compose up -d
```

4. **Inicialize o banco de dados**:
```bash
docker-compose exec app flask db upgrade
docker-compose exec app flask seed-db
```

5. **Acesse a aplicação**:
- API: http://localhost:5000
- Swagger: http://localhost:5000/swagger/

### Opção 2: Instalação Local

1. **Clone e crie ambiente virtual**:
```bash
git clone <repository-url>
cd payment-gateway
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows
```

2. **Instale dependências**:
```bash
pip install -r requirements.txt
```

3. **Configure variáveis de ambiente**:
```bash
cp .env.example .env
# Edite .env conforme necessário
```

4. **Configure banco de dados**:
```bash
flask db upgrade
flask seed-db
```

5. **Inicie Redis** (em outro terminal):
```bash
redis-server
```

6. **Inicie Celery Worker** (em outro terminal):
```bash
celery -A celery_worker.celery worker --loglevel=info
```

7. **Inicie a aplicação**:
```bash
flask run
# ou
python run.py
```

## 📚 Estrutura do Projeto

```
payment-gateway/
├── app/
│   ├── __init__.py              # Application factory
│   ├── extensions.py            # Flask extensions
│   ├── models/                  # Database models
│   │   ├── tenant.py
│   │   ├── user.py
│   │   ├── transaction.py
│   │   └── webhook_attempt.py
│   ├── modules/                 # Feature modules
│   │   ├── auth/               # Authentication
│   │   ├── tenants/            # Tenant management
│   │   ├── payments/           # Payment processing
│   │   │   └── providers/      # Bank providers
│   │   ├── webhooks/           # Webhook handling
│   │   └── admin/              # Admin endpoints
│   ├── schemas/                # Marshmallow schemas
│   └── utils/                  # Utilities
│       ├── security.py
│       ├── validators.py
│       └── webhook_helpers.py
├── tests/                      # Test suite
├── config.py                   # Configuration
├── run.py                      # Entry point
├── celery_worker.py           # Celery worker
├── frontend/                   # Interface web (React + Vite + Tailwind)
│   ├── src/
│   │   ├── pages/             # Login, Dashboard, Admin
│   │   └── api.js             # Cliente API
│   └── package.json
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
└── README.md
```

## 🌐 Frontend

O projeto inclui uma interface web React integrada ao backend:

```bash
# Terminal 1 - Backend
python run.py

# Terminal 2 - Frontend
cd frontend && npm install && npm run dev
```

Acesse: **http://localhost:5173**

- **Login** → Admin ou Tenant
- **Dashboard** (tenant) → Criar cobranças PIX, ver transações
- **Admin** → Estatísticas, transações globais, tenants

## 🔐 Autenticação

O sistema usa JWT (JSON Web Tokens) para autenticação:

### Login

```bash
POST /api/v1/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "password123"
}
```

**Resposta**:
```json
{
  "user": {...},
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

### Usando o Token

Inclua o token no header `Authorization`:

```bash
GET /api/v1/payments/transactions
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
```

## 💼 Uso da API

### 1. Criar um Tenant (Admin)

```bash
POST /api/v1/tenants
Authorization: Bearer <admin_token>
Content-Type: application/json

{
  "name": "Minha Loja",
  "email": "contato@minhaloja.com",
  "cnpj": "12345678000100",
  "pix_key": "contato@minhaloja.com",
  "bank_provider": "mock",
  "settings": {
    "primary_color": "#3B82F6",
    "logo_url": "https://example.com/logo.png"
  }
}
```

### 2. Criar uma Cobrança PIX

```bash
POST /api/v1/payments/charge
Authorization: Bearer <tenant_token>
Content-Type: application/json

{
  "amount": 100.50,
  "description": "Pagamento do pedido #123",
  "external_id": "ORDER_123"
}
```

**Resposta**:
```json
{
  "message": "Charge created successfully",
  "transaction": {
    "id": "uuid",
    "txid": "TXN20250302...",
    "amount": "100.50",
    "status": "pending",
    "qr_code": "data:image/png;base64,...",
    "qr_code_text": "00020126580014br.gov.bcb.pix...",
    "expires_at": "2025-03-02T15:00:00Z"
  }
}
```

### 3. Consultar Status de Transação

```bash
GET /api/v1/payments/transactions/<transaction_id>
Authorization: Bearer <tenant_token>
```

### 4. Listar Transações

```bash
GET /api/v1/payments/transactions?status=paid&page=1&per_page=20
Authorization: Bearer <tenant_token>
```

### 5. Webhook de Notificação do Banco

```bash
POST /api/v1/webhooks/bank
Content-Type: application/json
X-Signature: <signature>

{
  "txid": "TXN20250302...",
  "status": "paid",
  "amount": 100.50,
  "payer": {
    "name": "João Silva",
    "document": "12345678900"
  },
  "paid_at": "2025-03-02T14:30:00Z"
}
```

## 🔔 Sistema de Webhooks

### Webhooks de Entrada (Banco → Gateway)

O endpoint `/api/v1/webhooks/bank` recebe notificações dos bancos quando um pagamento é confirmado.

### Webhooks de Saída (Gateway → Tenant)

Quando um pagamento é confirmado, o sistema envia automaticamente uma notificação para a `webhook_url` configurada no tenant:

```json
{
  "transaction_id": "uuid",
  "txid": "TXN20250302...",
  "amount": "100.50",
  "currency": "BRL",
  "status": "paid",
  "description": "Pagamento do pedido #123",
  "payer_name": "João Silva",
  "payer_document": "12345678900",
  "paid_at": "2025-03-02T14:30:00Z",
  "created_at": "2025-03-02T14:00:00Z"
}
```

O webhook inclui um header `X-Webhook-Signature` para validação:

```python
import hmac
import hashlib
import json

def verify_webhook(payload, signature, secret):
    message = json.dumps(payload, sort_keys=True).encode()
    expected = hmac.new(secret.encode(), message, hashlib.sha256).hexdigest()
    return hmac.compare_digest(signature, expected)
```

### Retry Automático

Se a entrega do webhook falhar, o sistema tenta novamente com backoff exponencial:
- Tentativa 1: imediato
- Tentativa 2: após 2 minutos
- Tentativa 3: após 4 minutos
- Tentativa 4: após 8 minutos
- Tentativa 5: após 16 minutos

## 🏦 Providers de Pagamento

O sistema usa uma arquitetura de providers abstratos para integrar diferentes bancos/PSPs.

### Provider Mock (Desenvolvimento)

Incluído por padrão para desenvolvimento e testes:

```python
{
  "bank_provider": "mock"
}
```

### Implementando um Novo Provider

1. Crie uma classe herdando `BankProvider`:

```python
# app/modules/payments/providers/my_bank.py
from app.modules.payments.providers.base import BankProvider, ProviderError
import requests

class MyBankProvider(BankProvider):
    def create_charge(self, amount, pix_key, description=None, **kwargs):
        # Implementar integração com a API do banco
        response = requests.post(
            f"{self.config['api_url']}/charges",
            json={
                "amount": float(amount),
                "pix_key": pix_key,
                "description": description
            },
            headers=self._get_auth_headers()
        )
        
        if response.status_code != 200:
            raise ProviderError("Failed to create charge")
        
        data = response.json()
        return {
            'txid': data['transaction_id'],
            'qr_code': data['qr_code'],
            'qr_code_text': data['qr_code_text'],
            'expires_at': data['expires_at'],
            'status': 'pending',
            'raw_response': data
        }
    
    # Implementar outros métodos...
```

2. Registre no factory:

```python
# app/modules/payments/providers/factory.py
from app.modules.payments.providers.my_bank import MyBankProvider

providers = {
    'mock': MockProvider,
    'my_bank': MyBankProvider,
    # ...
}
```

## 🧪 Testes

### Executar todos os testes:

```bash
pytest
```

### Executar com cobertura:

```bash
pytest --cov=app --cov-report=html
```

### Executar testes específicos:

```bash
pytest tests/test_auth.py
pytest tests/test_payments.py -v
```

## 🔧 Comandos Flask CLI

### Inicializar banco de dados:
```bash
flask db upgrade
```

### Criar admin inicial:
```bash
flask create-admin
```

### Popular banco com dados de teste:
```bash
flask seed-db
```

### Criar migrations:
```bash
flask db migrate -m "Description"
flask db upgrade
```

## 📊 Monitoramento e Logs

Os logs são armazenados em `logs/gateway.log` e incluem:
- Criação de transações
- Webhooks recebidos e enviados
- Erros de integração com providers
- Tentativas de autenticação

## 🔒 Segurança

### Boas Práticas Implementadas:

- ✅ Senhas hasheadas com bcrypt
- ✅ Credenciais bancárias criptografadas
- ✅ JWT com expiração configurável
- ✅ Rate limiting em endpoints públicos
- ✅ Validação de entrada com schemas
- ✅ CORS configurável
- ✅ Assinatura de webhooks com HMAC
- ✅ Logs de auditoria

### Recomendações para Produção:

1. **Use HTTPS**: Configure SSL/TLS
2. **Variáveis de Ambiente**: Nunca commite secrets
3. **Firewall**: Restrinja acesso ao banco de dados
4. **Backup**: Configure backup automático do PostgreSQL
5. **Monitoring**: Use ferramentas como Sentry, New Relic
6. **Logs**: Centralize logs (ELK, CloudWatch)

## 🚀 Deploy em Produção

### Docker (Recomendado)

1. Configure variáveis de ambiente de produção
2. Use `docker-compose -f docker-compose.prod.yml up -d`
3. Configure reverse proxy (nginx/traefik) para SSL

### Heroku

```bash
heroku create my-payment-gateway
heroku addons:create heroku-postgresql
heroku addons:create heroku-redis
git push heroku main
heroku run flask db upgrade
```

### AWS/GCP/Azure

- Use serviços gerenciados (RDS, ElastiCache)
- Configure auto-scaling
- Use load balancer
- Configure health checks

## 📝 Variáveis de Ambiente

| Variável | Descrição | Padrão |
|----------|-----------|--------|
| `FLASK_ENV` | Ambiente (development/production) | development |
| `SECRET_KEY` | Chave secreta do Flask | - |
| `JWT_SECRET_KEY` | Chave secreta JWT | - |
| `DATABASE_URL` | URL do PostgreSQL | - |
| `REDIS_URL` | URL do Redis | redis://localhost:6379/0 |
| `DEFAULT_BANK_PROVIDER` | Provider padrão | mock |
| `WEBHOOK_RETRY_MAX_ATTEMPTS` | Máx tentativas webhook | 5 |
| `ENCRYPTION_KEY` | Chave de criptografia | - |

## 🤝 Contribuindo

1. Fork o projeto
2. Crie uma branch (`git checkout -b feature/nova-feature`)
3. Commit suas mudanças (`git commit -am 'Add nova feature'`)
4. Push para a branch (`git push origin feature/nova-feature`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT.

## 👥 Suporte

Para dúvidas ou problemas:
- Abra uma issue no GitHub
- Email: support@paymentgateway.com

## 🎯 Roadmap

- [ ] Suporte a cartão de crédito
- [ ] Integração com mais bancos brasileiros
- [ ] Split de pagamentos (marketplace)
- [ ] Gestão de assinaturas (recorrência)
- [ ] Dashboard administrativo (frontend)
- [ ] API de relatórios avançados
- [ ] Suporte a multi-currency
- [ ] SDK para diferentes linguagens

---

**Desenvolvido com ❤️ em Python/Flask**
