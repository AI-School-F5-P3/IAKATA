import React, { useState, useRef, useEffect } from 'react';
import { sendMessage } from '../../services/ChatbotServices';
import ChatIcon from '../../assets/img/ChatBotIcon2.svg';
import './Chatbot.css';
import Message from './Message';  

const Chatbot = () => {
  const [message, setMessage] = useState('');
  const [messages, setMessages] = useState([]);
  const [isOpen, setIsOpen] = useState(false);
  const messagesEndRef = useRef(null);

  // Función para desplazarse automáticamente al último mensaje
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  // Efecto para desplazarse al último mensaje cuando se añade uno nuevo
  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Cargar mensajes previos del almacenamiento local si existen
  useEffect(() => {
    if (isOpen) {
      const savedMessages = localStorage.getItem('chatMessages');
      if (savedMessages) {
        try {
          setMessages(JSON.parse(savedMessages));
        } catch (error) {
          console.error('Error al cargar mensajes guardados:', error);
        }
      }
    }
  }, [isOpen]);

  // Guardar mensajes en almacenamiento local cuando cambian
  useEffect(() => {
    if (messages.length > 0) {
      localStorage.setItem('chatMessages', JSON.stringify(messages));
    }
  }, [messages]);

  const handleSendMessage = async () => {
    if (!message.trim()) return;

    const userMessage = { sender: 'user', text: message };
    setMessages((prevMessages) => [...prevMessages, userMessage]);

    try {
      // Agregar mensaje de carga
      setMessages((prevMessages) => [
        ...prevMessages, 
        { sender: 'bot', text: '...', loading: true }
      ]);
      
      // Obtener respuesta del chatbot
      const botResponse = await sendMessage(message);
      
      // Reemplazar mensaje de carga con la respuesta real
      setMessages((prevMessages) => {
        const newMessages = prevMessages.filter(msg => !msg.loading);
        return [...newMessages, { 
          sender: 'bot', 
          text: botResponse || 'No tengo respuesta para esa consulta.',
          timestamp: new Date().toISOString()
        }];
      });
    } catch (error) {
      console.error('Error enviando el mensaje:', error);
      
      setMessages((prevMessages) => {
        const newMessages = prevMessages.filter(msg => !msg.loading);
        return [...newMessages, { 
          sender: 'bot', 
          text: 'Hubo un error al procesar la solicitud. Por favor, inténtalo de nuevo.',
          timestamp: new Date().toISOString()
        }];
      });
    }

    setMessage('');
  };

  // Manejar envío con tecla Enter
  const handleKeyDown = (e) => {
    if (e.key === 'Enter') {
      handleSendMessage();
    }
  };

  return (
    <div>
      <div className="chat-icon-button" onClick={() => setIsOpen(!isOpen)}>
        <img src={ChatIcon} alt="Chatbot" className="chat-icon" />
      </div>
      {isOpen && (
        <div className="chatbot-modal">
          <div className="chatbot-modal-content">
            <span className="close-button" onClick={() => setIsOpen(false)}>&times;</span>
            <div className="chat-messages">
              {messages.length === 0 ? (
                <div className="welcome-message">
                  <p>¡Hola! Soy tu asistente de Lean Kata. ¿En qué puedo ayudarte hoy?</p>
                </div>
              ) : (
                messages.map((msg, index) => (
                  <Message key={index} message={msg} />
                ))
              )}
              <div ref={messagesEndRef} />
            </div>
            <div className="chat-input">
              <input
                type="text"
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder="Escribe tu pregunta..."
              />
              <button onClick={handleSendMessage}>Enviar</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Chatbot;
