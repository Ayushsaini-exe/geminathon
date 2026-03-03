import { useState } from 'react';
import { Droplet, FileText, CheckCircle, Search, Beaker, Sprout } from 'lucide-react';
import { fetchSoilHealth } from '../../api';
import './Forms.css'; // Reusing the layout shell from Harvest Advisor

export default function SoilHealth() {
    const [loading, setLoading] = useState(false);
    const [result, setResult] = useState(null);
    const [error, setError] = useState(null);
    const [shcId, setShcId] = useState('');

    const handleFetch = async (e) => {
        e.preventDefault();
        if (!shcId.trim()) return;

        setLoading(true);
        setError(null);

        try {
            const data = await fetchSoilHealth(shcId);
            setResult({
                farmerName: data.farmer_name || "Unknown Farmer",
                dateTested: data.issue_date || "N/A",
                ph: data.ph_level || "N/A",
                organicCarbon: data.organic_carbon ? `${data.organic_carbon}%` : "N/A",
                npk: {
                    n: data.nitrogen_status || "Medium",
                    p: data.phosphorus_status || "Medium",
                    k: data.potassium_status || "Medium"
                },
                recommendation: data.recommendation || "Ensure balanced fertilizer application."
            });
        } catch (err) {
            setError(err.message);
            // Fallback mock
            setResult({
                farmerName: "MOCK: Rajesh Kumar",
                dateTested: "2025-10-12",
                ph: 6.8,
                organicCarbon: "0.45%",
                npk: { n: "Low", p: "Medium", k: "High" },
                recommendation: "Mock Recommendation: Apply 25kg/acre of Urea and 10kg/acre of DAP."
            });
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="form-page">
            <div className="form-header">
                <h2>Soil Health Intelligence</h2>
                <p>Sync your Government Soil Health Card to get personalized fertilizer recommendations.</p>
            </div>

            <div className="form-content">
                <div className="input-card glass-panel" style={{ height: 'fit-content' }}>
                    <h3>Fetch Soil Profile</h3>
                    <form className="advisor-form" onSubmit={handleFetch}>
                        <div className="form-group">
                            <label><FileText size={16} /> 12-Digit SHC Number</label>
                            <input
                                type="text"
                                required
                                placeholder="e.g., 1234-5678-9012"
                                value={shcId}
                                onChange={(e) => setShcId(e.target.value)}
                            />
                        </div>

                        <button type="submit" className="btn-primary analyze-btn" disabled={loading || !shcId}>
                            {loading ? 'Connecting to Govt Database...' : <><Search size={18} /> Fetch Profile</>}
                        </button>
                    </form>
                </div>

                <div className={`results-card glass-panel ${result ? 'active' : ''}`}>
                    {!result && !loading ? (
                        <div className="empty-state">
                            <Droplet size={48} className="empty-icon" />
                            <h3>No Profile Loaded</h3>
                            <p>Enter your SHC number to import your soil parameters and let the AI generate a crop nutrition plan.</p>
                        </div>
                    ) : loading ? (
                        <div className="loading-state">
                            <div className="spinner"></div>
                            <p>Analyzing NPK Ratios...</p>
                        </div>
                    ) : (
                        <div className="analysis-results">
                            <div className="optimal-callout" style={{ marginBottom: '1.5rem' }}>
                                <CheckCircle size={24} color="var(--color-success)" />
                                <div>
                                    <h4>Profile Synced</h4>
                                    <p>Data imported for {result.farmerName} on {result.dateTested}</p>
                                </div>
                            </div>

                            <div className="shc-parameters">
                                <h4><Beaker size={18} /> Lab Parameters</h4>
                                <div className="params-grid">
                                    <div className="param-box">
                                        <span>pH Level</span>
                                        <strong>{result.ph} <em>(Optimal)</em></strong>
                                    </div>
                                    <div className="param-box">
                                        <span>Organic Carbon</span>
                                        <strong className="text-warning">{result.organicCarbon} <em>(Low)</em></strong>
                                    </div>
                                </div>

                                <div className="npk-row">
                                    <div className="npk bad"><strong>N</strong> {result.npk.n}</div>
                                    <div className="npk okay"><strong>P</strong> {result.npk.p}</div>
                                    <div className="npk good"><strong>K</strong> {result.npk.k}</div>
                                </div>
                            </div>

                            <div className="treatment-plan" style={{ marginTop: '2rem', marginBottom: 0 }}>
                                <h4><Sprout size={18} /> AI Fertilizer Recommendation</h4>
                                <p>{result.recommendation}</p>
                            </div>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}
