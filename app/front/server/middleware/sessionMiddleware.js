import SocketManager from '../utils/socketManager.js';

const activeSessions = new Map();

export const sessionMiddleware = (socket, next) => {
  const token = socket.handshake.auth.token;
  
  if (!token) {
    return next(new Error('Authentication required'));
  }

  try {
    // Verify token and get user info
    const userId = getUserIdFromToken(token);
    
    // Check for existing session
    if (activeSessions.has(userId)) {
      const existingSocket = activeSessions.get(userId);
      existingSocket.emit('session-expired');
      existingSocket.disconnect();
    }

    // Store new session
    activeSessions.set(userId, socket);
    socket.userId = userId;

    socket.on('disconnect', () => {
      activeSessions.delete(userId);
      SocketManager.instance.broadcast('session', {
        type: 'USER_DISCONNECTED',
        userId
      });
    });

    next();
  } catch (error) {
    next(new Error('Invalid token'));
  }
};

function getUserIdFromToken(token) {
  // Implement token verification logic
  return token;
}

export const getActiveSessions = () => {
  return Array.from(activeSessions.keys());
};
