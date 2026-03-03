import { useState, useEffect } from 'react';
import { Navigate } from 'react-router-dom';
import { api } from '../api';
import { useAuth } from '../AuthContext';
import CreateProductModal from '../components/CreateProductModal';
import PaymentModal from '../components/PaymentModal';

export default function Products() {
  const { user } = useAuth();
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [selectedProduct, setSelectedProduct] = useState(null);
  const [showChargeModal, setShowChargeModal] = useState(false);
  const [showPaymentModal, setShowPaymentModal] = useState(false);
  const [paymentData, setPaymentData] = useState(null);
  const [chargeQuantity, setChargeQuantity] = useState(1);
  const [categoryFilter, setCategoryFilter] = useState('');
  const [page, setPage] = useState(1);
  const [total, setTotal] = useState(0);

  const loadProducts = async () => {
    setLoading(true);
    try {
      const params = { page, per_page: 12 };
      if (categoryFilter) params.category = categoryFilter;
      const data = await api.products.list(params);
      setProducts(data.products || []);
      setTotal(data.total || 0);
    } catch (err) {
      console.error('Erro ao carregar produtos:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadProducts();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [page, categoryFilter]);

  const handleCreateProduct = async (data) => {
    try {
      const result = await api.products.create(data);
      // Adicionar à lista sem recarregar tudo
      setProducts(prev => [result.product, ...prev]);
      setTotal(prev => prev + 1);
    } catch (err) {
      alert(`Erro: ${err.message}`);
      loadProducts();
    }
  };

  const handleCreateCharge = async (product) => {
    setSelectedProduct(product);
    setChargeQuantity(1);
    setShowChargeModal(true);
  };

  const handleConfirmCharge = async () => {
    try {
      const result = await api.products.createCharge(selectedProduct.id, {
        quantity: chargeQuantity,
      });
      
      // Fechar modal de quantidade e abrir modal de pagamento
      setShowChargeModal(false);
      setPaymentData(result);
      setShowPaymentModal(true);
      
      // Atualizar estoque do produto na lista (se tracking)
      if (selectedProduct.stock?.tracking) {
        setProducts(prev => prev.map(p => 
          p.id === selectedProduct.id
            ? { ...p, stock: { ...p.stock, quantity: (p.stock.quantity || 0) - chargeQuantity } }
            : p
        ));
      }
    } catch (err) {
      alert(`Erro ao criar cobrança: ${err.message}`);
    }
  };

  const handleClosePayment = () => {
    setShowPaymentModal(false);
    setPaymentData(null);
    setSelectedProduct(null);
  };

  const handleDeleteProduct = async (product) => {
    if (!confirm(`Deseja realmente deletar "${product.name}"?`)) return;
    
    const productId = product.id;
    const productName = product.name;
    
    try {
      console.log('Deletando produto:', productId, productName);
      
      // Remover da lista ANTES da requisição (UI otimista)
      setProducts(prev => prev.filter(p => p.id !== productId));
      setTotal(prev => Math.max(0, prev - 1));
      
      // Fazer a requisição
      await api.products.delete(productId);
      
      console.log('Produto deletado com sucesso no backend!');
      
      // Mostrar feedback
      alert(`✓ Produto "${productName}" deletado com sucesso!`);
      
    } catch (err) {
      console.error('Erro ao deletar:', err);
      alert(`Erro ao deletar produto: ${err.message}`);
      // Recarregar em caso de erro para restaurar estado correto
      loadProducts();
    }
  };

  if (!user) return <Navigate to="/" replace />;

  const categories = [...new Set(products.map(p => p.category).filter(Boolean))];

  return (
    <div className="max-w-7xl mx-auto space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold text-slate-100">Produtos</h1>
        <button
          onClick={() => setShowCreateModal(true)}
          className="px-4 py-2 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white font-medium transition flex items-center gap-2"
        >
          <span className="text-lg">+</span>
          Criar Produto
        </button>
      </div>

      {categories.length > 0 && (
        <div className="flex gap-2 items-center">
          <span className="text-sm text-slate-400">Categoria:</span>
          <button
            onClick={() => { setCategoryFilter(''); setPage(1); }}
            className={`px-3 py-1 rounded-lg text-sm transition ${
              categoryFilter === '' 
                ? 'bg-emerald-600 text-white' 
                : 'bg-slate-800 text-slate-400 hover:text-white'
            }`}
          >
            Todas
          </button>
          {categories.map((cat) => (
            <button
              key={cat}
              onClick={() => { setCategoryFilter(cat); setPage(1); }}
              className={`px-3 py-1 rounded-lg text-sm transition ${
                categoryFilter === cat 
                  ? 'bg-emerald-600 text-white' 
                  : 'bg-slate-800 text-slate-400 hover:text-white'
              }`}
            >
              {cat}
            </button>
          ))}
        </div>
      )}

      {loading ? (
        <div className="flex items-center justify-center h-64 text-slate-400">
          Carregando produtos...
        </div>
      ) : products.length === 0 ? (
        <div className="text-center py-16 text-slate-400">
          <p className="text-lg mb-2">Nenhum produto cadastrado</p>
          <p className="text-sm">Clique em "Criar Produto" para começar</p>
        </div>
      ) : (
        <>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {products.map((product) => (
              <div
                key={product.id}
                className="rounded-xl bg-slate-800/50 border border-slate-700 overflow-hidden hover:border-emerald-500/50 transition"
              >
                {product.image_url && (
                  <div className="h-48 bg-slate-900 overflow-hidden">
                    <img
                      src={product.image_url}
                      alt={product.name}
                      className="w-full h-full object-cover"
                      onError={(e) => {
                        e.target.style.display = 'none';
                      }}
                    />
                  </div>
                )}
                
                <div className="p-4 space-y-3">
                  <div>
                    <h3 className="text-lg font-semibold text-white mb-1">
                      {product.name}
                    </h3>
                    {product.category && (
                      <span className="inline-flex px-2 py-0.5 rounded text-xs bg-slate-700 text-slate-300">
                        {product.category}
                      </span>
                    )}
                  </div>

                  {product.description && (
                    <p className="text-sm text-slate-400 line-clamp-2">
                      {product.description}
                    </p>
                  )}

                  <div className="flex items-baseline gap-2">
                    <span className="text-2xl font-bold text-emerald-400">
                      R$ {product.price}
                    </span>
                    {product.sku && (
                      <span className="text-xs text-slate-500 font-mono">
                        {product.sku}
                      </span>
                    )}
                  </div>

                  {product.track_stock && (
                    <div className="text-sm text-slate-400">
                      Estoque: <span className="font-semibold text-white">{product.stock_quantity || 0}</span>
                    </div>
                  )}

                  <div className="flex gap-2 pt-2">
                    <button
                      onClick={() => handleCreateCharge(product)}
                      className="flex-1 px-4 py-2 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white text-sm font-medium transition"
                    >
                      Criar Cobrança
                    </button>
                    <button
                      onClick={() => handleDeleteProduct(product)}
                      className="px-4 py-2 rounded-lg bg-red-600/20 hover:bg-red-600/30 text-red-400 text-sm font-medium transition"
                    >
                      🗑️
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>

          {total > 12 && (
            <div className="flex justify-center items-center gap-4 pt-4">
              <button
                onClick={() => setPage((p) => Math.max(1, p - 1))}
                disabled={page <= 1}
                className="px-4 py-2 rounded-lg bg-slate-700 hover:bg-slate-600 disabled:opacity-50 disabled:cursor-not-allowed text-white transition"
              >
                Anterior
              </button>
              <span className="text-slate-400 text-sm">
                Página {page} de {Math.ceil(total / 12)}
              </span>
              <button
                onClick={() => setPage((p) => p + 1)}
                disabled={page * 12 >= total}
                className="px-4 py-2 rounded-lg bg-slate-700 hover:bg-slate-600 disabled:opacity-50 disabled:cursor-not-allowed text-white transition"
              >
                Próxima
              </button>
            </div>
          )}
        </>
      )}

      <CreateProductModal
        isOpen={showCreateModal}
        onClose={() => setShowCreateModal(false)}
        onSuccess={handleCreateProduct}
      />

      {showChargeModal && selectedProduct && (
        <div className="fixed inset-0 bg-black/60 flex items-center justify-center z-50 p-4">
          <div className="bg-slate-800 rounded-xl shadow-2xl max-w-md w-full border border-slate-700 p-6 space-y-4">
            <h2 className="text-xl font-bold text-white">Criar Cobrança</h2>
            
            <div className="p-4 rounded-lg bg-slate-900 space-y-2">
              <p className="text-slate-300 font-semibold">{selectedProduct.name}</p>
              <p className="text-sm text-slate-400">{selectedProduct.description}</p>
              <p className="text-lg font-bold text-emerald-400">
                R$ {selectedProduct.price}
              </p>
            </div>

            <div>
              <label className="block text-sm font-medium text-slate-300 mb-2">
                Quantidade
              </label>
              <input
                type="number"
                min="1"
                value={chargeQuantity}
                onChange={(e) => setChargeQuantity(parseInt(e.target.value) || 1)}
                className="w-full px-4 py-2 rounded-lg bg-slate-900 border border-slate-600 text-white focus:border-emerald-500 outline-none"
              />
            </div>

              <div className="p-4 rounded-lg bg-emerald-600/10 border border-emerald-600/30">
              <p className="text-sm text-slate-300">Total:</p>
              <p className="text-2xl font-bold text-emerald-400">
                {typeof selectedProduct.price === 'number' 
                  ? `R$ ${(selectedProduct.price * chargeQuantity).toFixed(2)}`
                  : selectedProduct.price_formatted
                }
              </p>
            </div>

            <div className="flex gap-3">
              <button
                onClick={() => {
                  setShowChargeModal(false);
                  setSelectedProduct(null);
                }}
                className="flex-1 px-4 py-2 rounded-lg bg-slate-700 hover:bg-slate-600 text-white font-medium transition"
              >
                Cancelar
              </button>
              <button
                onClick={handleConfirmCharge}
                className="flex-1 px-4 py-2 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white font-medium transition"
              >
                Confirmar
              </button>
            </div>
          </div>
        </div>
      )}

      <PaymentModal
        chargeData={paymentData}
        onClose={handleClosePayment}
      />
    </div>
  );
}
