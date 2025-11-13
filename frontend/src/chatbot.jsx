import { useState } from "react";
import "./chatbot.css";
import logoUdem from "../public/logo_udemedellin2.png";

function Chatbot() {
  const [messages, setMessages] = useState([
    {
      text: "🎓 Bienvenido al Asistente Virtual Inteligente de la Universidad de Medellín",
      type: "bot",
    },
    {
      text: "Soy tu asistente con IA y puedo ayudarte con información sobre materias, profesores, notas, eventos y más.",
      type: "bot",
    },
    {
      text: "Para brindarte información personalizada, por favor ingresa tu número de identificación:",
      type: "bot",
    },
  ]);
  const [inputValue, setInputValue] = useState("");
  const [identificacion, setIdentificacion] = useState(null);
  const [nombreUsuario, setNombreUsuario] = useState(null);
  const [esperandoIdentificacion, setEsperandoIdentificacion] = useState(true);
  const [cargandoIA, setCargandoIA] = useState(false);

  const mostrarMensaje = (texto, tipo) => {
    const urlRegex = /(https?:\/\/[^\s]+)/g;
    const textoConLinks = texto.replace(
      urlRegex,
      '<a href="$1" target="_blank">haz clic aquí</a>'
    );
    setMessages((prev) => [...prev, { text: textoConLinks, type: tipo }]);
  };

  const verificarIdentificacion = async (id) => {
    try {
      const response = await fetch(
        `http://localhost:8000/ai/verificar_identificacion/${id}`
      );
      const data = await response.json();
      return data;
    } catch (error) {
      console.error("Error verificando identificación:", error);
      return { encontrado: false };
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
          max_tokens: 800,
          temperature: 0.7,
          identificacion: identificacion, // Enviar la identificación si existe
          usar_contexto: true, // Siempre usar contexto
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
        mostrarMensaje(`🤖 ${data.text}`, "bot");
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

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!inputValue.trim()) return;

    mostrarMensaje(inputValue, "user");

    // Si está esperando identificación
    if (esperandoIdentificacion) {
      const id = inputValue.trim();
      if (id === "") {
        // Usuario no quiere dar identificación
        mostrarMensaje(
          "✅ Perfecto, continuemos sin identificación. ¿En qué puedo ayudarte?",
          "bot"
        );
        setEsperandoIdentificacion(false);
      } else {
        // Verificar identificación en la base de datos
        mostrarMensaje("🔍 Verificando identificación...", "bot");
        const resultado = await verificarIdentificacion(id);

        if (resultado.encontrado) {
          // Guardar identificación y nombre
          setIdentificacion(id);
          setNombreUsuario(resultado.nombre);
          mostrarMensaje(
            `✅ ¡Bienvenid@ ${resultado.nombre}! 👋\n\nTipo de usuario: ${resultado.tipo}\n\nAhora puedo darte información personalizada. ¿En qué puedo ayudarte?`,
            "bot"
          );
        } else {
          mostrarMensaje(
            `⚠️ No encontré la identificación "${id}" en el sistema.\n\nPuedes continuar sin identificación o intentar con otro número. ¿En qué puedo ayudarte?`,
            "bot"
          );
        }
        setEsperandoIdentificacion(false);
      }
      setInputValue("");
      return;
    }

    // Consultar IA
    consultarIA(inputValue);
    setInputValue("");
  };

  return (
    <div>
      <div className="chat-header">
        <button className="atras1">
          <a href="/">↶</a>
        </button>
        <img src={logoUdem} alt="logo udem" height="70" />
        {nombreUsuario && (
          <div
            style={{
              position: "absolute",
              right: "20px",
              top: "50%",
              transform: "translateY(-50%)",
              background: "#4CAF50",
              color: "white",
              padding: "8px 15px",
              borderRadius: "20px",
              fontSize: "14px",
              fontWeight: "bold",
            }}
          >
            👤 {nombreUsuario}
          </div>
        )}
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
            {cargandoIA && (
              <div style={{ marginBottom: "10px", color: "#4CAF50" }}>
                🤖 Pensando... ⏳
              </div>
            )}
            <form onSubmit={handleSubmit}>
              <input
                className="barra"
                type="text"
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                placeholder={
                  esperandoIdentificacion
                    ? "Número de identificación (o Enter para omitir)"
                    : "Escribe tu pregunta..."
                }
                disabled={cargandoIA}
              />
              <button className="flechita" type="submit" disabled={cargandoIA}>
                ➤
              </button>
              <button
                className="flechita"
                onClick={() => window.location.reload()}
                type="button"
              >
                🔄
              </button>
            </form>
          </center>
        </div>
      </div>
    </div>
  );
}

export default Chatbot;
