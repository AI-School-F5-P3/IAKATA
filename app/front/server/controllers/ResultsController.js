import ResultsModel from '../models/ResultsModel.js';

export const getResults = async (request, response) =>{
    try {
        const result = await ResultsModel.findAll();
        response.status(200).json(result);
    } catch(error) {
        response.status(500).json({message: error.message});
    }
}

export const addResult = async (req, res) => {
    try {
        let count = 1;
        const idResult  = await ResultsModel.findOne({order: [['id', 'DESC']]});
        if (idResult) {
            const numberId = parseInt(idResult.id.slice(2));
            count = numberId + 1;
        }
        const formatted_Id = 'RE' + count.toString().padStart(3, '0');

        const addResult = await ResultsModel.create({  id: formatted_Id, ...req.body, });
        res.status(201).json(addResult);
    }catch(error){
        console.log(error)
        return res.status(500).send({ error: 'Internal Server Error' });
    }
}

export const updateResult = async (req, res) => {   
    const resultId = req.params.id; 
    try {
        await ResultsModel.findOne({where: {id: resultId}});
        if (!resultId) {
            return res.status(404).json({ message: 'resultado no encontrado' });
        }
        await ResultsModel.update(req.body,{  where: {id: resultId}});
        const updatedResult = await ResultsModel.findOne({ where: { id: resultId } });
        res.status(200).json(updatedResult);
    } catch(error) {
        res.status(500).json({message: error.message});
    }   
}

export const getOneResult = async (req, res) =>{
    const resultId = req.params.id;
    try {
        const result = await ResultsModel.findOne({ where: {id: resultId }});
        res.status(200).json(result);
    } catch(error) {
        res.status(500).json({message: error.message});
    }   
}

export const deleteResult = async (req, res) => {
    const resultId = req.params.id;
    try {
        const result = await ResultsModel.findOne({ 
            where: { id: resultId} 
        });
        if (!result ) {
            return res.status(404).json({ message: 'Resultado no encontrado' });
        }
        await ResultsModel.destroy({ where: {id: resultId } });
        return res.status(201).send({
            id: resultId,
            deleted: true,
            experiment_id: result.experiment_id
        });

    } catch (error) {
        return res.status(500).send({ error: 'Internal Server Error' });
    }
};