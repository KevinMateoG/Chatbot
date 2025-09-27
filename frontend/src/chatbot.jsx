import React, { useState, useRef, useEffect } from 'react';
import './chatbot.css';

function Chatbot() {
  const [messages, setMessages] = useState([{
    type: 'bot',
    content: 'Bienvenido al asistente de Uvirtual, aquí resolveremos tus dudas de tu interés.'
  }, {
    type: 'bot',
    content: 'Por favor ingresa tu tipo de documento de identidad'
  }]);
  
  const [inputMessage, setInputMessage] = useState('');
  const chatBoxRef = useRef(null);

  useEffect(() => {
    if (chatBoxRef.current) {
      chatBoxRef.current.scrollTop = chatBoxRef.current.scrollHeight;
    }
  }, [messages]);

  const handleKeyDown = (event) => {
    if (event.key === 'Enter') {
      handleSendMessage();
    }
  };

  const handleSendMessage = async () => {
    if (inputMessage.trim() === '') return;

    // Agregar mensaje del usuario
    setMessages(prev => [...prev, {
      type: 'user',
      content: inputMessage
    }]);

    try {
      // Aquí irían las llamadas a tu backend en Python
      const response = await fetch('tu-endpoint-backend', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message: inputMessage })
      });

      const data = await response.json();
      
      // Agregar respuesta del bot
      setMessages(prev => [...prev, {
        type: 'bot',
        content: data.response
      }]);
    } catch (error) {
      console.error('Error:', error);
    }

    setInputMessage('');
  };

  return (
    <>
      <div className="chat-header">
        <a href="/">Atrás</a>
      </div>

      <div className="chat-container">
        <div className="chat-box" ref={chatBoxRef}>
          {messages.map((message, index) => (
            <div 
              key={index} 
              className={message.type === 'bot' ? 'bot-message' : 'user-message'}
              dangerouslySetInnerHTML={{ __html: message.content }}
            />
          ))}
        </div>

        <div className="input-container">
          <input
            type="text"
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Escribe tu mensaje..."
          />
          <button onClick={handleSendMessage}></button>
        </div>
      </div>
    </>
  );
}

export default Chatbot;