import { useEffect, useCallback } from 'react';
import { useWebSocket } from '../context/SocketContext';

export const useSocket = (eventType, challengeId, updateCallback) => {
    const { socket } = useWebSocket();

    const handleWebSocketMessage = useCallback((event) => {
        try {
            const data = JSON.parse(event.data);
            if (!data || !data.type || data.type !== eventType) return;

            if (!data.payload) return;
            if (Array.isArray(data.payload) && data.payload.length === 0) return;
            if (data.payload.type === 'close') return; 

            updateCallback(data.payload);
        } catch (error) {
            console.error('WebSocket message error:', error);
        }
    }, [eventType, updateCallback]);

    useEffect(() => {
        if (!socket) return;
        socket.addEventListener('message', handleWebSocketMessage);
        return () => socket.removeEventListener('message', handleWebSocketMessage);
    }, [socket, handleWebSocketMessage]);
};