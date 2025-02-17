import express from 'express';
import { getMentalContrast, addMentalContrast, updateMentalContrast, getOneMentalContrast, deleteMentalContrast } from '../controllers/MentalContrastController.js'; 
import { authRol } from '../middleware/rolMiddleware.js';
import handleValidationResults from '../helpers/validationHelper.js';

const router = express.Router();

router.get('/', authRol(['user','admin']),  getMentalContrast);

router.post('/', authRol(['user','admin']),  addMentalContrast);

router.put('/:id', authRol(['user','admin']), handleValidationResults,  updateMentalContrast);

router.delete('/:id', authRol(['user','admin']),  deleteMentalContrast);

router.get('/:id', authRol(['user','admin']),  getOneMentalContrast);

export default router;