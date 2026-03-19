import { useState, useEffect } from 'react';
import { useAuth } from '../../context/AuthContext';
import api from '../../api/client';

export default function ESGDashboard() {
  const { user } = useAuth();
  const [score, setScore] = useState(null);
  const [actionType, setActionType] = useState('organic_fertilizer');
  const [details, setDetails] = useState('5 tonnes applied');
  const [loading, setLoading] = useState(false);

  const loadScore = () => {
    if (user?.farmer_id) {
      api.get(`/api/esg/score/${user.farmer_id}`).then(setScore).catch(() => {});
    }
  };

  useEffect(() => { loadScore(); }, [user]);

  const logAction = async () => {
    setLoading(true);
    try {
      await api.post('/api/esg/action', {
        farmer_id: user?.farmer_id,
        action_type: actionType,
        details: { note: details },
      });
      loadScore();
    } catch {
    } finally {
      setLoading(false);
    }
  };

  const radius = 54;
  const circumference = 2 * Math.PI * radius;
  const progress = score ? (score.overall_score / 100) * circumference : 0;
  const scoreColor = score?.overall_score >= 70 ? 'var(--green-600)' : score?.overall_score >= 40 ? 'var(--gold-500)' : 'var(--red-500)';

  return (
    <>
      <div className="page-header">
        <div>
          <div className="page-title">ESG Score 📊</div>
          <div className="page-subtitle">Track your environmental, social, and governance sustainability</div>
        </div>
      </div>
      <div className="page-content">
        <div style={{ display: 'grid', gridTemplateColumns: '340px 1fr', gap: 24, alignItems: 'start' }}>
          <div>
            {score && (
              <div className="card fade-in" style={{ textAlign: 'center', marginBottom: 16 }}>
                <div className="score-ring">
                  <svg width="140" height="140">
                    <circle cx="70" cy="70" r={radius} fill="none" stroke="var(--gray-200)" strokeWidth="10" />
                    <circle cx="70" cy="70" r={radius} fill="none" stroke={scoreColor} strokeWidth="10"
                      strokeDasharray={circumference} strokeDashoffset={circumference - progress}
                      strokeLinecap="round" style={{ transition: 'stroke-dashoffset 1s ease' }} />
                  </svg>
                  <div className="score-value">{score.overall_score?.toFixed(0)}</div>
                </div>
                <div className="stats-grid" style={{ gridTemplateColumns: '1fr 1fr 1fr', gap: 8 }}>
                  <div style={{ textAlign: 'center' }}>
                    <div style={{ fontSize: '1.2rem', fontWeight: 700, color: 'var(--green-700)' }}>{score.environmental?.toFixed(0)}</div>
                    <div style={{ fontSize: '0.7rem', color: 'var(--gray-500)' }}>Environment</div>
                  </div>
                  <div style={{ textAlign: 'center' }}>
                    <div style={{ fontSize: '1.2rem', fontWeight: 700, color: 'var(--blue-500)' }}>{score.social?.toFixed(0)}</div>
                    <div style={{ fontSize: '0.7rem', color: 'var(--gray-500)' }}>Social</div>
                  </div>
                  <div style={{ textAlign: 'center' }}>
                    <div style={{ fontSize: '1.2rem', fontWeight: 700, color: 'var(--gold-500)' }}>{score.governance?.toFixed(0)}</div>
                    <div style={{ fontSize: '0.7rem', color: 'var(--gray-500)' }}>Governance</div>
                  </div>
                </div>
                <div className={`badge ${score.trend === 'improving' ? 'green' : score.trend === 'declining' ? 'red' : 'gold'}`}
                  style={{ marginTop: 12 }}>{score.trend}</div>
              </div>
            )}

            <div className="card">
              <h3 style={{ fontSize: '0.95rem', fontWeight: 600, marginBottom: 12 }}>Log Sustainability Action</h3>
              <div className="form-group">
                <label style={{ color: 'var(--gray-600)', fontSize: '0.8rem' }}>Action Type</label>
                <select className="form-select" value={actionType} onChange={e => setActionType(e.target.value)}
                  style={{ background: 'var(--gray-50)', color: 'var(--earth-900)', border: '1px solid var(--gray-300)' }}>
                  {['organic_fertilizer','water_conservation','crop_rotation','solar_usage','community_training','record_keeping'].map(a =>
                    <option key={a} value={a}>{a.replace(/_/g, ' ')}</option>
                  )}
                </select>
              </div>
              <div className="form-group">
                <label style={{ color: 'var(--gray-600)', fontSize: '0.8rem' }}>Details</label>
                <input className="form-input" value={details} onChange={e => setDetails(e.target.value)}
                  style={{ background: 'var(--gray-50)', color: 'var(--earth-900)', border: '1px solid var(--gray-300)' }} />
              </div>
              <button className="btn btn-green" onClick={logAction} disabled={loading}
                style={{ width: '100%', justifyContent: 'center' }}>
                {loading ? <><span className="spinner" /> Logging...</> : '✅ Log Action'}
              </button>
            </div>
          </div>

          <div>
            {score?.history && score.history.length > 0 && (
              <div className="result-section">
                <div className="result-header">📈 Score History</div>
                <div style={{ padding: 16 }}>
                  <table className="data-table">
                    <thead>
                      <tr>
                        <th>Date</th>
                        <th>Score</th>
                        <th>Actions</th>
                      </tr>
                    </thead>
                    <tbody>
                      {score.history.map((h, i) => (
                        <tr key={i}>
                          <td>{h.date}</td>
                          <td><strong>{h.score?.toFixed(1)}</strong></td>
                          <td>{h.actions_count}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </>
  );
}
