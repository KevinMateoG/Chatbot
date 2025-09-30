import "./App.css";
import logoUdem from "../public/logo_udemedellin2.png";
import { Link } from 'react-router-dom';

export default function Index() {
  return (
    <>
      <div className="loguito">
      <span className="vertical-text" >MinEducación</span>
      <img src={logoUdem} alt="logo udem" height="70" />
      </div>
      <center>
     <div>  
        <div className="estoy">
            <h1 class="centrado">Bienvenido</h1>
            <p className="descripcion">
                Bienvenido a nuestro ambiente digital, aquí podrás encontrar cursos, recursos y más.
            </p>
        </div>
     </div>
    </center>

    <center><ul class="centrado">
    
        <li >
            <a>Chat LMS▼</a>
        <ul>
            <li><Link to="/chatbot">PromeIA</Link></li>
            
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
    
    </ul>
    
    <button className="curso1">Fundamentos de Diseño de Software</button>
    <button className="curso2">Calculo</button>
    <button className="curso3">Legislacion</button>
    <button className="curso4">Fisica II</button>
    </center>
      <Link to="/chatbot" className="chatbot-btn" title="Abrir Chatbot">
        💬
      </Link>
    </>
  );
}
