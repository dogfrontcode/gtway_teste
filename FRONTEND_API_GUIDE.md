# 🚀 Guia de API Frontend - Produtos

## ✨ Endpoint Otimizado para Frontend

Criado endpoint **especial** que retorna **tudo pronto** para o frontend exibir!

### POST `/api/v1/products/<id>/charge`

**O que retorna**:
- ✅ Dados da transação formatados
- ✅ QR Code (imagem base64)
- ✅ Código PIX "copia e cola"
- ✅ Informações do produto
- ✅ Cálculos prontos (unit_price, total_price)
- ✅ Instruções de pagamento
- ✅ Tudo formatado para exibir

---

## 📦 Resposta Completa

```json
{
  "success": true,
  "transaction": {
    "id": "uuid",
    "txid": "TXN202603...",
    "amount": 197.0,
    "amount_formatted": "R$ 197,00",
    "currency": "BRL",
    "status": "pending",
    "description": "Curso de Python (x1)",
    "created_at": "2026-03-03T01:30:00Z",
    "expires_at": "2026-03-03T02:30:00Z"
  },
  "payment": {
    "qr_code_image": "data:image/png;base64,iVBORw0KG...",
    "qr_code_text": "00020126580014br.gov.bcb.pix...",
    "pix_key": "contato@loja.com"
  },
  "product": {
    "id": "uuid",
    "name": "Curso de Python",
    "unit_price": 197.0,
    "unit_price_formatted": "R$ 197,00",
    "quantity": 1,
    "total_price": 197.0,
    "total_price_formatted": "R$ 197,00"
  },
  "instructions": {
    "title": "Como pagar",
    "steps": [
      "Abra o app do seu banco",
      "Escolha Pix",
      "Escaneie o QR Code ou use o código copia e cola",
      "Confirme o pagamento",
      "Pronto! Pagamento será confirmado automaticamente"
    ]
  }
}
```

---

## 🎯 Como Usar no Frontend

### 1. Importar API

```javascript
import { api } from './api';
```

### 2. Criar Cobrança

```javascript
const result = await api.products.createCharge(productId, {
  quantity: 2,
  expires_in_minutes: 60
});

// Tudo pronto para usar!
const qrCode = result.payment.qr_code_image;
const pixCode = result.payment.qr_code_text;
const total = result.product.total_price_formatted;  // "R$ 394,00"
const instructions = result.instructions.steps;
```

### 3. Exibir Tela de Pagamento

```jsx
function PaymentScreen({ chargeData }) {
  const { transaction, payment, product, instructions } = chargeData;
  
  return (
    <div>
      <h1>Pagamento PIX</h1>
      
      {/* Produto */}
      <div>
        <h2>{product.name}</h2>
        <p>Quantidade: {product.quantity}</p>
        <p>Total: {product.total_price_formatted}</p>
      </div>
      
      {/* QR Code */}
      <img src={payment.qr_code_image} alt="QR Code" />
      
      {/* Código Copia e Cola */}
      <input value={payment.qr_code_text} readOnly />
      <button onClick={() => navigator.clipboard.writeText(payment.qr_code_text)}>
        Copiar
      </button>
      
      {/* Instruções */}
      <ol>
        {instructions.steps.map((step, i) => (
          <li key={i}>{step}</li>
        ))}
      </ol>
      
      {/* Info */}
      <p>TxID: {transaction.txid}</p>
      <p>Válido até: {new Date(transaction.expires_at).toLocaleString()}</p>
    </div>
  );
}
```

---

## 🎨 Componente Pronto para Usar

Já criado: `PaymentModal.jsx`

**Uso**:
```jsx
import PaymentModal from './components/PaymentModal';

function MyComponent() {
  const [paymentData, setPaymentData] = useState(null);
  
  const handleBuyProduct = async (productId) => {
    const result = await api.products.createCharge(productId, {
      quantity: 1
    });
    
    setPaymentData(result);  // Abre modal automaticamente
  };
  
  return (
    <>
      <button onClick={() => handleBuyProduct('product-id')}>
        Comprar
      </button>
      
      <PaymentModal
        chargeData={paymentData}
        onClose={() => setPaymentData(null)}
      />
    </>
  );
}
```

