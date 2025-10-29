import { useState, useEffect } from "react";
import "./chatbot.css";
import logoUdem from "../public/logo_udemedellin2.png";

function Chatbot() {
  const [messages, setMessages] = useState([
    {
      text: "Bienvenido al asistente de Uvirtual, aquí resolveremos tus dudas de tu interés.",
      type: "bot",
    },
    {
      text: "Por favor ingresa tu tipo de documento de identidad",
      type: "bot",
    },
  ]);
  const [inputValue, setInputValue] = useState("");
  const [estado, setEstado] = useState("pidiendo_tipo");
  const [identificacion, setIdentificacion] = useState("");
  const [opciones, setOpciones] = useState(null);
  const [nodoActual, setNodoActual] = useState(null);
  const [modoIA, setModoIA] = useState(false);
  const [cargandoIA, setCargandoIA] = useState(false);

  useEffect(() => {
    // Cargar opciones desde el backend de FastAPI
    fetch("http://localhost:8000/opciones")
      .then((res) => res.json())
      .then((data) => {
        setOpciones(data);
      });
  }, []);

  const mostrarMensaje = (texto, tipo) => {
    const urlRegex = /(https?:\/\/[^\s]+)/g;
    const textoConLinks = texto.replace(
      urlRegex,
      '<a href="$1" target="_blank">haz clic aquí</a>'
    );
    setMessages((prev) => [...prev, { text: textoConLinks, type: tipo }]);
  };

  const mostrarOpciones = (opcionesObj) => {
    const opcionesTexto = Object.entries(opcionesObj)
      .map(([k, v]) => `${k}. ${v.texto}`)
      .join("\n");
    mostrarMensaje(opcionesTexto, "bot");
  };

  const procesarFlujo = async (mensaje) => {
    const response = await fetch("http://localhost:8000/procesar_mensaje", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        mensaje,
        estado,
        identificacion,
        nodo_actual: nodoActual,
      }),
    });

    const data = await response.json();

    // Actualizar estado según la respuesta del backend
    setEstado(data.nuevo_estado);
    setIdentificacion(data.identificacion);
    setNodoActual(data.nodo_actual);

    // Mostrar mensajes de respuesta
    data.mensajes.forEach((msg) => {
      mostrarMensaje(msg, "bot");
    });

    if (data.opciones) {
      mostrarOpciones(data.opciones);
    }
  };

  const consultarIA = async (pregunta) => {
    setCargandoIA(true);
    try {
      const response = await fetch("http://localhost:8000/ai/generate", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          prompt: pregunta,
          max_tokens: 512,
          temperature: 0.7,
          identificacion:
            identificacion && identificacion.trim() !== ""
              ? identificacion
              : null, // Enviar null si está vacío
          usar_contexto: true, // Habilitar el uso de contexto del sistema
        }),
      });

      const data = await response.json();

      // Si hay error HTTP, mostrar detalle
      if (!response.ok) {
        console.error("Error de respuesta:", data);
        const errorMsg = data.detail
          ? typeof data.detail === "string"
            ? data.detail
            : JSON.stringify(data.detail)
          : `Error ${response.status}: ${response.statusText}`;
        mostrarMensaje(`❌ Error: ${errorMsg}`, "bot");
        return;
      }

      if (data.text) {
        // Mostrar si usó contexto
        const contextoInfo = data.contexto_usado
          ? " (con contexto del sistema)"
          : "";
        mostrarMensaje(`🤖 IA${contextoInfo}: ${data.text}`, "bot");
      } else if (data.detail) {
        mostrarMensaje(`❌ Error: ${data.detail}`, "bot");
      }
    } catch (error) {
      console.error("Error al consultar la IA:", error);
      mostrarMensaje(`❌ Error al consultar la IA: ${error.message}`, "bot");
    } finally {
      setCargandoIA(false);
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!inputValue.trim()) return;

    mostrarMensaje(inputValue, "user");

    // Si está en modo IA, consultar directamente a la IA
    if (modoIA) {
      consultarIA(inputValue);
    } else {
      procesarFlujo(inputValue);
    }

    setInputValue("");
  };

  const toggleModoIA = () => {
    setModoIA(!modoIA);
    if (!modoIA) {
      mostrarMensaje(
        "🤖 Modo IA activado. Ahora puedes hacer cualquier pregunta y la IA responderá.",
        "bot"
      );
    } else {
      mostrarMensaje(
        "📋 Modo normal activado. Continuando con el flujo del chatbot.",
        "bot"
      );
    }
  };

  const refrescarPagina = () => {
    window.location.reload(false);
  };

  return (
    <div>
      <div className="chat-header">
        <button className="atras1">
          <a href="/">↶</a>
        </button>
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
          <center>
            <div style={{ marginBottom: "10px" }}>
              <button
                onClick={toggleModoIA}
                style={{
                  padding: "8px 16px",
                  backgroundColor: modoIA ? "#4CAF50" : "#2196F3",
                  color: "white",
                  border: "none",
                  borderRadius: "5px",
                  cursor: "pointer",
                  fontSize: "14px",
                }}
              >
                {modoIA ? "🤖 Modo IA Activo" : "📋 Modo Normal"}{" "}
                {cargandoIA ? "⏳" : ""}
              </button>
            </div>
            <form onSubmit={handleSubmit}>
              <input
                className="barra"
                type="text"
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                placeholder={
                  modoIA ? "Pregunta a la IA..." : "Escribe tu mensaje..."
                }
                disabled={cargandoIA}
              />
              <button className="flechita" type="submit" disabled={cargandoIA}>
                ➤
              </button>
              <button
                className="flechita"
                onClick={refrescarPagina}
                type="button"
              >
                Limpiar
              </button>
            </form>
          </center>
        </div>
      </div>
    </div>
  );
}

export default Chatbot;
