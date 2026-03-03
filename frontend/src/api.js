const API_BASE = '/api/v1';

function getToken() {
  return localStorage.getItem('access_token');
}

function getHeaders(includeAuth = true) {
  const headers = {
    'Content-Type': 'application/json',
  };
  if (includeAuth) {
    const token = getToken();
    if (token) headers['Authorization'] = `Bearer ${token}`;
  }
  return headers;
}

async function request(url, options = {}) {
  const res = await fetch(`${API_BASE}${url}`, {
    ...options,
    headers: { ...getHeaders(options.auth !== false), ...options.headers },
  });
  const data = res.ok ? await res.json().catch(() => ({})) : await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(data.error || data.details || `HTTP ${res.status}`);
  return data;
}

export const api = {
  auth: {
    login: (email, password) => request('/auth/login', {
      method: 'POST',
      auth: false,
      body: JSON.stringify({ email, password }),
    }),
    me: () => request('/auth/me'),
    switchTenant: (tenantId) => request('/auth/switch-tenant', {
      method: 'POST',
      body: JSON.stringify({ tenant_id: tenantId }),
    }),
  },
  tenants: {
    list: (page = 1, perPage = 20) => request(`/tenants?page=${page}&per_page=${perPage}`),
    get: (id) => request(`/tenants/${id}`),
    create: (data) => request('/tenants', {
      method: 'POST',
      body: JSON.stringify(data),
    }),
    update: (id, data) => request(`/tenants/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    }),
    delete: (id) => request(`/tenants/${id}`, { method: 'DELETE' }),
  },
  payments: {
    createCharge: (data) => request('/payments/charge', {
      method: 'POST',
      body: JSON.stringify(data),
    }),
    listTransactions: (params = {}) => {
      const q = new URLSearchParams(params).toString();
      return request(`/payments/transactions${q ? '?' + q : ''}`);
    },
    getTransaction: (id) => request(`/payments/transactions/${id}`),
    cancelTransaction: (id) => request(`/payments/transactions/${id}/cancel`, { method: 'POST' }),
    getStatistics: (params = {}) => {
      const q = new URLSearchParams(params).toString();
      return request(`/payments/statistics${q ? '?' + q : ''}`);
    },
  },
  admin: {
    getDashboard: () => request('/admin/dashboard'),
    listTransactions: (params = {}) => {
      const q = new URLSearchParams(params).toString();
      return request(`/admin/transactions${q ? '?' + q : ''}`);
    },
  },
  products: {
    create: (data) => request('/products', {
      method: 'POST',
      body: JSON.stringify(data),
    }),
    list: (params = {}) => {
      const q = new URLSearchParams(params).toString();
      return request(`/products${q ? '?' + q : ''}`);
    },
    get: (id) => request(`/products/${id}`),
    update: (id, data) => request(`/products/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    }),
    delete: (id) => request(`/products/${id}`, { method: 'DELETE' }),
    getCategories: () => request('/products/categories'),
    createCharge: (id, data = {}) => request(`/products/${id}/charge`, {
      method: 'POST',
      body: JSON.stringify(data),
    }),
  },
};

export { getToken };
