import axios from "axios";
import Swal from 'sweetalert2';
import { getApiUrl, getHeaders } from './api';

const API_URL = getApiUrl('obstacle');

export const getObstacle = async () => {
    try {
        const headers = getHeaders();
        const response = await axios.get(`${API_URL}`, { headers });
        const data = await response.data;
        return data;
    } catch (error) {
        console.error("Error al obtener los Obstacle:", error);
        throw error;
    }
};

export const getOneObstacle = async (id) => {
    try {
        const headers = getHeaders();
        const response = await axios.get(`${API_URL}/${id}`, { headers });
        return response.data;
    } catch (error) {
        console.error("Error al obtener el Obstacle por ID", error);
        throw error;
    }
};

export const deleteObstacle = async (id) => {
        const headers = getHeaders();
        const response = await axios.delete(`${API_URL}/${id}`, { headers });
        return response.data;
};

        

export const postObstacle = async (data) => {
    const headers = getHeaders();
    const response = await axios.post(API_URL, data, { headers });
    return response;
  };


  export const updateObstacle = async (id, data) => {
    try {
        const headers = getHeaders();
        const response = await axios.put(`${API_URL}/${id}`, data, { headers });
        if (response.status === 200) {
            Swal.fire({
                icon: 'success',
                title: 'Actualizado!',
                text: 'El obstáculo ha sido actualizado.',
                confirmButtonColor: "#002661",
                background: '#ECF0F1',
                customClass: {
                    popup: 'swal-custom-popup',
                    title: 'swal-custom-title',
                    content: 'swal-custom-content',
                    confirmButton: 'swal-custom-confirm'
                }
            });
            return response.data;
        }
    } catch (error) {
        Swal.fire({
            icon: 'error',
            title: 'Error!',
            text: 'No se pudo actualizar el obstáculo.',
            confirmButtonColor: "#002661",
            background: '#ECF0F1',
            customClass: {
                popup: 'swal-custom-popup',
                title: 'swal-custom-title',
                content: 'swal-custom-content',
                confirmButton: 'swal-custom-confirm'
            }
        });
        throw error;
    }
};

// export const uploadImage = async (imageData) => {
//     try {
//         const response = await axios.post(
//             "http://api.cloudinary.com/v1_1/dpkll45y2/image/upload",
//             imageData
//         );
//         return response.data;
//     } catch (error) {
//         throw new Error("Error al cargar la imagen en Cloudinary: " + error.message);
//     }
// };
const cloudinaryAxios = axios.create();
cloudinaryAxios.interceptors.request.clear();

export const uploadImage = async (imageData) => {
    try {
        const response = await cloudinaryAxios.post(
            "https://api.cloudinary.com/v1_1/dpkll45y2/image/upload",
            imageData,
            {
                headers: {
                    'Content-Type': 'multipart/form-data'
                }
            }
        );
        return response.data;
    } catch (error) {
        console.error("Cloudinary upload error:", error);
        throw new Error("Error al cargar la imagen en Cloudinary: " + error.message);
    }
};

export const updateImage = async (imageData) => {
    try {
        const response = await axios.put(
            `http://api.cloudinary.com/v1_1/dpkll45y2/image/upload`,
            imageData
        );
        return response.data;
    } catch (error) {
        throw new Error("Error al cargar la imagen en Cloudinary: " + error.message);
    }
}
