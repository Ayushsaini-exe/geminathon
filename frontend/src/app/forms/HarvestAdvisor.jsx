import { useState } from 'react';
import { CalendarDays, MapPin, Sprout, TrendingUp, AlertTriangle, CheckCircle, BarChart3 } from 'lucide-react';
import { analyzeHarvest } from '../../api';
import './Forms.css';

export default function HarvestAdvisor() {
    const [loading, setLoading] = useState(false);
    const [result, setResult] = useState(null);
    const [error, setError] = useState(null);

    const handleAnalyze = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError(null);

        try {
            // Read form data (In a full app we'd bind inputs to state)
            const form = e.target;
            const cropType = form.elements[0].value;
            const sowingDays = parseInt(form.elements[1].value);
            const mandiDist = parseFloat(form.elements[2].value);

            const payload = {
                crop_type: cropType,
                sowing_days: sowingDays,
                mandi_distance_km: mandiDist
            };

            const data = await analyzeHarvest(payload);
            setResult({
                recommendation: data.recommendation || "Optimal Window Found",
                reason: data.reasoning || "Based on market trends and weather.",
                scenarios: data.scenarios || []
            });
        } catch (err) {
            setError(err.message);
            // Fallback mock
            setResult({
                recommendation: "MOCK: Harvest +3 Days",
                reason: "Mock data: Mandi prices are expected to rise.",
                scenarios: [
                    { day: "Today", profit: "₹45,000", risk: "Low", status: "neutral" },
                    { day: "+2 Days", profit: "₹46,200", risk: "Low", status: "neutral" },
                    { day: "+3 Days", profit: "₹46,800", risk: "Low", status: "optimal" }
                ]
            });
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="form-page">
            <div className="form-header">
                <h2>AI Harvest Advisor</h2>
                <p>Input your crop details to determine the most profitable harvest window.</p>
            </div>

            <div className="form-content">
                <div className="input-card glass-panel">
                    <h3>Crop Details</h3>
                    <form className="advisor-form" onSubmit={handleAnalyze}>
                        <div className="form-group">
                            <label><Sprout size={16} /> Crop Type</label>
                            <select required defaultValue="wheat">
                                <option value="wheat">Wheat</option>
                                <option value="rice">Rice</option>
                                <option value="cotton">Cotton</option>
                                <option value="tomato">Tomato</option>
                            </select>
                        </div>

                        <div className="form-group">
                            <label><CalendarDays size={16} /> Days Since Sowing</label>
                            <input type="number" required placeholder="e.g., 120" defaultValue="115" />
                        </div>

                        <div className="form-group">
                            <label><MapPin size={16} /> Nearest Mandi Distance (km)</label>
                            <input type="number" required placeholder="e.g., 25" defaultValue="15" />
                        </div>

                        <button type="submit" className="btn-primary analyze-btn" disabled={loading}>
                            {loading ? 'Running AI Simulations...' : 'Analyze Market Scenarios'}
                        </button>
                    </form>
                </div>

                <div className={`results-card glass-panel ${result ? 'active' : ''}`}>
                    {!result && !loading ? (
                        <div className="empty-state">
                            <BarChart3 size={48} className="empty-icon" />
                            <h3>Awaiting Input</h3>
                            <p>Submit your crop details to view AI profit predictions based on real-time weather and Mandi prices.</p>
                        </div>
                    ) : loading ? (
                        <div className="loading-state">
                            <div className="spinner"></div>
                            <p>Fetching Agmarknet Prices...</p>
                            <p>Checking OpenWeather API...</p>
                        </div>
                    ) : (
                        <div className="analysis-results">
                            <div className="optimal-callout">
                                <CheckCircle size={24} color="var(--color-success)" />
                                <div>
                                    <h4>Optimal Window: {result.recommendation}</h4>
                                    <p>{result.reason}</p>
                                </div>
                            </div>

                            <div className="scenarios-list">
                                <h4>3-Day Projection</h4>
                                {result.scenarios.map((s, idx) => (
                                    <div key={idx} className={`scenario-item ${s.status}`}>
                                        <div className="s-day">{s.day}</div>
                                        <div className="s-metrics">
                                            <span className="s-profit">{s.profit}</span>
                                            <span className="s-risk"><AlertTriangle size={14} /> Risk: {s.risk}</span>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}
