import { TK_SECRET } from '../config.js';
import jwt from 'jsonwebtoken';

const ERROR_CODES = {
    NO_AUTH: 'No authorization header',
    INVALID_TOKEN: 'Invalid token',
    UNAUTHORIZED: 'Unauthorized role',
    SERVER_ERROR: 'Internal server error'
};

export const authRol = (requiredRoles) => async (req, res, next) => {
    try {
        if (!req.headers?.authorization) {
            return res.status(401).json({
                success: false,
                error: ERROR_CODES.NO_AUTH,
                code: 'NO_AUTH_HEADER'
            });
        }

        const token = req.headers.authorization.split(' ')[1];
        
        try {
            const decoded = jwt.verify(token, TK_SECRET);
            
            if (!decoded.rol || !requiredRoles.includes(decoded.rol)) {
                return res.status(403).json({
                    success: false,
                    error: ERROR_CODES.UNAUTHORIZED,
                    code: 'INVALID_ROLE'
                });
            }

            // Cache control headers
            res.setHeader('Cache-Control', 'private, no-cache, no-store, must-revalidate');
            res.setHeader('Pragma', 'no-cache');
            res.setHeader('Expires', '0');

            next();
        } catch (jwtError) {
            return res.status(403).json({
                success: false,
                error: ERROR_CODES.INVALID_TOKEN,
                code: 'INVALID_TOKEN'
            });
        }
    } catch (error) {
        console.error('Role Middleware Error:', error);
        return res.status(500).json({
            success: false,
            error: ERROR_CODES.SERVER_ERROR,
            code: 'SERVER_ERROR'
        });
    }
};