import "./App.css";
import logoUdem from "../public/logo_udemedellin2.png";
import { Link } from 'react-router-dom';

export default function Index() {
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
              <Link to="/chatbot">Proet IA</Link>
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

      <Link to="/chatbot" className="chatbot-btn" title="Abrir Chatbot">
        💬
      </Link>
    </>
  );
}
