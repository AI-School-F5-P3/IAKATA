import UsersModel from '../models/userModel.js';

const responseHandler = (res, statusCode, success, data = null, error = null) => {
    return res.status(statusCode).json({
        success,
        ...(data && { data }),
        ...(error && { error })
    });
};

export const checkActiveSession = async (req, res, next) => {
    try {
        const userId = req.user?.id;

        if (!userId) {
            return responseHandler(res, 401, false, null, 'Authentication required');
        }

        const user = await UsersModel.findByPk(userId);

        if (!user || !user.isActive) {
            return responseHandler(res, 401, false, null, 'Session expired');
        }

        req.user = user;
        next();

    } catch (error) {
        console.error('Session verification error:', error);
        return responseHandler(res, 500, false, null, 'Error verifying session');
    }
};

export default checkActiveSession;