import LearningsModel from '..//models/LearningsModel.js';

export const getLearning = async (request, response) =>{
    try {
        const learning = await LearningsModel.findAll();
        response.status(200).json(learning);
    } catch(error) {
        response.status(500).json({message: error.message});
    }
}

export const addLearnings = async (req, res) => {
    try {
        let count = 1;
        const idLearning = await LearningsModel.findOne({order: [['id', 'DESC']]});
        if (idLearning) {
            const numberId = parseInt(idLearning.id.slice(2));
            count = numberId + 1;
        }
        const formatted_Id = 'AP' + count.toString().padStart(3, '0');     

        const addResults = await LearningsModel.create({  id: formatted_Id, ...req.body });
        res.status(201).json(addResults);
    }catch(error){
        return res.status(500).send({ error: 'Internal Server Error' });
    }
}

export const updateLearnings = async (req, res) => {   
    const learningId = req.params.id; 
    try {
        await LearningsModel.findOne({where: {id: learningId }});
        if (!learningId) {
            return res.status(404).json({ message: 'Aprendizaje no encontrado' });
        }
        await LearningsModel.update(req.body,{  where: {id: learningId }});
        const updatedLearning = await LearningsModel.findOne({ where: { id: learningId } });
        res.status(200).json(updatedLearning);
    } catch(error) {
        res.status(500).json({message: error.message});
    }   
}


export const getOneLearning = async (req, res) =>{
    const learningId = req.params.id;
    try {
        const learning = await LearningsModel.findOne({ where: {id: learningId  }});
        res.status(200).json(learning);
    } catch(error) {
        res.status(500).json({message: error.message});
    }   
}

export const deleteLearning = async (req, res) => {
    const learningId = req.params.id;
    try {
        const learning = await LearningsModel.findOne({ 
            where: { id: learningId} 
        });
        
        if (!learning ) {
            return res.status(404).json({ message: 'Aprendizaje no encontrado' });
        }

        await LearningsModel.destroy({ where: { id:learningId } });
        res.status(200).json({ 
            id: learningId,
            deleted: true,
            results_id: learning.results_id
        });
    } catch (error) {
        res.status(500).json({ message: error.message });
    }
};