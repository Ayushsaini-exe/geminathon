import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import api from '../../api/client';

export default function FarmerDashboard() {
  const { user } = useAuth();
  const [esg, setEsg] = useState(null);

  useEffect(() => {
    if (user?.farmer_id) {
      api.get(`/api/esg/score/${user.farmer_id}`).then(setEsg).catch(() => {});
    }
  }, [user]);

  const features = [
    { to: '/chat',    icon: '💬', color: 'green',  title: 'AI Chat',          desc: 'Ask anything about crops, diseases, or farming practices' },
    { to: '/disease', icon: '🔬', color: 'red',    title: 'Disease Scanner',  desc: 'Upload leaf images for instant AI-powered diagnosis' },
    { to: '/soil',    icon: '🧪', color: 'gold',   title: 'Soil Health',      desc: 'Fetch your Soil Health Card and get fertilizer advice' },
    { to: '/harvest', icon: '🌾', color: 'orange', title: 'Harvest Advisor',  desc: 'Optimize harvest timing with weather and market analysis' },
    { to: '/esg',     icon: '📊', color: 'blue',   title: 'ESG Score',        desc: 'Track your sustainability score and progress' },
    { to: '/reports', icon: '📄', color: 'green',  title: 'Reports',          desc: 'Generate PDF sustainability reports with QR verification' },
  ];

  return (
    <>
      <div className="page-header">
        <div>
          <div className="page-title">Welcome, {user?.name || 'Farmer'} 👋</div>
          <div className="page-subtitle">Your agricultural intelligence dashboard</div>
        </div>
      </div>

      <div className="page-content">
        <div className="stats-grid">
          <div className="stat-card" style={{ animationDelay: '0s' }}>
            <div className="stat-icon">🌱</div>
            <div className="stat-value">{user?.location || '—'}</div>
            <div className="stat-label">Location</div>
          </div>
          <div className="stat-card" style={{ animationDelay: '0.1s' }}>
            <div className="stat-icon">📊</div>
            <div className="stat-value">{esg?.overall_score?.toFixed(1) || '—'}</div>
            <div className="stat-label">ESG Score</div>
          </div>
          <div className="stat-card" style={{ animationDelay: '0.2s' }}>
            <div className="stat-icon">🧬</div>
            <div className="stat-value">{esg?.environmental?.toFixed(1) || '—'}</div>
            <div className="stat-label">Environmental</div>
          </div>
          <div className="stat-card" style={{ animationDelay: '0.3s' }}>
            <div className="stat-icon">📈</div>
            <div className="stat-value">{esg?.trend || '—'}</div>
            <div className="stat-label">Trend</div>
          </div>
        </div>

        <h2 style={{ fontSize: '1.2rem', fontWeight: 600, marginBottom: '16px', color: 'var(--earth-900)' }}>
          AI-Powered Tools
        </h2>

        <div className="features-grid">
          {features.map((f, i) => (
            <Link to={f.to} className="feature-card" key={f.to} style={{ animationDelay: `${i * 0.05}s` }}>
              <div className={`feature-icon ${f.color}`}>{f.icon}</div>
              <div className="feature-title">{f.title}</div>
              <div className="feature-desc">{f.desc}</div>
            </Link>
          ))}
        </div>
      </div>
    </>
  );
}
