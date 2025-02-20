import jwt from 'jsonwebtoken';
import rateLimit from 'express-rate-limit';
import { TK_SECRET } from '../config.js';

const limiter = rateLimit({
    windowMs: 15 * 60 * 1000, 
    max: 100 
});

const tokenBlacklist = new Set();

const securityHeaders = {
    'X-Content-Type-Options': 'nosniff',
    'X-Frame-Options': 'DENY',
    'X-XSS-Protection': '1; mode=block'
};

const authenticateToken = async (req, res, next) => {
    Object.entries(securityHeaders).forEach(([key, value]) => {
        res.setHeader(key, value);
    });

    try {
        const authHeader = req.headers['authorization'];
        if (!authHeader) {
            return res.status(401).json({
                error: 'No authentication token provided',
                code: 'NO_TOKEN'
            });
        }

        const token = authHeader.split(' ')[1];
        if (!token) {
            return res.status(401).json({
                error: 'Invalid token format',
                code: 'INVALID_TOKEN_FORMAT'
            });
        }

        if (tokenBlacklist.has(token)) {
            return res.status(401).json({
                error: 'Token has been revoked',
                code: 'TOKEN_REVOKED'
            });
        }

        const decoded = jwt.verify(token, TK_SECRET);

        if (!decoded?.userId || !decoded?.rol) {
            return res.status(403).json({
                error: 'Invalid token payload',
                code: 'INVALID_PAYLOAD'
            });
        }

        const currentTimestamp = Math.floor(Date.now() / 1000);
        if (decoded.exp && currentTimestamp >= decoded.exp) {
            return res.status(401).json({
                error: 'Token expired',
                code: 'TOKEN_EXPIRED'
            });
        }

        req.user = {
            userId: decoded.userId,
            rol: decoded.rol,
            email: decoded.email,
            tokenExp: decoded.exp
        };

        next();
    } catch (error) {
        if (error.name === 'JsonWebTokenError') {
            return res.status(403).json({
                error: 'Invalid token',
                code: 'INVALID_TOKEN'
            });
        }

        if (error.name === 'TokenExpiredError') {
            return res.status(401).json({
                error: 'Token expired',
                code: 'TOKEN_EXPIRED'
            });
        }

        return res.status(500).json({
            error: 'Authentication error',
            code: 'AUTH_ERROR'
        });
    }
};

export const revokeToken = (token) => tokenBlacklist.add(token);
export const isTokenRevoked = (token) => tokenBlacklist.has(token);

export default { authenticateToken, limiter };