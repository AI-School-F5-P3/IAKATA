// import { SocketManager } from '../utils/socketManager.js';

// export const socketBroadcast = (eventType) => (req, res, next) => {
//     const oldJson = res.json;
//     res.json = function(data) {
//         const result = oldJson.apply(res, arguments);
        
//         if (data.success !== false) {
//             try {
//                 console.log('Broadcasting through middleware:', eventType, data);
//                 SocketManager.broadcast(eventType, data);
//             } catch (error) {
//                 console.error('Error broadcasting event:', error);
//             }
//         }
//         return result;
//     };
//     next();
// };
// export const socketAuthenticate = (socket, request) => {
//     const token = request.headers['authorization'];
//     if (!token) {
//         socket.close(4001, 'No autorizado');
//         return false;
//     }
//     return true;
// };

import { SocketManager } from '../utils/socketManager.js';

export const socketBroadcast = (eventType) => (req, res, next) => {
    const oldJson = res.json;
    res.json = function(data) {
        const result = oldJson.apply(res, arguments);
        
        if (data.success !== false) {
            const sessionId = req.headers['x-session-id'];
            SocketManager.broadcast(eventType, data, sessionId);
        }
        return result;
    };
    next();
};

export const socketAuthenticate = (socket, request) => {
    try {
        const token = request.headers['authorization']?.split(' ')[1];
        if (!token) {
            socket.close(4001, 'No autorizado');
            return false;
        }

        const decoded = jwt.verify(token, JWT_SECRET);
        socket.userId = decoded.id;
        return true;
    } catch (error) {
        console.error('Socket authentication error:', error);
        socket.close(4003, 'Token inválido');
        return false;
    }
};

export const socketErrorHandler = (error, socket) => {
    console.error('WebSocket error:', error);
    socket.send(JSON.stringify({
        type: 'ERROR_EVENT',
        payload: {
            message: 'Error interno del servidor',
            code: 500
        }
    }));
};