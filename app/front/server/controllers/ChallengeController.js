import TribeModel from "../models/TribeModel.js";
import ChallengeModel from "../models/ChallengeModel.js";
import { Op, where } from 'sequelize';

export const getChallenge = async (request, response) => {
    try {
        const challenge = await ChallengeModel.findAll({
            include: [{
                model: TribeModel,
                as: 'Tribe',
                attributes: ['password']
            }]
        });
        response.status(200).json(challenge);
    } catch (error) {
        response.status(500).json({ message: error.message });
    }
}


export const addChallenge = async (req, res) => {
    try {

        const idChallenge = await ChallengeModel.findOne({ order: [['id', 'DESC']] });

        let count = 1;
        if (idChallenge) {
            const numberId = parseInt(idChallenge.id.slice(1));
            count = numberId + 1;
        }
        let tribeId;
        const formatted_Id = 'R' + count.toString().padStart(3, '0');

        const tribe = await TribeModel.findOne({ order: [['id', 'DESC']] });
        tribeId = tribe.id;

        const addChallenge = await ChallengeModel.create({ id: formatted_Id, ...req.body, tribe_id: tribeId });
        res.status(201).json(addChallenge);
    } catch (error) {
        return res.status(500).send({ error: 'Internal Server Error' + error });
    }
}

export const updateChallenge = async (req, res) => {
    const challengeId = req.params.id;
    try {
        const challenge = await ChallengeModel.findOne({ where: { id: challengeId } });
        if (!challenge) {
            return res.status(404).json({ message: 'Reto no encontrado' });
        }
        await ChallengeModel.update(req.body, { where: { id: challengeId } });
        const updatedChallenge = await ChallengeModel.findOne({ where: { id: challengeId },
            include: [{
                model: TribeModel,
                as: 'Tribe',
                attributes: ['password']
            }]
        }); 
        res.status(200).json({updatedChallenge});
    } catch (error) {
        res.status(500).json({ message: error.message });
    }
}

export const getOneChallenge = async (req, res) => {
    const challengeId = req.params.id;
    try {
        const challenge = await ChallengeModel.findOne({ where: { id: challengeId } });
        if (!challenge) {
            return res.status(404).json({ message: 'Challenge no encontrado' });
        }
        res.status(200).json(challenge);
    } catch (error) {
        res.status(500).json({ message: error.message });
    }
}

export const deleteChallenge = async (req, res) => {
    const challengeId = req.params.id;
    try {
        const challenge = await ChallengeModel.findOne({where: {id: challengeId}});
        if (!challenge) {
            return res.status(404).json({ message: 'Reto no encontrado' });
        }
        await ChallengeModel.destroy({ where: { id: challengeId } });
        return res.status(201).send({
            id: challengeId,
            deleted: true,
            tribe_id: challenge.tribe_id
         });

    } catch (error) {
        return res.status(500).send({ error: 'Internal Server Error' });
    }
};

export const searchChallenge = async (req, res) => {
    const searchText = req.query.texto;

    try {
        const challenges = await ChallengeModel.findAll({
            where: {
                [Op.or]: [
                    { name: { [Op.iLike]: `%${searchText}%` } },
                    { description: { [Op.iLike]: `%${searchText}%` } }
                ]
            }
        });

        res.status(200).json(challenges);
    } catch (error) {
        console.error('Error searching challenges:', error);
        res.status(500).json({ message: 'Internal Server Error' });
    }
}


export const validateChallengePassword = async (req, res) => {
    const { id } = req.params;
    const { password } = req.body;

    try {
        const challenge = await ChallengeModel.findOne({
            where: { id },
            include: [{
                model: TribeModel,
                as: 'Tribe',
                attributes: ['password']
            }]
        });

        if (!challenge?.Tribe?.password) {
            return res.json({ isValid: true });
        }

        const isValid = challenge.Tribe.password === password;

        res.json({ isValid });
    } catch (error) {
        res.status(500).json({ message: error.message });
    }
};