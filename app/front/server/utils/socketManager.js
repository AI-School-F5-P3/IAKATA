// import { WebSocketServer, WebSocket } from 'ws';
// import crypto from 'crypto';

// class SocketManager {
//     static EVENTS = {
//         USER: 'USER_EVENT',
//         PROCESS: 'PROCESS_EVENT',
//         TRIBE: 'TRIBE_EVENT',
//         CHALLENGE: 'CHALLENGE_EVENT',
//         ACTUAL_STATE: 'ACTUAL_STATE_EVENT',
//         TARGET_STATE: 'TARGET_STATE_EVENT',
//         MENTAL_CONTRAST: 'MENTAL_CONTRAST_EVENT',
//         OBSTACLE: 'OBSTACLE_EVENT',
//         HYPOTHESIS: 'HYPOTHESIS_EVENT',
//         EXPERIMENT: 'EXPERIMENT_EVENT',
//         TASK: 'TASK_EVENT',
//         RESULT: 'RESULT_EVENT',
//         LEARNING: 'LEARNING_EVENT',
//         ERROR: 'ERROR_EVENT',
//         HEARTBEAT: 'HEARTBEAT_EVENT',
//         SESSION_FORCE_LOGOUT: 'SESSION_FORCE_LOGOUT'
//     };

//     static wss = null;
//     static sessions = new Map();
//     static messageQueue = new Map();
//     static lastBroadcast = new Map();
//     static QUEUE_LIMIT = 100;
//     static BROADCAST_INTERVAL = 1000;

//     static userSessions = new Map();

//     static initialize(server) {
//         if (this.wss) return this;

//         this.wss = new WebSocketServer({ server });
//         this.setupServerHandlers();
//         return this;
//     }

//     static setupServerHandlers() {
//         this.wss.on('connection', (ws, req) => {
//             const sessionId = this.getSessionId(req);
//             this.handleConnection(ws, sessionId);
//         });
//     }

//     static getSessionId(req) {
//         const url = new URL(req.url, `http://${req.headers.host}`);
//         return url.searchParams.get('sessionId') || crypto.randomUUID();
//     }

//     static handleConnection(ws, sessionId) {
//         if (!this.sessions.has(sessionId)) {
//             this.sessions.set(sessionId, new Set());
//         }
        
//         const session = this.sessions.get(sessionId);
//         session.add(ws);
        
//         ws.sessionId = sessionId;
//         ws.isAlive = true;
        
//         this.setupClientHandlers(ws);
//         this.setupHeartbeat(ws);
//     }

//     static setupClientHandlers(ws) {
//         ws.on('message', (message) => this.handleMessage(ws, message));
//         ws.on('close', () => this.handleDisconnect(ws));
//         ws.on('error', (error) => this.handleError(ws, error));
//         ws.on('pong', () => { ws.isAlive = true; });
//     }

//     static handleMessage(ws, message) {
//         try {
//             const data = JSON.parse(message);
//             const messageId = this.generateMessageId(data);

//             if (data.type === this.EVENTS.HEARTBEAT) {
//                 ws.isAlive = true;
//                 return;
//             }

//             if (this.messageQueue.has(messageId)) return;
//             this.queueMessage(messageId, data, ws.sessionId);
//             this.processQueue();

//         } catch (error) {
//             this.handleError(ws, error);
//         }
//     }

//     static generateMessageId(data) {
//         const content = `${data.type}-${JSON.stringify(data.payload)}-${Date.now()}`;
//         return crypto.createHash('md5').update(content).digest('hex');
//     }

//     static queueMessage(messageId, data, sessionId) {
//         this.messageQueue.set(messageId, {
//             data,
//             sessionId,
//             timestamp: Date.now()
//         });

//         if (this.messageQueue.size > this.QUEUE_LIMIT) {
//             const oldestKey = this.messageQueue.keys().next().value;
//             this.messageQueue.delete(oldestKey);
//         }
//     }

