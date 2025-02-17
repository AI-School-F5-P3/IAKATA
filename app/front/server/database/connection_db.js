import { Sequelize } from 'sequelize';
import { DB_DEV_NAME, DB_USER, DB_PASSWORD } from '../config.js';

// Connection configuration
const config = {
    pool: {
        max: 25,
        min: 5,
        acquire: 60000,
        idle: 20000,
        handleDisconnects: true
    },
    dialectOptions: {
        connectTimeout: 60000
    },
    logging: (msg) => {
        if (!msg.includes('SELECT 1+1')) {
            console.log(`[Database Query]: ${msg}`);
        }
    }
};
// Create Sequelize instance
const sequelize = new Sequelize(DB_DEV_NAME, DB_USER, DB_PASSWORD, {
    host: 'localhost',
    dialect: 'mysql',
    ...config
});

// Health check function
const checkHealth = async () => {
    try {
        await sequelize.query('SELECT 1+1');
        return true;
    } catch (error) {
        console.error('Health check failed:', error);
        return false;
    }
};

// Connection test function
const testConnection = async () => {
    try {
        await sequelize.authenticate();
        console.log('Database connected successfully');
        return true;
    } catch (error) {
        console.error('Database connection failed:', error);
        return false;
    }
};

// Initial connection
sequelize.authenticate()
    .then(() => console.log('Database connected successfully 📦'))
    .catch(err => console.error('Unable to connect to database:', err));

// Reconnection handler
sequelize.afterDisconnect(async () => {
    console.log('Connection lost. Attempting to reconnect...');
    await testConnection();
});

// Cache mechanism for health checks
let lastHealthCheck = null;
let healthCheckTimeout = null;

const getCachedHealth = async () => {
    if (!lastHealthCheck || Date.now() - lastHealthCheck.timestamp > 30000) {
        if (healthCheckTimeout) {
            clearTimeout(healthCheckTimeout);
        }
        
        lastHealthCheck = {
            status: await checkHealth(),
            timestamp: Date.now()
        };

        healthCheckTimeout = setTimeout(() => {
            lastHealthCheck = null;
        }, 30000);
    }
    return lastHealthCheck.status;
};

export default sequelize;
export { testConnection, checkHealth, getCachedHealth };