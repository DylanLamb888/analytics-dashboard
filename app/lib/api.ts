import axios from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add auth token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('auth_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Handle auth errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('auth_token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export const authApi = {
  login: async (email: string, password: string) => {
    const response = await api.post('/api/auth/login', { email, password });
    return response.data;
  },

  logout: async () => {
    try {
      await api.post('/api/auth/logout');
    } catch (error) {
      // Continue with logout even if API call fails
      console.error('Logout API call failed:', error);
    }
  },
};

export const uploadApi = {
  uploadCsv: async (file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await api.post('/api/upload/csv', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },
};

export const ordersApi = {
  getOrders: async (params: {
    start_date?: string;
    end_date?: string;
    state?: string;
    item_sku?: string;
    limit?: number;
    offset?: number;
  }) => {
    const response = await api.get('/api/orders', { params });
    return response.data;
  },
};

export const metricsApi = {
  getDashboardMetrics: async (params: {
    start_date?: string;
    end_date?: string;
  }) => {
    const response = await api.get('/api/metrics/dashboard', { params });
    return response.data;
  },
};

export const exportApi = {
  exportToExcel: async (params: {
    start_date?: string;
    end_date?: string;
    state?: string;
    item_sku?: string;
  }) => {
    const response = await api.get('/api/export/excel', {
      params,
      responseType: 'blob',
    });
    
    // Create download link
    const url = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', `order_analytics_${new Date().toISOString().split('T')[0]}.xlsx`);
    document.body.appendChild(link);
    link.click();
    link.remove();
    window.URL.revokeObjectURL(url);
  },
};

export default api;