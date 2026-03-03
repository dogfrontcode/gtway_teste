# 🎨 Sistema de Logs Bonitos

## ✨ O Que Mudou

**ANTES**: Logs verbosos do SQLAlchemy poluindo terminal
```
2026-03-02 22:20:55,212 INFO sqlalchemy.engine.Engine SELECT users.id AS users_id...
2026-03-02 22:20:55,323 INFO sqlalchemy.engine.Engine SELECT tenants.id AS tenants_id...
127.0.0.1 - - [02/Mar/2026 22:20:55] "POST /api/v1/auth/login HTTP/1.1" 200 -
```

**AGORA**: Logs limpos, coloridos e informativos
```
[22:20:55] ✓ POST   /api/v1/auth/login 200 (150ms)
[22:20:56] 💳 Cobrança criada TXN202603... R$ 197,00 (sample-store)
[22:20:57] ✓ Produto criado: Curso de Python - R$ 197,00
```

---

## 🎯 Funcionalidades

### Banner de Inicialização
```
╔═══════════════════════════════════════════════════════════════════╗
║                                                                   ║
║              💳  Payment Gateway API                              ║
║                                                                   ║
╚═══════════════════════════════════════════════════════════════════╝

🚀 Servidor iniciado com sucesso!

► Backend:  http://localhost:5001
► Swagger:  http://localhost:5001/swagger/
► Frontend: http://localhost:5173

✓ Banco de dados: Conectado
✓ JWT: Configurado
✓ CORS: Habilitado

Pressione Ctrl+C para parar
```

### Logs de API
```
[22:20:55] ✓ GET    /api/v1/products 200 (45ms)
[22:20:56] ✓ POST   /api/v1/payments/charge 201 (234ms)
[22:20:57] ✗ GET    /api/v1/products/invalid 404 (12ms)
```

**Cores**:
- ✓ Verde: Status 2xx (sucesso)
- → Amarelo: Status 3xx (redirecionamento)
- ✗ Vermelho: Status 4xx/5xx (erro)

**Métodos coloridos**:
- GET: Azul
- POST: Verde
- PUT/PATCH: Amarelo
- DELETE: Vermelho

### Logs de Eventos
```
[22:20:55] ✓ Tenant criado: minha-loja
[22:20:56] ✓ Produto criado: Curso de Python - R$ 197,00
[22:20:57] 💳 Cobrança criada TXN202603... R$ 197,00 (sample-store)
[22:20:58] 🔔 Webhook ✓ success (tentativa 1) https://webhook.url...
[22:20:59] ⚠ Estoque baixo: Produto XYZ (5 unidades)
```

---

## 🛠️ Implementação

### Arquivos Criados

1. **app/utils/logger.py**
   - Funções de logging colorido
   - Colors class (ANSI codes)
   - Banner de inicialização

2. **app/middleware.py**
   - Middleware customizado
   - Tracking de requests
   - Logs de API formatados

### Arquivos Modificados

1. **config.py**
   - `SQLALCHEMY_ECHO = False` (desabilita logs SQL)

2. **run.py**
   - Banner de inicialização
   - Desabilita logs do werkzeug
   - Desabilita warnings

3. **app/__init__.py**
   - Registra middleware customizado

4. **app/modules/payments/services.py**
   - Log bonito para transações

5. **app/modules/tenants/services.py**
   - Log bonito para tenants

6. **app/modules/products/services.py**
   - Log bonito para produtos

---

## 🎨 Funções Disponíveis

```python
from app.utils.logger import (
    log_success,
    log_error,
    log_warning,
    log_info,
    log_api,
    log_transaction,
    log_webhook
)

# Logs simples
log_success("Operação concluída!")
log_error("Falha ao processar")
log_warning("Atenção: estoque baixo")
log_info("Servidor iniciando...")

# Log de API
log_api('GET', '/api/v1/products', 200, duration_ms=45.2)

# Log de transação
log_transaction('Cobrança criada', 'TXN123', 197.00, 'sample-store')

# Log de webhook
log_webhook('success', 'https://webhook.url', attempt=1)
```

---

## 📊 Antes vs Depois

