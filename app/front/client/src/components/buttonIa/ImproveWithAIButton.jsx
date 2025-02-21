import React from 'react';
import axios from 'axios';

const ImproveWithAIButton = ({ getValues, onResult }) => {
  const handleImprove = async () => {
    const formData = getValues(); // Obtener datos del formulario
    if (formData.idForm == "RE"){
      formData[0] = formData[0] + ": "+ formData[1];
    }
    const data = {"idForm": formData.idForm, "description": formData[0]};
    console.log('Datos enviados:', data);

    try {
      const response = await axios.post('http://localhost:5001/challenge/ai', data); // Tu API Node.js
      console.log('Respuesta de la IA:', response.data);

      // Llamada a la función para manejar el resultado
      onResult(response.data);
    } catch (error) {
      console.error('Error al mejorar con IA:', error);
    }
  };

  return (
    <button type="button" className="button-forms" onClick={handleImprove}>
      MEJORAR CON IA 🪄
    </button>
  );
};

export default ImproveWithAIButton;
