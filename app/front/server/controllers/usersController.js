import UsersModel from '../models/userModel.js';
import bcrypt from 'bcryptjs';
import sequelize from '../database/connection_db.js';

const HTTP_CODES = {
    OK: 200,
    CREATED: 201,
    BAD_REQUEST: 400,
    UNAUTHORIZED: 401,
    FORBIDDEN: 403,
    NOT_FOUND: 404,
    CONFLICT: 409,
    SERVER_ERROR: 500
};

const responseHandler = (res, statusCode, success, data = null, error = null) => {
    return res.status(statusCode).json({
        success,
        ...(data && { data }),
        ...(error && { error })
    });
};

const getUser = async (req, res) => {
    const { page = 1, limit = 10, sort = 'createdAt', order = 'DESC' } = req.query;
    try {
        const offset = (parseInt(page) - 1) * parseInt(limit);
        const users = await UsersModel.findAndCountAll({
            limit: parseInt(limit),
            offset,
            order: [[sort, order]],
            attributes: { exclude: ['password'] }
        });

        return responseHandler(res, HTTP_CODES.OK, true, {
            users: users.rows,
            total: users.count,
            currentPage: parseInt(page),
            totalPages: Math.ceil(users.count / parseInt(limit))
        });
    } catch (error) {
        return responseHandler(res, HTTP_CODES.SERVER_ERROR, false, null, 'Error retrieving users');
    }
};

const deleteUser = async (req, res) => {
    const transaction = await sequelize.transaction();
    try {
        const user = await UsersModel.findByPk(req.params.id);
        if (!user) {
            await transaction.rollback();
            return responseHandler(res, HTTP_CODES.NOT_FOUND, false, null, 'User not found');
        }

        await user.destroy({ transaction });
        await transaction.commit();
        return responseHandler(res, HTTP_CODES.OK, true, { message: 'User deleted successfully' });
    } catch (error) {
        await transaction.rollback();
        return responseHandler(res, HTTP_CODES.SERVER_ERROR, false, null, 'Error deleting user');
    }
};

const createUser = async (req, res) => {
    const transaction = await sequelize.transaction();
    try {
        const { password, email, ...userData } = req.body;
        
        const existingUser = await UsersModel.findOne({ where: { email } });
        if (existingUser) {
            await transaction.rollback();
            return responseHandler(res, HTTP_CODES.CONFLICT, false, null, 'Email already exists');
        }

        const hashedPassword = await bcrypt.hash(password, 10);
        const newUser = await UsersModel.create({
            ...userData,
            email,
            password: hashedPassword
        }, { transaction });

        const { password: _, ...userResponse } = newUser.toJSON();
        await transaction.commit();
        return responseHandler(res, HTTP_CODES.CREATED, true, userResponse);
    } catch (error) {
        await transaction.rollback();
        return responseHandler(res, HTTP_CODES.SERVER_ERROR, false, null, 'Error creating user');
    }
};

const updateUser = async (req, res) => {
    const transaction = await sequelize.transaction();
    try {
        const user = await UsersModel.findByPk(req.params.id);
        if (!user) {
            await transaction.rollback();
            return responseHandler(res, HTTP_CODES.NOT_FOUND, false, null, 'User not found');
        }

        const { password, ...updateData } = req.body;
        if (password) {
            updateData.password = await bcrypt.hash(password, 10);
        }

        await user.update(updateData, { transaction });
        const { password: _, ...userResponse } = user.toJSON();
        
        await transaction.commit();
        return responseHandler(res, HTTP_CODES.OK, true, userResponse);
    } catch (error) {
        await transaction.rollback();
        return responseHandler(res, HTTP_CODES.SERVER_ERROR, false, null, 'Error updating user');
    }
};

const getOneUser = async (req, res) => {
    const transaction = await sequelize.transaction();
    try {
        const user = await UsersModel.findByPk(req.params.id, {
            attributes: { exclude: ['password'] }
        });

        if (!user) {
            await transaction.rollback();
            return responseHandler(res, HTTP_CODES.NOT_FOUND, false, null, 'User not found');
        }

        await transaction.commit();
        return responseHandler(res, HTTP_CODES.OK, true, user);
    } catch (error) {
        await transaction.rollback();
        return responseHandler(res, HTTP_CODES.SERVER_ERROR, false, null, 'Error retrieving user');
    }
};

export { getUser, deleteUser, createUser, updateUser, getOneUser };