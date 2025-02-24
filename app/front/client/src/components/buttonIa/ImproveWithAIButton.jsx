import React, { useState } from 'react';
import { apiService } from '../../services/api';

const ImproveWithAIButton = ({ getValues, onResult, section }) => {
  const [isImproving, setIsImproving] = useState(false);
  const [suggestions, setSuggestions] = useState([]);
  const [error, setError] = useState(null);

  const handleImprove = async () => {
    const formData = getValues();
    setIsImproving(true);
    setError(null);
    
    try {
      // Enviar contenido actual al servicio de IA
      const response = await apiService.improve.content(
        formData,
        section,
        {
          userId: sessionStorage.getItem('userId'),
          boardContext: {
            section,
            timestamp: new Date().toISOString()
          }
        }
      );

      // Procesar sugerencias recibidas
      if (response.suggestions?.length > 0) {
        setSuggestions(response.suggestions);
      }

      // Notificar al componente padre si es necesario
      if (onResult) {
        onResult(response);
      }

    } catch (error) {
      console.error('Error al mejorar con IA:', error);
      setError('Error al procesar la mejora. Por favor intente nuevamente.');
    } finally {
      setIsImproving(false);
    }
  };

  return (
    <div className="w-full space-y-4">
      <button
        type="button"
        className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50"
        onClick={handleImprove}
        disabled={isImproving}
      >
        {isImproving ? 'MEJORANDO... 🔄' : 'MEJORAR CON IA 🪄'}
      </button>

      {error && (
        <Alert variant="destructive">
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {suggestions.length > 0 && (
        <div className="mt-4 p-4 bg-gray-50 rounded-md">
          <h3 className="font-semibold mb-2">Sugerencias de mejora:</h3>
          <ul className="space-y-2">
            {suggestions.map((suggestion, index) => (
              <li key={index} className="flex items-start gap-2">
                <span className="text-blue-600">•</span>
                <span>{suggestion}</span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
};

export default ImproveWithAIButton;