// import { createContext, useContext, useState, useEffect, useRef, useCallback } from 'react';

// const SocketContext = createContext(null);

// export const WS_EVENTS = {
//     USER: 'USER_EVENT',
//     PROCESS: 'PROCESS_EVENT', 
//     TRIBE: 'TRIBE_EVENT',
//     CHALLENGE: 'CHALLENGE_EVENT',
//     ACTUAL_STATE: 'ACTUAL_STATE_EVENT',
//     TARGET_STATE: 'TARGET_STATE_EVENT',
//     MENTAL_CONTRAST: 'MENTAL_CONTRAST_EVENT',
//     OBSTACLE: 'OBSTACLE_EVENT',
//     HYPOTHESIS: 'HYPOTHESIS_EVENT',
//     EXPERIMENT: 'EXPERIMENT_EVENT',
//     TASK: 'TASK_EVENT',
//     RESULT: 'RESULT_EVENT',
//     LEARNING: 'LEARNING_EVENT',
//     ERROR: 'ERROR_EVENT',
//     HEARTBEAT: 'HEARTBEAT_EVENT',
//     CONNECTION_ERROR: 'CONNECTION_ERROR',
//     RECONNECTING: 'RECONNECTING'
// };

// const CONFIG = {
//     MAX_RETRIES: 3,
//     RETRY_DELAY: 3000,
//     HEARTBEAT_INTERVAL: 30000,
//     MESSAGE_QUEUE_SIZE: 100
// };

// export const SocketProvider = ({ children }) => {
//     const [socket, setSocket] = useState(null);
//     const [isConnected, setIsConnected] = useState(false);
//     const reconnectTimeoutRef = useRef(null);
//     const messageQueueRef = useRef([]);
//     const retryCountRef = useRef(0);
//     const lastMessageRef = useRef(null);

//     const connectWebSocket = useCallback(() => {
//         try {
//             if (retryCountRef.current >= CONFIG.MAX_RETRIES) {
//                 console.error('Max reconnection attempts reached');
//                 return;
//             }

//             const ws = new WebSocket(`ws://${window.location.hostname}:5001/ws`);
            
//             ws.onopen = () => {
//                 console.log('WebSocket Connected');
//                 setIsConnected(true);
//                 setSocket(ws);
//                 retryCountRef.current = 0;

//                 // Send queued messages
//                 while (messageQueueRef.current.length > 0) {
//                     const msg = messageQueueRef.current.shift();
//                     ws.send(msg);
//                 }
//             };

//             ws.onclose = () => {
//                 console.log('WebSocket Disconnected');
//                 setIsConnected(false);
//                 retryCountRef.current += 1;
//                 reconnectTimeoutRef.current = setTimeout(connectWebSocket, CONFIG.RETRY_DELAY);
//             };

//             ws.onerror = (error) => {
//                 console.error('WebSocket Error:', error);
//             };

//             ws.onmessage = (event) => {
//                 const message = JSON.parse(event.data);
//                 lastMessageRef.current = message;
//                 console.log('WebSocket Message:', message);
//             };

//             const heartbeatInterval = setInterval(() => {
//                 if (ws.readyState === WebSocket.OPEN) {
//                     ws.send(JSON.stringify({ type: WS_EVENTS.HEARTBEAT }));
//                 }
//             }, CONFIG.HEARTBEAT_INTERVAL);

//             return () => {
//                 clearInterval(heartbeatInterval);
//                 ws.close();
//             };
    
//         } catch (error) {
//             console.error('Connection error:', error);
//             return null;
//         }
//     }, []);

//     useEffect(() => {
//         const cleanup = connectWebSocket();

//         return () => {
//             if (socket) {
//                 socket.close();
//             }
//             if (cleanup) {
//                 clearTimeout(reconnectTimeoutRef.current);
//             }
//         };
//     }, [connectWebSocket]);

//     const sendMessage = useCallback((type, payload) => {
//         const message = { type, payload, timestamp: Date.now() };

//         if (!socket || socket.readyState !== WebSocket.OPEN) {
//             if (messageQueueRef.current.length < CONFIG.MESSAGE_QUEUE_SIZE) {
//                 messageQueueRef.current.push(JSON.stringify(message));
//             } else {
//                 console.error('Message queue is full');
//             }
//             return;
//         }

//         try {
//             socket.send(JSON.stringify(message));
//         } catch (error) {
//             console.error('Send error:', error);
//             messageQueueRef.current.push(JSON.stringify(message));
//         }
//     }, [socket]);

//     return (
//         <SocketContext.Provider value={{ 
//             socket,
//             isConnected,
//             sendMessage,
//             WS_EVENTS
//         }}>
//             {children}
//         </SocketContext.Provider>
//     );
// };

// export const useWebSocket = () => {
//     const context = useContext(SocketContext);
//     if (!context) {
//         throw new Error('useWebSocket must be used within a SocketProvider');
//     }
//     return context;
// };

// export default SocketContext;

import { createContext, useContext, useState, useEffect, useRef, useCallback } from 'react';
import { v4 as uuidv4 } from 'uuid';

const SocketContext = createContext(null);

