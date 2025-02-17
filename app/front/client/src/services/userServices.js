import axios from 'axios';
import { getApiUrl } from './api';

export const getAllUsers = async (params = {}) => {
    try {
        const token = sessionStorage.getItem('token');
        const response = await axios.get(getApiUrl('users'), {
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            },
            params: {
                filter: params.filter || 'all',
                page: params.page || 1,
                limit: params.limit || 10
            }
        });
        return response.data;
    } catch (error) {
        console.error('Error in getAllUsers:', error.response?.data || error);
        throw error;
    }
};

export const updateUser = async (userId, data) => {
    try {
        const token = sessionStorage.getItem('token');
        const response = await axios.put(
            `${getApiUrl('users')}/${userId}`,
            data,
            {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            }
        );
        return response.data;
    } catch (error) {
        throw error;
    }
};

export const deleteUser = async (userId) => {
    const token = sessionStorage.getItem('token');
    const response = await axios.delete(`${getApiUrl('users')}/${userId}`, {
        headers: {
            'Authorization': `Bearer ${token}`
        }
    });
    return response.data;
};

export const getOneUser = async (userId) => {
    const token = sessionStorage.getItem('token');
    const response = await axios.get(`${getApiUrl('users')}/${userId}`, {
        headers: {
            'Authorization': `Bearer ${token}`
        }
    });
    return response.data;
};