import { useState, useRef, useEffect } from 'react';
import './chatbot.css';

function Chatbot() {
  const [messages, setMessages] = useState([{
    type: 'bot',
    content: 'Bienvenido al asistente de Uvirtual, aquí resolveremos tus dudas de tu interés.'
  }]);
  
  const [inputMessage, setInputMessage] = useState('');
  const chatBoxRef = useRef(null);

  // El auto-scroll es necesario para una buena UX
  useEffect(() => {
    if (chatBoxRef.current) {
      chatBoxRef.current.scrollTop = chatBoxRef.current.scrollHeight;
    }
  }, [messages]);

  const handleSendMessage = async () => {
    if (inputMessage.trim() === '') return;

    // Agregar mensaje del usuario
    setMessages(prev => [...prev, {
      type: 'user',
      content: inputMessage
    }]);

    try {
      // Llamada a FastAPI
      const response = await fetch('http://localhost:8000/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message: inputMessage })
      });

      const data = await response.json();
      
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
    <div className="chat-container">
      <div className="chat-box" ref={chatBoxRef}>
        {messages.map((message, index) => (
          <div 
            key={index} 
            className={message.type === 'bot' ? 'bot-message' : 'user-message'}
          >
            {message.content}
          </div>
        ))}
      </div>

      <div className="input-container">
        <input
          type="text"
          value={inputMessage}
          onChange={(e) => setInputMessage(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
          placeholder="Escribe tu mensaje..."
        />
        <button onClick={handleSendMessage}>Enviar</button>
      </div>
    </div>
  );
}

export default Chatbot;