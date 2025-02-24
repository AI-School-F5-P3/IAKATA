import React, { useState, useEffect, useRef } from 'react';
import { apiService } from '../../services/api';


const Chatbot = () => {
  const [message, setMessage] = useState('');
  const [messages, setMessages] = useState([]);
  const [isOpen, setIsOpen] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSendMessage = async (e) => {
    e?.preventDefault();
    
    if (!message.trim() || isLoading) return;

    const userMessage = { sender: 'user', text: message };
    setMessages(prev => [...prev, userMessage]);
    setIsLoading(true);

    try {
      // Obtener el contexto de los últimos mensajes
      const context = {
        previousMessages: messages.slice(-5).map(msg => ({
          role: msg.sender === 'user' ? 'user' : 'assistant',
          content: msg.text
        })),
        sessionId: sessionStorage.getItem('aiSessionId'),
        boardContext: {
          currentSection: window.location.pathname.split('/').pop()
        }
      };

      const response = await apiService.chat.sendMessage(message, context);

      const botMessage = {
        sender: 'bot',
        text: response.response || 'No se recibió una respuesta válida',
        suggestions: response.suggestions || [],
        sessionId: response.session_id
      };

      if (response.session_id) {
        sessionStorage.setItem('aiSessionId', response.session_id);
      }

      setMessages(prev => [...prev, botMessage]);
    } catch (error) {
      console.error('Error en el chat:', error);
      setMessages(prev => [...prev, {
        sender: 'bot',
        text: 'Lo siento, ocurrió un error al procesar tu mensaje.'
      }]);
    } finally {
      setIsLoading(false);
      setMessage('');
    }
  };

  return (
    <div className="fixed bottom-4 right-4 z-50">
      <button 
        onClick={() => setIsOpen(!isOpen)}
        className="bg-blue-600 text-white p-3 rounded-full shadow-lg"
      >
        {isOpen ? '✕' : '💬'}
      </button>

      {isOpen && (
        <div className="absolute bottom-16 right-0 w-96 bg-white rounded-lg shadow-xl">
          <div className="p-4 border-b">
            <h3 className="text-lg font-semibold">Asistente IAKATA</h3>
          </div>

          <div className="h-96 overflow-y-auto p-4 space-y-4">
            {messages.map((msg, index) => (
              <div
                key={index}
                className={`flex ${msg.sender === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={`max-w-[80%] rounded-lg p-3 ${
                    msg.sender === 'user'
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-100'
                  }`}
                >
                  <p>{msg.text}</p>
                  {msg.suggestions?.length > 0 && (
                    <div className="mt-2 text-sm">
                      <p className="font-semibold">Sugerencias:</p>
                      <ul className="list-disc list-inside">
                        {msg.suggestions.map((suggestion, idx) => (
                          <li key={idx}>{suggestion}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              </div>
            ))}
            {isLoading && (
              <div className="flex justify-start">
                <div className="bg-gray-100 rounded-lg p-3">
                  <div className="typing-indicator">
                    <span></span>
                    <span></span>
                    <span></span>
                  </div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          <form onSubmit={handleSendMessage} className="p-4 border-t">
            <div className="flex gap-2">
              <input
                type="text"
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                placeholder="Escribe tu mensaje..."
                className="flex-1 p-2 border rounded"
                disabled={isLoading}
              />
              <button
                type="submit"
                disabled={isLoading || !message.trim()}
                className="bg-blue-600 text-white px-4 py-2 rounded disabled:opacity-50"
              >
                {isLoading ? '...' : 'Enviar'}
              </button>
            </div>
          </form>
        </div>
      )}
    </div>
  );
};

export default Chatbot;