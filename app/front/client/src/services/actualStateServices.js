import axios from "axios";
import { getApiUrl, getHeaders } from './api';

const API_URL = getApiUrl('actual-states');

export const getActualState = async () => {
    try {
        const headers = getHeaders();
        const response = await axios.get(API_URL, { headers });
        return response.data;
    } catch (error) {
        console.error("Error al obtener los retos:", error);
        throw error;
    }
};

export const getOneActualState = async (id) => {
    try {
        const headers = getHeaders();
        const response = await axios.get(`${API_URL}/${id}`, {headers});
        return response;
    } catch (error) {
        console.error("Error al obtener el EA por ID", error);
        throw error;
    }
};

export const deleteActualState = async (id) => {
        try {
            const headers = getHeaders();
            const response = await axios.delete(`${API_URL}/${id}`, {headers});
            return response;
        } catch (error) {
            console.error("Error al eliminar el EA ", error);
            throw error;
        }
};

export const postActualState = async (data) => {
    const headers = getHeaders();
    const response = await axios.post(API_URL, data, {headers});
    return response;
  }


  export const updateActualState = async (id, data) => {
    try {
        const headers = getHeaders();
        const response = await axios.put(`${API_URL}/${id}`,data, {headers});
        if (response.status === 200) {
            return response.data;
        }
    } catch (error) {
        console.error("Error al actualizar el EA:", error);
        throw error;
    }
};

