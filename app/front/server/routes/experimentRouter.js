import express from 'express';
import { getExperiment, addExperiment, updateExperiment, getOneExperiment, deleteExperiment } from '../controllers/ExperimentController.js';
import { authRol } from '../middleware/rolMiddleware.js';
import handleValidationResults from '../helpers/validationHelper.js';
import processValidator from '../validators/processValidator.js';


const router = express.Router();

router.get('/', authRol(['user','admin']),  getExperiment);

router.post('/', authRol(['user','admin']),  addExperiment);

router.put('/:id', authRol(['user','admin']), processValidator, handleValidationResults, updateExperiment);

router.delete('/:id', authRol(['user','admin']),  deleteExperiment);

router.get('/:id', authRol(['user','admin']),  getOneExperiment);

export default router;