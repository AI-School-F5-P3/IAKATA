import express from 'express';
import { getProcess, addProcess, updateProcess, getOneProcess, deleteProcess } from '../controllers/ProcessController.js';
import { authRol } from '../middleware/rolMiddleware.js';
import handleValidationResults from '../helpers/validationHelper.js';
import processValidator from '../validators/processValidator.js';


const router = express.Router();

router.get('/', authRol(['user','admin']), getProcess);

router.post('/', authRol(['user','admin']), addProcess);

router.put('/:id', authRol(['user','admin']), processValidator, handleValidationResults, updateProcess);

router.delete('/:id',  authRol(['user','admin']), deleteProcess);

router.get('/:id', authRol(['user','admin']), getOneProcess);

export default router;