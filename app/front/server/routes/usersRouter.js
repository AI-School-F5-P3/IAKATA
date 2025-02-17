import express from 'express';
import { getUser, createUser, updateUser, deleteUser, getOneUser } from '../controllers/usersController.js';
import { authRol } from '../middleware/rolMiddleware.js';
import { checkActiveSession } from '../middleware/sessionCheck.js';
import { userValidator, updateUserValidator } from '../validators/usersValidator.js';
import handleValidationResults from '../validators/validateResult.js';

const userRouter = express.Router();

userRouter.use(checkActiveSession);

userRouter.get('/', getUser);
userRouter.get('/:id', getOneUser);
userRouter.post('/', 
    userValidator,
    handleValidationResults,
    createUser
);

userRouter.put('/:id',
    authRol(['admin']),
    updateUserValidator,
    handleValidationResults,
    updateUser
);

userRouter.delete('/:id',
    authRol(['admin']),
    deleteUser
);

export default userRouter;