### Antes ❌
```
/Library/Frameworks/Python.framework/Versions/3.13/lib/python3.13/site-packages/flask_limiter/extension.py:337: UserWarning: Using the in-memory storage...
2026-03-02 22:20:55,212 INFO sqlalchemy.engine.Engine SELECT users.id AS users_id, users.tenant_id AS users_tenant_id...
2026-03-02 22:20:55,323 INFO sqlalchemy.engine.Engine SELECT tenants.id AS tenants_id...
127.0.0.1 - - [02/Mar/2026 22:20:55] "POST /api/v1/auth/login HTTP/1.1" 200 -
```

**Problemas**:
- ❌ Muito verboso
- ❌ Difícil de ler
- ❌ Queries SQL poluindo
- ❌ Warnings irritantes
- ❌ Sem cores

### Depois ✅
```
╔═══════════════════════════════════════════════════════════════════╗
║              💳  Payment Gateway API                              ║
╚═══════════════════════════════════════════════════════════════════╝

🚀 Servidor iniciado com sucesso!

► Backend:  http://localhost:5001
► Swagger:  http://localhost:5001/swagger/

[22:20:55] ✓ POST   /api/v1/auth/login 200 (150ms)
[22:20:56] 💳 Cobrança criada TXN202603... R$ 197,00 (sample-store)
```

**Vantagens**:
- ✅ Limpo e organizado
- ✅ Fácil de ler
- ✅ Colorido
- ✅ Informativo
- ✅ Profissional

---

## 🚀 Como Usar

### Testar Agora

```bash
# Reiniciar com logs bonitos
pkill -f "python.*run.py"
make dev-backend
```

Você verá:
1. Banner bonito na inicialização
2. Logs coloridos de API
3. Eventos importantes destacados
4. Sem poluição de SQLAlchemy

### Exemplo de Uso

```bash
# Terminal 1: Backend com logs bonitos
make dev-backend

# Terminal 2: Frontend
make dev-frontend

# No terminal 1 você verá:
[22:20:55] ✓ POST   /api/v1/auth/login 200
[22:20:56] ✓ GET    /api/v1/products 200
[22:20:57] ✓ POST   /api/v1/products 201
[22:20:58] 💳 Cobrança criada TXN... R$ 197,00
```

---

## 💡 Customizar Cores

Edite `app/utils/logger.py`:

```python
# Mudar cor de sucesso
def log_success(message: str):
    # Verde → Ciano
    print(f"{Colors.CYAN}✓{Colors.RESET} {message}")
```

---

## 🎯 Logs por Tipo

### API Requests
```
[22:20:55] ✓ GET    /api/v1/products 200 (45ms)
[22:20:56] ✓ POST   /api/v1/products 201 (120ms)
[22:20:57] ✗ GET    /api/v1/invalid 404 (8ms)
```

### Transações
```
[22:20:55] 💳 Cobrança criada TXN202603... R$ 197,00 (sample-store)
[22:20:56] 💳 Pagamento confirmado TXN202603... R$ 197,00
```

### Produtos
```
[22:20:55] ✓ Produto criado: Curso de Python - R$ 197,00
[22:20:56] ✓ Produto atualizado: Curso de Python
```

### Tenants
```
[22:20:55] ✓ Tenant criado: minha-loja
[22:20:56] ✓ API key regenerada: minha-loja
```

### Webhooks
```
[22:20:55] 🔔 Webhook ✓ success (tentativa 1) https://webhook.url...
[22:20:56] 🔔 Webhook ✗ failed (tentativa 2) https://webhook.url...
```

---

## 📝 Logs Desabilitados

Para terminal limpo:
- ❌ SQLAlchemy queries
- ❌ Werkzeug request logs
- ❌ Flask-Limiter warnings
- ❌ Stack traces em desenvolvimento

---

## ✅ Resultado

Terminal **limpo, bonito e informativo**!

```
╔═══════════════════════════════════════════════════════════════════╗
║              💳  Payment Gateway API                              ║
╚═══════════════════════════════════════════════════════════════════╝

🚀 Servidor iniciado com sucesso!

► Backend:  http://localhost:5001
► Frontend: http://localhost:5173

✓ Banco: Conectado
✓ JWT: OK
✓ CORS: OK

Aguardando requisições...

[22:20:55] ✓ POST   /api/v1/auth/login 200 (150ms)
[22:20:56] ✓ GET    /api/v1/products 200 (45ms)
[22:20:57] ✓ POST   /api/v1/products 201 (120ms)
[22:20:58] 💳 Cobrança criada TXN... R$ 99.90 (minha-loja)
```

🎉 **Muito mais bonito!**
