# 🛍️ Sistema de Produtos - Nova Funcionalidade

## 📋 Resumo

Sistema completo de gerenciamento de produtos implementado com:
- ✅ Backend: API REST completa
- ✅ Frontend: Interface visual moderna
- ✅ Integração: Criar cobranças a partir de produtos
- ✅ Controle de estoque opcional
- ✅ Categorização de produtos
- ✅ Multi-tenant (cada tenant tem seus produtos)

---

## 🎯 Funcionalidades

### Backend (API)

#### 1. **Criar Produto**
```bash
POST /api/v1/products
Authorization: Bearer <token>

{
  "name": "Curso de Python",
  "description": "Curso completo",
  "sku": "CURSO-PY-001",
  "price": 197.00,
  "category": "Cursos",
  "image_url": "https://example.com/image.jpg",
  "track_stock": true,
  "stock_quantity": 100
}
```

#### 2. **Listar Produtos**
```bash
GET /api/v1/products?category=Cursos&page=1&per_page=20
Authorization: Bearer <token>
```

#### 3. **Obter Produto**
```bash
GET /api/v1/products/<product_id>
Authorization: Bearer <token>
```

#### 4. **Atualizar Produto**
```bash
PUT /api/v1/products/<product_id>
Authorization: Bearer <token>

{
  "name": "Novo Nome",
  "price": 297.00
}
```

#### 5. **Deletar Produto** (Soft Delete)
```bash
DELETE /api/v1/products/<product_id>
Authorization: Bearer <token>
```

#### 6. **Criar Cobrança a partir de Produto** 🆕
```bash
POST /api/v1/products/<product_id>/charge
Authorization: Bearer <token>

{
  "quantity": 2,
  "external_id": "ORDER_123",
  "expires_in_minutes": 60
}
```

**Resposta**:
```json
{
  "message": "Charge created successfully",
  "transaction": {
    "id": "uuid",
    "txid": "TXN...",
    "amount": "394.00",
    "qr_code": "data:image/png;base64,...",
    "qr_code_text": "00020126...",
    "status": "pending"
  },
  "product": {
    "id": "uuid",
    "name": "Curso de Python",
    "quantity": 2,
    "unit_price": "197.00",
    "total_price": "394.00"
  }
}
```

---

### Frontend (Interface Visual)

#### 1. **Página de Produtos** (`/products`)

**Funcionalidades**:
- ✅ Grid de produtos com cards visuais
- ✅ Imagem, nome, preço, categoria
- ✅ Filtro por categoria
- ✅ Paginação (12 por página)
- ✅ Botão "Criar Cobrança" em cada produto
- ✅ Botão deletar produto
- ✅ Indicador de estoque (se track_stock)

**Componentes**:
- `frontend/src/pages/Products.jsx`
- `frontend/src/components/CreateProductModal.jsx`

#### 2. **Modal Criar Produto**

**Campos**:
- Nome (obrigatório)
- Descrição
- Preço (obrigatório)
- SKU
- Categoria
- URL da imagem
- Controlar estoque (checkbox)
- Quantidade em estoque (se controlar)

#### 3. **Modal Criar Cobrança**

Ao clicar em "Criar Cobrança" em um produto:
- ✅ Mostra detalhes do produto
- ✅ Permite escolher quantidade
- ✅ Calcula total automaticamente
- ✅ Cria cobrança PIX instantaneamente
- ✅ Verifica estoque automaticamente
- ✅ Diminui estoque ao criar cobrança

---

## 🗄️ Modelo de Dados

### Product

```python
class Product(db.Model):
    id                  # UUID
    tenant_id           # FK para Tenant
    name                # Nome do produto
    description         # Descrição
    sku                 # Código SKU (único por tenant)
    price               # Preço (Decimal)
    currency            # Moeda (BRL)
    image_url           # URL da imagem
    category            # Categoria
    metadata            # JSON (dados extras)
    stock_quantity      # Quantidade em estoque
    track_stock         # Se controla estoque
    is_active           # Status (ativo/inativo)
    created_at          # Data de criação
    updated_at          # Data de atualização
```

