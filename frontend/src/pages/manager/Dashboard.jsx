import { useState, useEffect } from 'react';
import api from '../../api/client';

export default function ManagerDashboard() {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.get('/api/manager/stats')
      .then(setStats)
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="loading-screen">
        <div className="loading-content">
          <div className="loading-icon">📈</div>
          <div className="loading-text">Loading dashboard...</div>
        </div>
      </div>
    );
  }

  const cards = [
    { icon: '👥', value: stats?.total_farmers ?? 0, label: 'Total Farmers' },
    { icon: '🔐', value: stats?.total_users ?? 0, label: 'Registered Users' },
    { icon: '🔬', value: stats?.total_disease_scans ?? 0, label: 'Disease Scans' },
    { icon: '📄', value: stats?.total_reports ?? 0, label: 'Reports Generated' },
    { icon: '📊', value: stats?.avg_esg_score ?? 0, label: 'Avg ESG Score' },
  ];

  return (
    <>
      <div className="page-header">
        <div>
          <div className="page-title">Manager Dashboard 📈</div>
          <div className="page-subtitle">Platform overview and farmer management</div>
        </div>
      </div>
      <div className="page-content">
        <div className="stats-grid">
          {cards.map((c, i) => (
            <div className="stat-card fade-in" key={c.label} style={{ animationDelay: `${i * 0.07}s` }}>
              <div className="stat-icon">{c.icon}</div>
              <div className="stat-value">{c.value}</div>
              <div className="stat-label">{c.label}</div>
            </div>
          ))}
        </div>
      </div>
    </>
  );
}
