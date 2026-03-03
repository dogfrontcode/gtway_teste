import { useState } from 'react';

export default function PaymentModal({ chargeData, onClose }) {
  const [copied, setCopied] = useState(false);

  if (!chargeData) return null;

  const { transaction, payment, product, instructions } = chargeData;

  const copyToClipboard = async () => {
    try {
      await navigator.clipboard.writeText(payment.qr_code_text);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      alert('Erro ao copiar código PIX');
    }
  };

  return (
    <div className="fixed inset-0 bg-black/80 flex items-center justify-center z-50 p-4">
      <div className="bg-slate-800 rounded-2xl shadow-2xl max-w-lg w-full max-h-[90vh] overflow-y-auto border border-emerald-500/30">
        <div className="sticky top-0 bg-gradient-to-r from-emerald-600 to-emerald-500 p-6">
          <div className="flex justify-between items-center">
            <h2 className="text-2xl font-bold text-white">💳 Pagamento PIX</h2>
            <button
              onClick={onClose}
              className="text-white/80 hover:text-white transition text-2xl"
              type="button"
            >
              ✕
            </button>
          </div>
          <p className="text-emerald-100 text-sm mt-2">
            Cobrança criada com sucesso!
          </p>
        </div>

        <div className="p-6 space-y-6">
          {/* Produto Info */}
          <div className="p-4 rounded-xl bg-slate-900 border border-slate-700">
            <p className="text-slate-400 text-sm mb-1">Produto</p>
            <p className="text-white font-semibold text-lg">{product.name}</p>
            {product.quantity > 1 && (
              <p className="text-slate-400 text-sm mt-1">
                {product.unit_price_formatted} × {product.quantity} unidades
              </p>
            )}
          </div>

          {/* Total */}
          <div className="p-6 rounded-xl bg-gradient-to-br from-emerald-500/20 to-emerald-600/10 border-2 border-emerald-500/50">
            <p className="text-emerald-300 text-sm mb-1">Total a pagar</p>
            <p className="text-4xl font-bold text-emerald-400">
              {product.total_price_formatted}
            </p>
            <p className="text-emerald-200 text-sm mt-1">
              TxID: {transaction.txid}
            </p>
          </div>

          {/* QR Code */}
          <div className="text-center">
            <p className="text-slate-300 font-medium mb-4">Escaneie o QR Code</p>
            {payment.qr_code_image && (
              <div className="inline-block p-4 bg-white rounded-xl">
                <img
                  src={payment.qr_code_image}
                  alt="QR Code PIX"
                  className="w-64 h-64 mx-auto"
                />
              </div>
            )}
          </div>

          {/* Pix Copia e Cola */}
          <div>
            <p className="text-slate-300 text-sm font-medium mb-2">
              Ou copie o código PIX
            </p>
            <div className="flex gap-2">
              <input
                type="text"
                value={payment.qr_code_text}
                readOnly
                className="flex-1 px-4 py-3 rounded-lg bg-slate-900 border border-slate-600 text-slate-300 text-sm font-mono"
              />
              <button
                onClick={copyToClipboard}
                className="px-6 py-3 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white font-medium transition"
              >
                {copied ? '✓ Copiado!' : 'Copiar'}
              </button>
            </div>
          </div>

          {/* Instruções */}
          <div className="p-4 rounded-xl bg-slate-900 border border-slate-700">
            <p className="text-white font-semibold mb-3">{instructions.title}</p>
            <ol className="space-y-2">
              {instructions.steps.map((step, idx) => (
                <li key={idx} className="flex items-start gap-3 text-sm text-slate-300">
                  <span className="flex-shrink-0 w-6 h-6 rounded-full bg-emerald-500/20 text-emerald-400 flex items-center justify-center text-xs font-bold">
                    {idx + 1}
                  </span>
                  {step}
                </li>
              ))}
            </ol>
          </div>

          {/* Validade */}
          {transaction.expires_at && (
            <div className="text-center text-sm text-slate-400">
              Válido até: {new Date(transaction.expires_at).toLocaleString('pt-BR')}
            </div>
          )}

          {/* Fechar */}
          <button
            onClick={onClose}
            className="w-full px-4 py-3 rounded-lg bg-slate-700 hover:bg-slate-600 text-white font-medium transition"
          >
            Fechar
          </button>
        </div>
      </div>
    </div>
  );
}
