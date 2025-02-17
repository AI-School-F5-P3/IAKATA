import express from 'express';
import { getTribe, addTribe, updateTribe, getOneTribe, deleteTribe } from '../controllers/TribeController.js';
import { authRol } from '../middleware/rolMiddleware.js';
import handleValidationResults from '../helpers/validationHelper.js';

const router = express.Router();

router.get('/', authRol(['user','admin']),  getTribe);

router.post('/', authRol(['user','admin']),  addTribe);

router.put('/:id', authRol(['user','admin']), handleValidationResults,  updateTribe);

router.delete('/:id', authRol(['user','admin']),  deleteTribe);

router.get('/:id', authRol(['user','admin']),  getOneTribe);

export default router;