import axios from 'axios';

const NODE_API_URL = import.meta.env.VITE_NODE_API_URL || 'http://localhost:5001';
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
const API_PREFIX = '/api/v1';

console.log('API Configuration:', {
    NODE_API_URL,
    API_BASE_URL,
    API_PREFIX
});

// Maintain getApiUrl for compatibility
export const getApiUrl = (endpoint = '', useNode = false) => {
    const base = useNode ? NODE_API_URL : API_BASE_URL;
    return `${base}${API_PREFIX}${endpoint ? `/${endpoint}` : ''}`;
};

// Auth API instance
export const authApi = axios.create({
    baseURL: `${NODE_API_URL}${API_PREFIX}`,
    timeout: 30000,
    headers: {
        'Content-Type': 'application/json'
    }
});

// FastAPI instance
export const iaApi = axios.create({
    baseURL: `${API_BASE_URL}${API_PREFIX}`,
    timeout: 30000,
    headers: {
        'Content-Type': 'application/json'
    }
});

// Request interceptor for both instances
const requestInterceptor = (config) => {
    const token = sessionStorage.getItem('token');
    const userId = sessionStorage.getItem('userId');

    if (token) {
        config.headers.Authorization = `Bearer ${token}`;
    }

    if (userId && ['post', 'put'].includes(config.method)) {
        config.data = { ...config.data, userId: Number(userId) };
    }

    return config;
};

authApi.interceptors.request.use(requestInterceptor);
iaApi.interceptors.request.use(requestInterceptor);

// Response interceptor for both instances
const responseInterceptor = [
    response => response,
    error => {
        if (error.response?.status === 401) {
            sessionStorage.clear();
            window.location.href = '/login';
            return Promise.reject(new Error('Sesión expirada'));
        }
        return Promise.reject(error);
    }
];

authApi.interceptors.response.use(...responseInterceptor);
iaApi.interceptors.response.use(...responseInterceptor);

export const getHeaders = () => {
    const token = sessionStorage.getItem('token');
    return {
        'Content-Type': 'application/json',
        ...(token && { Authorization: `Bearer ${token}` })
    };
};

// Export apiService for compatibility
export const apiService = {
    auth: {
        login: async (credentials) => {
            const response = await authApi.post('/auth/login', credentials);
            if (response.data.token) {
                sessionStorage.setItem('token', response.data.token);
                sessionStorage.setItem('userId', response.data.userId);
            }
            return response.data;
        },
        logout: async () => {
            const response = await authApi.post('/auth/logout');
            sessionStorage.clear();
            return response.data;
        }
    },
    chat: {
        sendMessage: async (message, context = {}) => {
            const response = await iaApi.post('/chat', { message, context });
            return response.data;
        }
    },
    improve: {
        content: async (content, contentType, context = {}) => {
            const response = await iaApi.post('/improve', {
                content,
                content_type: contentType,
                context
            });
            return response.data;
        }
    },
    board: {
        challenge: {
            getAll: () => authApi.get('/challenge'),
            getOne: (id) => authApi.get(`/challenge/${id}`),
            create: (data) => authApi.post('/challenge', data),
            update: (id, data) => authApi.put(`/challenge/${id}`, data),
            delete: (id) => authApi.delete(`/challenge/${id}`)
        }
    }
};

export default {
    getApiUrl,
    getHeaders,
    authApi,
    iaApi,
    apiService
};