import { useState } from 'react';
import { useAuth } from '../../context/AuthContext';
import api from '../../api/client';

export default function SoilHealth() {
  const { user } = useAuth();
  const [shcId, setShcId] = useState('SHC-2024-001');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const fetch = async () => {
    setLoading(true);
    setError('');
    try {
      const data = await api.post('/api/shc/fetch', {
        farmer_id: user?.farmer_id,
        shc_id: shcId,
      });
      setResult(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const soil = result?.soil_parameters;

  return (
    <>
      <div className="page-header">
        <div>
          <div className="page-title">Soil Health 🧪</div>
          <div className="page-subtitle">Fetch your Soil Health Card data and get AI-powered fertilizer advice</div>
        </div>
      </div>
      <div className="page-content">
        <div className="card" style={{ maxWidth: 500, marginBottom: 24 }}>
          <div className="form-group">
            <label style={{ color: 'var(--earth-900)', fontWeight: 600 }}>SHC ID</label>
            <input
              className="form-input"
              style={{ background: 'var(--gray-50)', color: 'var(--earth-900)', border: '1px solid var(--gray-300)' }}
              placeholder="SHC-2024-001"
              value={shcId}
              onChange={e => setShcId(e.target.value)}
            />
          </div>
          <button className="btn btn-green" onClick={fetch} disabled={loading || !shcId}
            style={{ width: '100%', justifyContent: 'center' }}>
            {loading ? <><span className="spinner" /> Fetching...</> : '🧪 Fetch Soil Data'}
          </button>
        </div>

        {error && <div className="error-message" style={{ background: 'var(--red-100)', color: 'var(--red-500)', maxWidth: 500 }}>{error}</div>}

        {soil && (
          <div className="fade-in">
            <div className="stats-grid" style={{ maxWidth: 700 }}>
              {[
                { label: 'Nitrogen (N)', value: soil.N, unit: 'kg/ha' },
                { label: 'Phosphorus (P)', value: soil.P, unit: 'kg/ha' },
                { label: 'Potassium (K)', value: soil.K, unit: 'kg/ha' },
                { label: 'pH', value: soil.ph, unit: '' },
                { label: 'Organic Carbon', value: soil.organic_carbon, unit: '%' },
                { label: 'EC', value: soil.ec, unit: 'dS/m' },
              ].map(s => (
                <div className="stat-card" key={s.label}>
                  <div className="stat-value">{s.value ?? '—'}</div>
                  <div className="stat-label">{s.label} {s.unit && `(${s.unit})`}</div>
                </div>
              ))}
            </div>

            <div className="result-section" style={{ marginTop: 16 }}>
              <div className="result-header">🌿 Fertilizer Advice (AI-Generated)</div>
              <div className="result-body" style={{ whiteSpace: 'pre-wrap' }}>
                {result.fertilizer_advice}
              </div>
            </div>
          </div>
        )}
      </div>
    </>
  );
}
