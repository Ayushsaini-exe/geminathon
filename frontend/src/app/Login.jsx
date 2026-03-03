import { useNavigate } from 'react-router-dom';
import './Login.css';

export default function Login() {
    const navigate = useNavigate();

    const handleFarmerLogin = () => {
        // Basic mock login - just routes to dashboard for now
        navigate('/dashboard');
    };

    const handleIndustryLogin = () => {
        alert('Industry Partner Portal is coming soon!');
    };

    return (
        <div className="login-container">
            <div className="login-visual-half">
                <div className="visual-overlay"></div>
                <div className="visual-content">
                    <h1>Agro<span>Fix</span></h1>
                    <p className="tagline">The future of agricultural intelligence is here.</p>
                </div>
            </div>

            <div className="login-form-half">
                <div className="login-card glass-panel">
                    <h2>Welcome to AgroFix</h2>
                    <p className="subtitle">Please select your portal to continue.</p>

                    <div className="role-selection">
                        <button
                            className="role-card primary-role"
                            onClick={handleFarmerLogin}
                        >
                            <h3>Farmer Portal</h3>
                            <p>Access your digital twin, get crop advice, and view ESG scores.</p>
                        </button>

                        <button
                            className="role-card secondary-role"
                            onClick={handleIndustryLogin}
                        >
                            <h3>Industry Partner</h3>
                            <p>Access aggregated sustainability reports and analytics.</p>
                            <span className="badge">Coming Soon</span>
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
}
