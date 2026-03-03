import { useState, useEffect } from 'react';
import { Navigate } from 'react-router-dom';
import { api } from '../api';
import { useAuth } from '../AuthContext';
import CreateTenantModal from '../components/CreateTenantModal';

export default function Admin() {
  const { isAdmin } = useAuth();
  const [dashboard, setDashboard] = useState(null);
  const [transactions, setTransactions] = useState([]);
  const [tenants, setTenants] = useState([]);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);
  const [statusFilter, setStatusFilter] = useState('');
  const [tenantFilter, setTenantFilter] = useState('');
  const [total, setTotal] = useState(0);
  const [activeTab, setActiveTab] = useState('transactions');
  const [showCreateModal, setShowCreateModal] = useState(false);

  const loadDashboard = async () => {
    const data = await api.admin.getDashboard();
    setDashboard(data);
  };

  const loadTransactions = async () => {
    const params = { page };
    if (statusFilter) params.status = statusFilter;
    if (tenantFilter) params.tenant_id = tenantFilter;
    const data = await api.admin.listTransactions(params);
    setTransactions(data.transactions || []);
    setTotal(data.total || 0);
  };

  const loadTenants = async () => {
    const data = await api.tenants.list(1, 100);
    setTenants(data.tenants || []);
  };

  const handleCreateTenant = async (data) => {
    await api.tenants.create(data);
    await loadTenants();
    await loadDashboard();
  };

  useEffect(() => {
    const run = async () => {
      setLoading(true);
      try {
        await loadDashboard();
        await loadTenants();
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    run();
  }, []);

  useEffect(() => {
    if (activeTab === 'transactions') loadTransactions();
  }, [activeTab, page, statusFilter, tenantFilter]);

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

  if (!isAdmin) return <Navigate to="/" replace />;

  if (loading || !dashboard) {
    return (
      <div className="flex items-center justify-center h-64 text-slate-400">
        Carregando...
      </div>
    );
  }

  const { tenants: tStats, transactions: txStats, webhooks } = dashboard;

  return (
    <div className="max-w-6xl mx-auto space-y-8">
      <h1 className="text-2xl font-bold text-slate-100">Painel Admin</h1>

      <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4">
        <div className="p-4 rounded-xl bg-slate-800/50 border border-slate-700">
          <p className="text-slate-400 text-sm">Tenants</p>
          <p className="text-2xl font-bold text-white">{tStats?.total ?? 0}</p>
          <p className="text-slate-500 text-xs">ativos: {tStats?.active ?? 0}</p>
        </div>
        <div className="p-4 rounded-xl bg-slate-800/50 border border-slate-700">
          <p className="text-slate-400 text-sm">Transações</p>
          <p className="text-2xl font-bold text-white">{txStats?.total ?? 0}</p>
          <p className="text-slate-500 text-xs">hoje: {txStats?.today ?? 0}</p>
        </div>
        <div className="p-4 rounded-xl bg-slate-800/50 border border-slate-700">
          <p className="text-slate-400 text-sm">Pagas</p>
          <p className="text-2xl font-bold text-green-400">{txStats?.paid ?? 0}</p>
        </div>
        <div className="p-4 rounded-xl bg-slate-800/50 border border-slate-700">
          <p className="text-slate-400 text-sm">Pendentes</p>
          <p className="text-2xl font-bold text-yellow-400">{txStats?.pending ?? 0}</p>
        </div>
        <div className="p-4 rounded-xl bg-slate-800/50 border border-slate-700">
          <p className="text-slate-400 text-sm">Volume</p>
          <p className="text-xl font-bold text-emerald-400">
            R$ {(txStats?.total_amount ?? 0).toLocaleString('pt-BR')}
          </p>
        </div>
        <div className="p-4 rounded-xl bg-slate-800/50 border border-slate-700">
          <p className="text-slate-400 text-sm">Webhooks</p>
          <p className="text-2xl font-bold text-white">{webhooks?.total_attempts ?? 0}</p>
          <p className="text-slate-500 text-xs">taxa: {Math.round(webhooks?.success_rate ?? 0)}%</p>
        </div>
      </div>

      <div className="flex gap-2 border-b border-slate-700">
        <button
          onClick={() => setActiveTab('transactions')}
          className={`px-4 py-2 text-sm font-medium rounded-t-lg transition ${
            activeTab === 'transactions'
              ? 'bg-slate-800 text-emerald-400 border border-slate-700 border-b-0'
              : 'text-slate-400 hover:text-white'
          }`}
        >
          Transações
        </button>
        <button
          onClick={() => setActiveTab('tenants')}
          className={`px-4 py-2 text-sm font-medium rounded-t-lg transition ${
            activeTab === 'tenants'
              ? 'bg-slate-800 text-emerald-400 border border-slate-700 border-b-0'
              : 'text-slate-400 hover:text-white'
          }`}
        >
          Tenants
        </button>
      </div>

      {activeTab === 'tenants' && (
        <div className="rounded-xl bg-slate-800/50 border border-slate-700 overflow-hidden">
          <div className="p-4 border-b border-slate-700 flex justify-between items-center">
            <h2 className="text-lg font-semibold text-slate-200">Tenants</h2>
            <button
              onClick={() => setShowCreateModal(true)}
              className="px-4 py-2 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white font-medium transition flex items-center gap-2"
            >
              <span className="text-lg">+</span>
              Criar Tenant
            </button>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-slate-700">
                  <th className="text-left p-4 text-slate-400 font-medium">Nome</th>
                  <th className="text-left p-4 text-slate-400 font-medium">Email</th>
                  <th className="text-left p-4 text-slate-400 font-medium">Slug</th>
                  <th className="text-left p-4 text-slate-400 font-medium">Status</th>
                </tr>
              </thead>
              <tbody>
                {tenants.map((t) => (
                  <tr key={t.id} className="border-b border-slate-700/50 hover:bg-slate-800/50">
                    <td className="p-4 text-white">{t.name}</td>
                    <td className="p-4 text-slate-400">{t.email}</td>
                    <td className="p-4 font-mono text-slate-300">{t.slug}</td>
                    <td className="p-4">
                      <span
                        className={`inline-flex px-2 py-0.5 rounded text-xs ${
                          t.is_active ? 'bg-green-500/20 text-green-400' : 'bg-red-500/20 text-red-400'
                        }`}
                      >
                        {t.is_active ? 'Ativo' : 'Inativo'}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {activeTab === 'transactions' && (
        <>
          <div className="flex flex-wrap gap-4 mb-4">
            <select
              value={statusFilter}
              onChange={(e) => { setStatusFilter(e.target.value); setPage(1); }}
              className="px-3 py-2 rounded-lg bg-slate-800 border border-slate-600 text-white text-sm"
            >
              <option value="">Todos os status</option>
              <option value="pending">Pendente</option>
              <option value="paid">Pago</option>
              <option value="expired">Expirado</option>
              <option value="cancelled">Cancelado</option>
            </select>
            <select
              value={tenantFilter}
              onChange={(e) => { setTenantFilter(e.target.value); setPage(1); }}
              className="px-3 py-2 rounded-lg bg-slate-800 border border-slate-600 text-white text-sm"
            >
              <option value="">Todos os tenants</option>
              {tenants.map((t) => (
                <option key={t.id} value={t.id}>{t.name}</option>
              ))}
            </select>
          </div>
          <div className="rounded-xl bg-slate-800/50 border border-slate-700 overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-slate-700">
                    <th className="text-left p-4 text-slate-400 font-medium">TxID</th>
                    <th className="text-left p-4 text-slate-400 font-medium">Tenant</th>
                    <th className="text-left p-4 text-slate-400 font-medium">Valor</th>
                    <th className="text-left p-4 text-slate-400 font-medium">Status</th>
                    <th className="text-left p-4 text-slate-400 font-medium">Descrição</th>
                    <th className="text-left p-4 text-slate-400 font-medium">Data</th>
                  </tr>
                </thead>
                <tbody>
                  {transactions.map((t) => {
                    const tenant = tenants.find((tn) => tn.id === t.tenant_id);
                    return (
                    <tr key={t.id} className="border-b border-slate-700/50 hover:bg-slate-800/50">
                      <td className="p-4 font-mono text-slate-300">{t.txid}</td>
                      <td className="p-4 text-slate-400">{tenant?.name ?? t.tenant_id?.slice(0, 8) + '...'}</td>
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
                  );})}
                </tbody>
              </table>
            </div>
            {total > 20 && (
              <div className="p-4 border-t border-slate-700 flex justify-between items-center">
                <span className="text-slate-500 text-sm">{total} transações</span>
                <div className="flex gap-2">
                  <button
                    onClick={() => setPage((p) => Math.max(1, p - 1))}
                    disabled={page <= 1}
                    className="px-3 py-1 rounded bg-slate-700 hover:bg-slate-600 disabled:opacity-50 text-sm"
                  >
                    Anterior
                  </button>
                  <button
                    onClick={() => setPage((p) => p + 1)}
                    disabled={page * 20 >= total}
                    className="px-3 py-1 rounded bg-slate-700 hover:bg-slate-600 disabled:opacity-50 text-sm"
                  >
                    Próxima
                  </button>
                </div>
              </div>
            )}
          </div>
        </>
      )}

      <CreateTenantModal
        isOpen={showCreateModal}
        onClose={() => setShowCreateModal(false)}
        onSuccess={handleCreateTenant}
      />
    </div>
  );
}
