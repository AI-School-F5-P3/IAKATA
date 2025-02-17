import express from 'express';
import { getTargetState, addTargetState, updateTargetState, getOneTargetState, deleteTargetState } from '../controllers/TargetStateController.js'; 
import { authRol } from '../middleware/rolMiddleware.js';
import handleValidationResults from '../helpers/validationHelper.js';
import processValidator from '../validators/processValidator.js';


const router = express.Router();

router.get('/', authRol(['user','admin']),  getTargetState);

router.post('/', authRol(['user','admin']),  addTargetState);

router.put('/:id', authRol(['user','admin']), processValidator, handleValidationResults,  updateTargetState);

router.delete('/:id', authRol(['user','admin']),  deleteTargetState);

router.get('/:id', authRol(['user','admin']),  getOneTargetState);

export default router;