import { createContext, useContext, useState, useEffect } from "react";
import { checkSession, logoutUser } from '../services/logReg';
import Swal from 'sweetalert2';
import { useWebSocket } from "./SocketContext";
import '../components/forms/css/RegForm.css';

export const UserContext = createContext();

const UserProvider = ({ children }) => {
    const [user, setUser] = useState(null);
    const [userAuth, setUserAuth] = useState(false);
    const [isActive, setIsActive] = useState(false);
    const [checkedSession, setCheckedSession] = useState(false);
    const { WS_EVENTS, sendMessage } = useWebSocket();

    const handleExistingSession = async (userId) => {
        const result = await Swal.fire({
            title: 'Sesión Activa',
            text: 'Ya existe una sesión iniciada para este usuario',
            icon: 'warning',
            showCancelButton: true,
            confirmButtonColor: '#3085d6',
            cancelButtonColor: '#d33',
            confirmButtonText: '¿Deseas cerrar la otra sesión?',
            cancelButtonText: 'Cancelar'
        });

        if (result.isConfirmed) {
            localStorage.setItem(`sessionClosed_${userId}`, 'true');
            await logoutUser();
            return true;
        }
        return false;
    };

    useEffect(() => {
        const handleStorageChange = (e) => {
            const userId = sessionStorage.getItem("userId");
            if (e.key === `sessionClosed_${userId}`) {
                clearSessionData();
            }
        };

        window.addEventListener("storage", handleStorageChange);

        const validateSession = async () => {
            const token = sessionStorage.getItem("token");
            const userId = sessionStorage.getItem("userId");
            const sessionClosed = localStorage.getItem(`sessionClosed_${userId}`);

            if (!token || !userId || sessionClosed) {
                clearSessionData();
                return;
            }

            try {
                const sessionActive = await checkSession();
                if (sessionActive) {
                    const shouldContinue = await handleExistingSession(userId);
                    if (!shouldContinue) {
                        clearSessionData();
                        return;
                    }
                    setUserAuth(true);
                    setIsActive(true);
                } else {
                    await logout();
                }
            } catch (error) {
                console.error('Session validation error:', error);
                await logout();
            } finally {
                setCheckedSession(true);
            }
        };

        if (!checkedSession) {
            validateSession();
        }

        return () => window.removeEventListener("storage", handleStorageChange);
    }, [checkedSession]);

    const clearSessionData = () => {
        sessionStorage.clear();
        const userId = sessionStorage.getItem("userId");
        if (userId) localStorage.removeItem(`sessionClosed_${userId}`);
        setUser(null);
        setUserAuth(false);
        setIsActive(false);
        setCheckedSession(true);
    };

    const updateSessionState = (userData) => {
        if (!userData) {
            console.warn('No user data provided to updateSessionState');
            return;
        }

        setUser(userData);
        setUserAuth(true);
        setIsActive(Boolean(userData.isActive));

        sessionStorage.setItem("token", userData.token);
        sessionStorage.setItem("userId", userData.id);
        sessionStorage.setItem("isActive", userData.isActive);
        sessionStorage.setItem("lastLogin", new Date().toISOString());
    };

    const logout = async () => {
        try {
            const userId = sessionStorage.getItem("userId");
            
            setIsActive(false);
            
            const result = await logoutUser();
            
            if (result.success) {
                setUser(null);
                setUserAuth(false);
                
                sessionStorage.clear();
                if (userId) {
                    localStorage.removeItem(`sessionClosed_${userId}`);
                }
    
                sendMessage(WS_EVENTS.USER, {
                    userId,
                    isActive: false,
                    type: 'logout',
                    timestamp: Date.now()
                });
            }
        } catch (error) {
            console.error('Logout error:', error);
        } finally {
            setUser(null);
            setUserAuth(false);
            setIsActive(false);
            sessionStorage.clear();
        }
    };

    useEffect(() => {
        const userId = sessionStorage.getItem('userId');
        const sessionId = sessionStorage.getItem('sessionId');
        
        if (!userId) return;
    
        const socket = new WebSocket(`ws://${window.location.hostname}:5001/ws?userId=${userId}&sessionId=${sessionId}`);
    
        const handleSocketMessage = async (event) => {
            try {
                const data = JSON.parse(event.data);
                const currentUserId = sessionStorage.getItem('userId');
                
                if (data.type === 'SESSION_FORCE_LOGOUT' && 
                    data.payload.userId === Number(currentUserId)) {
                    console.log('Force logout received for user:', currentUserId);
                    
                    let timerInterval;
                    await Swal.fire({
                        title: 'Sesión Finalizada',
                        html: 'Esta sesión se cerrará en <b></b> segundos...',
                        timer: 10000,
                        timerProgressBar: true,
                        allowOutsideClick: false,
                        showConfirmButton: false,
                        confirmButtonColor: '#002661',
                        customClass: {
                            popup: 'swal-custom-popup',
                            title: 'swal-custom-title',
                            content: 'swal-custom-content',
                            timerProgressBar: 'timer-progress-bar-custom'
                        },
                        didOpen: () => {
                            const timer = Swal.getPopup().querySelector('b');
                            timerInterval = setInterval(() => {
                                timer.textContent = Math.ceil(Swal.getTimerLeft() / 1000);
                            }, 100);
                        },
                        willClose: () => {
                            clearInterval(timerInterval);
                        }
                    });
                    
    
                    await logout();
                    window.location.href = '/';
                }
            } catch (error) {
                console.error('Socket message error:', error);
            }
        };
    
        socket.addEventListener('message', handleSocketMessage);
        socket.addEventListener('open', () => {
            console.log('WebSocket connected for user:', userId);
        });
        socket.addEventListener('close', () => {
            console.log('WebSocket disconnected for user:', userId);
        });
    
        return () => {
            if (socket && socket.readyState === WebSocket.OPEN) {
                socket.close();
            }
        };
    }, [sessionStorage.getItem('userId')]);

    useEffect(() => {
        const handleSessionConflict = (event) => {
            const userId = event.detail.userId;
            if (userId) {
                localStorage.setItem(`sessionConflict_${userId}`, Date.now());
            }
        };

        window.addEventListener('sessionConflict', handleSessionConflict);
        return () => window.removeEventListener('sessionConflict', handleSessionConflict);
    }, []);

    if (!checkedSession) return (
        <div className="session-loading-container">
          <div className="session-loading-spinner"></div>
          <p>Validando sesión...</p>
        </div>
      );

    return (
        <UserContext.Provider value={{ 
            userAuth, 
            setUserAuth, 
            user, 
            setUser,
            isActive,
            setIsActive,
            logout,
            updateSessionState 
        }}>
            {children}
        </UserContext.Provider>
    );
};

export default UserProvider;
export const useUserContext = () => useContext(UserContext);