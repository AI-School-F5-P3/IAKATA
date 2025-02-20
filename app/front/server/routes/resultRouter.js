import express from 'express';
import { getResults, addResult, updateResult, getOneResult, deleteResult } from '../controllers/ResultsController.js';
import { authRol } from '../middleware/rolMiddleware.js';
import handleValidationResults from '../helpers/validationHelper.js';
import processValidator from '../validators/processValidator.js';


const router = express.Router();

router.get('/', authRol(['user','admin']),  getResults);

router.post('/', authRol(['user','admin']), processValidator, handleValidationResults,  addResult);

router.put('/:id', authRol(['user','admin']),  updateResult);

router.delete('/:id', authRol(['user','admin']),  deleteResult);

router.get('/:id', authRol(['user','admin']),  getOneResult);

export default router;