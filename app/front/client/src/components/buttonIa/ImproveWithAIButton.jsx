import React, { useState, useRef } from 'react';
import axios from 'axios';
import './ImproveWithAIWidget.css';

const ImproveWithAIButton = ({ getValues, onResult }) => {
  const [loading, setLoading] = useState(false);
  const [aiResponse, setAiResponse] = useState(null);
  const [showResponse, setShowResponse] = useState(false);
  const [originalText, setOriginalText] = useState("");
  const [position, setPosition] = useState({ x: window.innerWidth - 370, y: 100 });
  const dragRef = useRef(null);
  const [isDragging, setIsDragging] = useState(false);

  const handleImprove = async () => {
    setLoading(true);
    const formData = getValues();
    
    // Guardar texto original (CORRECTO)
    const originalContent = formData[0];
    setOriginalText(originalContent);
    
    if (formData.idForm === "RE") {
      formData[0] = formData[0] + ": " + formData[1];
    }
    
    // Asegurar que formData[0] contiene la descripción
    const data = {
      "idForm": formData.idForm, 
      "description": formData[0], // <- Este es el texto que envías a la IA
      "type": "concise"
    };
  
    try {
      console.log("Enviando datos a la API:", data);
      const response = await axios.post('http://localhost:8000/api/routes/board/ai', data);
      console.log("Respuesta recibida:", response.data);
      
      setAiResponse(response.data.data.description); // Respuesta de IA
      setShowResponse(true);
    } catch (error) {
      console.error('Error:', error);
      setAiResponse("Error al procesar la solicitud");
      setShowResponse(true);
    } finally {
      setLoading(false);
    }
  };

  // Lógica de aplicación modificada
// Modificar la función handleApply en ImproveWithAIButton.jsx
// Modificación al handleApply en ImproveWithAIButton.jsx
const handleApply = () => {
  if (aiResponse && onResult) {
    console.log("Aplicando respuesta IA:", aiResponse);
    
    try {
      // Estandarizar el formato para compatibilidad con todos los componentes
      let formattedResponse;
      
      // Preparar un objeto con la estructura esperada por Challenge.jsx
      if (typeof aiResponse === 'string') {
        formattedResponse = {
          data: {
            description: aiResponse
          }
        };
      } else if (aiResponse && typeof aiResponse === 'object') {
        // Si ya es un objeto, mantener la estructura esperada
        if (aiResponse.data && aiResponse.data.description) {
          formattedResponse = aiResponse;
        } else if (aiResponse.description) {
          formattedResponse = {
            data: {
              description: aiResponse.description
            }
          };
        } else {
          formattedResponse = {
            data: {
              description: JSON.stringify(aiResponse)
            }
          };
        }
      } else {
        // Caso por defecto
        formattedResponse = {
          data: {
            description: String(aiResponse)
          }
        };
      }
      
      // Añadir una propiedad 'keepWindowOpen' para indicar que no se debe cerrar la ventana
      formattedResponse.keepWindowOpen = true;
      
      console.log("Formato estandarizado para onResult:", formattedResponse);
      
      // Pasar el objeto formateado a onResult
      onResult(formattedResponse);
      
      console.log("Respuesta aplicada correctamente");
      
      // Simplemente cerramos la ventana de sugerencia, pero no la ventana de edición
      setShowResponse(false);
    } catch (applyError) {
      console.error("Error al aplicar la respuesta:", applyError);
    }
  } else {
    console.error("No se puede aplicar: aiResponse=", aiResponse, "onResult=", onResult);
  }
};

  // Lógica de arrastre
  const handleDragStart = (e) => {
    setIsDragging(true);
    dragRef.current = {
      offsetX: e.clientX - position.x,
      offsetY: e.clientY - position.y
    };
  };

  const handleDragMove = (e) => {
    if (isDragging && dragRef.current) {
      const newX = e.clientX - dragRef.current.offsetX;
      const newY = e.clientY - dragRef.current.offsetY;
      
      setPosition({
        x: Math.max(0, Math.min(newX, window.innerWidth - 350)),
        y: Math.max(0, Math.min(newY, window.innerHeight - 200))
      });
    }
  };

  const handleDragEnd = () => {
    setIsDragging(false);
  };

  return (
    <div className="ai-improve-wrapper">
      <button 
        type="button" 
        className="button-forms" 
        onClick={handleImprove}
        disabled={loading}
      >
        {loading ? 'Procesando...' : 'MEJORAR CON IA 🪄'}
      </button>
      
      {showResponse && (
        <div 
          className="ai-suggestion-container"
          style={{ left: position.x, top: position.y }}
          onMouseDown={handleDragStart}
          onMouseMove={handleDragMove}
          onMouseUp={handleDragEnd}
          onMouseLeave={handleDragEnd}
        >
          <div className="suggestion-header">
            <h4>Sugerencia de IA</h4>
            <button onClick={() => setShowResponse(false)} className="close-btn">×</button>
          </div>
          <div className="suggestion-content">
            {aiResponse}
          </div>
          <div className="suggestion-footer">
            <button className="action-btn" onClick={handleApply}>
              ✓ Aplicar esta sugerencia
            </button>
            <button className="action-btn secondary" onClick={() => setShowResponse(false)}>
              Cancelar
            </button>
          </div>
          <div className="suggestion-credit">
            🤖 Powered by IA Kata
          </div>
        </div>
      )}
    </div>
  );
};

export default ImproveWithAIButton;