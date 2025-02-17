import axios from "axios";
import { getApiUrl, getHeaders } from './api';

const API_URL = getApiUrl('hypothesis');

export const getHypothesis = async () => {
    try {
        const headers = getHeaders();
        const response = await axios.get(`${API_URL}`, {headers});
        const data = await response.data
        return data;
    } catch (error) {
        console.error("Error al obtener las Hypothesis:", error);
        throw error;
    }
};

export const getOneHypothesis = async (id) => {
    try {
        const headers = getHeaders();
        const response = await axios.get(`${API_URL}/${id}`, {headers});
        return response;
    } catch (error) {
        console.error("Error al obtener la Hypothesis por ID", error);
        throw error;
    }
};

export const deleteHypothesis = async (id) => {
    try {
        const headers = getHeaders();
        const response = await axios.delete(`${API_URL}/${id}`, { headers });
        return response;
    } catch (error) {
        console.error("Error al eliminar la Hypothesis:", error);
        throw error;
    }
};

export const postHypothesis = async (data) => {
    const headers = getHeaders();
    const response = await axios.post(API_URL, data, {headers});
    return response;
  }


  export const updateHypothesis = async (id, data) => {
    try {
        const headers = getHeaders();
        const response = await axios.put(`${API_URL}/${id}`, data, { headers });
        return response;
    } catch (error) {
        console.error("Error al actualizar la Hypothesis:", error);
        throw error;
    }
};

