const API_URL_CHATBOT = '/api/ask';

export const sendMessage = async (message) => {
  const headers = {
    'accept': 'application/json',
    'Content-Type': 'application/json'
  };
  const body = JSON.stringify({
    question: message
  });

  try {
    const response = await fetch(API_URL_CHATBOT, {
      method: 'POST',
      headers: headers,
      body: body
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    console.log(data)
    return data;
  } catch (error) {
    console.error('Error sending message:', error);
    throw error;
  }
};


