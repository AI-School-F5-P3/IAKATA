import express from 'express';
import { getObstacle, addObstacle, updateObstacle, getOneObstacle, deleteObstacle } from '../controllers/ObstacleController.js'; 
import { authRol } from '../middleware/rolMiddleware.js';
import handleValidationResults from '../helpers/validationHelper.js';

const router = express.Router();

router.get('/', authRol(['user','admin']),  getObstacle);

router.post('/', authRol(['user','admin']),  addObstacle);

router.put('/:id', authRol(['user','admin']), handleValidationResults,  updateObstacle);

router.delete('/:id', authRol(['user','admin']),  deleteObstacle);

router.get('/:id', authRol(['user','admin']),  getOneObstacle);

export default router;