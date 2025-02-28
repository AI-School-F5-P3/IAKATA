import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:3308';

// Definir getHeaders antes de usarla
export const getHeaders = () => {
    const token = sessionStorage.getItem('token');
    const sessionId = sessionStorage.getItem('sessionId');
    const deviceFingerprint = sessionStorage.getItem('deviceFingerprint');
    const userId = sessionStorage.getItem('userId');

    return {
        'Content-Type': 'application/json',
        ...(token && { 'Authorization': `Bearer ${token}` }),
        ...(sessionId && { 'X-Session-ID': sessionId }),
        ...(deviceFingerprint && { 'X-Device-Fingerprint': deviceFingerprint }),
        ...(userId && { 'X-User-ID': userId })
    };
};

// Configurar explícitamente la baseURL
axios.defaults.baseURL = API_BASE_URL;

// Crear una instancia específica
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: getHeaders()
});

export const getApiUrl = (endpoint) => `${API_BASE_URL}/${endpoint}`;

axios.interceptors.request.use(
    (config) => {
        config.headers = { ...config.headers, ...getHeaders() };

        if (['post', 'put'].includes(config.method?.toLowerCase())) {
            const userId = sessionStorage.getItem('userId');
            if (userId && config.data && typeof config.data === 'object') {
                config.data = {
                    ...config.data,
                    userId: Number(userId)
                };
            }
        }

        if (config.method?.toLowerCase() === 'get') {
            const userId = sessionStorage.getItem('userId');
            if (userId) {
                config.params = {
                    ...config.params,
                    userId: Number(userId)
                };
            }
        }

        return config;
    },
    (error) => Promise.reject(error)
);

axios.interceptors.response.use(
    (response) => response,
    (error) => {
        if (error.response?.status === 401 && !window.location.pathname.includes('/login')) {
            console.log('Auth error - redirecting to login');
            sessionStorage.clear();
            window.location.href = '/login';
        }
        return Promise.reject(error);
    }
);

// Exporta tanto axios como la instancia específica
export { api };
export default axios;