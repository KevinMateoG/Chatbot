import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Index from './index';
import Chatbot from './chatbot';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Index />} />
        <Route path="/chatbot" element={<Chatbot />} />
      </Routes>
    </Router>
  );
}

export default App;