export const WS_EVENTS = {
    USER: 'USER_EVENT',
    PROCESS: 'PROCESS_EVENT', 
    TRIBE: 'TRIBE_EVENT',
    CHALLENGE: 'CHALLENGE_EVENT',
    ACTUAL_STATE: 'ACTUAL_STATE_EVENT',
    TARGET_STATE: 'TARGET_STATE_EVENT',
    MENTAL_CONTRAST: 'MENTAL_CONTRAST_EVENT',
    OBSTACLE: 'OBSTACLE_EVENT',
    HYPOTHESIS: 'HYPOTHESIS_EVENT',
    EXPERIMENT: 'EXPERIMENT_EVENT',
    TASK: 'TASK_EVENT',
    RESULT: 'RESULT_EVENT',
    LEARNING: 'LEARNING_EVENT',
    ERROR: 'ERROR_EVENT',
    HEARTBEAT: 'HEARTBEAT_EVENT',
    CONNECTION_ERROR: 'CONNECTION_ERROR',
    RECONNECTING: 'RECONNECTING',
    USER_LOGOUT: 'USER_LOGOUT',
    SESSION_UPDATE: 'SESSION_UPDATE'
};

const CONFIG = {
    MAX_RETRIES: 3,
    RETRY_DELAY: 3000,
    HEARTBEAT_INTERVAL: 30000,
    QUEUE_SIZE: 100
};

export const SocketProvider = ({ children }) => {
    const [socket, setSocket] = useState(null);
    const [isConnected, setIsConnected] = useState(false);
    const sessionId = useRef(localStorage.getItem('sessionId') || uuidv4());
    const messageQueue = useRef([]);
    const retryCount = useRef(0);
    const reconnectTimeout = useRef(null);

    const connectWebSocket = useCallback(() => {
        try {
            if (retryCount.current >= CONFIG.MAX_RETRIES) {
                console.error('Max reconnection attempts reached');
                return null;
            }

            const userId = sessionStorage.getItem('userId');
            const wsUrl = new URL(`ws://${window.location.hostname}:5001/ws`);
            wsUrl.searchParams.append('sessionId', sessionId.current);
            if (userId) {
                wsUrl.searchParams.append('userId', userId);
            }

            const ws = new WebSocket(wsUrl.toString());

            ws.onopen = () => {
                console.log('WebSocket Connected');
                setIsConnected(true);
                setSocket(ws);
                retryCount.current = 0;
                processQueue(ws);
            };

            ws.onclose = () => {
                console.log('WebSocket Disconnected');
                setIsConnected(false);
                setSocket(null);
                retryCount.current++;
                reconnectTimeout.current = setTimeout(connectWebSocket, CONFIG.RETRY_DELAY);
            };

            ws.onerror = (error) => {
                console.error('WebSocket Error:', error);
            };

            const heartbeatInterval = setInterval(() => {
                if (ws.readyState === WebSocket.OPEN) {
                    ws.send(JSON.stringify({ type: WS_EVENTS.HEARTBEAT }));
                }
            }, CONFIG.HEARTBEAT_INTERVAL);

            return () => {
                clearInterval(heartbeatInterval);
                ws.close();
            };
        } catch (error) {
            console.error('Connection error:', error);
            return null;
        }
    }, []);

    const processQueue = useCallback((ws) => {
        while (messageQueue.current.length > 0 && ws.readyState === WebSocket.OPEN) {
            const message = messageQueue.current.shift();
            try {
                ws.send(message);
                
                const parsedMessage = JSON.parse(message);
                if (parsedMessage.type === WS_EVENTS.USER && 
                    parsedMessage.payload?.type === 'logout') {
                    sessionStorage.setItem('isActive', 'false');
                }
            } catch (error) {
                console.error('Error sending queued message:', error);
                messageQueue.current.unshift(message);
                break;
            }
        }
    }, []);

const sendMessage = useCallback((type, payload) => {
        const userId = sessionStorage.getItem('userId');
        const message = JSON.stringify({
            type,
            payload: {
                ...payload,
                userId: userId ? Number(userId) : undefined,
                sessionId: sessionId.current,
                timestamp: Date.now()
            }
        });

        if (!socket || socket.readyState !== WebSocket.OPEN) {
            if (messageQueue.current.length < CONFIG.QUEUE_SIZE) {
                messageQueue.current.push(message);
            }
            return;
        }

        try {
            socket.send(message);
            
            if (type === WS_EVENTS.USER && payload.type === 'logout') {
                sessionStorage.setItem('isActive', 'false');
            }
        } catch (error) {
            console.error('Send error:', error);
            messageQueue.current.push(message);
        }
    }, [socket]);

    useEffect(() => {
        localStorage.setItem('sessionId', sessionId.current);
        const cleanup = connectWebSocket();

        return () => {
            if (cleanup) cleanup();
            if (reconnectTimeout.current) {
                clearTimeout(reconnectTimeout.current);
            }
        };
    }, [connectWebSocket]);

    return (
        <SocketContext.Provider value={{
            socket,
            isConnected,
            sendMessage,
            sessionId: sessionId.current,
            WS_EVENTS
        }}>
            {children}
        </SocketContext.Provider>
    );
};

export const useWebSocket = () => {
    const context = useContext(SocketContext);
    if (!context) {
        throw new Error('useWebSocket must be used within a SocketProvider');
    }
    return context;
};

export default SocketContext;