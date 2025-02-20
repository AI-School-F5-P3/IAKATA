import axios from "axios";
import { getApiUrl, getHeaders } from './api';

const API_URL = getApiUrl('mentalcontrast'); 

export const getMentalContrast = async () => {
    try {
        const headers = getHeaders();
        const response = await axios.get(`${API_URL}`, { headers });
        const data = await response.data
        return data;
    } catch (error) {
        console.error("Error al obtener los MentalContrast:", error);
        throw error;
    }
};

export const getOneMentalContrast = async (id) => {
    try {
        const headers = getHeaders();
        const response = await axios.get(`${API_URL}/${id}`, { headers });
        return response;
    } catch (error) {
        console.error("Error al obtener el MentalContrast por ID", error);
        throw error;
    }
};

export const deleteMentalContrast = async (id) => {
    const headers = getHeaders();
    const response = await axios.delete(`${API_URL}/${id}`, { headers });
    return response.data;
};


export const postMentalContrast = async (data) => {
    const headers = getHeaders();
    const response = await axios.post(API_URL, data, { headers });
    return response;
  };


  export const updateMentalContrast = async (id, data) => {
    const headers = getHeaders();
    const response = await axios.put(`${API_URL}/${id}`, data, { headers });
    return response.data;
};