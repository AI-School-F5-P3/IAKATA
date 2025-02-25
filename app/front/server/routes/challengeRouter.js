import express from 'express';
import { getChallenge, addChallenge, updateChallenge, getOneChallenge, deleteChallenge, searchChallenge, validateChallengePassword } from '../controllers/ChallengeController.js';
import authToken from '../middleware/autMiddleware.js';
import { authRol } from '../middleware/rolMiddleware.js';
import handleValidationResults from '../helpers/validationHelper.js';
import processValidator from '../validators/processValidator.js';

import axios from 'axios';


const router = express.Router();

router.get('/', authRol(['user','admin']),  getChallenge);

router.post('/', authRol(['user','admin']),  addChallenge);

router.put('/:id', authRol(['user','admin']), processValidator, handleValidationResults,  updateChallenge);

router.delete('/:id', authRol(['user','admin']),  deleteChallenge);

router.get('/:id', authRol(['user','admin']),  getOneChallenge);

router.get('/search', authRol(['user','admin']),  searchChallenge);

router.post('/:id/validate-password', authToken, authRol(['user','admin']), validateChallengePassword);

router.post('/ai', async (req, res) => {
    try {
      const {idForm, description} = req.body;
      const filteredData = {idForm, description };

      const response = await axios.post('http://localhost:8001/board/ai', filteredData); // FastAPI
      res.json(response.data);
    } catch (error) {
      console.error('Error en la API FastAPI:', error);
      res.status(500).json({ error: 'Error al comunicarse con la IA' });
    }
  });

export default router;