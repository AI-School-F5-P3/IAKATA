const addUserMiddleware = (req, res, next) => {
    try {
        const userId = req.user?.id || req.headers['x-user-id'];

        if (!userId && !['GET', 'DELETE'].includes(req.method)) {
            return res.status(401).json({
                success: false,
                error: 'User ID not found'
            });
        }

        // Add userId to body for POST/PUT requests
        if (['POST', 'PUT'].includes(req.method) && 
            req.body && typeof req.body === 'object') {
            req.body.userId = Number(userId);
        }

        // Add userId to query for GET requests
        if (req.method === 'GET') {
            req.query.userId = Number(userId);
        }

        // Add userId to request object for use in other middleware
        req.userId = Number(userId);

        next();
    } catch (error) {
        console.error('User middleware error:', error);
        next(error);
    }
};

export default addUserMiddleware;