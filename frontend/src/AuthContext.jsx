import { createContext, useContext, useState, useEffect } from 'react';
import { api, getToken } from './api';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [activeTenant, setActiveTenant] = useState(null);
  const [loading, setLoading] = useState(true);

  const login = async (email, password) => {
    const data = await api.auth.login(email, password);
    localStorage.setItem('access_token', data.access_token);
    if (data.refresh_token) localStorage.setItem('refresh_token', data.refresh_token);
    setUser(data.user);
    setActiveTenant(data.user?.tenant_id ? { id: data.user.tenant_id } : null);  // tenant users
    return data.user;
  };

  const logout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    setUser(null);
    setActiveTenant(null);
  };

  const switchTenant = async (tenantId) => {
    const data = await api.auth.switchTenant(tenantId);
    localStorage.setItem('access_token', data.access_token);
    setActiveTenant(data.tenant || (data.tenant_id ? { id: data.tenant_id } : null));
    return data;
  };

  const refreshUser = async () => {
    if (!getToken()) return setLoading(false);
    try {
      const data = await api.auth.me();
      setUser(data.user);
      setActiveTenant(data.active_tenant || null);
    } catch {
      logout();
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    refreshUser();
  }, []);

  const isAdmin = user?.role === 'admin';

  return (
    <AuthContext.Provider value={{ user, activeTenant, loading, login, logout, refreshUser, switchTenant, isAdmin }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used within AuthProvider');
  return ctx;
}