### Transaction (Atualizado)

Agora tem campo `product_id` (opcional):
```python
class Transaction(db.Model):
    # ...
    product_id          # FK para Product (opcional)
    # ...
```

---

## 🚀 Como Usar

### 1. Criar Tabela de Produtos

```bash
# Recriar banco com nova tabela
make db-reset

# Ou criar migration
make db-migrate msg="Add products table"
make db-upgrade
```

### 2. Acessar Interface

```bash
# Iniciar desenvolvimento
make dev

# Acessar
http://localhost:5173
```

**Login**: `user@samplestore.com` / `user123`

### 3. Criar Produto

1. Login no frontend
2. Menu → **"Produtos"**
3. Clique em **"+ Criar Produto"**
4. Preencha:
   - Nome: "Meu Produto"
   - Preço: 99.90
   - Categoria: "Digital"
   - (opcional) Imagem, SKU, estoque
5. Clique "Criar Produto"
6. ✅ Produto criado!

### 4. Criar Cobrança a partir de Produto

1. Na lista de produtos
2. Clique **"Criar Cobrança"** no card do produto
3. Escolha quantidade (padrão: 1)
4. Veja o total calculado
5. Clique "Confirmar"
6. ✅ Cobrança PIX criada! (com QR Code)

---

## 📊 Fluxo Completo

```
1. Tenant cria produto
   └─> POST /api/v1/products
       └─> Produto salvo no banco

2. Cliente escolhe produto
   └─> Frontend mostra lista de produtos

3. Criar cobrança do produto
   └─> POST /api/v1/products/{id}/charge
       ├─> Verifica estoque (se track_stock)
       ├─> Calcula valor total (price * quantity)
       ├─> Cria transação PIX
       ├─> Gera QR Code
       └─> Diminui estoque (se track_stock)

4. Cliente paga
   └─> Webhook recebido
       └─> Transaction.status = 'paid'
```

---

## 🎨 Exemplos de Uso

### Exemplo 1: E-commerce

```javascript
// Criar produto
await api.products.create({
  name: 'Camiseta Premium',
  price: 79.90,
  sku: 'CAM-PREM-001',
  category: 'Roupas',
  track_stock: true,
  stock_quantity: 50,
  image_url: 'https://example.com/camiseta.jpg'
});

// Cliente compra 2 unidades
await api.products.createCharge(productId, { quantity: 2 });
// Total: R$ 159.80, Estoque: 50 → 48
```

### Exemplo 2: Infoprodutos

```javascript
// Curso digital (sem estoque)
await api.products.create({
  name: 'Curso de JavaScript',
  price: 197.00,
  category: 'Cursos',
  track_stock: false,  // Produto digital, estoque ilimitado
});

// Criar cobrança
await api.products.createCharge(productId, { quantity: 1 });
```

### Exemplo 3: Serviços

```javascript
// Consultoria (sem estoque)
await api.products.create({
  name: 'Consultoria 1 hora',
  price: 350.00,
  category: 'Serviços',
  description: 'Consultoria técnica especializada',
});
```

---

## 🧪 Testando

### Via API

```bash
# 1. Login
TOKEN=$(curl -X POST http://localhost:5001/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user@samplestore.com","password":"user123"}' \
  | jq -r '.access_token')

# 2. Criar produto
PRODUCT=$(curl -X POST http://localhost:5001/api/v1/products \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Produto Teste",
    "price": 99.90,
    "category": "Teste"
  }' | jq -r '.product.id')

# 3. Listar produtos
curl http://localhost:5001/api/v1/products \
  -H "Authorization: Bearer $TOKEN"

# 4. Criar cobrança do produto
curl -X POST http://localhost:5001/api/v1/products/$PRODUCT/charge \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"quantity": 2}'
```

### Via Interface

1. http://localhost:5173
2. Login: `user@samplestore.com` / `user123`
3. Menu → **Produtos**
4. Clique **"+ Criar Produto"**
5. Preencha e salve
6. Clique **"Criar Cobrança"** no produto
7. ✅ QR Code gerado!

---

## 📦 Arquivos Criados

