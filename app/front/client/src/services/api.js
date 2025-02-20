// // import axios from 'axios';

// // const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5001';

// // export const getApiUrl = (endpoint) => `${API_BASE_URL}/${endpoint}`;

// // export const getHeaders = () => {
// //     const token = sessionStorage.getItem('token');
// //     return {
// //         'Content-Type': 'application/json',
// //         ...(token ? { 'Authorization': `Bearer ${token}` } : {})
// //     };
// // };

// // const logRequestDetails = (config) => {
// //     // console.log('Request Details:', {
// //     //     url: config.url,
// //     //     method: config.method,
// //     //     userId: sessionStorage.getItem('userId'),
// //     //     data: config.data
// //     // });
// // };

// // // Request interceptor
// // axios.interceptors.request.use((config) => {
// //     const token = sessionStorage.getItem('token');
// //     if (token) {
// //         config.headers['Authorization'] = `Bearer ${token}`;
// //     }

// //     if (['post', 'put'].includes(config.method?.toLowerCase())) {
// //         config.data = {
// //             ...config.data,
// //             userId: sessionStorage.getItem('userId') || null
// //         };
// //     }
    
// //     logRequestDetails(config);
// //     return config;
// // }, (error) => Promise.reject(error));

// // // Response interceptor
// // // axios.interceptors.response.use(
// // //     (response) => response,
// // //     (error) => {
// // //         if (error.code === 'ERR_NETWORK') {
// // //             console.error('Network error - server may be down');
// // //             return Promise.reject(new Error('Error de conexión: servidor no disponible'));
// // //         }
// // //         if (error.response?.status === 401) {
// // //             sessionStorage.clear();
// // //             window.location.href = '/login';
// // //             return Promise.reject(new Error('Sesión expirada'));
// // //         }
// // //         return Promise.reject(error);
// // //     }
// // // );

// // // Axios instance
// // export const axiosInstance = axios.create({
// //     baseURL: API_BASE_URL,
// //     timeout: 10000,
// //     headers: getHeaders(),
// //     withCredentials: true
// // });

// // export { API_BASE_URL };
// // export default axiosInstance;

// import axios from 'axios';

// const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5001';

// export const getApiUrl = (endpoint) => `${API_BASE_URL}/${endpoint}`;

// export const getHeaders = () => {
//     const token = sessionStorage.getItem('token');
//     const sessionId = sessionStorage.getItem('sessionId');
//     const deviceFingerprint = sessionStorage.getItem('deviceFingerprint');

//     return {
//         'Content-Type': 'application/json',
//         ...(token && { 'Authorization': `Bearer ${token}` }),
//         ...(sessionId && { 'X-Session-ID': sessionId }),
//         ...(deviceFingerprint && { 'X-Device-Fingerprint': deviceFingerprint })
//     };
// };

// // Single axios instance
// const axiosInstance = axios.create({
//     baseURL: API_BASE_URL,
//     timeout: 10000,
//     headers: getHeaders()
// });

// // Request interceptor
// axiosInstance.interceptors.request.use((config) => {
//     // Get fresh headers on each request
//     config.headers = {
//         ...config.headers,
//         ...getHeaders()
//     };
//     return config;
// });

// // Response interceptor
// // axiosInstance.interceptors.response.use(
// //     response => response,
// //     error => {
// //         if (error.response?.status === 401 && !window.location.pathname.includes('/login')) {
// //             sessionStorage.clear();
// //             window.location.href = '/login';
// //         }
// //         return Promise.reject(error);
// //     }
// //);

// // Set global defaults
// axios.defaults = {
//     ...axios.defaults,
//     ...axiosInstance.defaults
// };

// // Share interceptors globally
// axios.interceptors.request.handlers = [...axiosInstance.interceptors.request.handlers];
// axios.interceptors.response.handlers = [...axiosInstance.interceptors.response.handlers];

// // export default axios;

import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5001';

export const getApiUrl = (endpoint) => `${API_BASE_URL}/${endpoint}`;

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

export default axios;