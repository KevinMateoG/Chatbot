import "./App.css";
import logoUdem from "../public/logo_udemedellin2.png";
import { Link } from 'react-router-dom';

export default function Index() {
  return (
    <>
      <div className="loguito">
      <span className="vertical-text">MinEducación</span>
      <img src={logoUdem} alt="logo udem" height="70" />
      </div>
      <center>
     <div>  
        <div>
            <h1 class="centrado">titulo 1</h1>
        </div>
     </div>
    </center>

    <center><ul class="centrado">
    
        <li >
            <a>ICONO 1 ▼</a>
        <ul>
            <li><a>INFORMACION</a></li>
            <li><a>INFORMACION</a></li>
        </ul>
        
        </li>

        <li>
            <a>ICONO 2 ▼</a>    
        <ul>
            <li><a>INFORMACION</a></li>
            <li><a>INFORMACION</a></li>
        </ul>
        
        </li>

        <li>
            <a>ICONO 3 ▼</a>
        <ul>
            <li><a>INFORMACION</a></li>
            <li><a>INFORMACION</a></li>
        </ul>
        
        </li>

        <li>
            <a>ICONO 4 ▼</a>
        <ul>
            <li><a>INFORMACION</a></li>
            <li><a>INFORMACION</a></li>
        </ul>
        </li>
    
    </ul>.
    </center>
      <Link to="/chatbot" className="chatbot-btn" title="Abrir Chatbot">
        💬
      </Link>
    </>
  );
}
