import express from 'express';
import { getActualState, addActualState, updateActualState, getOneActualState, deleteActualState, searchActualState  } from '../controllers/ActualStateController.js';
import { authRol } from '../middleware/rolMiddleware.js';
import handleValidationResults from '../helpers/validationHelper.js';
import processValidator from '../validators/processValidator.js';


const router = express.Router();

router.get('/', authRol(['user','admin']),  getActualState);

router.post('/', authRol(['user','admin']),  addActualState);

router.put('/:id', authRol(['user','admin']), processValidator, handleValidationResults,  updateActualState);

router.delete('/:id', authRol(['user','admin']),  deleteActualState);

router.get('/:id', authRol(['user','admin']),  getOneActualState);

router.get('/search', authRol(['user','admin']),  searchActualState);

export default router;