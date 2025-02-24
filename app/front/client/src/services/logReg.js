import { authApi } from './api';

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
        console.log('Attempting login with:', { email, forceLogin });
        sessionStorage.clear();

        const response = await authApi.post('/auth/login', 
            { 
                email, 
                password,
                forceLogin: Boolean(forceLogin)
            },
            {
                headers: {
                    'X-Force-Login': forceLogin ? 'true' : 'false'
                }
            }
        );

        console.log('Login response:', response.data);

        if (!response.data?.success) {
            if (response.data?.data?.isActive && !forceLogin) {
                const error = new Error('Active session exists');
                error.activeSession = true;
                error.userData = response.data.data;
                throw error;
            }
            throw new Error(response.data?.error || 'Invalid response format');
        }

        setSessionData(response.data.data);
        return response.data;
    } catch (error) {
        console.error('Login error:', error);
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

        const response = await authApi.post('/auth/logout', 
            { 
                userId, 
                forceLogout: Boolean(forceLogout),
                isActive: false  
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
        
        const response = await authApi.get('/auth/check-session', {
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
        const response = await authApi.post('/auth/register', {
            name,
            email,
            password
        });
        
        if (!response.data.success) {
            throw new Error(response.data.error || 'Error en el registro');
        }
        
        return response.data;
    } catch (error) {
        if (error.response?.status === 409) {
            throw new Error('El email ya está registrado');
        }
        throw error;
    }
};