import axios from "axios";
import { getApiUrl, getHeaders } from './api';

const API_URL = getApiUrl('learning');

export const getLearning = async () => {
    try {
        const headers = getHeaders();
        const response = await axios.get(`${API_URL}`, {headers});
        const data = await response.data
        return data;
    } catch (error) {
        console.error("Error al obtener los Learning:", error);
        throw error;
    }
};

export const getOneLearning = async (id) => {
    try {
        const headers = getHeaders();
        const response = await axios.get(`${API_URL}/${id}`, {headers});
        return response;
    } catch (error) {
        console.error("Error al obtener el Learning por ID", error);
        throw error;
    }
};

export const deleteLearning = async (id) => {
        try {
            const headers = getHeaders();
            const response = await axios.delete(`${API_URL}/${id}`, {headers});
           return response;
        } catch (error) {
            console.error("Error al eliminar el Learning ", error);
            throw error;
        }
};


export const postLearning = async (data) => {
    const headers = getHeaders();
    const response = await axios.post(API_URL, data, {headers});
    console.log(response);
    return response;
  };


  export const updateLearning = async (id, data) => {
    try {
        const headers = getHeaders();
        const response = await axios.put(`${API_URL}/${id}`,data, {headers});
        if (response.status === 200) {
            return response.data;
        }
    } catch (error) {
        console.error("Error al actualizar el Learning:", error);
        throw error;
    }
};