//     static processQueue() {
//         this.messageQueue.forEach((message, id) => {
//             const { data, sessionId, timestamp } = message;
            
//             if (Date.now() - timestamp > this.BROADCAST_INTERVAL) {
//                 this.broadcast(data.type, data.payload, sessionId);
//                 this.messageQueue.delete(id);
//             }
//         });
//     }

//     static async forceGlobalLogout(userId, email) {
//         if (!this.wss) return;

//         console.log(`Force logout initiated for user: ${userId} (${email})`);
        
//         const forceLogoutMessage = JSON.stringify({
//             type: this.EVENTS.SESSION_FORCE_LOGOUT,
//             payload: {
//                 userId: Number(userId),
//                 email,
//                 timestamp: Date.now(),
//                 reason: 'force_logout',
//                 countdown: 10, // seconds before force logout
//                 message: 'Nueva sesión iniciada en otro dispositivo'
//             }
//         });

//         let sentCount = 0;
//         const promises = [];

//         this.wss.clients.forEach(client => {
//             if (client.readyState === WebSocket.OPEN) {
//                 promises.push(new Promise((resolve) => {
//                     try {
//                         client.send(forceLogoutMessage, (error) => {
//                             if (!error) sentCount++;
//                             resolve();
//                         });
//                     } catch (error) {
//                         console.error('Force logout broadcast error:', error);
//                         resolve();
//                     }
//                 }));
//             }
//         });

//         await Promise.all(promises);
//         console.log(`Force logout message sent to ${sentCount} clients`);
        
//         // Wait for the countdown plus a small buffer
//         return new Promise(resolve => setTimeout(resolve, 11000));
//     }

//     static broadcast(type, payload, targetSessionId = null) {
//         if (!this.wss) return;

//         if (type === this.EVENTS.SESSION_FORCE_LOGOUT) {
//             return this.forceGlobalLogout(payload.userId, payload.email);
//         }
//         const now = Date.now();
//         const lastTime = this.lastBroadcast.get(type) || 0;
//         if (now - lastTime < this.BROADCAST_INTERVAL) return;
        
//         this.lastBroadcast.set(type, now);

//         const message = JSON.stringify({
//             type,
//             payload,
//             timestamp: now
//         });

//         if (targetSessionId && this.sessions.has(targetSessionId)) {
//             this.broadcastToSession(targetSessionId, message);
//         } else {
//             this.broadcastToAll(message);
//         }
//     }

//     static broadcastToSession(sessionId, message) {
//         const session = this.sessions.get(sessionId);
//         if (!session) return;

//         session.forEach(client => {
//             if (client.readyState === WebSocket.OPEN) {
//                 client.send(message);
//             }
//         });
//     }

//     static broadcastToAll(message) {
//         this.wss.clients.forEach(client => {
//             if (client.readyState === WebSocket.OPEN) {
//                 client.send(message);
//             }
//         });
//     }

//     static setupHeartbeat(ws) {
//         ws.heartbeatInterval = setInterval(() => {
//             if (!ws.isAlive) {
//                 this.handleDisconnect(ws);
//                 return;
//             }
//             ws.isAlive = false;
//             ws.ping();
//         }, 30000);
//     }

//     static handleDisconnect(ws) {
//         const session = this.sessions.get(ws.sessionId);
//         if (session) {
//             session.delete(ws);
//             if (session.size === 0) {
//                 this.sessions.delete(ws.sessionId);
//             }
//         }
//         clearInterval(ws.heartbeatInterval);
//         ws.terminate();
//     }

//     static handleError(ws, error) {
//         console.error('WebSocket error:', error);
//         if (ws.readyState === WebSocket.OPEN) {
//             ws.send(JSON.stringify({
//                 type: this.EVENTS.ERROR,
//                 payload: { message: 'Internal server error' }
//             }));
//         }
//     }

