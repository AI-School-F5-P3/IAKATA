import jwt from 'jsonwebtoken';
import { TK_SECRET } from '../config.js';
import UsersModel from '../models/userModel.js';

const ERROR_CODES = {
    NO_TOKEN: 'No authorization token provided',
    INVALID_TOKEN: 'Invalid token format',
    TOKEN_EXPIRED: 'Token has expired',
    USER_NOT_FOUND: 'User not found',
    SERVER_ERROR: 'Internal server error',
    INACTIVE_SESSION: 'Session is not active'
};

const authToken = async (req, res, next) => {
    try {
        const authHeader = req.headers.authorization;
        if (!authHeader?.startsWith('Bearer ')) {
            return res.status(401).json({
                success: false,
                error: ERROR_CODES.NO_TOKEN,
                code: 'NO_TOKEN'
            });
        }

        const token = authHeader.split(' ')[1];
        
        try {
            const decoded = jwt.verify(token, TK_SECRET);
            
            if (!decoded.userId || !decoded.rol) {
                return res.status(403).json({
                    success: false,
                    error: ERROR_CODES.INVALID_TOKEN,
                    code: 'INVALID_PAYLOAD'
                });
            }

            const user = await UsersModel.findByPk(decoded.userId);
            
            if (!user) {
                return res.status(404).json({
                    success: false,
                    error: ERROR_CODES.USER_NOT_FOUND,
                    code: 'USER_NOT_FOUND'
                });
            }

            if (!user.isActive) {
                return res.status(401).json({
                    success: false,
                    error: ERROR_CODES.INACTIVE_SESSION,
                    code: 'INACTIVE_SESSION'
                });
            }

            req.user = {
                id: user.id,
                rol: user.rol,
                isActive: user.isActive
            };

            res.setHeader('Cache-Control', 'no-store');
            res.setHeader('X-Content-Type-Options', 'nosniff');
            
            next();
        } catch (jwtError) {
            return res.status(403).json({
                success: false,
                error: ERROR_CODES.INVALID_TOKEN,
                code: 'INVALID_TOKEN'
            });
        }
    } catch (error) {
        console.error('Auth Middleware Error:', error);
        return res.status(500).json({
            success: false,
            error: ERROR_CODES.SERVER_ERROR,
            code: 'SERVER_ERROR'
        });
    }
};

export default authToken;