### Backend
```
app/models/product.py                    # Modelo Product
app/schemas/product_schemas.py          # Validação Marshmallow
app/modules/products/__init__.py         # Blueprint
app/modules/products/services.py         # Lógica de negócio
app/modules/products/views.py            # Endpoints API
```

### Frontend
```
frontend/src/pages/Products.jsx          # Página de produtos
frontend/src/components/CreateProductModal.jsx  # Modal criar
```

### Documentação
```
PRODUCTS_FEATURE.md                      # Este arquivo
```

### Modificados
```
app/__init__.py                          # Registrar blueprint
app/models/transaction.py                # Adicionar product_id
app/models/tenant.py                     # Relacionamento
app/modules/payments/services.py         # Suporte product_id
frontend/src/App.jsx                     # Rota /products
frontend/src/api.js                      # Métodos de produtos
frontend/src/components/Layout.jsx       # Link produtos
run.py                                   # Seed de produtos
```

---

## 🎯 Benefícios

### Para o Tenant
- ✅ **Catálogo organizado**: Todos os produtos em um lugar
- ✅ **Criação rápida**: Interface visual intuitiva
- ✅ **Cobranças simplificadas**: 1 clique para criar PIX
- ✅ **Controle de estoque**: Automático e opcional
- ✅ **Categorização**: Organizar por tipo

### Para o Cliente Final
- ✅ **Experiência melhor**: Descrição e imagem do produto
- ✅ **Transparência**: Sabe exatamente o que está pagando
- ✅ **Confiança**: Produto profissional

### Para o Sistema
- ✅ **Rastreabilidade**: Transaction vinculada a Product
- ✅ **Analytics**: Produtos mais vendidos, categorias populares
- ✅ **Automação**: Estoque controlado automaticamente
- ✅ **Escalabilidade**: Suporta milhares de produtos

---

## 📊 Casos de Uso

### 1. E-commerce
- Produtos físicos com controle de estoque
- Variações (tamanho, cor) via metadata
- Imagens dos produtos

### 2. Infoprodutos
- Cursos digitais (sem estoque)
- Ebooks (sem estoque)
- Assinaturas (sem estoque)

### 3. Serviços
- Consultorias
- Horas de trabalho
- Pacotes de serviços

### 4. Eventos
- Ingressos (com controle de quantidade)
- Workshops
- Conferências

---

## 🔧 Configuração

### 1. Criar Tabelas

```bash
# Opção 1: Reset completo (apaga dados)
make db-reset

# Opção 2: Migration (mantém dados)
make db-migrate msg="Add products table"
make db-upgrade
```

### 2. Popular Produtos de Exemplo

```bash
make db-seed
```

Isso cria 3 produtos de exemplo:
- Curso de Python Completo (R$ 197,00)
- Ebook: APIs REST com Flask (R$ 49,90)
- Consultoria 1 hora (R$ 250,00)

### 3. Acessar Interface

```bash
make dev
# Abrir: http://localhost:5173
# Login: user@samplestore.com / user123
# Menu → Produtos
```

---

## 🚀 API Client (Frontend)

### Importar

```javascript
import { api } from './api';
```

### Criar Produto

```javascript
const product = await api.products.create({
  name: 'Meu Produto',
  price: 99.90,
  category: 'Digital',
  description: 'Descrição do produto',
  track_stock: false,
});
```

### Listar Produtos

```javascript
// Todos os produtos
const data = await api.products.list();
const products = data.products;

// Filtrar por categoria
const data = await api.products.list({ category: 'Cursos' });

// Paginação
const data = await api.products.list({ page: 2, per_page: 20 });
```

### Criar Cobrança de Produto

```javascript
const result = await api.products.createCharge(productId, {
  quantity: 2,
  expires_in_minutes: 60,
});

const transaction = result.transaction;
const qrCode = transaction.qr_code;
const qrCodeText = transaction.qr_code_text;
```

### Atualizar Produto

```javascript
await api.products.update(productId, {
  price: 149.90,
  stock_quantity: 50,
});
```

### Deletar Produto

```javascript
await api.products.delete(productId);
```

---

