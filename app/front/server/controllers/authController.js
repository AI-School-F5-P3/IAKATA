import UsersModel from '../models/userModel.js';
import bcrypt from 'bcryptjs';
import jwt from 'jsonwebtoken';
import { TK_SECRET } from '../config.js';
import {SocketManager} from '../utils/socketManager.js';

const responseHandler = (res, statusCode, success, data = null, error = null) => {
    return res.status(statusCode).json({
        success,
        ...(data && { data }),
        ...(error && { error })
    });
};

export const register = async (req, res) => {
    try {
        const { email, password } = req.body;
        
        const existingUser = await UsersModel.findOne({ where: { email } });
        if (existingUser) {
            return responseHandler(res, 409, false, null, 'Email already registered');
        }

        const passwordHash = await bcrypt.hash(password, 10);
        const newUser = await UsersModel.create({
            ...req.body,
            password: passwordHash,
            isActive: true 
        });

        const token = jwt.sign(
            { userId: newUser.id, rol: newUser.rol },
            TK_SECRET,
            { expiresIn: '24h' }
        );

        const userData = {
            ...newUser.toJSON(),
            password: undefined,
            token
        };

        return responseHandler(res, 201, true, userData);
    } catch (error) {
        console.error('Registration error:', error);
        return responseHandler(res, 500, false, null, 'Server error during registration');
    }
};

export const login = async (req, res) => {
    try {
        const { email, password, forceLogin } = req.body;
        console.log('Login attempt:', { email, forceLogin });
        
        const user = await UsersModel.findOne({ 
            where: { email },
            attributes: { exclude: ['createdAt', 'updatedAt'] }
        });

        if (!user || !await bcrypt.compare(password, user.password)) {
            return responseHandler(res, 401, false, null, 'Invalid credentials');
        }

        if (user.isActive === true) {
            if (forceLogin) {
                SocketManager.currentSessionId = req.headers['x-session-id'];
                
                await SocketManager.forceGlobalLogout(user.id, user.email);
                
                await user.update({ 
                    isActive: false,
                    lastLogout: new Date()
                });
            } else {
                return responseHandler(res, 400, false, {
                    isActive: true,
                    userId: user.id,
                    email: user.email
                }, 'Active session exists');
            }
        }

        await user.update({ 
            isActive: true,
            lastLogin: new Date()
        });

        const userData = {
            id: user.id,
            email: user.email,
            rol: user.rol,
            name: user.name,
            isActive: true,
            token: jwt.sign({ 
                userId: user.id, 
                rol: user.rol,
                email: user.email,
                isActive: true,
                sessionCreated: Date.now()
            }, TK_SECRET, { expiresIn: '24h' })
        };

        return responseHandler(res, 200, true, userData);
    } catch (error) {
        console.error('Login error:', error);
        return responseHandler(res, 500, false, null, error.message);
    }
};

export const logout = async (req, res) => {
    try {
        const { userId } = req.body;
        
        if (!userId) {
            return responseHandler(res, 400, false, null, 'User ID required');
        }

        const user = await UsersModel.findByPk(userId);
        if (!user) {
            return responseHandler(res, 404, false, null, 'User not found');
        }

        await user.update({ 
            isActive: false,
            lastLogout: new Date()
        });

        console.log('User logged out:', userId, 'isActive:', false);

        await SocketManager.broadcast(SocketManager.EVENTS.USER, {
            userId,
            isActive: false,
            type: 'logout',
            timestamp: Date.now()
        });

        return responseHandler(res, 200, true, { 
            message: 'Logout successful',
            isActive: false
        });
    } catch (error) {
        console.error('Logout error:', error);
        return responseHandler(res, 500, false, null, error.message);
    }
};