**O modal mostra**:
- ✅ Banner bonito (gradient)
- ✅ Info do produto
- ✅ Total destacado
- ✅ QR Code grande
- ✅ Botão copiar código PIX
- ✅ Instruções passo-a-passo
- ✅ Validade
- ✅ Design profissional

---

## 📊 Dados Formatados Prontos

### Produto

```javascript
const product = {
  id: "uuid",
  name: "Curso de Python",
  price: 197.0,                    // número
  price_formatted: "R$ 197,00",    // string formatada
  description: "Curso completo...",
  category: "Cursos",
  image_url: "https://...",
  has_image: true,                 // boolean
  sku: "CURSO-PY-001",
  stock: {
    tracking: true,                // boolean
    quantity: 100,                 // número
    available: true,               // boolean
    display: "100 unidades"        // string formatada
  },
  is_active: true,
  metadata: {
    created_at: "2026-03-03T00:00:00Z",
    updated_at: "2026-03-03T00:00:00Z"
  }
};

// Usar diretamente:
<h1>{product.name}</h1>
<p>{product.price_formatted}</p>
<p>{product.stock.display}</p>
<img src={product.image_url} />
```

### Cobrança (Resposta Otimizada)

```javascript
const charge = {
  success: true,
  transaction: {
    amount_formatted: "R$ 197,00",  // Pronto para exibir
    txid: "TXN202603...",
    status: "pending"
  },
  payment: {
    qr_code_image: "data:image/png;base64...",  // Usar direto em <img>
    qr_code_text: "00020126...",                // Copiar para clipboard
  },
  product: {
    unit_price_formatted: "R$ 197,00",
    total_price_formatted: "R$ 394,00",  // quantity = 2
    quantity: 2
  },
  instructions: {
    title: "Como pagar",
    steps: [...]  // Array pronto para mapear
  }
};

// Usar:
<img src={charge.payment.qr_code_image} />
<p>{charge.product.total_price_formatted}</p>
<button onClick={() => copy(charge.payment.qr_code_text)}>Copiar</button>
```

---

## 🎯 Fluxo Completo no Frontend

### Exemplo Simples

```jsx
import { api } from './api';
import PaymentModal from './components/PaymentModal';

function ProductCard({ product }) {
  const [paymentData, setPaymentData] = useState(null);
  
  const handleBuy = async () => {
    try {
      const result = await api.products.createCharge(product.id, {
        quantity: 1
      });
      
      setPaymentData(result);  // Abre modal de pagamento
    } catch (err) {
      alert(`Erro: ${err.message}`);
    }
  };
  
  return (
    <>
      <div className="product-card">
        <img src={product.image_url} />
        <h2>{product.name}</h2>
        <p>{product.description}</p>
        <p className="price">{product.price_formatted}</p>
        <p className="stock">{product.stock.display}</p>
        
        <button onClick={handleBuy}>
          Comprar Agora
        </button>
      </div>
      
      <PaymentModal
        chargeData={paymentData}
        onClose={() => setPaymentData(null)}
      />
    </>
  );
}
```

### Exemplo Completo (com quantidade)

