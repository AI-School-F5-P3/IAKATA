import axios from "axios";
import { getApiUrl, getHeaders } from './api';

const CHATBOT_API_URL = import.meta.env.VITE_CHATBOT_API_URL || "http://localhost:8001/chat/message";

export const sendMessage = async (message) => {
  try {
    // Obtener información contextual actual
    const sessionData = {
      userId: sessionStorage.getItem('userId'),
      userName: sessionStorage.getItem('name'),
      tableId: getCurrentTableId(),
      sessionId: sessionStorage.getItem('sessionId'),
    };

    const headers = {
    'accept': 'application/json',
    'Content-Type': 'application/json'
    };
    const body = {
    query: message,
    context: sessionData
    };

    const response = await axios.post(CHATBOT_API_URL, body, { headers });
    return response.data.message || response.data;
  } catch (error) {
    console.error('Error enviando mensaje al chatbot:', error);
    throw error;
  }
};

// Función auxiliar para obtener el ID del tablero actual
const getCurrentTableId = () => {
  // Obtener ID del tablero desde la URL
  const path = window.location.pathname;
  const matches = path.match(/\/home\/card\/([A-Za-z0-9]+)/);
  if (matches && matches[1]) {
    return matches[1]; // ID del reto/tablero actual
  }
  return null; // No hay tablero específico
};

