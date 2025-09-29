import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Index from './index';
import Chatbot from './chatbot';
import './App.css';

function App() {
  return (
    <Router>
      <div className="app-container">
        <Routes>
          <Route path="/" element={<Index />} />
          <Route path="/chatbot" element={<Chatbot />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;