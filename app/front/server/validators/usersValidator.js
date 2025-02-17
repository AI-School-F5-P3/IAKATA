import { check } from 'express-validator';
import UsersModel from '../models/userModel.js';

const passwordStrengthScore = (password) => {
    let score = 0;
    if (password.length >= 12) score += 2;
    if (/[!@#$%^&*(),.?":{}|<>]{2,}/.test(password)) score += 2;
    if (/\d{2,}/.test(password)) score += 2;
    return score;
};

export const userValidator = [
    check('name')
        .trim()
        .notEmpty().withMessage('Name is required.')
        .isLength({ min: 2, max: 50 }).withMessage('Name must be between 2 and 50 characters.')
        .matches(/^[a-zA-Z\s]*$/).withMessage('Name can only contain letters and spaces.')
        .customSanitizer(value => value.replace(/\s+/g, ' ')),

    check('email')
        .trim()
        .notEmpty().withMessage('Email is required.')
        .isEmail().withMessage('Invalid email format.')
        .normalizeEmail()
        .custom(async (email) => {
            const existingUser = await UsersModel.findOne({ where: { email } });
            if (existingUser) {
                throw new Error('Email already registered');
            }
            return true;
        }),

    check('password')
        .notEmpty().withMessage('Password is required.')
        .isLength({ min: 8 }).withMessage('Password must be at least 8 characters long.')
        .matches(/[a-z]/).withMessage('Password must contain at least one lowercase letter.')
        .matches(/[A-Z]/).withMessage('Password must contain at least one uppercase letter.')
        .matches(/[0-9]/).withMessage('Password must contain at least one digit.')
        .matches(/[!@#$%^&*(),.?":{}|<>]/).withMessage('Password must contain at least one special character (!@#$%^&*(),.?":{}|<>).')
        .custom((password) => {
            if (passwordStrengthScore(password) < 4) {
                throw new Error('Password is too weak');
            }
            return true;
        }),

    check('rol')
        .optional()
        .isIn(['user', 'admin']).withMessage('Rol field must be either "user" or "admin".')
        .default('user')
];

export const updateUserValidator = [
    ...userValidator.map(validation => validation.optional())
];