```jsx
function ProductPage({ product }) {
  const [quantity, setQuantity] = useState(1);
  const [paymentData, setPaymentData] = useState(null);
  const [loading, setLoading] = useState(false);
  
  const total = product.price * quantity;
  
  const handleCheckout = async () => {
    setLoading(true);
    try {
      const result = await api.products.createCharge(product.id, {
        quantity: quantity
      });
      
      setPaymentData(result);
    } catch (err) {
      if (err.message.includes('Insufficient stock')) {
        alert(`Estoque insuficiente! Disponível: ${product.stock.quantity}`);
      } else {
        alert(`Erro: ${err.message}`);
      }
    } finally {
      setLoading(false);
    }
  };
  
  return (
    <>
      <div>
        <h1>{product.name}</h1>
        <p>{product.description}</p>
        <p className="price">{product.price_formatted}</p>
        
        <div>
          <label>Quantidade:</label>
          <input
            type="number"
            min="1"
            max={product.stock.tracking ? product.stock.quantity : 999}
            value={quantity}
            onChange={(e) => setQuantity(parseInt(e.target.value) || 1)}
          />
        </div>
        
        <div>
          <p>Total: R$ {total.toFixed(2)}</p>
        </div>
        
        <button onClick={handleCheckout} disabled={loading}>
          {loading ? 'Processando...' : 'Finalizar Compra'}
        </button>
      </div>
      
      <PaymentModal
        chargeData={paymentData}
        onClose={() => setPaymentData(null)}
      />
    </>
  );
}
```

---

## 🛒 Exemplo E-commerce Completo

```jsx
function Checkout({ cart }) {
  const [paymentData, setPaymentData] = useState(null);
  
  const handleCheckout = async () => {
    // Se for apenas 1 produto, usar endpoint otimizado
    if (cart.items.length === 1) {
      const item = cart.items[0];
      
      const result = await api.products.createCharge(item.product_id, {
        quantity: item.quantity,
        external_id: `ORDER_${Date.now()}`
      });
      
      setPaymentData(result);
    }
    // Se múltiplos produtos, criar cobrança manual
    else {
      const total = cart.items.reduce((sum, item) => 
        sum + (item.price * item.quantity), 0
      );
      
      const result = await api.payments.createCharge({
        amount: total,
        description: `Pedido com ${cart.items.length} produtos`
      });
      
      // Adaptar formato
      setPaymentData({
        success: true,
        transaction: {
          ...result.transaction,
          amount_formatted: `R$ ${result.transaction.amount}`
        },
        payment: {
          qr_code_image: result.transaction.qr_code,
          qr_code_text: result.transaction.qr_code_text
        },
        product: {
          name: `${cart.items.length} produtos`,
          total_price_formatted: `R$ ${total.toFixed(2)}`
        },
        instructions: {
          title: "Como pagar",
          steps: [
            "Abra o app do seu banco",
            "Escolha Pix",
            "Escaneie o QR Code",
            "Confirme o pagamento"
          ]
        }
      });
    }
  };
  
  return (
    <>
      <button onClick={handleCheckout}>
        Pagar R$ {cart.total.toFixed(2)}
      </button>
      
      <PaymentModal chargeData={paymentData} onClose={() => setPaymentData(null)} />
    </>
  );
}
```

---

## 🎨 Componentes Incluídos

### PaymentModal (Pronto!)

```jsx
import PaymentModal from './components/PaymentModal';

<PaymentModal
  chargeData={chargeData}  // Dados do endpoint
  onClose={() => setPaymentData(null)}
/>
```

**Features**:
- ✅ Banner gradient bonito
- ✅ Info do produto
- ✅ Total em destaque
- ✅ QR Code grande
- ✅ Botão copiar PIX
- ✅ Instruções numeradas
- ✅ Validade
- ✅ Responsivo

---

## 🔧 Funções Utilitárias

### Copiar Código PIX

```javascript
const copyPixCode = async (code) => {
  try {
    await navigator.clipboard.writeText(code);
    alert('Código PIX copiado!');
  } catch (err) {
    alert('Erro ao copiar');
  }
};

// Usar:
<button onClick={() => copyPixCode(payment.qr_code_text)}>
  Copiar PIX
</button>
```

### Formatar Preço

```javascript
// Já vem formatado do backend!
product.price_formatted  // "R$ 197,00"
product.total_price_formatted  // "R$ 394,00"

// Se precisar formatar manualmente:
const formatPrice = (value) => {
  return new Intl.NumberFormat('pt-BR', {
    style: 'currency',
    currency: 'BRL'
  }).format(value);
};
```

### Download QR Code