//     static cleanup() {
//         this.sessions.forEach(session => {
//             session.forEach(ws => ws.terminate());
//         });
//         this.sessions.clear();
//         this.messageQueue.clear();
//         this.lastBroadcast.clear();
//         if (this.wss) this.wss.close();
//     }
// }

// export { SocketManager };

import { WebSocketServer, WebSocket } from 'ws';
import crypto from 'crypto';

class SocketManager {
    static EVENTS = {
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
        SESSION_FORCE_LOGOUT: 'SESSION_FORCE_LOGOUT'
    };

    static wss = null;
    static sessions = new Map();
    static userSessions = new Map();
    static messageQueue = new Map();
    static lastBroadcast = new Map();
    static QUEUE_LIMIT = 100;
    static BROADCAST_INTERVAL = 1000;

    static initialize(server) {
        if (this.wss) return this;
        this.wss = new WebSocketServer({ server });
        this.setupServerHandlers();
        return this;
    }

    static setupServerHandlers() {
        this.wss.on('connection', (ws, req) => {
            const sessionId = this.getSessionId(req);
            const userId = this.getUserId(req);
            this.handleConnection(ws, sessionId, userId);
        });
    }

    static getSessionId(req) {
        const url = new URL(req.url, `http://${req.headers.host}`);
        return url.searchParams.get('sessionId') || crypto.randomUUID();
    }

    static getUserId(req) {
        const url = new URL(req.url, `http://${req.headers.host}`);
        return url.searchParams.get('userId');
    }

    static handleConnection(ws, sessionId, userId) {
        // Handle regular session
        if (!this.sessions.has(sessionId)) {
            this.sessions.set(sessionId, new Set());
        }
        const session = this.sessions.get(sessionId);
        session.add(ws);
        ws.sessionId = sessionId;

        // Handle user session if userId exists
        if (userId) {
            if (!this.userSessions.has(userId)) {
                this.userSessions.set(userId, new Set());
            }
            const userSession = this.userSessions.get(userId);
            userSession.add(ws);
            ws.userId = userId;
        }

        ws.isAlive = true;
        this.setupClientHandlers(ws);
        this.setupHeartbeat(ws);
    }

    static setupClientHandlers(ws) {
        ws.on('message', (message) => this.handleMessage(ws, message));
        ws.on('close', () => this.handleDisconnect(ws));
        ws.on('error', (error) => this.handleError(ws, error));
        ws.on('pong', () => { ws.isAlive = true; });
    }

    static handleMessage(ws, message) {
        try {
            const data = JSON.parse(message);
            const messageId = this.generateMessageId(data);

            if (data.type === this.EVENTS.HEARTBEAT) {
                ws.isAlive = true;
                return;
            }

            if (this.messageQueue.has(messageId)) return;
            this.queueMessage(messageId, data, ws.sessionId);
            this.processQueue();

        } catch (error) {
            this.handleError(ws, error);
        }
    }

    static generateMessageId(data) {
        const content = `${data.type}-${JSON.stringify(data.payload)}-${Date.now()}`;
        return crypto.createHash('md5').update(content).digest('hex');
    }

    static queueMessage(messageId, data, sessionId) {
        this.messageQueue.set(messageId, {
            data,
            sessionId,
            timestamp: Date.now()
        });

        if (this.messageQueue.size > this.QUEUE_LIMIT) {
            const oldestKey = this.messageQueue.keys().next().value;
            this.messageQueue.delete(oldestKey);
        }
    }

    static processQueue() {
        this.messageQueue.forEach((message, id) => {
            const { data, sessionId, timestamp } = message;
            
            if (Date.now() - timestamp > this.BROADCAST_INTERVAL) {
                this.broadcast(data.type, data.payload, sessionId);
                this.messageQueue.delete(id);
            }
        });
    }

