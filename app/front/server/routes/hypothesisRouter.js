import express from 'express';
import { getHypothesis, addHypothesis, updateHypothesis, getOneHypothesis, deleteHypothesis } from '../controllers/HypothesisController.js'; 
import { authRol } from '../middleware/rolMiddleware.js';
import handleValidationResults from '../helpers/validationHelper.js';
import processValidator from '../validators/processValidator.js';



const router = express.Router();

router.get('/', authRol(['user','admin']),  getHypothesis);

router.post('/', authRol(['user','admin']),  addHypothesis);

router.put('/:id', authRol(['user','admin']), processValidator, handleValidationResults, updateHypothesis);

router.delete('/:id', authRol(['user','admin']),  deleteHypothesis);

router.get('/:id', authRol(['user','admin']),  getOneHypothesis);

export default router;