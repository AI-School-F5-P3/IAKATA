import ExperimentModel from '../models/ExperimentModel.js';

export const getExperiment = async (request, response) =>{
    try {
        const experiment = await ExperimentModel.findAll();
        response.status(200).json(experiment);
    } catch(error) {
        response.status(500).json({message: error.message});
    }
}

export const addExperiment = async (req, res) => {
    try {
        
        let count = 1;
        const idExperiment= await ExperimentModel.findOne({order: [['id', 'DESC']]});
       
        if (idExperiment) {
            const numberId = parseInt(idExperiment.id.slice(2));
            count = numberId + 1;
        } 
        const formatted_Id = 'Ex' + count.toString().padStart(3, '0');
      
        const addExperiment = await ExperimentModel.create({  id: formatted_Id, ...req.body });
        res.status(201).json(addExperiment);
    }catch(error){
        console.log(error)
        return res.status(500).send({ error: 'Internal Server Error' });
    }
}

export const updateExperiment = async (req, res) => {   
    const experimentId = req.params.id; 
    try {
        await ExperimentModel.findOne({where: {id: experimentId}});
        if (!experimentId) {
            return res.status(404).json({ message: 'Experimento no encontrado' });       
        }
        await ExperimentModel.update(req.body,{  where: {id: experimentId}});
        const updatedExperiment = await ExperimentModel.findOne({ where: { id: experimentId } });
        res.status(200).json(updatedExperiment);
    } catch(error) {
        res.status(500).json({message: error.message});
    }   
}

export const getOneExperiment = async (req, res) =>{
    const  experimentId = req.params.id;
    try {
        const experiment = await ExperimentModel.findOne({ where: {id: experimentId }});
        res.status(200).json(experiment);
    } catch(error) {
        res.status(500).json({message: error.message});
    }   
}

export const deleteExperiment = async (req, res) => {
    const  experimentId = req.params.id;
    try {
        const experiment = await ExperimentModel.findOne({ where: {id: experimentId }});
        if (!experiment) {
            return res.status(404).json({ message: 'Experimento no encontrado' });
        }
        await ExperimentModel.destroy({ where: {id: experimentId } });
        return res.status(201).send({
            id: experimentId,
            deleted: true,
            hyphotesis_id: experiment.hyphotesis_id
        });

    } catch (error) {
        return res.status(500).send({ error: 'Internal Server Error' });
    }
};