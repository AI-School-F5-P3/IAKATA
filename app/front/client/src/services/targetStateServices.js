import axios from "axios";
import { getApiUrl, getHeaders } from './api';

const API_URL = getApiUrl('target-state'); 
export const getTargetState = async () => {
    try {
        const headers = getHeaders();
        const response = await axios.get(`${API_URL}`, {headers});
        const data = await response.data
        return data;
    } catch (error) {
        console.error("Error al obtener los TargetState:", error);
        throw error;
    }
};

export const getOneTargetState = async (id) => {
    try {
        const headers = getHeaders();
        const response = await axios.get(`${API_URL}/${id}`,{headers});
        return response;
    } catch (error) {
        console.error("Error al obtener el TargetState por ID", error);
        throw error;
    }
};

export const deleteTargetState = async (id) => {
    try {
        const headers = getHeaders();
        const response = await axios.delete(`${API_URL}/${id}`, { headers });
        return response.data;
    } catch (error) {
        console.error("Error al eliminar el TargetState:", error);
        throw error;
    }
};

export const updateTargetState = async (id, data) => {
    const headers = getHeaders();
    const response = await axios.put(`${API_URL}/${id}`, data, { headers });
    return response.data;
};

export const postTargetState = async (data) => {
    const headers = getHeaders();
    const response = await axios.post(API_URL, data, {headers});
    return response;
  };