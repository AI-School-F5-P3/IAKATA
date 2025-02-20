import express from 'express';
import { register, login, logout } from '../controllers/authController.js';
import { userValidator } from '../validators/usersValidator.js';
import handleValidationResults from '../helpers/validationHelper.js';

const router = express.Router();

router.post('/register', userValidator, handleValidationResults, register);
router.post('/login', login);
router.post('/logout', logout);

export default router;