    static async forceGlobalLogout(userId, email) {
        if (!this.wss || !userId) return;
    
        console.log(`Force logout initiated for user: ${userId} (${email})`);
    
        const forceLogoutMessage = JSON.stringify({
            type: this.EVENTS.SESSION_FORCE_LOGOUT,
            payload: {
                userId: Number(userId),
                email,
                timestamp: Date.now(),
                reason: 'force_logout',
                countdown: 10
            }
        });
    
        let sentCount = 0;
        const promises = [];
    
        this.wss.clients.forEach(client => {
            if (client.readyState === WebSocket.OPEN && 
                client.userId === userId.toString() &&
                client.sessionId !== this.currentSessionId) {  
                promises.push(new Promise((resolve) => {
                    try {
                        client.send(forceLogoutMessage, (error) => {
                            if (!error) {
                                console.log(`Force logout sent to session: ${client.sessionId}`);
                                sentCount++;
                            }
                            resolve();
                        });
                    } catch (error) {
                        console.error('Force logout broadcast error:', error);
                        resolve();
                    }
                }));
            }
        });
    
        await Promise.all(promises);
        console.log(`Force logout message sent to ${sentCount} sessions for user ${userId}`);
        
        return new Promise(resolve => setTimeout(resolve, 11000));
    }

    static broadcast(type, payload, targetSessionId = null) {
        if (!this.wss) return;

        // Handle force logout separately
        if (type === this.EVENTS.SESSION_FORCE_LOGOUT) {
            return this.forceGlobalLogout(payload.userId, payload.email);
        }

        const now = Date.now();
        const lastTime = this.lastBroadcast.get(type) || 0;
        if (now - lastTime < this.BROADCAST_INTERVAL) return;
        
        this.lastBroadcast.set(type, now);

        const message = JSON.stringify({
            type,
            payload,
            timestamp: now
        });

        if (targetSessionId && this.sessions.has(targetSessionId)) {
            this.broadcastToSession(targetSessionId, message);
        } else {
            this.broadcastToAll(message);
        }
    }

    static broadcastToSession(sessionId, message) {
        const session = this.sessions.get(sessionId);
        if (!session) return;

        session.forEach(client => {
            if (client.readyState === WebSocket.OPEN) {
                client.send(message);
            }
        });
    }

    static broadcastToAll(message) {
        this.wss.clients.forEach(client => {
            if (client.readyState === WebSocket.OPEN) {
                client.send(message);
            }
        });
    }

    static setupHeartbeat(ws) {
        ws.heartbeatInterval = setInterval(() => {
            if (!ws.isAlive) {
                this.handleDisconnect(ws);
                return;
            }
            ws.isAlive = false;
            ws.ping();
        }, 30000);
    }

    static handleDisconnect(ws) {
        // Clean up regular session
        const session = this.sessions.get(ws.sessionId);
        if (session) {
            session.delete(ws);
            if (session.size === 0) {
                this.sessions.delete(ws.sessionId);
            }
        }

        // Clean up user session
        if (ws.userId) {
            const userSession = this.userSessions.get(ws.userId);
            if (userSession) {
                userSession.delete(ws);
                if (userSession.size === 0) {
                    this.userSessions.delete(ws.userId);
                }
            }
        }

        clearInterval(ws.heartbeatInterval);
        ws.terminate();
    }

    static handleError(ws, error) {
        console.error('WebSocket error:', error);
        if (ws.readyState === WebSocket.OPEN) {
            ws.send(JSON.stringify({
                type: this.EVENTS.ERROR,
                payload: { message: 'Internal server error' }
            }));
        }
    }

    static cleanup() {
        this.sessions.forEach(session => {
            session.forEach(ws => ws.terminate());
        });
        this.userSessions.forEach(session => {
            session.forEach(ws => ws.terminate());
        });
        this.sessions.clear();
        this.userSessions.clear();
        this.messageQueue.clear();
        this.lastBroadcast.clear();
        if (this.wss) this.wss.close();
    }
}

export { SocketManager };