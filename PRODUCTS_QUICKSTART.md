# 🛍️ Guia Rápido - Sistema de Produtos

## ⚡ Começar em 3 Passos

### 1️⃣ Atualizar Banco de Dados

```bash
cd /Users/tidos/Desktop/scripts

# Recriar banco com tabela de produtos
make db-reset
```

Isso vai:
- ✅ Criar tabela `products`
- ✅ Popular com 3 produtos de exemplo
- ✅ Recriar admin e tenant

### 2️⃣ Iniciar Sistema

```bash
make dev
```

Acesse:
- **Frontend**: http://localhost:5173
- **Backend**: http://localhost:5001

### 3️⃣ Usar Produtos

1. Login: `user@samplestore.com` / `user123`
2. Menu → **"Produtos"**
3. Veja os 3 produtos de exemplo
4. Clique **"Criar Cobrança"** em qualquer produto
5. ✅ QR Code PIX gerado!

---

## 🎯 Funcionalidades

### Criar Produto

1. Página Produtos
2. Clique **"+ Criar Produto"**
3. Preencha:
   - **Nome**: "Meu Curso"
   - **Preço**: 197.00
   - **Categoria**: "Cursos"
   - **Descrição**: (opcional)
   - **Imagem**: (opcional)
   - **Estoque**: (opcional)
4. Clique "Criar Produto"
5. ✅ Produto aparece na lista!

### Criar Cobrança de Produto

1. Na lista de produtos
2. Clique **"Criar Cobrança"**
3. Escolha quantidade
4. Veja total calculado
5. Clique "Confirmar"
6. ✅ QR Code PIX gerado!
7. Estoque diminui automaticamente (se ativo)

### Filtrar por Categoria

- Clique nas categorias no topo da página
- Lista atualiza automaticamente

### Deletar Produto

- Clique no ícone 🗑️ no card do produto
- Confirme
- ✅ Produto desativado (soft delete)

---

## 📊 Produtos de Exemplo

Após `make db-reset`, você terá:

### 1. Curso de Python Completo
- **Preço**: R$ 197,00
- **Categoria**: Cursos
- **Estoque**: Ilimitado
- **Imagem**: ✅

### 2. Ebook: APIs REST com Flask
- **Preço**: R$ 49,90
- **Categoria**: Ebooks
- **Estoque**: 1000 unidades (controlado)

### 3. Consultoria 1 hora
- **Preço**: R$ 250,00
- **Categoria**: Consultoria
- **Estoque**: Ilimitado

---

## 🔧 API Endpoints

Todos os endpoints já funcionam:

```bash
# Listar produtos
GET /api/v1/products

# Criar produto
POST /api/v1/products

# Obter produto
GET /api/v1/products/<id>

# Atualizar produto
PUT /api/v1/products/<id>

# Deletar produto
DELETE /api/v1/products/<id>

# Criar cobrança de produto (NOVO!)
POST /api/v1/products/<id>/charge
```

---

## 💡 Dicas

### Produtos Digitais (Cursos, Ebooks)
- **track_stock**: `false`
- **Estoque**: Ilimitado

### Produtos Físicos (Camisetas, Livros)
- **track_stock**: `true`
- **stock_quantity**: Quantidade disponível

### Serviços (Consultoria, Horas)
- **track_stock**: `false`
- **Preço**: Por hora/sessão

---

## 🎨 Customizar

### Adicionar Campos

Edite `CreateProductModal.jsx` para adicionar:
- Tags
- Peso/dimensões (para frete)
- Marca
- Variações (tamanho, cor)

### Mudar Layout

Edite `Products.jsx`:
- Grid de 3 colunas → 4 colunas
- Card design
- Filtros adicionais

---

## 🐛 Problemas?

### "Table products does not exist"
```bash
make db-reset
```

### "Port already in use"
```bash
lsof -ti:5001 | xargs kill -9
lsof -ti:5173 | xargs kill -9
make dev
```

### "Cannot find module CreateProductModal"
```bash
cd frontend && npm install && cd ..
make dev
```

---

## 📖 Documentação Completa

- 📘 **PRODUCTS_FEATURE.md**: Documentação técnica completa
- 📗 **README.md**: Documentação principal
- 📙 **API_EXAMPLES.md**: Exemplos de API

---

## 🎉 Pronto!

Agora você pode:
- ✅ Criar produtos pelo painel
- ✅ Gerar cobranças em 1 clique
- ✅ Controlar estoque automaticamente
- ✅ Filtrar por categoria
- ✅ Interface visual moderna

**Teste agora**:
```bash
make db-reset && make dev
```

🛍️ **Sistema de Produtos 100% Funcional!**