## 💡 Exemplos Práticos

### Exemplo 1: Loja de Cursos Online

```javascript
// 1. Criar cursos
const cursoPython = await api.products.create({
  name: 'Python para Iniciantes',
  price: 197.00,
  category: 'Cursos',
  description: 'Aprenda Python do zero',
  track_stock: false,  // Produto digital
});

// 2. Cliente compra
const charge = await api.products.createCharge(cursoPython.id, {
  quantity: 1,
});

// 3. Mostrar QR Code
showQRCode(charge.transaction.qr_code);
```

### Exemplo 2: Loja de Camisetas

```javascript
// 1. Criar camiseta
const camiseta = await api.products.create({
  name: 'Camiseta Dev',
  price: 79.90,
  category: 'Roupas',
  sku: 'CAM-DEV-M',
  track_stock: true,
  stock_quantity: 100,
  image_url: 'https://example.com/camiseta.jpg',
});

// 2. Cliente compra 3 unidades
const charge = await api.products.createCharge(camiseta.id, {
  quantity: 3,  // Total: R$ 239,70
});

// Estoque automaticamente: 100 → 97
```

### Exemplo 3: Consultoria

```javascript
// 1. Criar serviço
const consultoria = await api.products.create({
  name: 'Consultoria Técnica - 1h',
  price: 350.00,
  category: 'Serviços',
  description: 'Consultoria especializada em arquitetura de software',
  track_stock: false,
});

// 2. Agendar consultoria
const charge = await api.products.createCharge(consultoria.id, {
  external_id: 'AGENDA_2026_03_15',
});
```

---

## 🎯 Integração com Dashboard

### Mostrar Produtos no Dashboard

```javascript
// Listar produtos ativos
const { products } = await api.products.list({ is_active: true });

// Renderizar grid
products.map(product => (
  <ProductCard 
    product={product}
    onCreateCharge={() => handleCharge(product)}
  />
));
```

### Criar Cobrança Rápida

```javascript
// Botão "Pagar" ao lado do produto
<button onClick={() => {
  api.products.createCharge(product.id, { quantity: 1 })
    .then(result => {
      showPaymentModal(result.transaction);
    });
}}>
  Pagar R$ {product.price}
</button>
```

---

## 📈 Próximas Melhorias Sugeridas

### Curto Prazo
- [ ] Editar produto (modal de edição)
- [ ] Upload de imagem (não só URL)
- [ ] Variações de produto (tamanho, cor)
- [ ] Produtos em destaque

### Médio Prazo
- [ ] Histórico de vendas por produto
- [ ] Relatório de produtos mais vendidos
- [ ] Desconto por quantidade
- [ ] Cupons de desconto

### Longo Prazo
- [ ] Produtos com assinatura
- [ ] Bundle de produtos
- [ ] Frete (para físicos)
- [ ] Marketplace (produtos de múltiplos tenants)

---

## ✅ Checklist de Implementação

- [x] Modelo Product criado
- [x] Schemas de validação
- [x] Service layer
- [x] Endpoints API (6 endpoints)
- [x] Frontend: Página de produtos
- [x] Frontend: Modal criar produto
- [x] Frontend: Criar cobrança de produto
- [x] Controle de estoque
- [x] Filtro por categoria
- [x] Paginação
- [x] Relacionamento com Transaction
- [x] Seed de produtos exemplo
- [x] Documentação completa

---

## 🎉 Conclusão

Sistema de produtos **100% funcional**:

- ✅ **Backend**: API completa com 6 endpoints
- ✅ **Frontend**: Interface visual moderna
- ✅ **Integração**: Criar cobranças em 1 clique
- ✅ **Estoque**: Controle automático opcional
- ✅ **Documentação**: Guia completo

**Status**: ✅ **Pronto para Uso**

**Como testar**:
```bash
make db-reset  # Recria banco com produtos
make dev       # Inicia sistema
# Abrir: http://localhost:5173 → Produtos
```

---

**Implementado em**: 03/03/2026  
**Versão**: 1.2.0  
**Funcionalidade**: Sistema de Produtos Completo 🛍️
