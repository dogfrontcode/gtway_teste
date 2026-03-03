# 🚀 Guia de Início Rápido - Payment Gateway

## 📝 Para Começar AGORA (5 minutos)

### 1️⃣ Instalar Dependências

```bash
# Instalar tudo
make setup
```

Isso vai:
- ✅ Instalar dependências Python
- ✅ Instalar dependências Node (frontend)
- ✅ Criar banco de dados
- ✅ Popular com dados de exemplo

### 2️⃣ Iniciar Desenvolvimento

```bash
# Inicia backend + frontend em paralelo
make dev
```

Acesse:
- **Backend API**: http://localhost:5001
- **Frontend**: http://localhost:5173
- **Swagger**: http://localhost:5001/swagger/

### 3️⃣ Login

Credenciais criadas automaticamente:

**Admin**:
- Email: `admin@gateway.com`
- Senha: `admin123`

**Tenant (Sample Store)**:
- Email: `user@samplestore.com`
- Senha: `user123`

---

## 🎯 Testando a API

### Fazer Login

```bash
curl -X POST http://localhost:5001/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@samplestore.com",
    "password": "user123"
  }'
```

Copie o `access_token` da resposta.

### Criar uma Cobrança PIX

```bash
curl -X POST http://localhost:5001/api/v1/payments/charge \
  -H "Authorization: Bearer SEU_TOKEN_AQUI" \
  -H "Content-Type: application/json" \
  -d '{
    "amount": 100.50,
    "description": "Teste de pagamento"
  }'
```

Resposta:
- ✅ QR Code (base64)
- ✅ Texto PIX "copia e cola"
- ✅ TxID para acompanhar
- ✅ Data de expiração

### Listar Transações

```bash
curl http://localhost:5001/api/v1/payments/transactions \
  -H "Authorization: Bearer SEU_TOKEN_AQUI"
```

---

## 💼 Painel Admin

1. Acesse http://localhost:5173
2. Login com `admin@gateway.com` / `admin123`
3. Clique em "Admin" no menu
4. Clique em "Criar Tenant" para adicionar novos clientes

**Funcionalidades Admin**:
- 📊 Dashboard com estatísticas
- 👥 Gerenciar tenants
- 💳 Ver todas as transações
- 🔔 Histórico de webhooks

---

## 🛠️ Comandos Úteis

```bash
# Ver todos os comandos
make help

# Apenas backend
make dev-backend

# Apenas frontend
make dev-frontend

# Iniciar Celery worker (para webhooks)
make celery

# Rodar testes
make test

# Criar backup do banco
make db-backup

# Resetar banco (apaga tudo!)
make db-reset
```

---

## 📚 Próximos Passos

1. **Explore a API**: http://localhost:5001/swagger/
2. **Leia a documentação completa**: [README.md](./README.md)
3. **Veja exemplos de uso**: [API_EXAMPLES.md](./API_EXAMPLES.md)
4. **Análise técnica**: [ANALYSIS.md](./ANALYSIS.md)

---

## 🐛 Problemas Comuns

### "ModuleNotFoundError"
```bash
make install-backend
```

### "Cannot find module"
```bash
make install-frontend
```

### "Database locked"
```bash
# Mate processos que estão usando o banco
pkill -f python
make db-reset
```

### "Port already in use"
```bash
# Backend (5001)
lsof -ti:5001 | xargs kill -9

# Frontend (5173)
lsof -ti:5173 | xargs kill -9
```

---

## 🔥 Demo Rápido - Criar Tenant via API

```bash
# 1. Login como admin
TOKEN=$(curl -X POST http://localhost:5001/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@gateway.com","password":"admin123"}' \
  | jq -r '.access_token')

# 2. Criar tenant
curl -X POST http://localhost:5001/api/v1/tenants \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Minha Loja",
    "email": "contato@minhaloja.com",
    "pix_key": "contato@minhaloja.com",
    "bank_provider": "mock",
    "settings": {
      "primary_color": "#FF5733",
      "logo_url": "https://example.com/logo.png"
    }
  }'
```

---

## 💡 Dicas

- Use o **Swagger** para testar endpoints interativamente
- Configure `.env` antes de produção (mude secrets!)
- Use `make check` para verificar ambiente
- Logs ficam em `logs/gateway.log`
- Frontend é React + Tailwind (fácil customizar)

---

**Pronto para começar!** 🚀

Dúvidas? Veja a [documentação completa](./README.md) ou abra uma issue.
