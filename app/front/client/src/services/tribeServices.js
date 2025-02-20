import axios from "axios";
import Swal from 'sweetalert2';
import { getApiUrl, getHeaders } from './api';

const API_URL_AE = getApiUrl('tribe');

export const getTribe = async () => {
    try {
        const headers = getHeaders();
        const response = await axios.get(`${API_URL_AE}`, {headers});
        const data = await response.data
        return data;
    } catch (error) {
        console.error("Error al obtener las tribus:", error);
        throw error;
    }
};

export const getOneTribe = async (id) => {
    try {
        const headers = getHeaders();
        const response = await axios.get(`${API_URL_AE}/${id}`, {headers});
        return response;
    } catch (error) {
        console.error("Error al obtener la tribu por ID", error);
        throw error;
    }
};

export const deleteTribe = async (id) => {
        try {
            const headers = getHeaders();
            const response = await axios.delete(`${API_URL_AE}/${id}`, {headers});
           return response;
        } catch (error) {
            console.error("Error al eliminar la tribu", error);
            throw error;
        }
};

export const postTribe = async (data) => {
    const headers = getHeaders();
    const response = await axios.post(API_URL_AE, data, {headers});
    return response;
  }


  export const updateTribe = async (id, data) => {
    try {
        const headers = getHeaders();
        console.log('Updating tribe with data:', data);
        const response = await axios.put(`${API_URL_AE}/${id}`,data, {headers});
        console.log(response);
        if (response.status === 200) {
            return response.data;
        }
    } catch (error) {
        console.error("Error al actualizar la tribu:", error);
        throw error;
    }
};  

// export const updateTribe = async (id, data) => {
//     try {
//         // Validar que los campos requeridos existan
//         if (!data.name_tribe || !data.team_members) {
//             throw new Error('Los campos nombre de tribu y miembros del equipo son obligatorios');
//         }

//         const headers = getHeaders();
        
//         // Asegurar que solo enviamos los campos necesarios
//         const tribeData = {
//             name_tribe: data.name_tribe,
//             team_members: data.team_members
//         };

//         console.log('Datos a actualizar:', tribeData);
        
//         const response = await axios.put(`${API_URL_AE}/${id}`, tribeData, {headers});
        
//         if (response.status === 200) {
//             console.log('Tribu actualizada exitosamente');
//             return response.data;
//         }
//     } catch (error) {
//         if (error.response) {
//             console.error("Error del servidor:", error.response.data);
//             throw new Error(`Error al actualizar: ${error.response.data.message || 'Error desconocido'}`);
//         }
//         console.error("Error al actualizar la tribu:", error);
//         throw error;
//     }
// };
