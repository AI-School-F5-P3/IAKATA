import express from 'express';
import { getTask, addTask, updateTask, getOneTask, deleteTask } from '../controllers/TaskController.js'; 
import { authRol } from '../middleware/rolMiddleware.js';
import handleValidationResults from '../helpers/validationHelper.js';
import processValidator from '../validators/processValidator.js';


const router = express.Router();

router.get('/', authRol(['user','admin']),  getTask);

router.post('/', authRol(['user','admin']),  addTask);

router.put('/:id', authRol(['user','admin']), processValidator, handleValidationResults,  updateTask);

router.delete('/:id', authRol(['user','admin']),  deleteTask);

router.get('/:id', authRol(['user','admin']),  getOneTask);

export default router;