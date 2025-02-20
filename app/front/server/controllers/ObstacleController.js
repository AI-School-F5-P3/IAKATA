import ObstacleModel from '../models/ObstacleModel.js';

export const getObstacle = async (request, response) =>{
    try {
        const obstacle = await ObstacleModel.findAll();
        response.status(200).json(obstacle);
    } catch(error) {
        response.status(500).json({message: error.message});
    }
}

export const addObstacle = async (req, res) => {
    try {
        
        let count = 1;
        const idObstacle = await ObstacleModel.findOne({order: [['id', 'DESC']]});
       
        if (idObstacle) {
            const numberId = parseInt(idObstacle.id.slice(2));
            count = numberId + 1;
        } 
        const formatted_Id = 'OB' + count.toString().padStart(3, '0');

        const addObstacle = await ObstacleModel.create({ id: formatted_Id, ...req.body });
        res.status(201).json(addObstacle);
    }catch(error){
        console.log(error)
        return res.status(500).send({ error: 'Internal Server Error' });
    }
}

export const updateObstacle = async (req, res) => {   
    const obstacleId = req.params.id; 
    try {
        const obstacle = await ObstacleModel.findOne({ where: { id: obstacleId } });
        if (!obstacle) {
            return res.status(404).json({ message: 'Obstacle not found' });
        }

        await ObstacleModel.update(req.body, { where: { id: obstacleId } });
        const updatedObstacle = await ObstacleModel.findOne({ where: { id: obstacleId } });
        
        res.status(200).json(updatedObstacle);
    } catch(error) {
        res.status(500).json({ message: error.message });
    }   
};

export const getOneObstacle = async (req, res) =>{
    const  obstacleId = req.params.id;
    try {
        const obstacle = await ObstacleModel.findOne({ where: {id:  obstacleId }});
        res.status(200).json(obstacle);
    } catch(error) {
        res.status(500).json({message: error.message});
    }   
}

export const deleteObstacle = async (req, res) => {
    const obstacleId = req.params.id;
    try {
        const obstacle = await ObstacleModel.findOne({ where: { id: obstacleId } });
        if (!obstacle) {
            return res.status(404).json({ message: 'Obstacle not found' });
        }

        await ObstacleModel.destroy({ where: { id: obstacleId } });
        
        res.status(200).json({
            id: obstacleId,
            deleted: true,
            target_state_id: obstacle.target_state_id
        });
    } catch (error) {
        res.status(500).json({ message: error.message });
    }
};