import express from 'express';
import http from 'http';
import cors from 'cors';
import compression from 'compression';
import connection_db from "./database/connection_db.js";
import { PORT } from './config.js';

// Middleware imports
import authToken from './middleware/autMiddleware.js';
import { checkActiveSession } from './middleware/sessionCheck.js';
import { SocketManager } from './utils/socketManager.js';
import { socketBroadcast } from './middleware/socketMiddleware.js';
import UsersModel from './models/userModel.js';

// Router imports
import authRouter from './routes/authRouter.js';
import usersRouter from './routes/usersRouter.js';
import processRouter from './routes/processRouter.js';
import tribeRouter from './routes/tribeRouter.js';
import challengeRouter from './routes/challengeRouter.js';
import targetStateRouter from './routes/targetStateRouter.js';
import actualstateRouter from './routes/actualstateRouter.js';
import mentalContrastRouter from './routes/mentalContrastRouter.js';
import obstacleRouter from './routes/obstacleRouter.js';
import hypothesisRouter from './routes/hypothesisRouter.js';
import experimentRouter from './routes/experimentRouter.js';
import taskRouter from './routes/taskRouter.js';
import resultRouter from './routes/resultRouter.js';
import learningRouter from './routes/learningRouter.js';

const app = express();
const server = http.createServer(app);
const socketManager = SocketManager.initialize(server);

app.use(cors({
    origin: '*',
    methods: ['GET', 'POST', 'PUT', 'DELETE'],
    allowedHeaders: [
        'Content-Type', 
        'Authorization',
        'X-Force-Login',
        'X-Force-Logout',  
        'X-Device-Fingerprint',
        'X-Session-ID',
        'X-User-ID' 
    ],
    exposedHeaders: ['X-Force-Login', 'X-Force-Logout'],
    credentials: true
}));

app.use(express.json());
app.use(compression());

app.use('/auth', authRouter);
app.use('/users', authToken, checkActiveSession, socketBroadcast(SocketManager.EVENTS.USER), usersRouter);
app.use('/process', authToken, checkActiveSession, socketBroadcast(SocketManager.EVENTS.PROCESS), processRouter);
app.use('/tribe', authToken, checkActiveSession, socketBroadcast(SocketManager.EVENTS.TRIBE), tribeRouter);
app.use('/challenge', authToken, checkActiveSession, socketBroadcast(SocketManager.EVENTS.CHALLENGE), challengeRouter);
app.use('/target-state', authToken, checkActiveSession, socketBroadcast(SocketManager.EVENTS.TARGET_STATE), targetStateRouter);
app.use('/actual-states', authToken, checkActiveSession, socketBroadcast(SocketManager.EVENTS.ACTUAL_STATE), actualstateRouter);
app.use('/mentalcontrast', authToken, checkActiveSession, socketBroadcast(SocketManager.EVENTS.MENTAL_CONTRAST), mentalContrastRouter);
app.use('/obstacle', authToken, checkActiveSession, socketBroadcast(SocketManager.EVENTS.OBSTACLE), obstacleRouter);
app.use('/hypothesis', authToken, checkActiveSession, socketBroadcast(SocketManager.EVENTS.HYPOTHESIS), hypothesisRouter);
app.use('/experiment', authToken, checkActiveSession, socketBroadcast(SocketManager.EVENTS.EXPERIMENT), experimentRouter);
app.use('/task', authToken, checkActiveSession, socketBroadcast(SocketManager.EVENTS.TASK), taskRouter);
app.use('/results', authToken, checkActiveSession, socketBroadcast(SocketManager.EVENTS.RESULT), resultRouter);
app.use('/learning', authToken, checkActiveSession, socketBroadcast(SocketManager.EVENTS.LEARNING), learningRouter);

app.get('/health', async (req, res) => {
    try {
        await connection_db.authenticate();
        res.json({
            status: 'ok',
            uptime: process.uptime(),
            timestamp: new Date(),
            wsClients: socketManager.wss?.clients.size || 0
        });
    } catch (error) {
        res.status(503).json({
            status: 'error',
            message: 'Database check failed'
        });
    }
});

app.get('/ws-health', (req, res) => {
    res.json({
        wsServer: SocketManager.wss ? 'running' : 'stopped',
        connections: SocketManager.getConnectionCount(),
        uptime: process.uptime()
    });
    console.log('WebSocket health check');
});

// bloque añadido
app.get('/', (req, res) => {
    res.json({
        success: true,
        message: "El backend está funcionando correctamente 🚀"
    });
});








app.use((err, req, res, next) => {
    console.error('Error:', err.stack);
    res.status(500).json({
        success: false,
        error: 'Error interno del servidor'
    });
});

app.use((req, res) => {
    console.log('Ruta no encontrada:', req.path);
    res.status(404).json({
        success: false,
        error: 'Ruta no encontrada'
    });
});

try {
    await connection_db.authenticate();
    await connection_db.sync({ alter: true });
    await UsersModel.sync();

    console.log('All models synchronized successfully 👏👏👏');

    server.listen(PORT, () => {
        console.log(`API running on http://localhost:${PORT} 🚀`);
        console.log('WebSocket server initialized 🔌');
    });

    const cleanup = () => {
        socketManager.cleanup();
        server.close(() => {
            console.log('Server closed gracefully');
            process.exit(0);
        });
    };

    process.on('SIGTERM', cleanup);
    process.on('SIGINT', cleanup);

} catch (error) {
    console.error('Unable to start server:', error);
    process.exit(1);
}

export { app, server };