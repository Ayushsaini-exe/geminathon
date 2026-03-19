import { useState } from 'react';
import { useAuth } from '../../context/AuthContext';
import api from '../../api/client';

export default function HarvestAdvisor() {
  const { user } = useAuth();
  const [form, setForm] = useState({ crop: 'wheat', location: user?.location || 'Punjab', current_maturity_pct: 85 });
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const set = (k) => (e) => setForm({ ...form, [k]: e.target.value });

  const analyze = async () => {
    setLoading(true);
    setError('');
    try {
      const data = await api.post('/api/harvest/analyze', {
        farmer_id: user?.farmer_id,
        ...form,
        current_maturity_pct: parseFloat(form.current_maturity_pct),
      });
      setResult(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <div className="page-header">
        <div>
          <div className="page-title">Harvest Advisor 🌾</div>
          <div className="page-subtitle">Optimize harvest timing with weather and market analysis</div>
        </div>
      </div>
      <div className="page-content">
        <div className="card" style={{ maxWidth: 500, marginBottom: 24 }}>
          <div className="form-group">
            <label style={{ color: 'var(--earth-900)', fontWeight: 600 }}>Crop</label>
            <input className="form-input" value={form.crop} onChange={set('crop')}
              style={{ background: 'var(--gray-50)', color: 'var(--earth-900)', border: '1px solid var(--gray-300)' }} />
          </div>
          <div className="form-group">
            <label style={{ color: 'var(--earth-900)', fontWeight: 600 }}>Location</label>
            <input className="form-input" value={form.location} onChange={set('location')}
              style={{ background: 'var(--gray-50)', color: 'var(--earth-900)', border: '1px solid var(--gray-300)' }} />
          </div>
          <div className="form-group">
            <label style={{ color: 'var(--earth-900)', fontWeight: 600 }}>Crop Maturity %</label>
            <input type="number" className="form-input" value={form.current_maturity_pct} onChange={set('current_maturity_pct')}
              style={{ background: 'var(--gray-50)', color: 'var(--earth-900)', border: '1px solid var(--gray-300)' }} min={0} max={100} />
          </div>
          <button className="btn btn-green" onClick={analyze} disabled={loading}
            style={{ width: '100%', justifyContent: 'center' }}>
            {loading ? <><span className="spinner" /> Analyzing...</> : '📊 Analyze Scenarios'}
          </button>
        </div>

        {error && <div className="error-message" style={{ background: 'var(--red-100)', color: 'var(--red-500)', maxWidth: 500 }}>{error}</div>}

        {result && (
          <div className="fade-in">
            <div className="result-section" style={{ marginBottom: 16 }}>
              <div className="result-header">🏆 Recommended: {result.recommended_scenario}</div>
            </div>

            <div style={{ overflowX: 'auto' }}>
              <table className="data-table">
                <thead>
                  <tr>
                    <th>Scenario</th>
                    <th>Yield (q/acre)</th>
                    <th>Price (₹/q)</th>
                    <th>Net Profit (₹)</th>
                    <th>Weather Risk</th>
                  </tr>
                </thead>
                <tbody>
                  {result.scenarios?.map((s, i) => (
                    <tr key={i}>
                      <td><strong>{s.label}</strong></td>
                      <td>{s.estimated_yield}</td>
                      <td>₹{s.market_price}</td>
                      <td style={{ color: s.net_profit > 0 ? 'var(--green-700)' : 'var(--red-500)', fontWeight: 600 }}>
                        ₹{s.net_profit?.toLocaleString()}
                      </td>
                      <td>
                        <span className={`badge ${s.weather_risk === 'high' ? 'red' : s.weather_risk === 'medium' ? 'orange' : 'green'}`}>
                          {s.weather_risk}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            {result.recommendation && (
              <div className="result-section" style={{ marginTop: 16 }}>
                <div className="result-header">💡 AI Recommendation</div>
                <div className="result-body" style={{ whiteSpace: 'pre-wrap' }}>{result.recommendation}</div>
              </div>
            )}
          </div>
        )}
      </div>
    </>
  );
}
