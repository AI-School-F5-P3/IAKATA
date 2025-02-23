import express from 'express';
import { getTask, addTask, updateTask, getOneTask, deleteTask } from '../controllers/TaskController.js'; 
import { authRol } from '../middleware/rolMiddleware.js';
import handleValidationResults from '../helpers/validationHelper.js';
import processValidator from '../validators/processValidator.js';


const router = express.Router();

router.get('/', authRol(['user','admin']),  getTask);

router.post('/', authRol(['user','admin']),  addTask);

router.put('/:id', authRol(['user','admin']), processValidator, handleValidationResults,  updateTask);

router.delete('/:id', authRol(['user','admin']),  deleteTask);

router.get('/:id', authRol(['user','admin']),  getOneTask);

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