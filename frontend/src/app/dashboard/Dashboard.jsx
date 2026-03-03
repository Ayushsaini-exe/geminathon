import { useNavigate } from 'react-router-dom';
import './Dashboard.css';
import { Sprout, CloudRain, Sun, Leaf } from 'lucide-react';

export default function Dashboard() {
    const navigate = useNavigate();

    return (
        <div className="dashboard-wrapper">
            <div className="welcome-banner glass-panel">
                <div>
                    <h2>Farm Overview</h2>
                    <p>Here is the latest intelligence gathered for your fields.</p>
                </div>
                <div className="weather-widget">
                    <CloudRain size={24} color="var(--color-primary)" />
                    <div>
                        <strong>18°C</strong>
                        <span>Light Rain Expected</span>
                    </div>
                </div>
            </div>

            <div className="stats-grid">
                <div className="stat-card glass-panel">
                    <div className="stat-icon"><Leaf color="var(--color-success)" /></div>
                    <div className="stat-info">
                        <h3>ESG Score</h3>
                        <p className="stat-value text-success">85/100</p>
                        <span className="stat-trend">↑ 2% this month</span>
                    </div>
                </div>

                <div className="stat-card glass-panel">
                    <div className="stat-icon"><Sprout color="var(--color-secondary)" /></div>
                    <div className="stat-info">
                        <h3>Upcoming Harvest</h3>
                        <p className="stat-value">Wheat (North Field)</p>
                        <span className="stat-trend warning">Optimal: +3 Days</span>
                    </div>
                </div>

                <div className="stat-card glass-panel">
                    <div className="stat-icon"><Sun color="var(--color-warning)" /></div>
                    <div className="stat-info">
                        <h3>Digital Twin Status</h3>
                        <p className="stat-value">2 Alerts</p>
                        <span className="stat-trend danger">Check South Sector</span>
                    </div>
                </div>
            </div>

            <div className="quick-actions-section">
                <h3>Quick Actions</h3>
                <div className="actions-grid">
                    <button className="action-btn primary" onClick={() => navigate('/chat')}>Ask Agri-AI</button>
                    <button className="action-btn secondary" onClick={() => navigate('/disease-scanner')}>Scan Disease</button>
                    <button className="action-btn outline" onClick={() => navigate('/soil-health')}>Update Soil Health</button>
                </div>
            </div>
        </div>
    );
}
