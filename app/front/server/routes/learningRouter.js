import express from 'express';
import { getLearning, addLearnings, updateLearnings, getOneLearning, deleteLearning } from '../controllers/LearningController.js'; 
import { authRol } from '../middleware/rolMiddleware.js';
import handleValidationResults from '../helpers/validationHelper.js';
import processValidator from '../validators/processValidator.js';



const router = express.Router();

router.get('/', authRol(['user','admin']),  getLearning);

router.post('/', authRol(['user','admin']),  addLearnings);

router.put('/:id', authRol(['user','admin']), processValidator, handleValidationResults,  updateLearnings);

router.delete('/:id', authRol(['user','admin']),  deleteLearning);

router.get('/:id', authRol(['user','admin']),  getOneLearning);

export default router;