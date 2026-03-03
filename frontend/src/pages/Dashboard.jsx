import { useState, useEffect } from 'react';
import { api } from '../api';

export default function Dashboard() {
  const [transactions, setTransactions] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [creating, setCreating] = useState(false);
  const [amount, setAmount] = useState('');
  const [description, setDescription] = useState('');
  const [error, setError] = useState('');

  const load = async () => {
    setLoading(true);
    try {
      const [txRes, statsRes] = await Promise.all([
        api.payments.listTransactions(),
        api.payments.getStatistics(),
      ]);
      setTransactions(txRes.transactions || []);
      setStats(statsRes.statistics || {});
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
  }, []);

  const handleCreateCharge = async (e) => {
    e.preventDefault();
    const val = parseFloat(amount);
    if (!val || val <= 0) return setError('Informe um valor válido');
    setCreating(true);
    setError('');
    try {
      await api.payments.createCharge({
        amount: val,
        description: description || undefined,
      });
      setAmount('');
      setDescription('');
      load();
    } catch (err) {
      setError(err.message);
    } finally {
      setCreating(false);
    }
  };

  const statusClass = (s) => {
    const m = {
      pending: 'bg-yellow-500/20 text-yellow-400',
      paid: 'bg-green-500/20 text-green-400',
      expired: 'bg-slate-500/20 text-slate-400',
      cancelled: 'bg-red-500/20 text-red-400',
      refunded: 'bg-orange-500/20 text-orange-400',
    };
    return m[s] || 'bg-slate-500/20 text-slate-400';
  };

  return (
    <div className="max-w-5xl mx-auto space-y-8">
      <h1 className="text-2xl font-bold text-slate-100">Dashboard</h1>

      {stats && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="p-4 rounded-xl bg-slate-800/50 border border-slate-700">
            <p className="text-slate-400 text-sm">Total</p>
            <p className="text-xl font-semibold text-white">{stats.total_transactions ?? 0}</p>
            <p className="text-slate-500 text-xs">transações</p>
          </div>
          <div className="p-4 rounded-xl bg-slate-800/50 border border-slate-700">
            <p className="text-slate-400 text-sm">Pendentes</p>
            <p className="text-xl font-semibold text-yellow-400">{stats.pending_transactions ?? 0}</p>
          </div>
          <div className="p-4 rounded-xl bg-slate-800/50 border border-slate-700">
            <p className="text-slate-400 text-sm">Pagas</p>
            <p className="text-xl font-semibold text-green-400">{stats.paid_transactions ?? 0}</p>
          </div>
          <div className="p-4 rounded-xl bg-slate-800/50 border border-slate-700">
            <p className="text-slate-400 text-sm">Total Recebido</p>
            <p className="text-xl font-semibold text-emerald-400">
              R$ {(stats.total_amount ?? 0).toLocaleString('pt-BR')}
            </p>
          </div>
        </div>
      )}

      <div className="p-6 rounded-xl bg-slate-800/50 border border-slate-700">
        <h2 className="text-lg font-semibold text-slate-200 mb-4">Nova cobrança PIX</h2>
        {error && (
          <div className="mb-4 p-3 rounded-lg bg-red-500/20 border border-red-500/50 text-red-400 text-sm">
            {error}
          </div>
        )}
        <form onSubmit={handleCreateCharge} className="flex flex-col sm:flex-row gap-4">
          <input
            type="number"
            step="0.01"
            min="0.01"
            placeholder="Valor (R$)"
            value={amount}
            onChange={(e) => setAmount(e.target.value)}
            className="px-4 py-2 rounded-lg bg-slate-900 border border-slate-600 text-white w-full sm:w-40"
          />
          <input
            type="text"
            placeholder="Descrição"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            className="flex-1 px-4 py-2 rounded-lg bg-slate-900 border border-slate-600 text-white"
          />
          <button
            type="submit"
            disabled={creating}
            className="px-6 py-2 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white font-medium transition disabled:opacity-50"
          >
            {creating ? 'Criando...' : 'Criar cobrança'}
          </button>
        </form>
      </div>

      <div className="rounded-xl bg-slate-800/50 border border-slate-700 overflow-hidden">
        <h2 className="text-lg font-semibold text-slate-200 p-4 border-b border-slate-700">Transações</h2>
        {loading ? (
          <div className="p-8 text-center text-slate-400">Carregando...</div>
        ) : transactions.length === 0 ? (
          <div className="p-8 text-center text-slate-500">Nenhuma transação ainda</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-slate-700">
                  <th className="text-left p-4 text-slate-400 font-medium">ID</th>
                  <th className="text-left p-4 text-slate-400 font-medium">Valor</th>
                  <th className="text-left p-4 text-slate-400 font-medium">Status</th>
                  <th className="text-left p-4 text-slate-400 font-medium">Descrição</th>
                  <th className="text-left p-4 text-slate-400 font-medium">Data</th>
                </tr>
              </thead>
              <tbody>
                {transactions.map((t) => (
                  <tr key={t.id} className="border-b border-slate-700/50 hover:bg-slate-800/50">
                    <td className="p-4 font-mono text-slate-300">{t.txid}</td>
                    <td className="p-4 font-semibold text-white">R$ {t.amount}</td>
                    <td className="p-4">
                      <span
                        className={`inline-flex px-2 py-0.5 rounded text-xs font-medium ${statusClass(t.status)}`}
                      >
                        {t.status}
                      </span>
                    </td>
                    <td className="p-4 text-slate-400">{t.description || '-'}</td>
                    <td className="p-4 text-slate-500">
                      {t.created_at ? new Date(t.created_at).toLocaleString('pt-BR') : '-'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
