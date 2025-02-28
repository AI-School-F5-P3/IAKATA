import axios from 'axios';
import { getApiUrl } from './api';

const API_URL = getApiUrl('auth');

const getDeviceInfo = () => ({
  userAgent: navigator.userAgent,
  platform: navigator.platform,
  language: navigator.language,
  screenResolution: `${window.screen.width}x${window.screen.height}`,
  timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
  timestamp: Date.now(),
  colorDepth: window.screen.colorDepth,
  pixelRatio: window.devicePixelRatio
});

const setSessionData = (data) => {
    if (!data) return;
    
    const token = data.token;
    const payload = JSON.parse(atob(token.split('.')[1]));
    
    const sessionData = {
        token,
        sessionId: payload.sessionId,
        userId: data.id,
        deviceFingerprint: payload.deviceId,
        isActive: data.isActive,
        loginTime: Date.now()
    };

    Object.entries(sessionData).forEach(([key, value]) => {
        if (value !== undefined) {
            sessionStorage.setItem(key, value.toString());
        }
    });
};

export const loginUser = async (email, password, forceLogin = false) => {
    try {
        sessionStorage.clear();

        const response = await axios.post(`${API_URL}/login`, 
            { 
                email, 
                password,
                forceLogin: Boolean(forceLogin)
            },
            {
                headers: {
                    'Content-Type': 'application/json',
                    'X-Force-Login': forceLogin ? 'true' : 'false'
                }
            }
        );

        if (!response.data?.success) {
            if (response.data?.data?.isActive && !forceLogin) {
                const error = new Error('Active session exists');
                error.activeSession = true;
                error.userData = response.data.data;
                throw error;
            }
            throw new Error(response.data?.error || 'Invalid response format');
        }
        console.log('Login response:', response.data);

        if (forceLogin) {
            await new Promise(resolve => setTimeout(resolve, 1500));
        }

        setSessionData(response.data.data);
        return response.data;
    } catch (error) {
        sessionStorage.clear();
        throw error;
    }
};

export const logoutUser = async (forceLogout = false) => {
    try {
        const userId = sessionStorage.getItem('userId');
        const token = sessionStorage.getItem('token');
        
        if (!userId || !token) {
            sessionStorage.clear();
            return { success: true };
        }

        sessionStorage.setItem('isActive', 'false');
        console.log('Logging out user:', userId);

        const response = await axios.post(`${API_URL}/logout`, 
            { 
                userId, 
                forceLogout: Boolean(forceLogout),
                isActive: false  
            },
            {
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                }
            }
        );

        console.log('Logout response:', response.data);
        sessionStorage.clear();
        return response.data;
    } catch (error) {
        console.error('Logout error:', error);
        sessionStorage.clear();
        throw error;
    }
};

export const checkSession = async () => {
  try {
      const deviceFingerprint = sessionStorage.getItem('deviceFingerprint');
      const sessionId = sessionStorage.getItem('sessionId');
      
      if (!deviceFingerprint || !sessionId) return false;
      
      const response = await axios.get(`${API_URL}/check-session`, {
          headers: {
              'X-Device-Fingerprint': deviceFingerprint,
              'X-Session-ID': sessionId
          }
      });
      
      return response.data.success;
  } catch {
      return false;
  }
};





export const registerUser = async (name, email, password) => {
    try {
      console.log('Enviando datos de registro:', { name, email });
      
      const response = await axios.post(getApiUrl('auth/register'), {
        name,
        email,
        password,
        // Añade cualquier otro campo obligatorio según userValidator
        // Por ejemplo, podrías necesitar:
        // rol: 'user',  // Si rol es obligatorio
      });
      
      console.log('Respuesta del servidor:', response.data);
      
      if (!response.data.success && response.data.error) {
        throw new Error(response.data.error);
      }
      
      return response.data;
    } catch (error) {
      console.error('Error completo:', error);
      
      if (error.response) {
        console.error('Código de estado:', error.response.status);
        console.error('Datos de respuesta:', error.response.data);
        
        if (error.response.status === 409) {
          throw new Error('El email ya está registrado');
        } else if (error.response.status === 400) {
          // Mejor manejo para error 400
          if (error.response.data && typeof error.response.data === 'object') {
            if (error.response.data.error) {
              throw new Error(error.response.data.error);
            } else if (error.response.data.errors) {
              const errorMessages = Array.isArray(error.response.data.errors)
                ? error.response.data.errors.map(e => e.msg || e.message || JSON.stringify(e)).join(', ')
                : error.response.data.errors;
              throw new Error(errorMessages);
            } else {
              throw new Error(JSON.stringify(error.response.data));
            }
          } else {
            throw new Error('Datos de registro inválidos');
          }
        } else if (error.response.status === 500) {
          throw new Error('Error en el servidor. Por favor, intente más tarde.');
        }
      }
      
      throw error;
    }
  };