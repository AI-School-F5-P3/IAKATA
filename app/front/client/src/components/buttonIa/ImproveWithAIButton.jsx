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
      const response = await axios.post('http://localhost:8001/board/ai', data);
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
  // Lógica original de aplicación
  const handleApply = () => {
    if (aiResponse && onResult) {
      onResult({ data: { description: aiResponse } });
      setShowResponse(false);
    }
  };

  // Nuevo: Lógica de arrastre
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