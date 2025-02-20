import { validationResult } from 'express-validator';

const handleValidationResults = (req, res, next) => {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
        return res.status(400).json({
            success: false,
            errors: errors.array(),
            code: 'VALIDATION_ERROR'
        });
    }
    next();
};

export default handleValidationResults;