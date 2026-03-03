import { useState, useEffect } from 'react';
import { useAuth } from '../AuthContext';
import { api } from '../api';

/**
 * Seletor de tenant para admin - permite trocar de conta PJ em produção.
 */
export default function TenantSwitcher() {
  const { isAdmin, activeTenant, switchTenant } = useAuth();
  const [tenants, setTenants] = useState([]);
  const [loading, setLoading] = useState(false);
  const [open, setOpen] = useState(false);

  useEffect(() => {
    if (isAdmin) {
      api.tenants.list(1, 100).then((d) => setTenants(d.tenants || []));
    }
  }, [isAdmin]);

  if (!isAdmin) return null;

  const handleSwitch = async (tenantId) => {
    setLoading(true);
    try {
      await switchTenant(tenantId);
      setOpen(false);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="relative">
      <button
        onClick={() => setOpen(!open)}
        className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 text-sm transition"
      >
        <span className="max-w-[140px] truncate">
          {activeTenant?.name || 'Selecionar conta'}
        </span>
        <span className="text-slate-500">▾</span>
      </button>
      {open && (
        <div className="absolute right-0 top-full mt-1 py-1 rounded-lg bg-slate-800 border border-slate-700 shadow-xl z-50 min-w-[200px]">
          <button
            onClick={() => handleSwitch(null)}
            disabled={loading}
            className="w-full text-left px-4 py-2 text-sm text-slate-400 hover:bg-slate-700 hover:text-white"
          >
            — Admin (global)
          </button>
          {tenants.map((t) => (
            <button
              key={t.id}
              onClick={() => handleSwitch(t.id)}
              disabled={loading}
              className={`w-full text-left px-4 py-2 text-sm hover:bg-slate-700 ${
                activeTenant?.id === t.id ? 'text-emerald-400 bg-slate-700/50' : 'text-slate-300'
              }`}
            >
              {t.name}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