```javascript
const downloadQRCode = (qrCodeBase64, filename = 'qrcode-pix.png') => {
  const link = document.createElement('a');
  link.href = qrCodeBase64;
  link.download = filename;
  link.click();
};

// Usar:
<button onClick={() => downloadQRCode(payment.qr_code_image)}>
  Baixar QR Code
</button>
```

---

## 📱 Exemplo Mobile-Friendly

```jsx
function MobileCheckout({ product }) {
  const [paymentData, setPaymentData] = useState(null);
  
  const handlePay = async () => {
    const result = await api.products.createCharge(product.id, { quantity: 1 });
    setPaymentData(result);
  };
  
  return (
    <div className="mobile-checkout">
      <div className="product-summary">
        <img src={product.image_url} alt={product.name} />
        <h2>{product.name}</h2>
        <p className="price">{product.price_formatted}</p>
      </div>
      
      <button
        onClick={handlePay}
        className="buy-button"
      >
        🛒 Pagar com PIX
      </button>
      
      {paymentData && (
        <div className="payment-sheet">
          {/* QR Code fullscreen no mobile */}
          <img
            src={paymentData.payment.qr_code_image}
            className="qr-code-large"
          />
          
          <button
            onClick={() => {
              navigator.clipboard.writeText(paymentData.payment.qr_code_text);
              alert('Código PIX copiado!');
            }}
          >
            📋 Copiar Código PIX
          </button>
          
          <div className="instructions">
            {paymentData.instructions.steps.map((step, i) => (
              <div key={i}>
                <span>{i + 1}.</span> {step}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
```

---

## 🎯 Vantagens da API Otimizada

### Antes (API genérica)
```javascript
const result = await api.payments.createCharge({
  amount: product.price * quantity,
  description: product.name
});

// Você precisa:
- Calcular total manualmente ❌
- Formatar preços manualmente ❌
- Criar instruções manualmente ❌
- Gerenciar estoque manualmente ❌
```

### Agora (API otimizada)
```javascript
const result = await api.products.createCharge(productId, {
  quantity: 2
});

// Você recebe TUDO pronto:
✅ Total calculado
✅ Preços formatados
✅ QR Code
✅ Instruções
✅ Estoque gerenciado automaticamente
✅ Transaction vinculada ao produto
```

---

## 🚀 API Methods Disponíveis

```javascript
import { api } from './api';

// Produtos
await api.products.list({ category: 'Cursos', page: 1 });
await api.products.get(productId);
await api.products.create(data);
await api.products.update(productId, data);
await api.products.delete(productId);

// Criar cobrança (OTIMIZADO!)
await api.products.createCharge(productId, {
  quantity: 2,
  expires_in_minutes: 60,
  external_id: 'ORDER_123'
});

// Categorias
await api.products.getCategories();  // Lista categorias
```

---

## ✅ Checklist de Integração

### Backend
- [x] Endpoint otimizado criado
- [x] Retorna dados formatados
- [x] Inclui QR Code e PIX
- [x] Calcula totais automaticamente
- [x] Gerencia estoque
- [x] Instruções incluídas

### Frontend
- [x] PaymentModal criado
- [x] API methods atualizados
- [x] Integração no Products.jsx
- [x] Copiar código PIX
- [x] Design profissional

### Features
- [x] 1 clique para gerar cobrança
- [x] Modal bonito de pagamento
- [x] QR Code grande
- [x] Instruções passo-a-passo
- [x] Responsivo

---

## 🎉 Resultado

Agora você tem um **endpoint perfeito** para o frontend:

**1 chamada de API** → **Tudo pronto** para exibir! 🚀

```javascript
// 1 linha de código:
const payment = await api.products.createCharge(productId, { quantity: 1 });

// Resultado: Tudo pronto!
payment.transaction.amount_formatted   // "R$ 197,00"
payment.payment.qr_code_image          // Base64 pronto
payment.product.total_price_formatted  // "R$ 197,00"
payment.instructions.steps             // Array pronto
```

**Zero processamento** no frontend - só exibir! ✅

---

**Documentação**: Frontend totalmente integrado e otimizado! 🎨
