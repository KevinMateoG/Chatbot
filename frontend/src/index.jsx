import "./App.css";
import logoUdem from "../public/logo_udemedellin2.png";

export default function index() {
  return (
    <>
      <span className="vertical-text">MinEducación</span>
      <img src={logoUdem} alt="logo udem" height="70" />
      <div>
        <div>
          <h1 className="centrado">título 1</h1>
        </div>
      </div>

      <ul className="centrado">
        <li>
          <a>Icono 1 ▼</a>
          <ul>
            <li>
              <a href="/chatbot">Promet IA</a>
            </li>
            <li>
              <a>Información</a>
            </li>
          </ul>
        </li>

        <li>
          <a>Icono 2 ▼</a>
          <ul>
            <li>
              <a>Información</a>
            </li>
            <li>
              <a>Información</a>
            </li>
          </ul>
        </li>

        <li>
          <a>Icono 3 ▼</a>
          <ul>
            <li>
              <a>Información</a>
            </li>
            <li>
              <a>Información</a>
            </li>
          </ul>
        </li>

        <li>
          <a>Icono 4 ▼</a>
          <ul>
            <li>
              <a>Información</a>
            </li>
            <li>
              <a>Información</a>
            </li>
          </ul>
        </li>
      </ul>

      <a href="/chatbot" className="chatbot-btn" title="Abrir Chatbot">
        💬
      </a>
    </>
  );
}
