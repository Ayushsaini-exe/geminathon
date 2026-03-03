import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Login from './app/Login';
import Layout from './components/Layout';
import Dashboard from './app/dashboard/Dashboard';
import GenericScanner from './app/scanners/GenericScanner';
import Chat from './app/chat/Chat';
import HarvestAdvisor from './app/forms/HarvestAdvisor';
import SoilHealth from './app/forms/SoilHealth';
import Sustainability from './app/sustainability/Sustainability';
import './App.css';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/login" element={<Login />} />

        {/* Protected Farmer Routes */}
        <Route path="/" element={<Layout />}>
          <Route index element={<Navigate to="/dashboard" replace />} />
          <Route path="dashboard" element={<Dashboard />} />
          <Route path="chat" element={<Chat />} />
          <Route path="disease-scanner" element={<GenericScanner title="Crop Disease Scanner" description="Upload a clear photo of the affected plant leaf for AI diagnosis." isPesticide={false} />} />
          <Route path="pesticide-check" element={<GenericScanner title="Pesticide Authenticity Check" description="Take a photo of the pesticide bottle showing the batch number or QR code." isPesticide={true} />} />
          <Route path="soil-health" element={<SoilHealth />} />
          <Route path="harvest-advisor" element={<HarvestAdvisor />} />
          <Route path="digital-twin" element={<div className="placeholder-page" style={{ textAlign: 'center', padding: '4rem' }}><h2>Digital Twin Map</h2><p>Interactive farm visualization coming in next phase.</p></div>} />
          <Route path="sustainability" element={<Sustainability />} />
        </Route>
      </Routes>
    </Router>
  );
}

export default App;
