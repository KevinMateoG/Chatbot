import { useState, useEffect } from 'react';
import './chatbot.css';
import logoUdem from "../public/logo_udemedellin2.png";



function Chatbot() {
  const [messages, setMessages] = useState([
    { text: "Bienvenido al asistente de Uvirtual, aquí resolveremos tus dudas de tu interés.", type: "bot" },
    { text: "Por favor ingresa tu tipo de documento de identidad", type: "bot" }
  ]);
  const [inputValue, setInputValue] = useState('');
  const [estado, setEstado] = useState('pidiendo_tipo');
  const [identificacion, setIdentificacion] = useState({});
  const [opciones, setOpciones] = useState(null);
  const [nodoActual, setNodoActual] = useState(null);

  useEffect(() => {
    // Cargar opciones desde el backend de FastAPI
    fetch('http://localhost:8000/opciones')
      .then(res => res.json())
      .then(data => {
        setOpciones(data);
      });
  }, []);

  const mostrarMensaje = (texto, tipo) => {
    const urlRegex = /(https?:\/\/[^\s]+)/g;
    const textoConLinks = texto.replace(urlRegex, '<a href="$1" target="_blank">haz clic aquí</a>');
    setMessages(prev => [...prev, { text: textoConLinks, type: tipo }]);
  };

  const mostrarOpciones = (opcionesObj) => {
    const opcionesTexto = Object.entries(opcionesObj)
      .map(([k, v]) => `${k}. ${v.texto}`)
      .join('\n');
    mostrarMensaje(opcionesTexto, 'bot');
  };

  const procesarFlujo = async (mensaje) => {
    const response = await fetch('http://localhost:8000/procesar_mensaje', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        mensaje,
        estado,
        identificacion,
        nodo_actual: nodoActual
      }),
    });
      
    const data = await response.json();
    
    // Actualizar estado según la respuesta del backend
    setEstado(data.nuevo_estado);
    setIdentificacion(data.identificacion);
    setNodoActual(data.nodo_actual);

    // Mostrar mensajes de respuesta
    data.mensajes.forEach(msg => {
      mostrarMensaje(msg, 'bot');
    });

    if (data.opciones) {
      mostrarOpciones(data.opciones);
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!inputValue.trim()) return;

    mostrarMensaje(inputValue, 'user');
    procesarFlujo(inputValue);
    setInputValue('');
  };

  return (
    
    <div>
      <div className="chat-header">

       <button className='atras1'><a href="/">↶</a></button> 
        <img src={logoUdem} alt="logo udem" height="70" />
      </div>

       

      <div className="chat-container">
        <div className="chat-box">
          {messages.map((msg, index) => (
            <div 
              key={index} 
              className={`${msg.type}-message`}
              dangerouslySetInnerHTML={{ __html: msg.text }}
            />
          ))}
        </div>

        <div className="input-container">
          <center><form onSubmit={handleSubmit}>
            <input className='barra'
              type="text"
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              placeholder="Escribe tu mensaje..."
            />
            <button className='flechita' type="submit">➤</button>
          </form></center>
        </div>
      </div>
    </div>
  );
}

export default Chatbot;