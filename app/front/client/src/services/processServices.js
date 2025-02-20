import axios from "axios";
import Swal from 'sweetalert2';
import { getApiUrl, getHeaders } from './api';

const API_URL_AE = getApiUrl('process');

export const getProcess = async () => {
    try {
        const headers = getHeaders();
        const response = await axios.get(`${API_URL_AE}`, {headers});
        const data = await response.data
        return data;
    } catch (error) {
        console.error("Error al obtener los procesos:", error);
        throw error;
    }
};

export const getOneProcess = async (id) => {
    try {
        const headers = getHeaders();
        const response = await axios.get(`${API_URL_AE}/${id}`, {headers});
        return response;
    } catch (error) {
        console.error("Error al obtener el EA por ID", error);
        throw error;
    }
};

export const deleteProcess = async (id) => {
        try {
            const headers = getHeaders();
            const response = await axios.delete(`${API_URL_AE}/${id}`, {headers});
           return response;
        } catch (error) {
            console.error("Error al eliminar el proceso ", error);
            throw error;
        }
};

export const postProcess = async (data) => {
    const headers = getHeaders();
    const response = await axios.post(API_URL_AE, data,{headers});
    return response;
  }


  export const updateProcess = async (id, data) => {
    try {
        const headers = getHeaders();
        const response = await axios.put(`${API_URL_AE}/${id}`,data, {headers});
        if (response.status === 200) {
            return response.data;
        }
    } catch (error) {
        console.error("Error al actualizar el Proceso:", error);
        throw error;
    }
};
