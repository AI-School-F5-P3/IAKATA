import TaskModel from '../models/TaskModel.js';

export const getTask = async (request, response) =>{
    try {
        const task = await TaskModel.findAll();
        response.status(200).json(task);
    } catch(error) {
        response.status(500).json({message: error.message});
    }
}

export const addTask = async (req, res) => {
    try {
        
        let count = 1;
        const idTask = await TaskModel.findOne({order: [['id', 'DESC']]});
       
        if (idTask) {
            const numberId = parseInt(idTask.id.slice(1));
            count = numberId + 1;
        } 
        const formatted_Id = 'T' + count.toString().padStart(3, '0');

        const addTask = await TaskModel.create({  id: formatted_Id, ...req.body });
        res.status(201).json(addTask);
    }catch(error){
        console.log(error)
        return res.status(500).send({ error: 'Internal Server Error' });
    }
}

export const updateTask = async (req, res) => {   
    const taskId = req.params.id; 
    try {
        await TaskModel.findOne({where: {id: taskId}});
        if (!taskId) {
            return res.status(404).json({ message: 'Tarea no encontrada' });
        }
        await TaskModel.update(req.body,{  where: {id: taskId}});
        const updatedTask = await TaskModel.findOne({ where: { id: taskId } });
        res.status(200).json(updatedTask);
    } catch(error) {
        res.status(500).json({message: error.message});
    }   
}

export const getOneTask = async (req, res) =>{
    const taskId = req.params.id;
    try {
        const task = await TaskModel.findOne({ where: {id: taskId }});
        res.status(200).json(task);
    } catch(error) {
        res.status(500).json({message: error.message});
    }   
}

export const deleteTask = async (req, res) => {
    const taskId = req.params.id;
    try {
        const task = await TaskModel.findOne({ 
            where: { id: taskId } 
        });
        if (!task ) {
            return res.status(404).json({ message: 'Tarea no encontrada' });
        }
        await TaskModel.destroy({ where: {id: taskId  } });
        return res.status(201).send({
            id: taskId ,
            deleted: true,
            experiment_id: task.experiment_id
        });

    } catch (error) {
        return res.status(500).send({ error: 'Internal Server Error' });
    }
};