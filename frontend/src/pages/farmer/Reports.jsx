import { useState } from 'react';
import { useAuth } from '../../context/AuthContext';
import api from '../../api/client';

export default function Reports() {
  const { user } = useAuth();
  const [sections, setSections] = useState(['soil', 'chemicals', 'esg']);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const allSections = ['soil', 'chemicals', 'esg', 'crops', 'weather'];

  const toggle = (s) => {
    setSections(prev =>
      prev.includes(s) ? prev.filter(x => x !== s) : [...prev, s]
    );
  };

  const generate = async () => {
    setLoading(true);
    setError('');
    try {
      const data = await api.post('/api/report/generate', {
        farmer_id: user?.farmer_id,
        include_sections: sections,
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
          <div className="page-title">Reports 📄</div>
          <div className="page-subtitle">Generate PDF sustainability reports with QR verification</div>
        </div>
      </div>
      <div className="page-content">
        <div className="card" style={{ maxWidth: 500, marginBottom: 24 }}>
          <h3 style={{ fontSize: '0.95rem', fontWeight: 600, marginBottom: 16 }}>Select Report Sections</h3>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8, marginBottom: 16 }}>
            {allSections.map(s => (
              <button
                key={s}
                className={`badge ${sections.includes(s) ? 'green' : ''}`}
                onClick={() => toggle(s)}
                style={{
                  cursor: 'pointer',
                  padding: '8px 16px',
                  fontSize: '0.85rem',
                  border: sections.includes(s) ? 'none' : '1px solid var(--gray-300)',
                  background: sections.includes(s) ? 'var(--green-200)' : 'var(--white)',
                  color: sections.includes(s) ? 'var(--green-800)' : 'var(--gray-600)',
                }}
              >
                {s}
              </button>
            ))}
          </div>
          <button className="btn btn-green" onClick={generate} disabled={loading || sections.length === 0}
            style={{ width: '100%', justifyContent: 'center' }}>
            {loading ? <><span className="spinner" /> Generating PDF...</> : '📄 Generate Report'}
          </button>
        </div>

        {error && <div className="error-message" style={{ background: 'var(--red-100)', color: 'var(--red-500)', maxWidth: 500 }}>{error}</div>}

        {result && (
          <div className="card fade-in" style={{ maxWidth: 500 }}>
            <h3 style={{ marginBottom: 12 }}>✅ Report Generated!</h3>
            <div style={{ fontSize: '0.9rem', color: 'var(--gray-600)', lineHeight: 1.8 }}>
              <p><strong>Report ID:</strong> {result.report_id}</p>
              <p><strong>Generated:</strong> {result.generated_at}</p>
              {result.pdf_url && <p><strong>PDF:</strong> <a href={result.pdf_url} target="_blank" rel="noopener noreferrer" style={{ color: 'var(--green-700)' }}>Download Report</a></p>}
              {result.qr_url && <p><strong>QR Code:</strong> <a href={result.qr_url} target="_blank" rel="noopener noreferrer" style={{ color: 'var(--green-700)' }}>View QR</a></p>}
            </div>
          </div>
        )}
      </div>
    </>
  );
}
