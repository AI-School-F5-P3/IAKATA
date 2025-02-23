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