import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import Layout from './components/Layout';
import Login from './pages/Login';
import Register from './pages/Register';
import FarmerDashboard from './pages/farmer/Dashboard';
import Chat from './pages/farmer/Chat';
import DiseaseScanner from './pages/farmer/DiseaseScanner';
import SoilHealth from './pages/farmer/SoilHealth';
import HarvestAdvisor from './pages/farmer/HarvestAdvisor';
import ESGDashboard from './pages/farmer/ESGDashboard';
import Reports from './pages/farmer/Reports';
import ManagerDashboard from './pages/manager/Dashboard';
import FarmerList from './pages/manager/FarmerList';

function ProtectedRoute({ children }) {
  const { user, loading } = useAuth();
  if (loading) {
    return (
      <div className="loading-screen">
        <div className="loading-content">
          <div className="loading-icon">🌱</div>
          <div className="loading-text">Loading AgroFix...</div>
        </div>
      </div>
    );
  }
  return user ? children : <Navigate to="/login" />;
}

function DashboardRouter() {
  const { user } = useAuth();
  if (user?.role === 'manager') return <ManagerDashboard />;
  return <FarmerDashboard />;
}

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />

          <Route element={<ProtectedRoute><Layout /></ProtectedRoute>}>
            <Route path="/dashboard" element={<DashboardRouter />} />

            {/* Farmer routes */}
            <Route path="/chat" element={<Chat />} />
            <Route path="/disease" element={<DiseaseScanner />} />
            <Route path="/soil" element={<SoilHealth />} />
            <Route path="/harvest" element={<HarvestAdvisor />} />
            <Route path="/esg" element={<ESGDashboard />} />
            <Route path="/reports" element={<Reports />} />

            {/* Manager routes */}
            <Route path="/farmers" element={<FarmerList />} />
          </Route>

          <Route path="*" element={<Navigate to="/dashboard" />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}
