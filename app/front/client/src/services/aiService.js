class AIService {
    static async sendChatMessage(message, context = {}) {
      try {
        const response = await fetch(getApiUrl('CHAT'), {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            message,
            context
          })
        });
  
        if (!response.ok) {
          throw new Error('Error en la comunicación con el servicio de IA');
        }
  
        return await response.json();
      } catch (error) {
        console.error('Error en chat:', error);
        throw error;
      }
    }
  
    static async improveContent(content, contentType, context = {}) {
      try {
        const response = await fetch(getApiUrl('IMPROVE'), {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            content,
            content_type: contentType,
            context
          })
        });
  
        if (!response.ok) {
          throw new Error('Error al mejorar el contenido');
        }
  
        return await response.json();
      } catch (error) {
        console.error('Error en mejora:', error);
        throw error;
      }
    }
  
    static async validateContent(content, validationType, criteria = {}) {
      try {
        const response = await fetch(getApiUrl('VALIDATE'), {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            content,
            validation_type: validationType,
            criteria
          })
        });
  
        if (!response.ok) {
          throw new Error('Error en la validación');
        }
  
        return await response.json();
      } catch (error) {
        console.error('Error en validación:', error);
        throw error;
      }
    }
  }
  
  export default AIService;